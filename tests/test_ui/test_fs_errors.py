"""Tests para ui/fs_errors — detección de ENOSPC."""

import errno

from umbral.ui.fs_errors import handle_write_error, is_no_space_on_device


def test_enospc_detected():
    e = OSError(errno.ENOSPC, "No space")
    assert is_no_space_on_device(e) is True


def test_errno_28():
    e = OSError(28, "No space")
    assert is_no_space_on_device(e) is True


def test_other_oserror():
    e = OSError(errno.ENOENT, "Missing")
    assert is_no_space_on_device(e) is False


def test_not_oserror():
    assert is_no_space_on_device(ValueError("x")) is False


def test_handle_write_returns_true_for_enospc(tmp_path):
    e = OSError(errno.ENOSPC, "x")
    assert handle_write_error(e, tmp_path) is True
