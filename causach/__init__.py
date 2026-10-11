"""Cầu Sách: allocation engine for the textbook-shortage transition plan."""
from .data import District, GeneratorConfig, Problem, build_problem, generate_district
from .model import Plan, Settings
from .optimize import solve
from .baselines import greedy_nearest, no_coordination
from .metrics import evaluate

__all__ = [
    "District", "GeneratorConfig", "Problem", "build_problem", "generate_district",
    "Plan", "Settings", "solve", "greedy_nearest", "no_coordination", "evaluate",
]
