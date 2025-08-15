import builtins
import pytest


@pytest.fixture(autouse=True)
def non_interactive_input(monkeypatch):
    """Stub input() during tests to avoid interactive prompts."""
    def fake_input(prompt: str = "") -> str:
        p = (prompt or "").lower()
        if "email" in p:
            return "test@example.com"
        if "whatsapp" in p:
            return "+1234567890"
        if "name" in p:
            return "Test User"
        if "proceed" in p:
            return "n"
        return "n"

    monkeypatch.setattr(builtins, "input", fake_input)
