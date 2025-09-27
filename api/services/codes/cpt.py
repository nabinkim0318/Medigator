# api/services/codes/cpt.py
import ast
from typing import Any

from .engine import CPTRule

# safe evaluator (boolean/comparison/logic only)
_ALLOWED = {
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Load,
    ast.Name,
    ast.Constant,
    ast.And,
    ast.Or,
    ast.NotEq,
    ast.Eq,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.Subscript,
    ast.Attribute,
}


def _safe_eval(expr: str, env: dict[str, Any]) -> bool:
    if not expr:
        return False
    try:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if type(node) not in _ALLOWED:
                return False

        # Use safer evaluation with restricted environment
        code = compile(tree, "<pred>", "eval")
        # Create a safe environment with only allowed variables
        safe_env = {k: v for k, v in env.items() if isinstance(k, str) and k.isidentifier()}
        return bool(
            eval(code, {"__builtins__": {}}, safe_env)
        )  # nosec B307 - Safe eval with restricted environment
    except (SyntaxError, ValueError, TypeError):
        return False


def suggest_cpt(rules: list[CPTRule], env: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in rules:
        ok = _safe_eval(r.predicate, env)
        if not ok:
            continue
        out.append(
            {
                "code": r.code,
                "label": r.label,
                "pos": r.pos,
                "bundling": r.bundling,
                "payer_note": r.payer_note,
                "reason": r.rationale_key,
                "tags": r.tags or ["triggered"],
            },
        )
    # NCCI/MUE are tagged in memo (no auto-block)
    return out
