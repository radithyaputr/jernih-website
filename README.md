<div align="center">
  <img src="https://via.placeholder.com/150x150.png?text=Logo+JERNIH" alt="JERNIH Logo" width="120" height="120">

  # 🌟 JERNIH.
  **AI Civic Platform**

  *"Informasi yang Terang, Bukan yang Bising" — Platform Kecerdasan Artifisial Multimodal Komunitas*

  [![Kompetisi](https://img.shields.io/badge/LKS_Nasional-2026-gold?style=for-the-badge)](https://#)
  [![Kategori](https://img.shields.io/badge/Eksibisi_AI-Studi_Kasus_1-blue?style=for-the-badge)](https://#)
  [![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![Lisensi](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

   [![Live Demo](https://img.shields.io/badge/LIVE_DEMO-streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://jernih-project.streamlit.app) • [Dokumentasi](#-fitur-unggulan) • [Arsitektur](#-arsitektur-sistem--multi-ai-fallback) • [Tim Pengembang](#-identitas-tim-pengembang)
</div>

---

## 📖 Latar Belakang
Perkembangan teknologi mempercepat distribusi informasi, namun memicu eskalasi hoaks secara masif. Di tingkat akar rumput, warga kerap mengalami disorientasi validitas, asimetri informasi publik, dan keterbatasan literasi multimodal terkait layanan birokrasi dan bantuan sosial.

**JERNIH.** hadir sebagai solusi inklusif yang mentransformasi ekosistem informasi kewarganegaraan dari hilir ke hulu. Kami membangun asisten informasi terintegrasi yang mampu menyajikan jawaban kontekstual berbasis dokumen hukum resmi secara instan dan memvisualisasikan data publik lintas generasi.

## 🚀 Keunggulan Inovasi Utama (The Core Engine)
Tidak seperti *chatbot* konvensional, JERNIH. dibangun dengan **4-Tier Graceful Fallback System**. Sistem ini mendistribusikan beban komputasi secara dinamis melintasi klaster API global, memastikan aplikasi tetap beroperasi 100% (*zero-downtime*) meski terjadi kegagalan jaringan atau pembatasan kuota (*rate limit*) pada API eksternal.

| Tier | Infrastruktur / Provider | Model AI Utama | Peran Strategis |
| :---: | :--- | :--- | :--- |
| 🥇 **1** | **Groq Cloud API** | Llama 3.1 70B / Mixtral 8x7B | Pemrosesan utama dengan latensi ultrarendah. |
| 🥈 **2** | **Google Gemini API** | Gemini 1.5 Flash / 2.0 Flash | Analisis dokumen multimodal & konteks panjang. |
| 🥉 **3** | **OpenRouter API** | Nemotron 3 / GPT-4o-Mini | Cadangan global jika Tier 1 & 2 *downtime*. |
| 🛡️ **4** | **Rule-Based Fallback** | Deterministic Regex & Offline KB | Sistem darurat lokal tanpa internet. |

## ✨ Fitur Unggulan
Aplikasi diwujudkan melalui **8 modul fungsional terintegrasi** yang saling melengkapi:

1. 🤖 **AI Civic Copilot (RAG Engine)**: Asisten interaktif berteknologi *Retrieval-Augmented Generation* (RAG) yang melakukan *query* langsung ke dokumen regulasi legal untuk menekan halusinasi AI.
2. 🛡️ **Hoax Checker**: Mesin deteksi disinformasi multimodal yang memverifikasi klaim pengguna dengan repositori data tepercaya.
3. 🗺️ **Action Plan Generator**: Mengonversi instruksi birokrasi kompleks (mis: "Mengurus KTP Hilang") menjadi *roadmap* langkah-demi-langkah yang linier.
4. 📈 **Policy Simulator**: Modul simulasi untuk memberikan proyeksi dampak kebijakan publik terhadap metrik sosial ekonomi.
5. 🕸️ **Knowledge Graph Kewarganegaraan**: Visualisasi relasi dinamis antar program pemerintah, dasar hukum, dan instansi.
6. 📄 **Smart Scanner (OCR 3 Lapis)**: *Pipeline Computer Vision* untuk mengekstrak dan menata data dari dokumen fisik (KTP/KK) yang buram/rusak.
7. 🌍 **Predictive Map (Peta 3D)**: Dashboard spasial PyDeck yang memetakan kerawanan hoaks, bencana, dan distribusi bansos.
8. 🧩 **Architecture Interactive View**: Halaman edukasi transparansi operasional sistem *Multi-AI fallback* untuk kemudahan audit.

## 🛠️ Tumpukan Teknologi (Tech Stack)
*   **Frontend & Core Framework:** Streamlit (v1.38+)
*   **Orkestrasi AI & Memori:** LangChain & ChromaDB (Local Vector DB)
*   **Data & Visualisasi:** PyDeck, NetworkX, Pandas
*   **Ekosistem LLM:** Llama 3.1, Gemini 1.5, Nemotron (Via API endpoint)

## ⚖️ Tata Kelola & Responsible AI
Kami mematuhi etika kecerdasan buatan melalui implementasi keamanan berlapis:

| Identifikasi Risiko | Strategi Mitigasi Teknis | Metrik / Output |
| :--- | :--- | :--- |
| **AI Hallucination** | RAG dengan temperature `0.2`. Mewajibkan kutipan sumber hukum. | *Confidence Score (%)* berbasis pencocokan sumber. |
| **Prompt Injection** | Validasi input terpusat via `security.py`. Sanitasi karakter ilegal. | Penolakan otomatis tanpa *forwarding* ke LLM. |
| **API Rate Limiting** | Aktivasi pipa interseptor failover otomatis (< 1.5 detik peralihan). | *Zero-failure rate*, kontinuitas operasional 100%. |

## 📊 Sumber Data Publik (Open Data)
Sesuai regulasi LKS 2026, JERNIH. 100% menggunakan *Open Data* dan data sintetis tanpa mengeksploitasi PII (Personal Identifiable Information):
- **Kemensos RI & BPJS**: Regulasi PKH, BPNT, dan Jaminan Sosial.
- **BNPB & BPS**: Dataset kebencanaan dan statistik demografi wilayah.
- **MAFINDO & Kominfo**: API TurnBackHoax dan dataset aduan konten disinformasi.

## 💻 Cara Instalasi

### Option A: Deploy ke Streamlit Community Cloud (Recommended)
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Klik **"New app"**
3. Pilih repo `radithyaputr/jernih-project`
4. Set **Main file path**: `streamlit_app/app.py`
5. Klik **"Deploy"**

Aplikasi akan live di `https://<your-username>-jernih-project.streamlit.app`

> **Note:** API keys (OpenRouter, Gemini, Groq) perlu ditambahkan di menu **Advanced Settings** > **Secrets** saat deploy.

### Option B: Jalankan Secara Lokal
1. **Clone Repositori**
   ```bash
   git clone https://github.com/radithyaputr/jernih-project.git
   cd jernih-project
   ```

2. **Buat Virtual Environment (Direkomendasikan)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/Mac
   venv\Scripts\activate     # Untuk Windows
   ```

3. **Instalasi Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi API Keys**
   Buat file `streamlit_app/.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   GEMINI_API_KEY = "your_gemini_api_key"
   OPENROUTER_API_KEY = "your_openrouter_api_key"
   ```
   > Tanpa API keys, aplikasi tetap berjalan menggunakan **rule-based fallback** (offline mode).

5. **Jalankan Aplikasi**
   ```bash
   cd streamlit_app
   streamlit run app.py
   ```

### Arsitektur Folder
```
jernih-project/
├── streamlit_app/
│   ├── app.py                    # Entry point
│   ├── pages/                    # Halaman multipage
│   │   ├── 06_Smart_Scanner.py
│   │   ├── 07_Predictive_Map.py
│   │   └── 08_About.py
│   ├── src/
│   │   ├── agents.py             # 4 AI agents
│   │   ├── config.py             # API config
│   │   ├── ui_components.py      # UI components
│   │   └── utils.py              # CSS & helpers
│   └── .streamlit/
│       ├── config.toml           # Theme config
│       └── secrets.toml          # API keys (gitignored)
├── requirements.txt
├── packages.txt                  # System deps (tesseract)
└── .gitignore
```

## 👨‍💻 Identitas Tim Pengembang
**SMK Negeri 1 Kota Bengkulu**

| Nama | Peran |
| :--- | :--- |
| **Muhammad Fikri Haikal** | AI Engineer / Lead Developer |
| **Adiel Raditya Putra Irwana** | Data Scientist |
| **Muhammad Aditya Anugerah** | Backend & System Architecture |
| **Fachri Majidan Afandi** | Frontend & Visual Data |
| **Muhammad Irsyad Sholih** | Research & Policy Analyst |

## 📜 Lisensi
Didistribusikan di bawah lisensi **MIT License**. Lihat file [LICENSE](LICENSE) untuk informasi lebih lanjut.

---

<div align="center">
  <strong>JERNIH.</strong> — *Informasi yang Terang, Bukan yang Bising*<br>
  Dibangun dengan ❤️ oleh Tim LKS Nasional 2026 — SMK Negeri 1 Kota Bengkulu
</div>
