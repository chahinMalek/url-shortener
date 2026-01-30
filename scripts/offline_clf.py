import asyncio
from pathlib import Path

from app.container import db_service
from core.services.classification.classifier.bert_classifier import BertUrlClassifier
from infra.db.repositories.urls import PostgresUrlRepository
from workers.config import settings as worker_settings

LIMIT = 10


async def main():
    print(f"Fetching up to {LIMIT} pending URLs...")

    model_path = Path(worker_settings.BERT_MODEL_PATH)
    tokenizer_path = Path(worker_settings.BERT_TOKENIZER_PATH)

    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return

    print(f"Loading BERT classifier from {model_path}...")
    classifier = BertUrlClassifier(model_path=model_path, tokenizer_path=tokenizer_path)

    async for session in db_service.get_session():
        url_repo = PostgresUrlRepository(session)
        pending_urls = await url_repo.get_pending_urls(limit=LIMIT)

        if not pending_urls:
            print("No pending URLs found in the database.")
            return

        print(f"Found {len(pending_urls)} pending URLs. Starting classification...\n")

        for url in pending_urls:
            print(f"Classifying: {url.long_url} ({url.short_code})")
            try:
                result = await classifier.classify(url.long_url)
                print(f"- Result: {result.status.value}")
                print(f"- Score: {result.threat_score:.4f}")
            except Exception as e:
                print(f"- Error: {e}")
            print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
