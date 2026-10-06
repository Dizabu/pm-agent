from fastapi.testclient import TestClient

from app.llm import get_provider
from app.llm.fake import FakeProvider
from app.main import app

app.dependency_overrides[get_provider] = FakeProvider
client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_uses_provider():
    res = client.post("/chat", json={"message": "hello"})
    assert res.status_code == 200
    assert res.json() == {"reply": "echo: hello"}
