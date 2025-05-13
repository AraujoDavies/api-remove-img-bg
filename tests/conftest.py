from code.app import app

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client_fastapi():
    client = TestClient(app)
    yield client
