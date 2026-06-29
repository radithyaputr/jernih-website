# 🌟 JERNIH OS — Streamlit Deployment

## 🚀 Deploy ke Streamlit Cloud

### Cara 1: Deploy Otomatis (via GitHub)

1. **Push folder `streamlit_app/` ke GitHub**
   ```bash
   git add streamlit_app/
   git commit -m "Add Streamlit deployment"
   git push
   ```

2. **Buka [share.streamlit.io](https://share.streamlit.io)**

3. **Klik "New app"**
   - Repository: pilih repo ini (`radithyaputr/jernih-project`)
   - Branch: `main`
   - Main file path: `streamlit_app/app.py`

4. **Klik "Deploy"**

5. ✅ **Aplikasi akan live dalam 2-3 menit!**

### Cara 2: Deploy Manual (via Streamlit CLI)

```bash
# 1. Masuk ke folder streamlit_app
cd streamlit_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan lokal
streamlit run app.py

# 4. Untuk deploy, upload folder ini ke Streamlit Cloud manual
```

---

## 📁 Struktur Folder

```
streamlit_app/
├── app.py                        # Main application (all-in-one + AI + fallback)
├── requirements.txt              # Python dependencies
├── .streamlit/
│   ├── config.toml               # Streamlit theme & server config
│   └── secrets.toml.example      # API key template (copy to secrets.toml)
└── README.md                    # Deployment guide
```

## ⚙️ Fitur yang Tersedia

| Fitur | Halaman | Deskripsi |
|-------|---------|-----------|
| 🏠 Beranda | Landing page | Overview dengan metrik dampak |
| 🤖 AI Civic Copilot | Chat interaktif | Analisis situasi warga (AI + rule-based fallback) |
| 📋 Action Plan Generator | Form-based | Rencana aksi personal terstruktur |
| 🔍 Hoax Checker | Text analysis | Verifikasi informasi & deteksi hoaks |
| 📊 Policy Simulator | Interactive form | Simulasi dampak perubahan kebijakan |
| 📈 Analytics Dashboard | Dashboard | Skor kesehatan komunitas & regional |
| 🔗 Knowledge Graph | Filterable list | Hubungan program, dokumen & instansi |

## 🔑 Setup API Key (Agar AI Bisa Jawab General Questions)

App ini punya **dual-mode**: AI (via OpenRouter) + fallback rule-based.

### Jika API key tersedia:
- AI bisa jawab **pertanyaan umum** ("hari ini hari apa?", "siapa presiden?", "buatkan puisi")
- Analisis situasi warga jadi lebih akurat dan kontekstual
- Hoax checker dan action plan juga pake AI

### Jika API key kosong:
- Otomatis fallback ke **rule-based** (tetap berfungsi penuh untuk 20+ topik layanan publik)

### Cara Setup:

**Di Streamlit Cloud:**
1. Buka app di Streamlit Cloud → **Settings** → **Secrets**
2. Tambahkan:
   ```toml
   OPENAI_API_KEY = "sk-or-v1-..."
   ```
3. Get free key: https://openrouter.ai/keys (no credit card, 200 req/min)

**Lokal:**
```bash
# Copy example file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit dengan API key asli
```

## 🧠 Teknologi

- **Streamlit** — Frontend UI framework
- **Pure Python** — Backend logic (no FastAPI needed)
- **OpenRouter AI** — GPT-4o-mini untuk respon cerdas (optional)
- **Rule-based fallback** — 20+ topik layanan publik Indonesia

## 🔧 Catatan

- Aplikasi ini adalah **all-in-one monolithic app** — backend + frontend dalam satu file
- Tidak perlu database atau API terpisah
- Jika API key tidak diset, semua fitur tetap berfungsi via rule-based
- Cocok untuk demo, exhibition, dan production