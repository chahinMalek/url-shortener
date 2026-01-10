class ClassificationError(Exception):
    def __init__(
        self, message: str, classifier_version: str, original_error: Exception | None = None
    ):
        super().__init__(message)
        self.classifier_version = classifier_version
        self.original_error = original_error
