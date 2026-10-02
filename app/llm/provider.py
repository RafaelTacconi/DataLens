"""LLM provider interface (R14).

A provider-neutral Protocol (SDD §35). The LLM is an untrusted planner: it
interprets, plans, drafts SQL and explains, but never connects to the
database, never receives credentials, and never executes anything. Prompts
live separately (app/llm/prompts.py), not in business logic.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """The boundary through which the application reaches an LLM."""

    name: str
    model: str

    def interpret(self, request) -> dict:
        """Return a structured interpretation of the user's request."""

    def plan(self, request) -> dict:
        """Return a structured query plan."""

    def generate_sql(self, request) -> str:
        """Return a draft SQL string (never executed directly)."""

    def explain(self, request) -> str:
        """Return an explanation of a verified result."""