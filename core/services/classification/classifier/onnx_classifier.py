from abc import abstractmethod
from pathlib import Path

import onnxruntime as ort

from core.entities.classification import ClassificationResult
from core.enums.safety_status import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier
from core.services.classification.exceptions import ClassificationError


class OnnxUrlClassifier(BaseUrlClassifier):
    def __init__(self, model_path: Path):
        self._model_path = model_path
        self._model_name = self._model_path.stem

        if not self._model_path.exists():
            raise ClassificationError(
                message=f"Model file not found: {self._model_path}",
            )
        self._session: ort.InferenceSession = ort.InferenceSession(
            str(self._model_path),
            providers=["CPUExecutionProvider"],
        )

    @property
    def key(self) -> str:
        return self._model_name

    @abstractmethod
    def build_inputs(self, url: str) -> dict:
        pass

    async def classify(self, url: str) -> ClassificationResult:
        try:
            inputs = self.build_inputs(url)
            outputs = self._session.run(None, inputs)

            prediction = outputs[0][0]
            probs = outputs[1][0]

            return ClassificationResult(
                status=SafetyStatus.MALICIOUS if prediction == 1 else SafetyStatus.PENDING,
                threat_score=float(probs[1]),
                classifier=self.key,
            )

        except Exception as e:
            raise ClassificationError(f"ONNX inference failed: {e}") from e
