"""Conf Test Module"""

import pytest


@pytest.fixture
def hello():
    """sum"""
    yield "world"
