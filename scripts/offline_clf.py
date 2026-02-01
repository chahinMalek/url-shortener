import asyncio
from pathlib import Path

from core.services.classification.classifier.bert_classifier import BertUrlClassifier
from infra.db.repositories.urls import PostgresUrlRepository
from workers.config import config as worker_config
from workers.db import get_db_session, init_db_engine

LIMIT = 10


async def main():
    print(f"Fetching up to {LIMIT} pending URLs...")

    model_path = Path(worker_config.bert_model_path)
    tokenizer_path = Path(worker_config.bert_tokenizer_path)

    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return

    print(f"Loading BERT classifier from {model_path}...")
    classifier = BertUrlClassifier(model_path=model_path, tokenizer_path=tokenizer_path)

    print("Initializing database...")
    init_db_engine()

    async with get_db_session() as session:
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
