"""Tests for app/llm/provider.py (R14)."""

from app.llm.provider import LLMProvider


class StandinLLM:
    """A scripted stand-in that satisfies the provider Protocol."""

    name = "standin"
    model = "standin-model"

    def interpret(self, request):
        return {"intent": "aggregate"}

    def plan(self, request):
        return {"tables": ["trades"]}

    def generate_sql(self, request):
        return "SELECT * FROM trades"

    def explain(self, request):
        return "explanation"


def test_standin_satisfies_protocol():
    """R14: a stand-in provider is accepted by the provider-neutral interface."""
    provider = StandinLLM()
    assert isinstance(provider, LLMProvider)
    assert provider.interpret({}) == {"intent": "aggregate"}
    assert provider.plan({}) == {"tables": ["trades"]}
    assert provider.generate_sql({}) == "SELECT * FROM trades"
    assert provider.explain({}) == "explanation"