# syntax_match.py
import ast
from typing import List, Union, Dict, Tuple
from collections import defaultdict
import tokenize
from io import BytesIO
import re

def normalize_ast(node: ast.AST) -> ast.AST:
    """Normalize AST by removing variable names and literals"""
    if isinstance(node, ast.AST):
        new_node = type(node)()
        for field in node._fields:
            value = getattr(node, field)
            if isinstance(value, (ast.Name, ast.arg)):
                setattr(new_node, field, ast.Name(id='_', ctx=value.ctx))
            elif isinstance(value, (ast.Str, ast.Num)):
                setattr(new_node, field, ast.Str(s='_'))
            elif isinstance(value, (ast.AST, list)):
                setattr(new_node, field, normalize_ast(value))
            else:
                setattr(new_node, field, value)
        return new_node
    elif isinstance(node, list):
        return [normalize_ast(x) for x in node]
    return node

def get_ast_ngrams(tree: ast.AST, n: int = 2) -> Dict[Tuple[str, ...], int]:
    """Extract n-grams from AST with subtree matching"""
    ngrams = defaultdict(int)
    for node in ast.walk(tree):
        if isinstance(node, ast.AST):
            node_type = type(node).__name__
            children = list(ast.iter_child_nodes(node))
            if n > 1 and children:
                child_types = tuple(type(c).__name__ for c in children[:n-1])
                ngram = (node_type,) + child_types
                ngrams[ngram] += 1
            ngrams[(node_type,)] += 1  # Unigram
    return ngrams

def compare_ast_ngrams(candidate: Dict[Tuple[str, ...], int], 
                      reference: Dict[Tuple[str, ...], int]) -> float:
    """Calculate AST similarity using n-gram overlap"""
    common = sum(min(candidate[k], reference[k]) for k in candidate if k in reference)
    total = sum(candidate.values())
    return common / total if total > 0 else 0.0

def calc_syntax_match(reference_texts: Union[str, List[str]], 
                    candidate_text: str, 
                    lang: str = 'python') -> float:
    """Calculate syntax match score between candidate and references"""
    references = [reference_texts] if isinstance(reference_texts, str) else reference_texts
    return corpus_syntax_match([references], [candidate_text])

def corpus_syntax_match(reference_corpus: List[List[str]],
                       candidate_corpus: List[str],
                       ngram_order: int = 2) -> float:
    """Calculate corpus-level syntax match score"""
    total_score = 0.0
    num_samples = 0

    for references, candidate in zip(reference_corpus, candidate_corpus):
        try:
            candidate_tree = ast.parse(candidate.strip())
            candidate_ngrams = get_ast_ngrams(normalize_ast(candidate_tree), ngram_order)
        except (SyntaxError, ValueError):
            continue

        best_score = 0.0
        for reference in references:
            try:
                ref_tree = ast.parse(reference.strip())
                ref_ngrams = get_ast_ngrams(normalize_ast(ref_tree), ngram_order)
                score = compare_ast_ngrams(candidate_ngrams, ref_ngrams)
                best_score = max(best_score, score)
            except (SyntaxError, ValueError):
                continue

        total_score += best_score
        num_samples += 1

    return round(total_score / num_samples, 4) if num_samples > 0 else 0.0