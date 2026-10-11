"""Phiếu Cầu: worksheet generation from curriculum requirements, with automatic checks."""
from .curriculum import Lesson, get_lesson, load_lessons
from .generate import GenerationResult, generate
from .llm import OpenAIModel, ScriptedModel
from .verify import Report, verify

__all__ = ["Lesson", "get_lesson", "load_lessons", "GenerationResult", "generate",
           "OpenAIModel", "ScriptedModel", "Report", "verify"]
