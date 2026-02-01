import asyncio
import time
from pathlib import Path

from core.entities.classification_result import ClassificationResult
from core.enums.safety_status import SafetyStatus
from core.services.classification import BertUrlClassifier
from core.services.classification.exceptions import ClassificationError
from infra.db.repositories.classification_results import PostgresClassificationResultRepository
from infra.db.repositories.urls import PostgresUrlRepository
from workers.celery_app import celery_app
from workers.config import get_config
from workers.db import get_db_session
from workers.logging import get_logger
from workers.models.batch_result import ClassificationBatchResult

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    soft_time_limit=get_config().task_soft_time_limit,
    time_limit=get_config().task_time_limit,
    max_retries=3,
    default_retry_delay=60,
)
def classify_pending_batch(self, batch_size: int | None = None) -> dict:
    """Task for classifying pending URLs in batches using the offline BERT classifier."""
    batch_size = batch_size or get_config().batch_size
    logger.info("classify_pending_batch_started", batch_size=batch_size, task_id=self.request.id)

    try:
        result = asyncio.run(_classify_pending_batch(batch_size))
        logger.info(
            "classify_pending_batch_completed",
            task_id=self.request.id,
            total_processed=result.total_processed,
            safe_count=result.safe_count,
            malicious_count=result.malicious_count,
            error_count=result.error_count,
            processing_time_ms=result.processing_time_ms,
        )
        return result.to_dict()

    except Exception as err:
        logger.error(
            "classify_pending_batch_failed", task_id=self.request.id, error=str(err), exc_info=True
        )
        raise self.retry(exc=err) from err


async def _classify_pending_batch(batch_size: int) -> ClassificationBatchResult:
    start_time = time.perf_counter()
    result = ClassificationBatchResult()

    # Initialize classifier
    model_path = Path(get_config().bert_model_path)
    tokenizer_path = Path(get_config().bert_tokenizer_path)

    if not model_path.exists():
        error_msg = f"BERT model not found at {model_path}"
        logger.error("bert_model_not_found", path=str(model_path))
        raise FileNotFoundError(error_msg)

    if not tokenizer_path.exists():
        error_msg = f"BERT tokenizer not found at {tokenizer_path}"
        logger.error("bert_tokenizer_not_found", path=str(tokenizer_path))
        raise FileNotFoundError(error_msg)

    classifier = BertUrlClassifier(model_path=model_path, tokenizer_path=tokenizer_path)
    logger.info("bert_classifier_initialized", model=classifier.key)

    async with get_db_session() as session:
        url_repo = PostgresUrlRepository(session)
        result_repo = PostgresClassificationResultRepository(session)

        pending_urls = await url_repo.get_pending_urls(limit=batch_size)
        logger.info("pending_urls_fetched", count=len(pending_urls))

        if not pending_urls:
            logger.info("no_pending_urls_found")
            result.processing_time_ms = (time.perf_counter() - start_time) * 1000
            return result

        for url_entity in pending_urls:
            result.total_processed += 1
            short_code = url_entity.short_code
            long_url = url_entity.long_url

            try:
                # track classification time
                classify_start = time.perf_counter()
                classifier_result = await classifier.classify(long_url)
                classify_time_ms = (time.perf_counter() - classify_start) * 1000

                classification_result = ClassificationResult.from_classifier_result(
                    classifier_result=classifier_result,
                    latency_ms=classify_time_ms,
                )

                # store classification result
                await result_repo.add(short_code=short_code, result=classification_result)

                # update URL safety status
                await url_repo.set_safety_status(
                    short_code=short_code,
                    status=classifier_result.status,
                    threat_score=classifier_result.threat_score,
                    classifier=classifier.key,
                )

                # disable URL if malicious
                if classifier_result.status == SafetyStatus.MALICIOUS:
                    await url_repo.disable(short_code)
                    result.malicious_count += 1
                    logger.info(
                        "url_classified_as_malicious",
                        short_code=short_code,
                        threat_score=classifier_result.threat_score,
                        url_disabled=True,
                    )
                else:
                    result.safe_count += 1
                    logger.debug(
                        "url_classified_as_safe",
                        short_code=short_code,
                        threat_score=classifier_result.threat_score,
                    )

                await session.commit()

            except ClassificationError as e:
                logger.warning(
                    "url_classification_failed",
                    short_code=short_code,
                    long_url=long_url,
                    error=str(e),
                )
                result.add_error(short_code=short_code, error=str(e))
                await session.rollback()

            except Exception as e:
                logger.error(
                    "unexpected_classification_error",
                    short_code=short_code,
                    long_url=long_url,
                    error=str(e),
                    exc_info=True,
                )
                result.add_error(short_code=short_code, error=f"Unexpected error: {e}")
                await session.rollback()

    result.processing_time_ms = (time.perf_counter() - start_time) * 1000
    return result
