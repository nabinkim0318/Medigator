# api/services/codes/cpt.py
import ast, operator as op
from typing import Any, Dict, List
from .engine import CPTRule

# safe evaluator (boolean/comparison/logic only)
_ALLOWED = {
    ast.Expression, ast.BoolOp, ast.UnaryOp, ast.BinOp, ast.Compare,
    ast.Load, ast.Name, ast.Constant, ast.And, ast.Or, ast.NotEq, ast.Eq,
    ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Subscript, ast.Attribute
}

def _safe_eval(expr: str, env: Dict[str, Any]) -> bool:
    if not expr: return False
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if type(node) not in _ALLOWED:
            return False
    code = compile(tree, "<pred>", "eval")
    return bool(eval(code, {"__builtins__": {}}, env))

def suggest_cpt(rules: List[CPTRule], env: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rules:
        ok = _safe_eval(r.predicate, env)
        if not ok: 
            continue
        out.append({
            "code": r.code,
            "label": r.label,
            "pos": r.pos,
            "bundling": r.bundling,
            "payer_note": r.payer_note,
            "reason": r.rationale_key,
            "tags": r.tags or ["triggered"]
        })
    # NCCI/MUE are tagged in memo (no auto-block)
    return out
