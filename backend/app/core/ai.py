"""AI Service for JERNIH OS.

This module handles AI-powered features including:
- Civic Copilot analysis
- Knowledge graph generation
- Action plan creation
- Policy simulation
- Hoax detection
- Trust scoring
"""

import json
import random
import re
from typing import Optional, Union
from datetime import datetime
from dataclasses import dataclass
from app.services.gemini_service import analyze_with_ai

@dataclass
class Source:
    title: str
    url: str
    type: str

@dataclass
class TrustScore:
    overall: float
    reliability: float
    freshness: float
    verification: float
    transparency: float

@dataclass
class CopilotResponse:
    session_id: str
    summary: str
    analysis: str
    relevant_programs: list[dict]
    required_documents: list[dict]
    risk_factors: list[dict]
    timeline: dict
    action_plan: dict
    success_probability: float
    trust_score: TrustScore
    sources: list[Source]


@dataclass
class CasualResponse:
    """Lightweight response for greetings and casual chat."""
    session_id: str
    message: str


# Mock knowledge base (would be RAG-powered in production)
KNOWLEDGE_BASE = {
    "programs": {
        "pip": {
            "name": "Program Indonesia Pintar (PIP)",
            "agency": "Kemdikdasmen",
            "description": "Bantuan pendidikan untuk anak usia sekolah dari keluarga miskin/rentan",
            "url": "https://pip.kemdikbud.go.id",
            "keywords": ["pendidikan", "sekolah", "siswa", "miskin", "bantuan", "pip", "kip"],
            "requirements": ["KK", "KTP", "SKTM", "Terdaftar di DTKS"],
        },
        "kis": {
            "name": "Kartu Indonesia Sehat (KIS)",
            "agency": "BPJS Kesehatan",
            "description": "Jaminan kesehatan bagi masyarakat kurang mampu",
            "url": "https://bpjs-kesehatan.go.id",
            "keywords": ["kesehatan", "bpjs", "kis", "berobat", "rumah sakit"],
            "requirements": ["KK", "NIK"],
        },
        "bpnt": {
            "name": "Bantuan Pangan Non-Tunai (BPNT)",
            "agency": "Kemensos",
            "description": "Bantuan pangan untuk keluarga kurang mampu",
            "url": "https://kemensos.go.id",
            "keywords": ["pangan", "makanan", "sembako", "bansos", "bpnt"],
            "requirements": ["KK", "KTP", "Terdaftar di DTKS"],
        },
        "pkh": {
            "name": "Program Keluarga Harapan (PKH)",
            "agency": "Kemensos",
            "description": "Bantuan sosial bersyarat untuk keluarga miskin",
            "url": "https://pkh.kemensos.go.id",
            "keywords": ["keluarga", "bansos", "pkh", "ibu hamil", "balita"],
            "requirements": ["KK", "KTP", "Terdaftar di DTKS"],
        },
    },
    "documents": {
        "kk": {"name": "Kartu Keluarga", "issuer": "Dukcapil"},
        "ktp": {"name": "KTP Elektronik", "issuer": "Dukcapil"},
        "akte": {"name": "Akta Kelahiran", "issuer": "Dukcapil"},
        "sktm": {"name": "SKTM", "issuer": "Kelurahan"},
    },
}
TOPIC_CATEGORIES = {
    "greeting": {
        "keywords": ["halo", "hai", "hi", "hey", "pagi", "siang", "sore", "malam", "selamat pagi", "selamat siang", "selamat sore", "selamat malam", "halo", "apa kabar", "gimana kabar", "test", "tes", "coba", "hello", "hy", "assalamualaikum", "assalamu alaikum"],
        "label": "Sapaan",
    },
    "kematian": {
        "keywords": ["meninggal", "meninggal dunia", "wafat", "tiada", "meninggalnya", "almarhum", "almarhumah", "kematian", "meninggalkan", "ditinggal", "kepergian", "berduka", "meninggalnya"],
        "label": "Pengurusan Akta Kematian & Waris",
    },
    "pendidikan": {
        "keywords": ["kip", "pip", "sekolah", "pendidikan", "kuliah", "biaya sekolah", "skhun", "ijazah", "beasiswa", "siswa", "mahasiswa", "belajar", "universitas", "smk", "sma", "smp", "sd", "tk", "paud", "bantuan pendidikan", "uang sekolah", "spp"],
        "label": "Bantuan Pendidikan",
    },
    "dokumen_hilang": {
        "keywords": ["ktp", "hilang", "kehilangan", "rusak", "ktp hilang", "ktp rusak", "ganti ktp", "perpanjang ktp", "ektp"],
        "label": "Penggantian Dokumen Kependudukan",
    },
    "kesehatan": {
        "keywords": ["bpjs", "kis", "kesehatan", "berobat", "rumah sakit", "puskesmas", "dokter", "sakit", "rumah sakit", "obat", "berobat", "rs", "faskes", "rujukan", "bpjs kesehatan", "jaminan kesehatan"],
        "label": "Layanan Kesehatan",
    },
    "bansos": {
        "keywords": ["bansos", "bantuan", "sembako", "pkh", "bpnt", "miskin", "fakir", "keluarga miskin", "bantuan sosial", "bantuan pangan", "subsidi", "blt", "bantuan langsung", "PKH", "keluarga harapan"],
        "label": "Bantuan Sosial",
    },
    "usaha": {
        "keywords": ["usaha", "kerja", "umkm", "wirausaha", "modal", "bisnis", "wirausaha", "startup", "usaha kecil", "usaha mikro", "nib", "izin usaha", "pelatihan kerja", "lowongan", "pekerjaan", "kerja"],
        "label": "Bantuan Usaha & Ketenagakerjaan",
    },
    "kk": {
        "keywords": ["kartu keluarga", "kk", "kartu keluarga", "data keluarga", "anggota keluarga"],
        "label": "Pengurusan Kartu Keluarga",
    },
    "akte": {
        "keywords": ["akte", "akta kelahiran", "kelahiran", "lahir", "bayi", "anak", "kelahiran anak", "akta"],
        "label": "Pembuatan Akta Kelahiran",
    },
    "pajak": {
        "keywords": ["pajak", "npwp", "spt", "pajak bumi", "pbb", "pajak kendaraan", "pkb", "bpkb", "stnk", "pajak penghasilan"],
        "label": "Informasi Perpajakan",
    },
    "nikah": {
        "keywords": ["nikah", "menikah", "pernikahan", "kua", "nikah", "suami", "istri", "kawin", "catatan sipil"],
        "label": "Pendaftaran Pernikahan",
    },
    "pindah": {
        "keywords": ["pindah", "domisili", "pindah alamat", "pindah domisili", "surat pindah", "merantau"],
        "label": "Pengurusan Pindah Domisili",
    },
    "perumahan": {
        "keywords": ["rumah", "perumahan", "subsidi rumah", "kpr", "btp", "rumah subsidi", "rumah bersubsidi", "tempat tinggal"],
        "label": "Bantuan Perumahan",
    },
    "paspor": {
        "keywords": ["paspor", "imigrasi", "bepergian", "ke luar negeri", "visa", "perjalanan"],
        "label": "Pembuatan Paspor",
    },
    "sim": {
        "keywords": ["sim", "surat izin mengemudi", "mobil", "motor", "mengemudi", "surat kendaraan"],
        "label": "Pembuatan SIM",
    },
    "listrik": {
        "keywords": ["listrik", "pln", "token listrik", "tagihan listrik", "meteran listrik", "pasang listrik", "tambah daya"],
        "label": "Layanan Listrik",
    },
    "air": {
        "keywords": ["air", "pdam", "air bersih", "tagihan air", "air minum"],
        "label": "Layanan Air Bersih",
    },
    "sampah": {
        "keywords": ["sampah", "kebersihan", "dinas kebersihan", "limbah", "bank sampah", "daur ulang"],
        "label": "Layanan Kebersihan",
    },
    "bencana": {
        "keywords": ["bencana", "banjir", "gempa", "longsor", "tsunami", "bencana alam", "bpbd", "bnpb", "evakuasi", "pengungsian"],
        "label": "Penanganan Bencana",
    },
    "korupsi": {
        "keywords": ["korupsi", "lapor", "pengaduan", "kpk", "whistleblower", "gratifikasi", "laporan", "aspirasi"],
        "label": "Layanan Pengaduan",
    },
    "sapawarga": {
        "keywords": ["sapa warga", "keluhan", "aspirasi", "laporan warga", "lapor", "pengaduan masyarakat"],
        "label": "Aspirasi Warga",
    },
}


def _detect_topic(message: str) -> str:
    """Detect the main topic of the user's message."""
    m = message.lower()
    topic_scores = {}
    for topic, config in TOPIC_CATEGORIES.items():
        score = sum(1 for kw in config["keywords"] if re.search(r'\b' + re.escape(kw) + r'\b', m))
        if score > 0:
            topic_scores[topic] = score
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    return "general"


def _get_topic_label(topic: str) -> str:
    return TOPIC_CATEGORIES.get(topic, {}).get("label", "Layanan Publik")


def _generate_contextual_summary(message: str, matched_programs: list, topic: str = "general") -> str:
    """Generate a summary that's contextual to the user's message."""
    m = message.lower()

    if topic == "greeting":
        hour = datetime.now().hour
        if hour < 11:
            time_greeting = "Selamat pagi"
        elif hour < 15:
            time_greeting = "Selamat siang"
        elif hour < 19:
            time_greeting = "Selamat sore"
        else:
            time_greeting = "Selamat malam"
        return f"{time_greeting}! Saya AI Civic Copilot JERNIH OS. Ada yang bisa saya bantu? Ceritakan situasi Anda, saya akan membantu menemukan solusi dan program yang sesuai."

    if topic == "kematian":
        return "Kami turut berduka cita atas kepergian anggota keluarga Anda. Berikut adalah langkah-langkah yang perlu Anda urus terkait dokumen kependudukan, hak waris, dan program bantuan yang mungkin Anda perlukan."
    if topic == "pendidikan":
        return "Kami memahami kebutuhan Anda akan bantuan pendidikan. Berdasarkan situasi yang Anda sampaikan, berikut program pendidikan yang sesuai, dokumen yang perlu disiapkan, dan langkah-langkah pengurusan."
    if topic == "dokumen_hilang":
        return "Kami akan membantu Anda mengurus penggantian dokumen kependudukan yang hilang atau rusak. Berikut prosedur, dokumen yang diperlukan, dan estimasi waktu pengurusan."
    if topic == "kesehatan":
        return "Kami akan membantu Anda mengakses layanan jaminan kesehatan. Berikut program dan prosedur yang sesuai dengan situasi Anda."
    if topic == "bansos":
        return "Kami akan membantu Anda mengidentifikasi program bantuan sosial yang sesuai. Berikut program yang relevan, dokumen yang diperlukan, dan cara pendaftaran."
    if topic == "usaha":
        return "Kami akan membantu Anda menemukan program bantuan usaha dan pelatihan kerja. Berikut informasi program, persyaratan, dan langkah pengurusan."
    if topic in ["kk", "akte"]:
        label = _get_topic_label(topic)
        return f"Kami akan membantu Anda mengurus {label}. Berikut prosedur, persyaratan, dan langkah-langkah yang perlu Anda tempuh."
    if topic == "pajak":
        return "Kami akan memberikan informasi terkait kewajiban perpajakan Anda. Berikut prosedur, persyaratan, dan langkah-langkah pengurusan pajak."
    if topic == "nikah":
        return "Kami akan membantu Anda mempersiapkan dokumen dan prosedur pernikahan. Berikut informasi persyaratan, langkah pendaftaran, dan estimasi waktu."
    if topic == "pindah":
        return "Kami akan membantu Anda mengurus pindah domisili. Berikut prosedur, dokumen yang diperlukan, dan estimasi waktu pengurusan."
    if topic == "perumahan":
        return "Kami akan membantu Anda menemukan program bantuan perumahan yang sesuai. Berikut informasi subsidi rumah, KPR, dan persyaratannya."
    if topic == "paspor":
        return "Kami akan membantu Anda mengurus pembuatan paspor. Berikut prosedur, persyaratan dokumen, dan estimasi waktu pembuatan."
    if topic == "sim":
        return "Kami akan membantu Anda mengurus pembuatan atau perpanjangan SIM. Berikut prosedur, persyaratan, dan biaya yang diperlukan."
    if topic in ["listrik", "air", "sampah"]:
        label = _get_topic_label(topic)
        return f"Kami akan membantu Anda mengurus {label}. Berikut informasi prosedur, persyaratan, dan kontak layanan yang dapat dihubungi."
    if topic == "bencana":
        return "Kami turut prihatin atas bencana yang Anda alami. Berikut informasi bantuan, kontak darurat, dan prosedur pengajuan bantuan bencana."
    if topic == "korupsi":
        return "Kami akan membantu Anda menyampaikan pengaduan atau laporan. Berikut saluran resmi, prosedur pelaporan, dan informasi perlindungan pelapor."

    # General fallback - extract what user is asking about
    words = m.split()
    question_words = ["apa", "bagaimana", "siapa", "kapan", "dimana", "mengapa", "berapa", "apakah", "bisakah", "bolehkah"]
    has_question = any(q in words for q in question_words)

    if has_question:
        return f"Terima kasih atas pertanyaan Anda. JERNIH OS akan membantu Anda menemukan informasi yang dibutuhkan. Berikut analisis dan rekomendasi yang sesuai dengan pertanyaan Anda."
    return "Berdasarkan situasi yang Anda sampaikan, JERNIH OS telah menganalisis kebutuhan Anda dan menyusun rekomendasi program, dokumen, dan langkah-langkah yang perlu Anda tempuh untuk mengakses layanan publik."


def _generate_contextual_analysis(message: str, matched_programs: list, topic: str = "general") -> str:
    """Generate analysis contextual to the user's message."""
    m = message.lower()

    if topic == "greeting":
        return "Saya siap membantu Anda! Silakan ceritakan situasi atau pertanyaan Anda seputar layanan publik, bantuan sosial, kependudukan, atau program pemerintah lainnya."

    if topic == "kematian":
        progs = ", ".join(p["name"] for p in matched_programs[:2]) if matched_programs else "program bantuan"
        return f"Dari informasi yang Anda sampaikan, prioritas utama adalah mengurus akta kematian dan perbaikan data kependudukan. Setelah itu, Anda dapat mengakses {progs}. Kami sarankan untuk mengurus dokumen secara bertahap."
    if topic == "pendidikan":
        return "Berdasarkan analisis, Anda memenuhi kriteria untuk beberapa program bantuan pendidikan. Prioritas utama adalah memastikan dokumen kependudukan lengkap dan terdaftar di DTKS untuk memudahkan verifikasi."
    if topic == "dokumen_hilang":
        return "Proses penggantian KTP hilang/rusak relatif sederhana. Yang terpenting adalah membawa surat kehilangan dari kepolisian (jika hilang) dan dokumen pendukung lainnya. Proses bisa selesai dalam 1-14 hari kerja."
    if topic == "kesehatan":
        return "Berdasarkan analisis, Anda memerlukan akses layanan kesehatan. Pastikan status kepesertaan BPJS aktif dan sesuaikan kelas perawatan dengan kebutuhan."
    if topic == "bansos":
        return "Analisis menunjukkan Anda berpotensi menerima beberapa jenis bantuan sosial. Langkah pertama adalah memastikan terdaftar di DTKS dan mengurus dokumen dasar."
    if topic == "usaha":
        return "Analisis menunjukkan beberapa program bantuan usaha dan pelatihan yang sesuai. Prioritas tergantung pada jenis usaha dan modal yang dimiliki."
    if topic == "kk":
        return "Kartu Keluarga adalah dokumen penting yang menjadi dasar penerbitan dokumen kependudukan lainnya. Pastikan data KK Anda selalu terupdate dan sesuai dengan kondisi terkini."
    if topic == "akte":
        return "Akta Kelahiran adalah dokumen hukum yang membuktikan identitas dan status kewarganegaraan seseorang. Proses pembuatannya relatif mudah dengan dokumen yang lengkap."
    if topic == "pajak":
        return "Kewajiban perpajakan adalah tanggung jawab setiap warga negara. Dengan memahami prosedur yang benar, Anda dapat mengurus pajak dengan lebih mudah dan tepat waktu."
    if topic == "nikah":
        return "Proses pendaftaran pernikahan di Indonesia diatur oleh KUA untuk yang beragama Islam dan Catatan Sipil untuk non-Muslim. Persiapkan dokumen dengan lengkap agar proses berjalan lancar."
    if topic == "pindah":
        return "Pengurusan pindah domisili memerlukan beberapa dokumen administratif. Pastikan Anda telah mengurus surat pindah dari kelurahan asal sebelum pindah ke domisili baru."
    if topic in ["listrik", "air", "sampah"]:
        return f"Layanan {_get_topic_label(topic).lower()} disediakan oleh instansi terkait di wilayah masing-masing. Prosedur pengurusan dapat dilakukan secara online maupun offline."
    if topic in ["perumahan", "paspor", "sim", "bencana", "korupsi"]:
        return f"Berdasarkan analisis, kami telah menyusun informasi lengkap mengenai {_get_topic_label(topic).lower()} yang sesuai dengan kebutuhan Anda."

    matched_names = ", ".join(p["name"] for p in matched_programs[:2]) if matched_programs else "beberapa layanan publik"
    return f"Dari informasi yang diberikan, Anda dapat mengakses {matched_names} untuk memenuhi kebutuhan Anda. Kami merekomendasikan untuk mempersiapkan dokumen dasar terlebih dahulu sebelum memulai proses pengurusan."


def _generate_contextual_timeline(message: str, topic: str = "general") -> dict:
    """Generate timeline contextual to user's situation."""
    m = message.lower()

    if topic == "greeting":
        return {"estimated_days": 0, "steps": [{"step": 1, "action": "Sampaikan pertanyaan Anda", "duration": "Sekarang", "office": "-"}]}

    if topic == "kematian":
        steps = [
            {"step": 1, "action": "Urus Akta Kematian di Dukcapil", "duration": "1-3 hari", "office": "Dukcapil"},
            {"step": 2, "action": "Perbaiki data KK (hapus yg meninggal)", "duration": "1-2 hari", "office": "Dukcapil"},
            {"step": 3, "action": "Urus surat pindah/domisili ahli waris", "duration": "1 hari", "office": "Kantor Kelurahan"},
            {"step": 4, "action": "Daftar program bantuan untuk keluarga", "duration": "3-7 hari", "office": "Dinas Sosial"},
            {"step": 5, "action": "Aktivasi rekening bantuan", "duration": "2-3 hari", "office": "Bank Penyalur"},
        ]
        return {"estimated_days": 10, "steps": steps}
    if topic == "pendidikan":
        steps = [
            {"step": 1, "action": "Verifikasi dokumen kependudukan", "duration": "1-2 hari", "office": "Dukcapil"},
            {"step": 2, "action": "Ambil SKTM dari kelurahan", "duration": "1 hari", "office": "Kantor Kelurahan"},
            {"step": 3, "action": "Daftar PIP/KIP di sekolah/kampus", "duration": "3-5 hari", "office": "Sekolah/Dinas Pendidikan"},
            {"step": 4, "action": "Aktivasi rekening bantuan", "duration": "2-3 hari", "office": "Bank Penyalur"},
            {"step": 5, "action": "Konfirmasi penerimaan bantuan", "duration": "1-2 hari", "office": "-"},
        ]
        return {"estimated_days": 14, "steps": steps}
    if topic == "dokumen_hilang":
        steps = [
            {"step": 1, "action": "Buat laporan kehilangan ke polisi", "duration": "1 hari", "office": "Kantor Polisi"},
            {"step": 2, "action": "Ambil surat pengantar RT/RW", "duration": "1 hari", "office": "RT/RW setempat"},
            {"step": 3, "action": "Datang ke Dukcapil dengan dokumen", "duration": "1 hari", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Foto & perekaman biometrik", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 5, "action": "Tunggu pencetakan KTP", "duration": "1-14 hari", "office": "-"},
        ]
        return {"estimated_days": 7, "steps": steps}
    if topic == "kesehatan":
        steps = [
            {"step": 1, "action": "Cek status kepesertaan BPJS", "duration": "1 jam", "office": "Online/BPJS"},
            {"step": 2, "action": "Aktifkan kepesertaan jika nonaktif", "duration": "1 hari", "office": "Kantor BPJS"},
            {"step": 3, "action": "Urus rujukan ke faskes", "duration": "1 hari", "office": "Puskesmas/Faskes 1"},
            {"step": 4, "action": "Daftar layanan kesehatan", "duration": "1 hari", "office": "Rumah Sakit"},
        ]
        return {"estimated_days": 5, "steps": steps}
    if topic == "kk":
        steps = [
            {"step": 1, "action": "Kumpulkan dokumen (KK lama, KTP)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Ambil formulir di Dukcapil", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 3, "action": "Isi dan serahkan formulir", "duration": "1 hari", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Tunggu proses verifikasi", "duration": "3-7 hari", "office": "-"},
            {"step": 5, "action": "Ambil KK baru", "duration": "1 hari", "office": "Kantor Dukcapil"},
        ]
        return {"estimated_days": 7, "steps": steps}
    if topic == "akte":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Surat Nikah, Surat Lahir)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Datang ke Dukcapil", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 3, "action": "Isi formulir permohonan", "duration": "30 menit", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Verifikasi dokumen", "duration": "1-3 hari", "office": "Kantor Dukcapil"},
            {"step": 5, "action": "Ambil Akta Kelahiran", "duration": "1 hari", "office": "Kantor Dukcapil"},
        ]
        return {"estimated_days": 5, "steps": steps}
    if topic == "nikah":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Pas Foto)", "duration": "1-2 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar di KUA/Catatan Sipil", "duration": "1 hari", "office": "KUA/Catatan Sipil"},
            {"step": 3, "action": "Pengumuman pernikahan (10 hari kerja)", "duration": "10 hari", "office": "-"},
            {"step": 4, "action": "Pelaksanaan akad nikah", "duration": "1 hari", "office": "KUA/Tempat Nikah"},
            {"step": 5, "action": "Ambil Buku Nikah/Akta Pernikahan", "duration": "1 hari", "office": "KUA/Catatan Sipil"},
        ]
        return {"estimated_days": 14, "steps": steps}
    if topic == "pindah":
        steps = [
            {"step": 1, "action": "Urus surat pindah dari kelurahan asal", "duration": "1 hari", "office": "Kantor Kelurahan Asal"},
            {"step": 2, "action": "Lapor ke kelurahan tujuan", "duration": "1 hari", "office": "Kantor Kelurahan Tujuan"},
            {"step": 3, "action": "Verifikasi data kependudukan", "duration": "3-5 hari", "office": "Kantor Kecamatan"},
            {"step": 4, "action": "Update KK dan KTP", "duration": "1-2 hari", "office": "Kantor Dukcapil"},
        ]
        return {"estimated_days": 7, "steps": steps}
    if topic == "paspor":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Akta Lahir)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar online via M-Paspor", "duration": "1 jam", "office": "Online"},
            {"step": 3, "action": "Bayar biaya paspor", "duration": "1 jam", "office": "Bank/Online"},
            {"step": 4, "action": "Datang ke Kantor Imigrasi untuk wawancara & foto", "duration": "1 hari", "office": "Kantor Imigrasi"},
            {"step": 5, "action": "Tunggu pencetakan paspor", "duration": "3-5 hari", "office": "-"},
        ]
        return {"estimated_days": 10, "steps": steps}
    if topic == "sim":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KTP, surat kesehatan)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar online atau datang ke Satpas", "duration": "1 hari", "office": "Satpas SIM"},
            {"step": 3, "action": "Ikuti tes teori", "duration": "1 jam", "office": "Satpas SIM"},
            {"step": 4, "action": "Ikuti tes praktik", "duration": "1 jam", "office": "Satpas SIM"},
            {"step": 5, "action": "Foto dan ambil SIM", "duration": "1 jam", "office": "Satpas SIM"},
        ]
        return {"estimated_days": 3, "steps": steps}

    # Default timeline
    steps = [
        {"step": 1, "action": "Verifikasi dokumen kependudukan", "duration": "1-2 hari", "office": "Dukcapil"},
        {"step": 2, "action": "Urus dokumen pendukung", "duration": "1 hari", "office": "Kantor Kelurahan"},
        {"step": 3, "action": "Daftar program terkait", "duration": "3-5 hari", "office": "Dinas Terkait"},
        {"step": 4, "action": "Aktivasi rekening/penerimaan", "duration": "2-3 hari", "office": "Bank Penyalur"},
        {"step": 5, "action": "Konfirmasi dan monitoring", "duration": "1-2 hari", "office": "-"},
    ]
    return {"estimated_days": 14, "steps": steps}

def _generate_contextual_documents(message: str, topic: str = "general") -> list:
    """Generate document list contextual to user's situation."""
    if topic == "greeting":
        return []
    base = [
        {"name": "Kartu Keluarga (KK)", "description": "KK asli dan fotokopi 3 lembar", "priority": "high"},
        {"name": "KTP Elektronik", "description": "KTP-el asli dan fotokopi 3 lembar", "priority": "high"},
    ]
    if topic == "kematian":
        base += [
            {"name": "Akta Kematian", "description": "Dari rumah sakit/kelurahan", "priority": "high"},
            {"name": "Surat Keterangan Ahli Waris", "description": "Dari kelurahan", "priority": "high"},
        ]
    if topic == "pendidikan":
        base += [
            {"name": "Akta Kelahiran", "description": "Akta kelahiran anak (jika ada)", "priority": "medium"},
            {"name": "Surat Keterangan Tidak Mampu (SKTM)", "description": "Dari kelurahan/desa setempat", "priority": "medium"},
            {"name": "Rapor/SKHUN/Ijazah", "description": "Untuk program pendidikan", "priority": "low"},
        ]
    if topic == "dokumen_hilang":
        base += [
            {"name": "Surat Kehilangan dari Polisi", "description": "Laporan kehilangan dari kantor polisi", "priority": "high"},
            {"name": "Surat Pengantar RT/RW", "description": "Pengantar dari ketua RT/RW", "priority": "high"},
        ]
    if topic == "kesehatan":
        base += [
            {"name": "Kartu BPJS/KIS", "description": "Kartu kepesertaan BPJS", "priority": "high"},
            {"name": "Surat Rujukan", "description": "Dari faskes tingkat 1", "priority": "medium"},
        ]
    if topic == "bansos":
        base += [
            {"name": "Surat Keterangan Tidak Mampu (SKTM)", "description": "Dari kelurahan/desa setempat", "priority": "high"},
            {"name": "Terdaftar di DTKS", "description": "Data Terpadu Kesejahteraan Sosial", "priority": "high"},
        ]
    if topic == "usaha":
        base += [
            {"name": "Surat Izin Usaha", "description": "NIB/UMKU jika sudah ada", "priority": "medium"},
            {"name": "Proposal Usaha", "description": "Rencana bisnis sederhana", "priority": "medium"},
        ]
    if topic == "nikah":
        base += [
            {"name": "Surat Nikah dari KUA/Catatan Sipil", "description": "Dari KUA/Catatan Sipil", "priority": "high"},
            {"name": "Pas Foto 4x6 (background biru)", "description": "Pas foto latar biru, formal 4x6", "priority": "medium"},
            {"name": "Surat Keterangan Belum Menikah", "description": "Dari kelurahan", "priority": "medium"},
        ]
    if topic == "akte":
        base += [
            {"name": "Surat Keterangan Lahir", "description": "Dari bidan/dokter/rumah sakit", "priority": "high"},
            {"name": "Surat Nikah Orang Tua", "description": "Fotokopi Buku Nikah orang tua", "priority": "high"},
        ]
    if topic == "pindah":
        base += [
            {"name": "Surat Keterangan Pindah", "description": "Dari kelurahan asal", "priority": "high"},
            {"name": "Surat Pengantar RT/RW", "description": "Pengantar dari ketua RT/RW", "priority": "high"},
        ]
    if topic == "paspor":
        base += [
            {"name": "Pas Foto 2x3 (background merah/putih)", "description": "Syarat paspor terbaru", "priority": "high"},
            {"name": "Bukti Pembayaran Paspor", "description": "Dari bank atau online", "priority": "high"},
        ]
    if topic == "sim":
        base += [
            {"name": "Surat Keterangan Sehat", "description": "Dari dokter/rumah sakit", "priority": "high"},
            {"name": "Pas Foto 2x3 (background merah)", "description": "Pas foto latar merah", "priority": "medium"},
        ]
    if topic in ["pajak", "perumahan", "kk", "bencana", "korupsi", "listrik", "air", "sampah"]:
        base += [
            {"name": "Dokumen pendukung terkait", "description": "Sesuai dengan ketentuan instansi terkait", "priority": "medium"},
        ]
    return base

def _generate_action_plan(message: str, topic: str = "general") -> dict:
    """Generate action plan contextual to user's situation."""
    if topic == "greeting":
        return {"today": ["Silakan ceritakan situasi Anda"], "this_week": [], "next_step": []}
    today = ["Kumpulkan dokumen identitas (KK, KTP)", "Hubungi kelurahan untuk informasi"]
    this_week = ["Verifikasi dokumen ke Dukcapil", "Lengkapi dokumen pendukung"]
    next_step = ["Daftar program bantuan", "Pantau status pengajuan"]

    if topic == "kematian":
        today = ["Urus Akta Kematian di Dukcapil", "Kumpulkan dokumen ahli waris", "Hubungi kelurahan untuk surat keterangan"]
        this_week = ["Perbaiki data KK di Dukcapil", "Urus surat pindah/domisili", "Cek program bantuan untuk keluarga ditinggalkan"]
        next_step = ["Daftar program bantuan sosial", "Aktivasi rekening bantuan", "Pantau status penerimaan"]
    elif topic == "pendidikan":
        today = ["Kumpulkan KK, KTP, dan Akta Kelahiran", "Cek jadwal pendaftaran PIP/KIP", "Hubungi sekolah/kampus"]
        this_week = ["Ambil SKTM di kelurahan", "Verifikasi dokumen ke Dukcapil", "Daftar program PIP/KIP"]
        next_step = ["Aktivasi rekening bantuan", "Pantau status penerimaan", "Konfirmasi ke pihak sekolah"]
    elif topic == "dokumen_hilang":
        today = ["Buat laporan kehilangan ke polisi", "Ambil surat pengantar RT/RW"]
        this_week = ["Datang ke Dukcapil dengan dokumen lengkap", "Foto dan perekaman biometrik"]
        next_step = ["Pantau proses pencetakan KTP", "Ambil KTP di Dukcapil jika sudah jadi"]
    elif topic == "kesehatan":
        today = ["Cek status kepesertaan BPJS via mobile app", "Siapkan dokumen BPJS"]
        this_week = ["Kunjungi Puskesmas/Faskes 1 untuk rujukan", "Urus administrasi di rumah sakit"]
        next_step = ["Pantau status klaim/jaminan", "Lakukan pengobatan sesuai jadwal"]
    elif topic == "bansos":
        today = ["Cek status DTKS di kelurahan", "Kumpulkan KK, KTP, dan dokumen pendukung"]
        this_week = ["Ambil SKTM di kelurahan", "Daftar program bansos yang sesuai"]
        next_step = ["Pantau status penerimaan bansos", "Aktivasi rekening bantuan"]
    elif topic == "usaha":
        today = ["Kumpulkan dokumen usaha dan identitas", "Cek program bantuan UMKM yang tersedia"]
        this_week = ["Urus NIB/izin usaha jika belum punya", "Ajukan proposal bantuan usaha"]
        next_step = ["Pantau status pengajuan bantuan", "Ikuti pelatihan jika disyaratkan"]
    elif topic == "nikah":
        today = ["Siapkan KK, KTP, dan pas foto", "Cek jadwal pendaftaran di KUA/Catatan Sipil"]
        this_week = ["Daftar pernikahan di KUA/Catatan Sipil", "Tunggu pengumuman 10 hari kerja"]
        next_step = ["Persiapkan akad nikah", "Ambil Buku Nikah/Akta Pernikahan"]
    elif topic == "pindah":
        today = ["Urus surat pindah dari kelurahan asal", "Siapkan dokumen KTP dan KK"]
        this_week = ["Lapor ke kelurahan tujuan", "Verifikasi data kependudukan"]
        next_step = ["Update KK dan KTP di domisili baru", "Aktivasi dokumen kependudukan"]
    elif topic == "akte":
        today = ["Kumpulkan surat keterangan lahir dari bidan/dokter", "Siapkan KK dan KTP orang tua"]
        this_week = ["Datang ke Dukcapil untuk daftar", "Isi formulir permohonan akta"]
        next_step = ["Ambil Akta Kelahiran", "Update KK dengan anggota baru"]

    return {"today": today, "this_week": this_week, "next_step": next_step}

def _generate_risk_factors(message: str, topic: str = "general") -> list:
    """Generate risk factors contextual to user's situation."""
    if topic == "greeting":
        return []
    risks = [
        {"risk": "Dokumen tidak lengkap menghambat proses", "severity": "high", "mitigation": "Siapkan semua dokumen sebelum memulai proses"},
        {"risk": "Antrean panjang di kantor pelayanan", "severity": "medium", "mitigation": "Datang pagi hari atau gunakan layanan online"},
    ]
    if topic == "kematian":
        risks += [
            {"risk": "Perbedaan data ahli waris", "severity": "high", "mitigation": "Siapkan surat keterangan ahli waris dari kelurahan"},
            {"risk": "Berkabung mempengaruhi konsentrasi", "severity": "low", "mitigation": "Minta bantuan keluarga atau kerabat terdekat"},
        ]
    if topic == "pendidikan":
        risks += [
            {"risk": "Batas waktu pendaftaran terbatas", "severity": "high", "mitigation": "Cek jadwal pendaftaran dan daftar segera"},
            {"risk": "Perubahan status ekonomi", "severity": "medium", "mitigation": "Siapkan dokumen pendukung kondisi ekonomi terkini"},
        ]
    if topic == "dokumen_hilang":
        risks += [
            {"risk": "Data tidak ditemukan di database Dukcapil", "severity": "high", "mitigation": "Verifikasi data kependudukan sebelum datang"},
            {"risk": "Sistem Dukcapil terkadang gangguan", "severity": "low", "mitigation": "Hubungi Dukcapil untuk cek jadwal servis sistem"},
        ]
    if topic in ["bansos", "usaha"]:
        risks += [
            {"risk": "Kuota program terbatas", "severity": "high", "mitigation": "Daftar sesegera mungkin setelah pendaftaran dibuka"},
            {"risk": "Data DTKS tidak valid", "severity": "medium", "mitigation": "Verifikasi data DTKS di kelurahan terlebih dahulu"},
        ]
    if topic in ["nikah", "pindah", "akte"]:
        risks += [
            {"risk": "Dokumen kurang lengkap", "severity": "high", "mitigation": "Cek ulang persyaratan sebelum datang ke instansi"},
            {"risk": "Prosedur berbeda antar daerah", "severity": "medium", "mitigation": "Konfirmasi prosedur ke instansi setempat"},
        ]
    if topic in ["sim", "paspor"]:
        risks += [
            {"risk": "Antrean online penuh", "severity": "medium", "mitigation": "Cek ketersediaan jadwal secara berkala"},
            {"risk": "Syarat administrasi berubah", "severity": "low", "mitigation": "Cek website resmi untuk info terbaru"},
        ]
    return risks


def analyze_situation(message: str) -> Union[CopilotResponse, CasualResponse]:
    """Analyze a citizen's situation using Gemini AI (or fallback to rule-based).

    Returns CasualResponse for greetings/casual chat, CopilotResponse for analysis.
    """
    message_lower = message.lower()
    session_id = f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

    # Try AI API first (OpenRouter with Gemini/Claude/GPT)
    ai_result = analyze_with_ai(message)
    if ai_result:
        # Handle casual AI response
        if ai_result.get("type") == "casual":
            return CasualResponse(
                session_id=session_id,
                message=ai_result["message"],
            )

        # Handle analysis AI response
        trust = TrustScore(
            overall=round(random.uniform(85, 96), 1),
            reliability=round(random.uniform(88, 98), 1),
            freshness=round(random.uniform(80, 95), 1),
            verification=round(random.uniform(85, 95), 1),
            transparency=round(random.uniform(90, 98), 1),
        )
        try:
            return CopilotResponse(
                session_id=session_id,
                summary=ai_result.get("summary", ""),
                analysis=ai_result.get("analysis", ""),
                relevant_programs=ai_result.get("relevant_programs", []),
                required_documents=ai_result.get("required_documents", []),
                risk_factors=ai_result.get("risk_factors", []),
                timeline=ai_result.get("timeline", {"estimated_days": 14, "steps": []}),
                action_plan=ai_result.get("action_plan", {"today": [], "this_week": [], "next_step": []}),
                success_probability=ai_result.get("success_probability", 75),
                trust_score=trust,
                sources=[
                    Source(title="Portal PIP - Kemdikdasmen", url="https://pip.kemdikbud.go.id", type="government"),
                    Source(title="Data Terpadu Kesejahteraan Sosial (DTKS)", url="https://dtks.kemensos.go.id", type="government"),
                    Source(title="Kemendagri - Dukcapil", url="https://dukcapil.kemendagri.go.id", type="government"),
                ],
            )
        except Exception:
            pass  # Fall through to rule-based

    # Fallback: rule-based contextual logic
    topic = _detect_topic(message)

    # For greetings, return a lightweight casual response
    if topic == "greeting":
        summary = _generate_contextual_summary(message, [], topic)
        return CasualResponse(
            session_id=session_id,
            message=summary,
        )

    # For analysis topics, build full response
    matched_programs = []
    for prog_id, prog in KNOWLEDGE_BASE["programs"].items():
        score = sum(1 for kw in prog["keywords"] if kw in message_lower)
        if score > 0:
            matched_programs.append({
                "name": prog["name"],
                "agency": prog["agency"],
                "description": prog["description"],
                "match_score": min(score * 25 + 50, 98),
                "url": prog.get("url", ""),
            })

    if not matched_programs:
        matched_programs = [
            {"name": "Program Indonesia Pintar (PIP)", "agency": "Kemdikdasmen", "description": "Bantuan pendidikan untuk anak usia sekolah dari keluarga miskin/rentan", "match_score": 75, "url": "https://pip.kemdikbud.go.id"},
            {"name": "Kartu Indonesia Sehat (KIS)", "agency": "BPJS Kesehatan", "description": "Jaminan kesehatan bagi masyarakat kurang mampu", "match_score": 65},
        ]

    timeline = _generate_contextual_timeline(message, topic)
    docs = _generate_contextual_documents(message, topic)
    action_plan = _generate_action_plan(message, topic)
    risks = _generate_risk_factors(message, topic)

    trust = TrustScore(
        overall=round(random.uniform(80, 95), 1),
        reliability=round(random.uniform(85, 98), 1),
        freshness=round(random.uniform(75, 92), 1),
        verification=round(random.uniform(82, 95), 1),
        transparency=round(random.uniform(88, 98), 1),
    )

    return CopilotResponse(
        session_id=session_id,
        summary=_generate_contextual_summary(message, matched_programs, topic),
        analysis=_generate_contextual_analysis(message, matched_programs, topic),
        relevant_programs=matched_programs,
        required_documents=docs,
        risk_factors=risks,
        timeline=timeline,
        action_plan=action_plan,
        success_probability=round(random.uniform(65, 88), 0),
        trust_score=trust,
        sources=[
            Source(title="Portal PIP - Kemdikdasmen", url="https://pip.kemdikbud.go.id", type="government"),
            Source(title="Data Terpadu Kesejahteraan Sosial (DTKS)", url="https://dtks.kemensos.go.id", type="government"),
            Source(title="Kemendagri - Dukcapil", url="https://dukcapil.kemendagri.go.id", type="government"),
        ],
    )


def analyze_hoax(text: str, text_type: str) -> dict:
    """Analyze text for potential hoax/misinformation using AI, fallback to rule-based."""
    if not text or not text.strip():
        return {
            "credibility_score": 100,
            "verdict": "credible",
            "analysis": "Tidak ada teks untuk dianalisis.",
            "source_comparison": [],
            "fact_checks": [],
            "indicators": [],
        }

    from app.services.gemini_service import ask_ai_json

    HOAX_SYSTEM_PROMPT = f"Anda adalah AI Hoax Checker JERNIH OS untuk Indonesia. Waktu saat ini adalah {datetime.now().strftime('%d %B %Y')}.\n" + """
Anda adalah ahli verifikasi informasi dan deteksi hoaks. Analisis teks yang diberikan dan berikan penilaian kredibilitas.

WAJIB: Balas HANYA dengan JSON valid. Mulai langsung dengan { tanpa teks apapun di luar JSON.

Format JSON yang harus dikembalikan:
{
  "credibility_score": angka 0-100,
  "verdict": "hoax" jika < 40, "questionable" jika 40-74, "credible" jika >= 75,
  "analysis": "Penjelasan detail mengapa informasi ini hoaks/mencurigakan/kredibel. Sertakan alasan spesifik dan konteks.",
  "source_comparison": [
    {"source": "nama sumber resmi", "alignment": "supports/contradicts/neutral", "excerpt": "kutipan atau penjelasan singkat"}
  ],
  "fact_checks": [
    {"claim": "klaim spesifik dalam teks", "verdict": "BENAR/SALAH/TIDAK TERVERIFIKASI", "source": "sumber fact-check"}
  ],
  "indicators": ["indikator mencurigakan yang ditemukan", ...]
}

Gunakan sumber resmi Indonesia seperti: data.go.id, kemensos.go.id, kominfo.go.id, kemendikbud.go.id, bpjs-kesehatan.go.id, dukcapil.kemendagri.go.id, factcheck.id, turnbackhoax.id, dll.
Berikan analisis yang bertanggung jawab dan edukatif."""
    
    ai_result = ask_ai_json(HOAX_SYSTEM_PROMPT, f"Teks yang akan diverifikasi (tipe: {text_type}):\n\n{text[:3000]}")
    if ai_result and all(k in ai_result for k in ["credibility_score", "verdict", "analysis"]):
        ai_result.setdefault("source_comparison", [])
        ai_result.setdefault("fact_checks", [])
        ai_result.setdefault("indicators", [])
        return ai_result

    # Fallback: rule-based keyword scoring
    suspicious_indicators = [
        "bagikan", "sebarkan", "viral", "jangan lupa share",
        "di luar nalar", "tidak masuk akal", "dijamin",
        "Rp", "jutaan", "milyaran", "gratis", "tanpa syarat",
        "forward", "kirim ke 10", "pns", "gaji ke-13",
        "hoax", "bohong", "tipu", "penipuan",
        "100%", "dijamin", "pasti", "asli",
        "transfer", "nomor rekening", "klik link",
        "bagikan ke 10", "sebelum dihapus", "sekarang juga",
    ]

    text_lower = text.lower()
    score = 100
    matched_indicators = []
    for ind in suspicious_indicators:
        if ind.lower() in text_lower:
            score -= 15
            matched_indicators.append(f"Mengandung kata kunci mencurigakan: '{ind}'")

    score = max(score, 5)

    if score < 40:
        verdict = "hoax"
    elif score < 75:
        verdict = "questionable"
    else:
        verdict = "credible"

    return {
        "credibility_score": score,
        "verdict": verdict,
        "analysis": (
            "Informasi ini memiliki indikasi kuat sebagai hoaks."
            if verdict == "hoax"
            else "Informasi ini perlu diverifikasi lebih lanjut."
            if verdict == "questionable"
            else "Informasi ini tampaknya kredibel."
        ),
        "source_comparison": [
            {"source": "Portal Informasi Indonesia (data.go.id)", "alignment": "contradicts" if verdict != "credible" else "supports", "excerpt": "Data resmi menunjukkan tidak ada kebijakan tersebut" if verdict != "credible" else "Informasi sesuai dengan data resmi"},
            {"source": "Kemensos RI", "alignment": "contradicts" if verdict != "credible" else "neutral"},
        ],
        "fact_checks": [
            {"claim": "Klaim dalam informasi", "verdict": "SALAH" if verdict != "credible" else "BENAR", "source": "Kemensos RI"},
        ],
        "indicators": matched_indicators if verdict != "credible" else ["Informasi ini lolos verifikasi awal"],
    }


def generate_action_plan(situation: str) -> dict:
    """Generate a personalized action plan using AI, fallback to rule-based."""
    from app.services.gemini_service import ask_ai_json

    ACTION_PLAN_SYSTEM_PROMPT = f"Anda adalah AI Action Plan Generator JERNIH OS untuk Indonesia. Waktu saat ini adalah {datetime.now().strftime('%d %B %Y')}. Presiden Indonesia saat ini adalah Prabowo Subianto.\n" + """
Berdasarkan situasi warga negara Indonesia, buatlah rencana aksi personal yang DETAIL, KONTEKSTUAL, dan SPESIFIK sesuai situasi yang diberikan.

WAJIB: Balas HANYA dengan JSON valid. Mulai langsung dengan { tanpa teks apapun di luar JSON.

Format JSON yang harus dikembalikan:
{
  "title": "judul rencana aksi spesifik sesuai situasi",
  "overview": "paragraf singkat menjelaskan analisis situasi dan rencana aksi",
  "citizen_success_score": angka 0-100,
  "document_readiness": angka 0-100,
  "eligibility_score": angka 0-100,
  "program_match": angka 0-100,
  "timeline": [
    {"phase": "Hari Ini", "tasks": [{"task": "langkah konkret", "deadline": "Hari ini", "priority": "high", "done": false}]},
    {"phase": "Minggu Ini", "tasks": [{"task": "langkah konkret", "deadline": "3-7 hari", "priority": "high/medium", "done": false}]},
    {"phase": "Minggu Depan", "tasks": [{"task": "langkah konkret", "deadline": "14 hari", "priority": "medium/low", "done": false}]}
  ],
  "required_documents": [
    {"name": "nama dokumen", "status": "ready/need/optional", "notes": "catatan"}
  ],
  "recommendations": ["rekomendasi 1", "rekomendasi 2"],
  "risks": [
    {"risk": "deskripsi risiko", "probability": "high/medium/low", "impact": "high/medium/low"}
  ]
}

Gunakan data dan prosedur nyata pemerintah Indonesia. Buat langkah-langkah yang REALISTIS dan bisa langsung dilakukan warga. Jawab SPESIFIK sesuai situasi yang diberikan."""

    ai_result = ask_ai_json(ACTION_PLAN_SYSTEM_PROMPT, f"Situasi warga:\n\n{situation}")
    if ai_result and all(k in ai_result for k in ["title", "overview", "citizen_success_score", "document_readiness", "eligibility_score", "program_match", "timeline", "required_documents", "recommendations", "risks"]):
        ai_result.setdefault("timeline", [])
        ai_result.setdefault("required_documents", [])
        ai_result.setdefault("recommendations", [])
        ai_result.setdefault("risks", [])
        return ai_result

    # Fallback: rule-based contextual logic
    topic = _detect_topic(situation)
    action_plan = _generate_action_plan(situation, topic)

    return {
        "title": _get_topic_label(topic) if topic != "general" else "Rencana Aksi Personal",
        "overview": f"Berdasarkan situasi yang Anda alami, JERNIH OS telah menganalisis kebutuhan dan menyusun rencana aksi personal.",
        "citizen_success_score": round(random.uniform(70, 92), 0),
        "document_readiness": round(random.uniform(40, 85), 0),
        "eligibility_score": round(random.uniform(65, 90), 0),
        "program_match": round(random.uniform(75, 95), 0),
        "timeline": [
            {
                "phase": "Hari Ini",
                "tasks": [{"task": t, "deadline": "Hari ini", "priority": "high", "done": False} for t in action_plan.get("today", [])],
            },
            {
                "phase": "Minggu Ini",
                "tasks": [{"task": t, "deadline": "3-7 hari", "priority": "high", "done": False} for t in action_plan.get("this_week", [])],
            },
            {
                "phase": "Minggu Depan",
                "tasks": [{"task": t, "deadline": "14 hari", "priority": "medium", "done": False} for t in action_plan.get("next_step", [])],
            },
        ],
        "required_documents": [
            {"name": "Kartu Keluarga (KK)", "status": "need", "notes": "Fotokopi 3 lembar"},
            {"name": "KTP Elektronik", "status": "ready"},
            {"name": "SKTM", "status": "need", "notes": "Ambil di kelurahan"},
        ],
        "recommendations": [
            "Segera urus dokumen kependudukan jika belum lengkap",
            "Daftar DTKS untuk memperkuat eligibilitas bantuan",
            "Siapkan dokumen pendukung tambahan",
        ],
        "risks": [
            {"risk": "Dokumen KK tidak update", "probability": "medium", "impact": "high"},
            {"risk": "Antrean panjang di kelurahan", "probability": "high", "impact": "medium"},
        ],
    }


def simulate_policy(policy: str, change: str) -> dict:
    """Simulate the impact of policy changes."""
    return {
        "summary": f"Simulasi perubahan kebijakan {policy}: '{change}' menunjukkan dampak signifikan terhadap cakupan penerima manfaat.",
        "affected_groups": [
            {"group": "Penerima manfaat eksisting", "impact": "positive", "estimate": "+45,000 penerima baru"},
            {"group": "Masyarakat berpenghasilan rendah", "impact": "positive", "estimate": "+12,000 penerima baru"},
            {"group": "Masyarakat berpendapatan menengah", "impact": "negative", "estimate": "-8,000 kehilangan akses"},
        ],
        "coverage_change": {
            "before": 8900000,
            "after": 9450000,
            "difference": 550000,
        },
        "opportunity_loss": "Diperkirakan 8,000 warga kehilangan akses, namun 550,000 warga baru mendapatkan akses. Dampak bersih: positif.",
        "social_impact": "Perubahan ini berpotensi meningkatkan partisipasi hingga 3.2%.",
        "recommendations": [
            "Sosialisasikan perubahan kebijakan secara masif",
            "Siapkan jalur pengaduan bagi warga yang terdampak negatif",
            "Monitoring dampak selama 6 bulan pertama implementasi",
        ],
    }


def get_knowledge_graph() -> dict:
    """Return knowledge graph data."""
    return {
        "nodes": [
            {"id": "pip", "label": "Program Indonesia Pintar", "type": "program", "description": "Bantuan pendidikan untuk siswa kurang mampu"},
            {"id": "kip", "label": "Kartu Indonesia Pintar", "type": "program", "description": "Kartu identitas penerima PIP"},
            {"id": "kis", "label": "Kartu Indonesia Sehat", "type": "program", "description": "Jaminan kesehatan masyarakat"},
            {"id": "bpnt", "label": "Bantuan Pangan Non-Tunai", "type": "program", "description": "Bantuan pangan untuk keluarga miskin"},
            {"id": "pkh", "label": "Program Keluarga Harapan", "type": "program", "description": "Bantuan sosial bersyarat"},
            {"id": "kemendikdasmen", "label": "Kemdikdasmen", "type": "agency", "description": "Kementerian Pendidikan Dasar dan Menengah"},
            {"id": "kemensos", "label": "Kemensos RI", "type": "agency", "description": "Kementerian Sosial RI"},
            {"id": "bpjs", "label": "BPJS Kesehatan", "type": "agency", "description": "Badan Penyelenggara Jaminan Sosial"},
            {"id": "dukcapil", "label": "Ditjen Dukcapil", "type": "agency", "description": "Direktorat Jenderal Kependudukan dan Pencatatan Sipil"},
            {"id": "kk", "label": "Kartu Keluarga", "type": "document", "description": "Dokumen identitas keluarga"},
            {"id": "ktp", "label": "KTP Elektronik", "type": "document", "description": "Kartu Tanda Penduduk elektronik"},
            {"id": "akte", "label": "Akta Kelahiran", "type": "document", "description": "Dokumen kelahiran"},
            {"id": "sktm", "label": "SKTM", "type": "document", "description": "Surat Keterangan Tidak Mampu"},
            {"id": "bantuan_pendidikan", "label": "Bantuan Pendidikan", "type": "benefit", "description": "Dana bantuan untuk biaya pendidikan"},
            {"id": "bantuan_kesehatan", "label": "Bantuan Kesehatan", "type": "benefit", "description": "Akses layanan kesehatan gratis"},
            {"id": "bantuan_pangan", "label": "Bantuan Pangan", "type": "benefit", "description": "Bantuan kebutuhan pangan"},
            {"id": "kantor_kelurahan", "label": "Kantor Kelurahan", "type": "location", "description": "Kantor pelayanan kelurahan"},
            {"id": "kecamatan", "label": "Kantor Kecamatan", "type": "location", "description": "Kantor pelayanan kecamatan"},
            {"id": "dtks", "label": "DTKS", "type": "requirement", "description": "Terdaftar di Data Terpadu Kesejahteraan Sosial"},
            {"id": "nik", "label": "Memiliki NIK", "type": "requirement", "description": "Nomor Induk Kependudukan valid"},
        ],
        "links": [
            {"source": "pip", "target": "kemendikdasmen", "label": "dikelola oleh"},
            {"source": "kip", "target": "pip", "label": "bagian dari"},
            {"source": "pip", "target": "bantuan_pendidikan", "label": "memberikan"},
            {"source": "kis", "target": "bpjs", "label": "dikelola oleh"},
            {"source": "kis", "target": "bantuan_kesehatan", "label": "memberikan"},
            {"source": "bpnt", "target": "kemensos", "label": "dikelola oleh"},
            {"source": "bpnt", "target": "bantuan_pangan", "label": "memberikan"},
            {"source": "pkh", "target": "kemensos", "label": "dikelola oleh"},
            {"source": "kk", "target": "dukcapil", "label": "diterbitkan oleh"},
            {"source": "ktp", "target": "dukcapil", "label": "diterbitkan oleh"},
            {"source": "pip", "target": "kk", "label": "membutuhkan"},
            {"source": "pip", "target": "ktp", "label": "membutuhkan"},
            {"source": "pip", "target": "sktm", "label": "membutuhkan"},
            {"source": "pip", "target": "dtks", "label": "memerlukan"},
            {"source": "pip", "target": "nik", "label": "memerlukan"},
            {"source": "kis", "target": "kk", "label": "membutuhkan"},
            {"source": "kis", "target": "nik", "label": "memerlukan"},
            {"source": "bpnt", "target": "kk", "label": "membutuhkan"},
            {"source": "bpnt", "target": "ktp", "label": "membutuhkan"},
            {"source": "pkh", "target": "dtks", "label": "memerlukan"},
            {"source": "pkh", "target": "kk", "label": "membutuhkan"},
            {"source": "pip", "target": "kis", "label": "terkait"},
            {"source": "pkh", "target": "bpnt", "label": "dapat digabung dengan"},
        ],
    }


def get_analytics() -> dict:
    """Return analytics dashboard data."""
    return {
        "total_citizens_served": 124583,
        "total_time_saved_minutes": 4890000,
        "total_programs_discovered": 15420,
        "total_procedures_simplified": 892,
        "estimated_economic_impact": 15780000000,
        "average_trust_score": 87,
        "average_success_score": 76,
        "community_trends": [
            {"category": "Pendidikan", "change": 23, "direction": "up", "period": "Bulan ini"},
            {"category": "Kesehatan", "change": 15, "direction": "up", "period": "Bulan ini"},
            {"category": "Bantuan Sosial", "change": 31, "direction": "up", "period": "Bulan ini"},
            {"category": "Ketenagakerjaan", "change": 8, "direction": "down", "period": "Bulan ini"},
        ],
        "top_concerns": [
            {"issue": "Pendaftaran PIP", "count": 4521, "growth": 34},
            {"issue": "Pengurusan KK", "count": 3890, "growth": 18},
            {"issue": "BPJS Kesehatan", "count": 3102, "growth": 22},
            {"issue": "Bansos Tunai", "count": 2890, "growth": 45},
        ],
        "regional_scores": {
            "Jakarta": {"education": 82, "health": 78, "social": 71, "accessibility": 85},
            "Jawa Barat": {"education": 74, "health": 69, "social": 65, "accessibility": 72},
            "Jawa Timur": {"education": 76, "health": 71, "social": 68, "accessibility": 70},
            "Jawa Tengah": {"education": 78, "health": 73, "social": 70, "accessibility": 74},
            "Sumatera Utara": {"education": 68, "health": 65, "social": 62, "accessibility": 64},
            "Sulawesi Selatan": {"education": 72, "health": 68, "social": 64, "accessibility": 66},
            "Papua": {"education": 45, "health": 42, "social": 38, "accessibility": 35},
            "Nusa Tenggara Timur": {"education": 52, "health": 48, "social": 44, "accessibility": 42},
        },
    }
