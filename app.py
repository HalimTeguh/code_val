# app.py
from flask import Flask, request, jsonify
from bleu import compute_bleu, tokenize_code
from weighted_ngram_match import compute_weighted_bleu
from syntax_match import calc_syntax_match
from dataflow_match import corpus_dataflow_match
from typing import Dict
import ast

app = Flask(__name__)

def load_keywords_weights(file_path: str, default_weight: float = 1.5) -> Dict[str, float]:
    """Load keyword weights from file"""
    weights = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            keyword = line.strip()
            if keyword:
                weights[keyword] = default_weight
    return weights

keyword_weights = load_keywords_weights('keywords_python.txt')

@app.route('/evaluate', methods=['POST'])
def evaluate_code():
    data = request.get_json()
    reference_code = data.get('reference_code', '')
    hypothesis_code = data.get('hypothesis_code', '')

    if not reference_code or not hypothesis_code:
        return jsonify({'error': 'Both reference_code and hypothesis_code are required'}), 400

    # Tokenize code properly
    ref_tokens = [tokenize_code(reference_code)]
    hyp_tokens = tokenize_code(hypothesis_code)

    # Compute scores
    bleu_score = compute_bleu([ref_tokens], [hyp_tokens])
    weighted_bleu = compute_weighted_bleu([ref_tokens], [hyp_tokens], keyword_weights)
    syntax_score = calc_syntax_match(reference_code, hypothesis_code)
    dataflow_score = corpus_dataflow_match([reference_code], hypothesis_code)

    # Combine scores (CodeBLEU uses 0.25 weight for each component)
    total_score = round(0.25*bleu_score + 0.25*weighted_bleu + 0.5*syntax_score + 0.25*dataflow_score, 4)

    return jsonify({
        'ngram_match_score': bleu_score,
        'weighted_ngram_match_score': weighted_bleu,
        'syntax_match_score': syntax_score,
        'dataflow_match_score': dataflow_score,
        'total_score': total_score
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)