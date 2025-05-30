
# Code Similarity Evaluation System (Python)

Sistem ini merupakan API berbasis Flask yang digunakan untuk menilai kemiripan kode Python siswa terhadap kode referensi. Sistem ini terinspirasi dari CodeBLEU namun dibuat lebih ringan dan dapat di-deploy secara mandiri, sehingga cocok untuk digunakan di berbagai platform (Windows/Linux/Mac).

---

## ✨ Fitur

✅ **N-gram Match Score (BLEU)**  
Mengukur kemiripan token antara kode referensi dan kode siswa menggunakan tokenisasi Python standar.

✅ **Weighted N-gram Match Score**  
Sama seperti BLEU, namun dengan bobot tambahan pada kata kunci Python (keyword) agar sistem dapat menilai penggunaan sintaks yang tepat.

✅ **Syntax Match Score (AST)**  
Mengukur kemiripan struktur sintaks (AST) antara kode referensi dan kode siswa menggunakan AST Python. Variabel dan literal dinormalisasi agar lebih adil dalam penilaian.

✅ **Dataflow Match Score**  
Mengukur kesamaan alur data antar variabel menggunakan analisis AST Python. Sistem akan menangkap assignment dan juga pseudo-edge pada function call agar lebih mendekati metode CodeBLEU asli.

✅ **Total Score**  
Gabungan dari keempat skor di atas dengan bobot:
- BLEU: 0.25
- Weighted BLEU: 0.25
- Syntax Match: 0.5
- Dataflow Match: 0.25

---

## 🗂️ Struktur Folder

```
.
├── app.py                      # API utama (Flask)
├── bleu.py                     # N-gram matching (BLEU)
├── weighted_ngram_match.py     # Weighted BLEU
├── syntax_match.py             # Syntax AST matching
├── dataflow_match.py           # Dataflow matching
├── requirements.txt            # Dependensi
```

---

## 🔧 Cara Instalasi

1️⃣ Clone repository ini (atau download zip):
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2️⃣ Buat virtual environment (opsional namun disarankan):
```bash
python -m venv venv
```
Aktifkan environment:
- Windows:
  ```bash
  venv\Scriptsctivate
  ```
- Mac/Linux:
  ```bash
  source venv/bin/activate
  ```

3️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan

```bash
python app.py
```

API akan berjalan di:
```
http://127.0.0.1:5000/
```

---

## 📬 Cara Menggunakan

### Endpoint
- `POST /evaluate`

### Request JSON:
```json
{
  "reference_code": "def greet(name):\n    print('Hello', name)",
  "hypothesis_code": "def greet(username):\n    print('Hi', username)"
}
```

### Response JSON:
```json
{
  "ngram_match_score": 0.85,
  "weighted_ngram_match_score": 0.88,
  "syntax_match_score": 0.75,
  "dataflow_match_score": 1.0,
  "total_score": 0.85
}
```

---

## 📌 Catatan

- Sistem ini **hanya mendukung bahasa Python** untuk saat ini.
- Dataflow Match akan bernilai 0 jika kode hanya berisi statement print() tanpa assignment atau penggunaan variabel dalam konteks yang dianalisis.
- Syntax Match membutuhkan kode Python yang valid agar dapat di-parse oleh AST Python.

---

## 📝 License

MIT License.

---

## 📮 Kontak

Untuk pertanyaan lebih lanjut, silakan hubungi [halimteguhsaputro@gmail.com] atau melalui GitHub Issues.

---

Selamat mencoba! 🚀
