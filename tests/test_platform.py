from __future__ import annotations

import pytest

from movidesk.sender import resolve_platform


def test_platform_empresas():
    assert resolve_platform("Projuris Empresas") == "empresas"


def test_platform_enterprise():
    assert resolve_platform("Projuris Enterprise") == "enterprise"


def test_platform_invalid():
    with pytest.raises(ValueError):
        resolve_platform("Outro")
