# bleu.py
import math
import collections
import tokenize
from io import BytesIO
from typing import List, Union, Sequence, Dict

def tokenize_code(code: str) -> List[str]:
    """Tokenize Python code using Python's tokenizer"""
    try:
        tokens = []
        for tok in tokenize.tokenize(BytesIO(code.encode('utf-8')).readline):
            if tok.type not in {tokenize.COMMENT, tokenize.ENCODING, tokenize.NEWLINE, tokenize.NL}:
                tokens.append(tok.string)
        return tokens
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # Fallback to simple tokenizer if syntax is invalid
        return [t for t in re.findall(r'\w+|\S', code) if t.strip()]

def get_ngrams(segment: Sequence[str], max_order: int) -> collections.Counter:
    """Extract n-grams up to max_order"""
    ngrams = collections.Counter()
    for order in range(1, max_order + 1):
        for i in range(len(segment) - order + 1):
            ngram = tuple(segment[i:i + order])
            ngrams[ngram] += 1
    return ngrams

def compute_bleu(reference_corpus: List[List[Sequence[str]]],
                translation_corpus: List[Sequence[str]],
                max_order: int = 4,
                smooth: bool = True) -> float:
    """Compute BLEU score between translations and references"""
    matches_by_order = [0] * max_order
    possible_matches_by_order = [0] * max_order
    ref_length = 0
    trans_length = 0

    for references, translation in zip(reference_corpus, translation_corpus):
        ref_len_list = [len(ref) for ref in references]
        ref_length += min(ref_len_list, key=lambda x: abs(x - len(translation)))
        trans_length += len(translation)

        merged_ref_ngrams = collections.Counter()
        for reference in references:
            merged_ref_ngrams |= get_ngrams(reference, max_order)

        trans_ngrams = get_ngrams(translation, max_order)
        overlap = trans_ngrams & merged_ref_ngrams

        for ngram, count in overlap.items():
            matches_by_order[len(ngram)-1] += count

        for order in range(1, max_order+1):
            possible_matches = len(translation) - order + 1
            if possible_matches > 0:
                possible_matches_by_order[order-1] += possible_matches

    precisions = []
    for i in range(max_order):
        if smooth:
            numerator = matches_by_order[i] + 1.0
            denominator = possible_matches_by_order[i] + 1.0
        else:
            numerator = matches_by_order[i]
            denominator = possible_matches_by_order[i] or 1.0
        precisions.append(numerator / denominator)

    if min(precisions) > 0:
        p_log_sum = sum((1.0/max_order) * math.log(p) for p in precisions)
        geo_mean = math.exp(p_log_sum)
    else:
        geo_mean = 0.0

    ratio = trans_length / ref_length if ref_length > 0 else 0.0
    bp = 1.0 if ratio > 1.0 else math.exp(1 - 1.0/ratio) if ratio > 0 else 0.0

    return round(geo_mean * bp, 4)