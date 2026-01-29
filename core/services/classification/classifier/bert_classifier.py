from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

from core.entities.classifier_result import ClassifierResult
from core.enums.safety_status import SafetyStatus
from core.services.classification.classifier.onnx_classifier import OnnxUrlClassifier
from core.services.classification.exceptions import ClassificationError


class BertUrlClassifier(OnnxUrlClassifier):
    def __init__(self, model_path: Path, tokenizer_path: Path):
        super().__init__(model_path)
        self._tokenizer_path = tokenizer_path
        self._tokenizer = AutoTokenizer.from_pretrained(str(self._tokenizer_path))
        self._id2label = {0: SafetyStatus.SAFE, 1: SafetyStatus.MALICIOUS}
        self._label2id = {SafetyStatus.SAFE: 0, SafetyStatus.MALICIOUS: 1}

    @property
    def key(self) -> str:
        return self._model_name

    def build_inputs(self, url: str) -> dict:
        if not url or not url.strip():
            raise ClassificationError("Cannot classify empty URL")

        url = url.strip()
        try:
            encoded = self._tokenizer(
                url,
                padding="max_length",
                truncation=True,
                max_length=64,
                return_tensors="np",
            )
            return {
                "input_ids": encoded["input_ids"].astype(np.int64),
                "attention_mask": encoded["attention_mask"].astype(np.int64),
                "token_type_ids": encoded["token_type_ids"].astype(np.int64),
            }
        except Exception as e:
            raise ClassificationError(f"Failed to tokenize URL: {e}") from e

    async def classify(self, url: str) -> ClassifierResult:
        try:
            inputs = self.build_inputs(url)
            outputs = self._session.run(
                output_names=["logits"],
                input_feed={
                    "input_ids": inputs["input_ids"].astype(np.int64),
                    "attention_mask": inputs["attention_mask"].astype(np.int64),
                    "token_type_ids": inputs["token_type_ids"].astype(np.int64),
                },
            )

            logits = outputs[0]
            predicted_label = np.argmax(logits, axis=1)[0]
            predicted_status = self._id2label[predicted_label]
            probabilities = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
            threat_score = float(probabilities[0][self._label2id[SafetyStatus.MALICIOUS]])

            return ClassifierResult(
                status=predicted_status,
                threat_score=threat_score,
                classifier=self.key,
            )

        except Exception as e:
            raise ClassificationError(f"BERT inference failed: {e}") from e
