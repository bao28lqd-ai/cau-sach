"""Model clients.

Everything else talks to a model through one method:

    complete_json(system, user, schema, name) -> (data: dict, usage: dict)

so the generator, the verifier and the evaluation never depend on a vendor.
`OpenAIModel` is the real client; `ScriptedModel` replays canned answers and
is what the tests and the offline demo use.
"""
from __future__ import annotations

import copy
import json
import os
import re
from typing import Callable, Protocol

DEFAULT_MODEL = "gpt-5-mini"


class Model(Protocol):
    name: str

    def complete_json(self, system: str, user: str, schema: dict, name: str) -> tuple[dict, dict]: ...


class OpenAIModel:
    """OpenAI Responses API with Structured Outputs (strict JSON schema).

    Reads OPENAI_API_KEY (and optionally OPENAI_MODEL) from the environment.
    The key is never logged or written to disk by this project.
    """

    def __init__(self, model: str | None = None, reasoning_effort: str | None = "low"):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on the user's environment
            raise RuntimeError("install the OpenAI SDK first: pip install openai") from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set; put it in a .env file (see .env.example)")
        self.client = OpenAI()
        self.name = model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
        self.reasoning_effort = reasoning_effort

    def complete_json(self, system: str, user: str, schema: dict, name: str) -> tuple[dict, dict]:
        kwargs = {
            "model": self.name,
            "instructions": system,
            "input": user,
            "text": {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}},
        }
        # Reasoning models (gpt-5*, o*) accept an effort setting; others reject it.
        if self.reasoning_effort and re.match(r"^(gpt-5|o\d)", self.name):
            kwargs["reasoning"] = {"effort": self.reasoning_effort}
        response = self.client.responses.create(**kwargs)
        data = json.loads(response.output_text)
        usage = getattr(response, "usage", None)
        return data, {
            "input_tokens": getattr(usage, "input_tokens", 0) or 0,
            "output_tokens": getattr(usage, "output_tokens", 0) or 0,
        }


class ScriptedModel:
    """Replays canned answers, keyed by schema name.

    Each handler receives the user prompt and returns the JSON payload, so a
    script can react to which exercise ids the prompt asks about.
    """

    def __init__(self, handlers: dict[str, Callable[[str], dict]], name: str = "scripted"):
        self.handlers = handlers
        self.name = name
        self.calls: list[str] = []

    def complete_json(self, system: str, user: str, schema: dict, name: str) -> tuple[dict, dict]:
        self.calls.append(name)
        if name not in self.handlers:
            raise KeyError(f"no scripted answer for {name}")
        return copy.deepcopy(self.handlers[name](user)), {"input_tokens": 0, "output_tokens": 0}


def ids_in_prompt(prompt: str) -> list[str]:
    """Exercise ids written as [B3] in a prompt, in order."""
    return re.findall(r"\[(B\d+)\]", prompt)
