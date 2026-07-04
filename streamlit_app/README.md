# 🧠 JERNIH — AI Civic Information Platform

**Informasi yang Terang, Bukan yang Bising**

JERNIH adalah platform AI terintegrasi untuk membantu warga mengakses informasi publik, memverifikasi berita, merencanakan aksi, dan mensimulasikan kebijakan — semuanya berbasis RAG (Retrieval-Augmented Generation) dengan transparansi penuh.

---

## ✨ Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 🏠 **Beranda** | Dashboard dengan KPI dampak dan akses cepat ke semua fitur |
| 🤖 **AI Civic Copilot** | Chatbot berbasis RAG untuk konsultasi layanan publik |
| 🔍 **Hoax Checker** | Verifikasi berita/klaim dengan confidence score dan sumber |
| 📋 **Action Plan Generator** | Rencana aksi langkah demi langkah berbasis kebijakan resmi |
| 📊 **Policy Simulator** | Simulasi dampak kebijakan (ekonomi, sosial, lingkungan) |
| 🧠 **Knowledge Graph** | Visualisasi interaktif hubungan isu → kebijakan → dampak |

---

## 🚀 Cara Menjalankan

### 1. Clone repositori
```bash
git clone https://github.com/radithyaputr/jernih-project.git
cd jernih-project/streamlit_app
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup API Key
Buat file `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-or-v1-..."
```
Dapatkan API key gratis di https://openrouter.ai/keys

### 4. Jalankan aplikasi
```bash
streamlit run app.py
```

Aplikasi akan berjalan di `http://localhost:8501`

---

## 📁 Struktur Proyek

```
streamlit_app/
├── app.py                          # Main aplikasi (semua halaman)
├── requirements.txt                # Dependensi Python
├── .streamlit/
│   ├── config.toml                 # Konfigurasi tema Streamlit
│   └── secrets.toml.example        # Template API key
├── src/
│   ├── __init__.py
│   ├── models.py                   # Data models (Source, RAGResult, dll)
│   ├── utils.py                    # CSS, UI components, helpers
│   ├── rag_engine.py               # RAG Engine (ChromaDB + OpenAI embeddings)
│   └── agents.py                   # Agent classes (Civic, Hoax, ActionPlan, Policy)
├── data/
│   └── documents/                  # Dokumen sumber untuk RAG (.txt)
│       ├── program-indonesia-pintar.txt
│       ├── kartu-indonesia-sehat.txt
│       ├── bansos-pkh.txt
│       ├── layanan-dukcapil.txt
│       └── dtks.txt
└── README.md
```

---

## 🔑 API Key

Aplikasi ini membutuhkan OpenAI API key (via OpenRouter) untuk:
- Menjalankan RAG (text-embedding-3-small)
- Menghasilkan jawaban AI (GPT-4o-mini)

Jika API key tidak tersedia, aplikasi akan berjalan dalam mode terbatas.

---

## 🎯 Keunggulan Kompetisi (LKS 2026)

1. **Transparansi Penuh** — Setiap jawaban AI menampilkan sumber secara inline (langsung terlihat)
2. **Confidence Score** — Setiap jawaban dilengkapi skor kepercayaan
3. **Responsible AI** — System prompt ketat yang mencegah halusinasi
4. **Dark Theme Premium** — Desain modern dengan aksesibilitas tinggi
5. **Multi-language** — Toggle Indonesia/English di sidebar
6. **RAG-based** — Semua jawaban berdasarkan dokumen resmi, bukan generasi bebas

---

## 🛠️ Teknologi

- **Streamlit** — Frontend framework
- **LangChain** — RAG pipeline
- **ChromaDB** — Vector database
- **OpenAI / OpenRouter** — Embeddings + LLM
- **Plotly + NetworkX** — Knowledge Graph visualization
- **Python 3.10+**
