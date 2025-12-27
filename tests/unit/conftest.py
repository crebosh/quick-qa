import pytest


@pytest.fixture
def hello():
    yield "world"
