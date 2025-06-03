from flask import Flask, request, jsonify
from bleu import compute_bleu, tokenize_code
from weighted_ngram_match import compute_weighted_bleu
from syntax_match import calc_syntax_match
from dataflow_match import corpus_dataflow_match
from typing import Dict
from dotenv import load_dotenv
import ast
import os
import requests
import json
import logging

# Setup logger for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

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

    ref_tokens = [tokenize_code(reference_code)]
    hyp_tokens = tokenize_code(hypothesis_code)

    bleu_score = compute_bleu([ref_tokens], [hyp_tokens])
    weighted_bleu = compute_weighted_bleu([ref_tokens], [hyp_tokens], keyword_weights)
    syntax_score = calc_syntax_match(reference_code, hypothesis_code)
    dataflow_score = corpus_dataflow_match([reference_code], hypothesis_code)

    total_score = round(0.25*bleu_score + 0.25*weighted_bleu + 0.5*syntax_score + 0.25*dataflow_score, 4)

    return jsonify({
        'ngram_match_score': bleu_score,
        'weighted_ngram_match_score': weighted_bleu,
        'syntax_match_score': syntax_score,
        'dataflow_match_score': dataflow_score,
        'total_score': total_score
    })

@app.route('/askLlama', methods=['POST'])
def generate_soal():
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'success': False, 'message': 'Prompt harus diisi.'}), 400

        api_url = 'https://router.huggingface.co/together/v1/chat/completions'
        api_token = os.environ.get('HUGGINGFACE_API_TOKEN')

        response = requests.post(
            api_url,
            headers={'Authorization': f'Bearer {api_token}'},
            json={
                'model': 'meta-llama/Llama-3.3-70B-Instruct-Turbo',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'top_p': 0.85,
                'max_tokens': 3072
            },
            timeout=600
        )

        if response.status_code != 200:
            logger.error(f"Hugging Face API error: {response.status_code} {response.text}")
            return jsonify({'success': False, 'message': 'Model gagal merespons.'}), 500

        json_text = response.json().get('choices', [{}])[0].get('message', {}).get('content')
        if not json_text:
            return jsonify({'success': False, 'message': 'Tidak ada konten yang dikembalikan oleh model.'}), 422

        json_start = json_text.find('[')
        if json_start == -1:
            return jsonify({'success': False, 'message': 'Output tidak mengandung JSON array.'}), 422

        clean_json = json_text[json_start:]
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return jsonify({'success': False, 'message': f'Gagal parsing JSON: {str(e)}', 'raw': clean_json}), 422

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        logger.exception("Unexpected error in /askLlama")
        return jsonify({'success': False, 'message': f'Terjadi kesalahan saat memanggil API: {str(e)}'}), 500

# Note: Tidak perlu lagi app.run() di production.
