"""Exact, sandboxed evaluation of the machine-readable fields of an exercise.

The model writes two strings per exercise:
    bieu_thuc  an expression that computes the answer from the problem's data
    dap_an     the final answer, in the form the exercise asks for

Both are parsed with Python's `ast` module and evaluated here with SymPy's
exact rationals. Nothing is passed to `eval`, so model output cannot run code.
Only numbers, + - * / **, parentheses and a short list of named functions are
accepted.
"""
from __future__ import annotations

import ast
from functools import reduce

import sympy as sp

MAX_LENGTH = 300
MAX_EXPONENT = 64
MAX_MAGNITUDE = sp.Integer(10) ** 40


class ExpressionError(ValueError):
    """The string is not a permitted expression or cannot be evaluated."""


def _rational(value) -> sp.Rational:
    value = sp.nsimplify(value) if not isinstance(value, sp.Rational) else value
    if not isinstance(value, sp.Rational):
        raise ExpressionError("kết quả không phải số hữu tỉ")
    return value


def lam_tron(x, n=0) -> sp.Rational:
    """Round half away from zero to n decimal places (n < 0 rounds to tens, hundreds…)."""
    x, n = _rational(x), int(n)
    if not -6 <= n <= 6:
        raise ExpressionError("chỉ làm tròn đến tối đa 6 chữ số")
    scale = sp.Integer(10) ** n
    magnitude = sp.floor(abs(x) * scale + sp.Rational(1, 2)) / scale
    return magnitude if x >= 0 else -magnitude


def _ucln(*args):
    if len(args) < 2:
        raise ExpressionError("ucln cần ít nhất hai số")
    return reduce(sp.gcd, (_integer(a) for a in args))


def _bcnn(*args):
    if len(args) < 2:
        raise ExpressionError("bcnn cần ít nhất hai số")
    return reduce(sp.lcm, (_integer(a) for a in args))


def _phan_so(a, b):
    if _rational(b) == 0:
        raise ExpressionError("mẫu số bằng 0")
    return _rational(a) / _rational(b)


def _integer(value) -> sp.Integer:
    value = _rational(value)
    if value.q != 1:
        raise ExpressionError("cần số nguyên")
    return sp.Integer(value)


FUNCTIONS = {"ucln": _ucln, "bcnn": _bcnn, "lam_tron": lam_tron, "phan_so": _phan_so}


def normalize(text: str) -> str:
    """Accept a few common non-Python spellings the model may use."""
    return (text.strip()
            .replace("^", "**")
            .replace("×", "*").replace("·", "*")
            .replace(":", "/")
            .replace("−", "-"))


def parse(text: str) -> ast.expr:
    if not isinstance(text, str) or not text.strip():
        raise ExpressionError("biểu thức rỗng")
    text = normalize(text)
    if len(text) > MAX_LENGTH:
        raise ExpressionError("biểu thức quá dài")
    try:
        return ast.parse(text, mode="eval").body
    except SyntaxError as exc:
        raise ExpressionError(f"sai cú pháp: {text}") from exc


def evaluate(text: str) -> sp.Rational:
    return _eval(parse(text))


def _eval(node: ast.expr) -> sp.Rational:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        value = sp.Integer(node.value) if isinstance(node.value, int) else sp.Rational(repr(node.value))
        return _bounded(value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _eval(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp):
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Add):
            return _bounded(left + right)
        if isinstance(node.op, ast.Sub):
            return _bounded(left - right)
        if isinstance(node.op, ast.Mult):
            return _bounded(left * right)
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ExpressionError("chia cho 0")
            return _bounded(left / right)
        if isinstance(node.op, ast.Pow):
            if right.q != 1 or abs(right) > MAX_EXPONENT:
                raise ExpressionError("số mũ phải là số nguyên nhỏ")
            if left == 0 and right < 0:
                raise ExpressionError("chia cho 0")
            return _bounded(left ** right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS:
        if node.keywords:
            raise ExpressionError("không dùng tham số có tên")
        return _bounded(_rational(FUNCTIONS[node.func.id](*[_eval(a) for a in node.args])))
    raise ExpressionError(f"không được phép: {ast.dump(node)[:60]}")


def _bounded(value) -> sp.Rational:
    value = _rational(value)
    if abs(value.p) > MAX_MAGNITUDE or value.q > MAX_MAGNITUDE:
        raise ExpressionError("số quá lớn")
    return value


# ---------------------------------------------------------------------------
# Answer-form checks. Each returns an error message, or None if the form is right.
# ---------------------------------------------------------------------------
def _int_literal(node: ast.expr) -> int | None:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    return None


def _signed_int(node: ast.expr) -> int | None:
    """An integer literal, optionally with a leading sign: 3, -3, +3."""
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _int_literal(node.operand)
        if value is None:
            return None
        return -value if isinstance(node.op, ast.USub) else value
    return _int_literal(node)


def _factors(node: ast.expr) -> list[ast.expr]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _factors(node.left) + _factors(node.right)
    return [node]


def check_prime_factorization(answer: str) -> str | None:
    """'2**2*3*5' is accepted; '4*15' and '60' are not."""
    for factor in _factors(parse(answer)):
        base = factor.left if isinstance(factor, ast.BinOp) and isinstance(factor.op, ast.Pow) else factor
        exponent = factor.right if base is not factor else ast.Constant(1)
        b, e = _int_literal(base), _int_literal(exponent)
        if b is None or e is None or e < 1:
            return "mỗi thừa số phải có dạng p hoặc p**k"
        if not sp.isprime(b):
            return f"{b} không phải số nguyên tố"
    return None


def check_single_power(answer: str) -> str | None:
    """'2**7' is accepted; '128' and '2**3*2**4' are not."""
    node = parse(answer)
    if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow)):
        return "đáp án phải viết dưới dạng một lũy thừa"
    if _signed_int(node.left) is None or _int_literal(node.right) is None:
        return "cơ số và số mũ phải là số nguyên"
    return None


def check_reduced_fraction(answer: str) -> str | None:
    """'7/12' and '3' are accepted; '14/24' is not."""
    node = parse(answer)
    if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.BinOp):
        node = node.operand                      # -(3/4)
    if _signed_int(node) is not None:
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        p, q = _signed_int(node.left), _signed_int(node.right)
        if p is None or q is None or q == 0:
            return "phân số phải có dạng a/b với a, b là số nguyên"
        if sp.gcd(p, q) != 1:
            return f"{p}/{q} chưa tối giản"
        return None
    return "phân số phải có dạng a/b"


def check_integer(answer: str) -> str | None:
    """'64' and '-3' are accepted; '9/2' and '4.5' are not."""
    if _signed_int(parse(answer)) is None:
        return "đáp án phải là một số nguyên"
    return None


def noop_roundings(text: str) -> list[str]:
    """lam_tron(x, n) calls whose result equals x: a rounding exercise with nothing to round."""
    found = []
    for node in ast.walk(parse(text)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "lam_tron" and node.args):
            if _eval(node) == _eval(node.args[0]):
                found.append(ast.unparse(node))
    return found


FORM_CHECKS = {
    "gia_tri": lambda answer: None,
    "so_nguyen": check_integer,
    "phan_so_toi_gian": check_reduced_fraction,
    "mot_luy_thua": check_single_power,
    "phan_tich_nguyen_to": check_prime_factorization,
}
