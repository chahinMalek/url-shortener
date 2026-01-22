import asyncio
import logging
from pathlib import Path

from core.services.classification.classifier.online_classifier import OnlineClassifierV1


async def main():
    clf = OnlineClassifierV1(Path("assets/models/online_classifier_xgb_v1.0.0.onnx"))
    result = await clf.classify("https://google.com")
    logger = logging.getLogger(__name__)
    adapter = logging.LoggerAdapter(logger, {"service": "user-api", "env": "prod"})
    adapter.error(result)


if __name__ == "__main__":
    asyncio.run(main())
