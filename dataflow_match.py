import ast
import keyword
from typing import List, Set

# Python keywords and built-in functions to exclude
PYTHON_KEYWORDS = set(keyword.kwlist)
PYTHON_BUILTINS = set([
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 
    'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr', 
    'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 
    'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr', 
    'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 
    'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 
    'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord', 
    'pow', 'print', 'property', 'range', 'repr', 'reversed', 
    'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod', 
    'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__'
])

class DataflowVisitor(ast.NodeVisitor):
    def __init__(self):
        self.identifiers = set()

    def visit_Name(self, node):
        """Capture variable names in store/load context"""
        if node.id not in PYTHON_BUILTINS and node.id not in PYTHON_KEYWORDS:
            self.identifiers.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Capture function definition names"""
        if node.name not in PYTHON_BUILTINS and node.name not in PYTHON_KEYWORDS:
            self.identifiers.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Capture class definition names"""
        if node.name not in PYTHON_BUILTINS and node.name not in PYTHON_KEYWORDS:
            self.identifiers.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node):
        """Capture function call names, filtering out built-ins"""
        if isinstance(node.func, ast.Name):
            if node.func.id not in PYTHON_BUILTINS and node.func.id not in PYTHON_KEYWORDS:
                self.identifiers.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr not in PYTHON_BUILTINS and node.func.attr not in PYTHON_KEYWORDS:
                self.identifiers.add(node.func.attr)
        self.generic_visit(node)

def extract_identifiers(code: str) -> Set[str]:
    """Extract identifiers from Python code"""
    try:
        tree = ast.parse(code.strip())
        visitor = DataflowVisitor()
        visitor.visit(tree)
        return visitor.identifiers
    except Exception:
        # Return empty set on any parsing errors
        return set()

def normalize_identifiers(identifiers: Set[str]) -> Set[str]:
    """Normalize variable names to var0, var1, ..."""
    norm_map = {}
    for idx, name in enumerate(sorted(identifiers)):
        norm_map[name] = f'var{idx}'
    return set(norm_map.values())

def corpus_dataflow_match(reference_texts: List[str], candidate_text: str) -> float:
    """
    Calculate dataflow match score between candidate and references.
    Normalizes variable names to var0, var1, etc. to simulate CodeBLEU DFG behavior.
    """
    ref_ids = set()
    for ref_code in reference_texts:
        ref_ids |= extract_identifiers(ref_code)

    cand_ids = extract_identifiers(candidate_text)

    # Normalisasi variable names
    norm_ref_ids = normalize_identifiers(ref_ids)
    norm_cand_ids = normalize_identifiers(cand_ids)

    # Handle edge cases
    if not norm_ref_ids:
        if not norm_cand_ids:
            return 1.0
        return 0.0

    common_ids = norm_ref_ids & norm_cand_ids
    precision = len(common_ids) / len(norm_cand_ids) if norm_cand_ids else 0.0
    recall = len(common_ids) / len(norm_ref_ids)

    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return round(f1, 4)
