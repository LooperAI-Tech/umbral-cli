"""Tests para validation/drift_detector.py."""

from umbral.core.ede import EDE, EDEMetadata, EDEStatus
from umbral.validation.drift_detector import DriftLevel, assess_drift


def test_drift_no_code_files(tmp_path):
    ede = EDE(
        metadata=EDEMetadata(slug="s", title="T", level=1, status=EDEStatus.APPROVED),
        what_and_how="prediction " * 5 + "model training pipeline",
        why="R" * 10,
    )
    r = assess_drift(ede, tmp_path)
    assert r.level == DriftLevel.NONE
    assert "código" in r.note.lower() or "compar" in r.note.lower()


def test_drift_with_overlap(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        "def prediction():\n    model = 1\ntraining = True\n" * 3,
        encoding="utf-8",
    )
    ede = EDE(
        metadata=EDEMetadata(slug="s", title="T", level=1, status=EDEStatus.APPROVED),
        what_and_how="We use a prediction model and training pipeline for data.",
        why="B" * 20,
    )
    r = assess_drift(ede, tmp_path)
    assert r.level in (DriftLevel.NONE, DriftLevel.MINOR)
