# weighted_ngram_match.py
import math
import collections
from typing import List, Dict, Tuple, Sequence
from bleu import get_ngrams

def compute_weighted_bleu(reference_corpus: List[List[Sequence[str]]],
                         translation_corpus: List[Sequence[str]],
                         weights_dict: Dict[str, float] = None,
                         max_order: int = 4,
                         smooth: bool = True) -> float:
    """Compute weighted BLEU score with keyword weighting"""
    matches_by_order = [0.0] * max_order
    possible_matches_by_order = [0] * max_order
    ref_length = 0
    trans_length = 0

    for references, translation in zip(reference_corpus, translation_corpus):
        ref_length += min(len(r) for r in references)
        trans_length += len(translation)

        merged_ref_ngrams = collections.Counter()
        for reference in references:
            merged_ref_ngrams |= get_ngrams(reference, max_order)

        trans_ngrams = get_ngrams(translation, max_order)
        overlap = trans_ngrams & merged_ref_ngrams

        for ngram, count in overlap.items():
            order = len(ngram)
            weight = 1.0
            if order == 1 and weights_dict:
                token = ngram[0]
                weight = weights_dict.get(token, 1.0)
            matches_by_order[order-1] += count * weight

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