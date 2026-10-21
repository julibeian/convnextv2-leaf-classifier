import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_artifact.py"
SPEC = importlib.util.spec_from_file_location("verify_artifact", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ArtifactVerificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.artifact = self.root / "model.bin"
        self.artifact.write_bytes(b"synthetic-test-content")
        self.labels = self.root / "labels.json"
        self.write_labels({"0": "class_a", "1": "class_b"})
        self.artifact_digest = self.digest(self.artifact)
        self.labels_digest = self.digest(self.labels)

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_labels(self, mapping):
        self.labels.write_text(json.dumps(mapping), encoding="utf-8")

    def verify(self, **overrides):
        arguments = dict(artifact=self.artifact, artifact_sha256=self.artifact_digest,
                         labels=self.labels, labels_sha256=self.labels_digest, class_count=2)
        arguments.update(overrides)
        return MODULE.verify(**arguments)

    def test_valid_files_are_accepted_without_model_deserialization(self):
        self.assertTrue(self.verify()["verified"])

    def test_changed_model_bytes_are_rejected(self):
        self.artifact.write_bytes(b"different-content")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.verify()

    def test_changed_label_order_is_rejected(self):
        self.write_labels({"0": "class_b", "1": "class_a"})
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.verify()

    def test_placeholder_digest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "64 hexadecimal"):
            self.verify(artifact_sha256="REPLACE_WITH_MODEL_SHA256")

    def test_incorrect_output_dimension_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "class count"):
            self.verify(class_count=3)

    def test_noncontiguous_label_indices_are_rejected(self):
        self.write_labels({"0": "class_a", "2": "class_b"})
        with self.assertRaisesRegex(ValueError, "contiguous"):
            self.verify(labels_sha256=self.digest(self.labels))

    def test_duplicate_labels_are_rejected(self):
        self.write_labels({"0": "class_a", "1": "class_a"})
        with self.assertRaisesRegex(ValueError, "unique"):
            self.verify(labels_sha256=self.digest(self.labels))

    def test_missing_artifact_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "existing regular file"):
            self.verify(artifact=self.root / "missing.bin")


if __name__ == "__main__":
    unittest.main()
