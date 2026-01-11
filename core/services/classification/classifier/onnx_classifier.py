from abc import abstractmethod
from pathlib import Path

import onnxruntime as ort

from core.entities.url import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier
from core.services.classification.exceptions import ClassificationError
from core.services.classification.result import ClassificationResult


class OnnxUrlClassifier(BaseUrlClassifier):
    def __init__(
        self,
        model_path: Path,
        version: str,
        threshold: float = 0.5,
    ):
        self._model_path = model_path
        self._version = version
        self._threshold = threshold
        self._session: ort.InferenceSession | None = None

    @property
    def version(self) -> str:
        return self._version

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def _load_model(self) -> ort.InferenceSession:
        if self._session is None:
            if not self._model_path.exists():
                raise ClassificationError(
                    f"Model file not found: {self._model_path}",
                    classifier_version=self.key,
                )
            self._session = ort.InferenceSession(
                str(self._model_path),
                providers=["CPUExecutionProvider"],
            )
        return self._session

    @abstractmethod
    def _build_inputs(self, url: str) -> dict:
        pass

    async def classify(self, url: str) -> ClassificationResult:
        try:
            session = self._load_model()
            inputs = self._build_inputs(url)
            outputs = session.run(None, inputs)

            raw_output = outputs[0]
            if raw_output.ndim == 2 and raw_output.shape[1] == 2:
                threat_score = float(raw_output[0, 1])
            else:
                threat_score = float(raw_output[0])

            if threat_score >= self._threshold:
                status = SafetyStatus.MALICIOUS
            else:
                status = SafetyStatus.PENDING

            return ClassificationResult(
                status=status,
                threat_score=threat_score,
                classifier_version=self.key,
                details={"model_path": str(self._model_path)},
            )

        except ClassificationError:
            raise

        except Exception as e:
            raise ClassificationError(
                f"ONNX inference failed: {e}",
                classifier_version=self.key,
                original_error=e,
            ) from e
