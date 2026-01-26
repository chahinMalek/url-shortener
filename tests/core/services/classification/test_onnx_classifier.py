from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from core.enums.safety_status import SafetyStatus
from core.services.classification.classifier.online_classifier import OnlineClassifierV1
from core.services.classification.exceptions import ClassificationError


class TestOnnxClassifier:
    @pytest.fixture
    def model_path(self):
        return Path("assets/models/online_classifier_xgb_v1.0.0.onnx")

    @pytest.fixture
    def classifier(self, model_path):
        # mock the model file existence check (purpose: ci compatibility)
        with patch.object(Path, "exists", return_value=True):
            # mock the ONNX InferenceSession
            with patch(
                "core.services.classification.classifier.onnx_classifier.ort.InferenceSession"
            ) as mock_session_class:
                mock_session = Mock()
                # set default return value for session.run() - prediction=0, probs=[0.9, 0.1]
                mock_session.run.return_value = [[0], [[0.9, 0.1]]]
                mock_session_class.return_value = mock_session

                classifier = OnlineClassifierV1(model_path=model_path)
                return classifier

    def test_init_with_valid_model(self, classifier, model_path):
        assert classifier._model_path == model_path
        assert classifier._model_name == "online_classifier_xgb_v1.0.0"
        assert classifier._session is not None

    def test_init_with_missing_model_raises_error(self):
        non_existent_path = Path("assets/models/non_existent_model.onnx")

        with pytest.raises(ClassificationError) as exc_info:
            OnlineClassifierV1(model_path=non_existent_path)

        assert "Model file not found" in str(exc_info.value)
        assert str(non_existent_path) in str(exc_info.value)

    def test_key_property(self, classifier):
        assert classifier.key == "online_classifier_xgb_v1.0.0"

    def test_num_features_constant(self, classifier):
        assert classifier.NUM_FEATURES == 19
        assert OnlineClassifierV1.NUM_FEATURES == 19

    def test_build_inputs_url_length_features(self, classifier):
        url = "https://example.com/path?query=value"
        inputs = classifier.build_inputs(url)

        assert "input" in inputs
        assert inputs["input"].shape == (1, classifier.NUM_FEATURES)

        # Check that features are extracted (url_length should be > 0)
        assert inputs["input"][0][0] == float(len(url))

    def test_build_inputs_hostname_length(self, classifier):
        url = "https://subdomain.example.com/path"
        inputs = classifier.build_inputs(url)

        # hostname_length is the second feature
        assert inputs["input"][0][1] == float(len("subdomain.example.com"))

    def test_build_inputs_ip_detection(self, classifier):
        url_with_ip = "http://192.168.1.1/page"
        url_without_ip = "http://example.com/page"

        inputs_with_ip = classifier.build_inputs(url_with_ip)
        inputs_without_ip = classifier.build_inputs(url_without_ip)

        # contains_ip is feature at index 13 (after 4 length + 9 count features)
        assert inputs_with_ip["input"][0][13] == 1.0
        assert inputs_without_ip["input"][0][13] == 0.0

    def test_build_inputs_shortened_url_detection(self, classifier):
        url_shortened = "http://bit.ly/abc123"
        url_normal = "http://example.com/page"

        inputs_shortened = classifier.build_inputs(url_shortened)
        inputs_normal = classifier.build_inputs(url_normal)

        # is_shortened is feature at index 14
        assert inputs_shortened["input"][0][14] == 1.0
        assert inputs_normal["input"][0][14] == 0.0

    def test_build_inputs_https_detection(self, classifier):
        url_https = "https://example.com"
        url_http = "http://example.com"

        inputs_https = classifier.build_inputs(url_https)
        inputs_http = classifier.build_inputs(url_http)

        # has_https is feature at index 15
        assert inputs_https["input"][0][15] == 1.0
        assert inputs_http["input"][0][15] == 0.0

    def test_build_inputs_suspicious_words(self, classifier):
        url_suspicious = "https://example.com/login-verify-account"
        url_normal = "https://example.com/products"

        inputs_suspicious = classifier.build_inputs(url_suspicious)
        inputs_normal = classifier.build_inputs(url_normal)

        # suspicious_word_count is the last feature at index 18 (19 features total, 0-indexed)
        assert inputs_suspicious["input"][0][18] >= 3.0  # contains "login", "verify", "account"
        assert inputs_normal["input"][0][18] == 0.0

    @pytest.mark.asyncio
    async def test_classify_real_model(self, classifier):
        url = "https://example.com/safe-page"
        result = await classifier.classify(url)

        assert result.status in [SafetyStatus.MALICIOUS, SafetyStatus.PENDING]
        assert 0.0 <= result.threat_score <= 1.0
        assert result.classifier == "online_classifier_xgb_v1.0.0"

    @pytest.mark.asyncio
    async def test_classify_inference_error_raises(self, classifier):
        # Mock the session to raise an error
        classifier._session = Mock()
        classifier._session.run = Mock(side_effect=RuntimeError("Inference failed"))

        with pytest.raises(ClassificationError) as exc_info:
            await classifier.classify("https://example.com")

        assert "ONNX inference failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_classify_malicious_prediction(self, classifier):
        # Mock the session to return malicious prediction
        mock_session = Mock()
        mock_session.run = Mock(return_value=[[1], [[0.1, 0.9]]])  # prediction=1, probs=[0.1, 0.9]
        classifier._session = mock_session

        result = await classifier.classify("https://malicious-site.com")

        assert result.status == SafetyStatus.MALICIOUS
        assert result.threat_score == 0.9

    @pytest.mark.asyncio
    async def test_classify_pending_prediction(self, classifier):
        # Mock the session to return safe/pending prediction
        mock_session = Mock()
        mock_session.run = Mock(
            return_value=[[0], [[0.95, 0.05]]]
        )  # prediction=0, probs=[0.95, 0.05]
        classifier._session = mock_session

        result = await classifier.classify("https://safe-site.com")

        assert result.status == SafetyStatus.PENDING
        assert result.threat_score == 0.05
