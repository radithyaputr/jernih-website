# JERNIH OS — AI Civic Operating System

**Informasi yang Terang, Bukan yang Bising**

AI Civic Assistant untuk membantu warga Indonesia mengakses layanan publik.

## Deploy ke Streamlit Cloud

1. **Push ke GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push
   ```

2. **Buka** [share.streamlit.io](https://share.streamlit.io)
3. **New app** → pilih repo → branch `main` → file `streamlit_app/app.py`
4. **Set API Key** (opsional): Settings → Secrets → `OPENAI_API_KEY = "sk-or-v1-..."`
   - Dapatkan key gratis di https://openrouter.ai/keys

5. **Deploy**

## Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 🤖 AI Civic Copilot | Chat analisis situasi warga (AI + fallback rule-based) |
| 📋 Action Plan Generator | Rencana aksi personal terstruktur |
| 🔍 Hoax Checker | Verifikasi informasi & deteksi hoaks |
| 📊 Policy Simulator | Simulasi dampak perubahan kebijakan |
| 📈 Analytics Dashboard | Skor kesehatan komunitas & regional |
| 🔗 Knowledge Graph | Hubungan program, dokumen & instansi |

## Struktur

```
jernih-website/
├── streamlit_app/
│   ├── app.py                  # All-in-one app (AI + UI)
│   ├── requirements.txt        # Dependencies
│   └── .streamlit/
│       ├── config.toml         # Theme & server config
│       └── secrets.toml.example # API key template
├── README.md
└── .gitignore
```
