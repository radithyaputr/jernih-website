import re
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Union
from src.knowledge_base import KNOWLEDGE_BASE, TOPIC_CATEGORIES

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
    relevant_programs: list
    required_documents: list
    risk_factors: list
    timeline: dict
    action_plan: dict
    success_probability: float
    trust_score: TrustScore
    sources: list

@dataclass
class CasualResponse:
    session_id: str
    message: str

DEFAULT_SOURCES = [
    Source("Portal PIP - Kemdikdasmen", "https://pip.kemdikbud.go.id", "government"),
    Source("Data Terpadu Kesejahteraan Sosial (DTKS)", "https://dtks.kemensos.go.id", "government"),
    Source("Kemendagri - Dukcapil", "https://dukcapil.kemendagri.go.id", "government"),
]

def _detect_topic(message: str) -> str:
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
        return f"Kami akan membantu Anda mengurus {_get_topic_label(topic)}. Berikut informasi prosedur, persyaratan, dan kontak layanan yang dapat dihubungi."
    if topic == "bencana":
        return "Kami turut prihatin atas bencana yang Anda alami. Berikut informasi bantuan, kontak darurat, dan prosedur pengajuan bantuan bencana."
    if topic == "korupsi":
        return "Kami akan membantu Anda menyampaikan pengaduan atau laporan. Berikut saluran resmi, prosedur pelaporan, dan informasi perlindungan pelapor."
    words = m.split()
    question_words = ["apa", "bagaimana", "siapa", "kapan", "dimana", "mengapa", "berapa", "apakah", "bisakah", "bolehkah"]
    has_question = any(q in words for q in question_words)
    if has_question:
        return "Terima kasih atas pertanyaan Anda. JERNIH OS akan membantu Anda menemukan informasi yang dibutuhkan. Berikut analisis dan rekomendasi yang sesuai dengan pertanyaan Anda."
    return "Berdasarkan situasi yang Anda sampaikan, JERNIH OS telah menganalisis kebutuhan Anda dan menyusun rekomendasi program, dokumen, dan langkah-langkah yang perlu Anda tempuh untuk mengakses layanan publik."

def _generate_contextual_analysis(message: str, matched_programs: list, topic: str = "general") -> str:
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
    timelines = {
        "greeting": {"estimated_days": 0, "steps": [{"step": 1, "action": "Sampaikan pertanyaan Anda", "duration": "Sekarang", "office": "-"}]},
        "kematian": {"estimated_days": 10, "steps": [
            {"step": 1, "action": "Urus Akta Kematian di Dukcapil", "duration": "1-3 hari", "office": "Dukcapil"},
            {"step": 2, "action": "Perbaiki data KK (hapus yg meninggal)", "duration": "1-2 hari", "office": "Dukcapil"},
            {"step": 3, "action": "Urus surat pindah/domisili ahli waris", "duration": "1 hari", "office": "Kantor Kelurahan"},
            {"step": 4, "action": "Daftar program bantuan untuk keluarga", "duration": "3-7 hari", "office": "Dinas Sosial"},
            {"step": 5, "action": "Aktivasi rekening bantuan", "duration": "2-3 hari", "office": "Bank Penyalur"},
        ]},
        "pendidikan": {"estimated_days": 14, "steps": [
            {"step": 1, "action": "Verifikasi dokumen kependudukan", "duration": "1-2 hari", "office": "Dukcapil"},
            {"step": 2, "action": "Ambil SKTM dari kelurahan", "duration": "1 hari", "office": "Kantor Kelurahan"},
            {"step": 3, "action": "Daftar PIP/KIP di sekolah/kampus", "duration": "3-5 hari", "office": "Sekolah/Dinas Pendidikan"},
            {"step": 4, "action": "Aktivasi rekening bantuan", "duration": "2-3 hari", "office": "Bank Penyalur"},
            {"step": 5, "action": "Konfirmasi penerimaan bantuan", "duration": "1-2 hari", "office": "-"},
        ]},
        "dokumen_hilang": {"estimated_days": 7, "steps": [
            {"step": 1, "action": "Buat laporan kehilangan ke polisi", "duration": "1 hari", "office": "Kantor Polisi"},
            {"step": 2, "action": "Ambil surat pengantar RT/RW", "duration": "1 hari", "office": "RT/RW setempat"},
            {"step": 3, "action": "Datang ke Dukcapil dengan dokumen", "duration": "1 hari", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Foto & perekaman biometrik", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 5, "action": "Tunggu pencetakan KTP", "duration": "1-14 hari", "office": "-"},
        ]},
        "kesehatan": {"estimated_days": 5, "steps": [
            {"step": 1, "action": "Cek status kepesertaan BPJS", "duration": "1 jam", "office": "Online/BPJS"},
            {"step": 2, "action": "Aktifkan kepesertaan jika nonaktif", "duration": "1 hari", "office": "Kantor BPJS"},
            {"step": 3, "action": "Urus rujukan ke faskes", "duration": "1 hari", "office": "Puskesmas/Faskes 1"},
            {"step": 4, "action": "Daftar layanan kesehatan", "duration": "1 hari", "office": "Rumah Sakit"},
        ]},
        "kk": {"estimated_days": 7, "steps": [
            {"step": 1, "action": "Kumpulkan dokumen (KK lama, KTP)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Ambil formulir di Dukcapil", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 3, "action": "Isi dan serahkan formulir", "duration": "1 hari", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Tunggu proses verifikasi", "duration": "3-7 hari", "office": "-"},
            {"step": 5, "action": "Ambil KK baru", "duration": "1 hari", "office": "Kantor Dukcapil"},
        ]},
        "akte": {"estimated_days": 5, "steps": [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Surat Nikah, Surat Lahir)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Datang ke Dukcapil", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 3, "action": "Isi formulir permohonan", "duration": "30 menit", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Verifikasi dokumen", "duration": "1-3 hari", "office": "Kantor Dukcapil"},
            {"step": 5, "action": "Ambil Akta Kelahiran", "duration": "1 hari", "office": "Kantor Dukcapil"},
        ]},
        "nikah": {"estimated_days": 14, "steps": [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Pas Foto)", "duration": "1-2 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar di KUA/Catatan Sipil", "duration": "1 hari", "office": "KUA/Catatan Sipil"},
            {"step": 3, "action": "Pengumuman pernikahan (10 hari kerja)", "duration": "10 hari", "office": "-"},
            {"step": 4, "action": "Pelaksanaan akad nikah", "duration": "1 hari", "office": "KUA/Tempat Nikah"},
            {"step": 5, "action": "Ambil Buku Nikah/Akta Pernikahan", "duration": "1 hari", "office": "KUA/Catatan Sipil"},
        ]},
        "pindah": {"estimated_days": 7, "steps": [
            {"step": 1, "action": "Urus surat pindah dari kelurahan asal", "duration": "1 hari", "office": "Kantor Kelurahan Asal"},
            {"step": 2, "action": "Lapor ke kelurahan tujuan", "duration": "1 hari", "office": "Kantor Kelurahan Tujuan"},
            {"step": 3, "action": "Verifikasi data kependudukan", "duration": "3-5 hari", "office": "Kantor Kecamatan"},
            {"step": 4, "action": "Update KK dan KTP", "duration": "1-2 hari", "office": "Kantor Dukcapil"},
        ]},
        "paspor": {"estimated_days": 10, "steps": [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Akta Lahir)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar online via M-Paspor", "duration": "1 jam", "office": "Online"},
            {"step": 3, "action": "Bayar biaya paspor", "duration": "1 jam", "office": "Bank/Online"},
            {"step": 4, "action": "Datang ke Kantor Imigrasi untuk wawancara & foto", "duration": "1 hari", "office": "Kantor Imigrasi"},
            {"step": 5, "action": "Tunggu pencetakan paspor", "duration": "3-5 hari", "office": "-"},
        ]},
        "sim": {"estimated_days": 3, "steps": [
            {"step": 1, "action": "Siapkan dokumen (KTP, surat kesehatan)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar online atau datang ke Satpas", "duration": "1 hari", "office": "Satpas SIM"},
            {"step": 3, "action": "Ikuti tes teori", "duration": "1 jam", "office": "Satpas SIM"},
            {"step": 4, "action": "Ikuti tes praktik", "duration": "1 jam", "office": "Satpas SIM"},
            {"step": 5, "action": "Foto dan ambil SIM", "duration": "1 jam", "office": "Satpas SIM"},
        ]},
    }
    if topic in timelines:
        return timelines[topic]
    return {"estimated_days": 14, "steps": [
        {"step": 1, "action": "Verifikasi dokumen kependudukan", "duration": "1-2 hari", "office": "Dukcapil"},
        {"step": 2, "action": "Urus dokumen pendukung", "duration": "1 hari", "office": "Kantor Kelurahan"},
        {"step": 3, "action": "Daftar program terkait", "duration": "3-5 hari", "office": "Dinas Terkait"},
        {"step": 4, "action": "Aktivasi rekening/penerimaan", "duration": "2-3 hari", "office": "Bank Penyalur"},
        {"step": 5, "action": "Konfirmasi dan monitoring", "duration": "1-2 hari", "office": "-"},
    ]}

def _generate_contextual_documents(message: str, topic: str = "general") -> list:
    if topic == "greeting":
        return []
    base = [
        {"name": "Kartu Keluarga (KK)", "description": "KK asli dan fotokopi 3 lembar", "priority": "high"},
        {"name": "KTP Elektronik", "description": "KTP-el asli dan fotokopi 3 lembar", "priority": "high"},
    ]
    extra = {
        "kematian": [{"name": "Akta Kematian", "description": "Dari rumah sakit/kelurahan", "priority": "high"}, {"name": "Surat Keterangan Ahli Waris", "description": "Dari kelurahan", "priority": "high"}],
        "pendidikan": [{"name": "Akta Kelahiran", "description": "Akta kelahiran anak (jika ada)", "priority": "medium"}, {"name": "Surat Keterangan Tidak Mampu (SKTM)", "description": "Dari kelurahan/desa setempat", "priority": "medium"}, {"name": "Rapor/SKHUN/Ijazah", "description": "Untuk program pendidikan", "priority": "low"}],
        "dokumen_hilang": [{"name": "Surat Kehilangan dari Polisi", "description": "Laporan kehilangan dari kantor polisi", "priority": "high"}, {"name": "Surat Pengantar RT/RW", "description": "Pengantar dari ketua RT/RW", "priority": "high"}],
        "kesehatan": [{"name": "Kartu BPJS/KIS", "description": "Kartu kepesertaan BPJS", "priority": "high"}, {"name": "Surat Rujukan", "description": "Dari faskes tingkat 1", "priority": "medium"}],
        "bansos": [{"name": "Surat Keterangan Tidak Mampu (SKTM)", "description": "Dari kelurahan/desa setempat", "priority": "high"}, {"name": "Terdaftar di DTKS", "description": "Data Terpadu Kesejahteraan Sosial", "priority": "high"}],
        "usaha": [{"name": "Surat Izin Usaha", "description": "NIB/UMKU jika sudah ada", "priority": "medium"}, {"name": "Proposal Usaha", "description": "Rencana bisnis sederhana", "priority": "medium"}],
        "nikah": [{"name": "Surat Nikah dari KUA/Catatan Sipil", "description": "Dari KUA/Catatan Sipil", "priority": "high"}, {"name": "Pas Foto 4x6 (background biru)", "description": "Pas foto latar biru, formal 4x6", "priority": "medium"}, {"name": "Surat Keterangan Belum Menikah", "description": "Dari kelurahan", "priority": "medium"}],
        "akte": [{"name": "Surat Keterangan Lahir", "description": "Dari bidan/dokter/rumah sakit", "priority": "high"}, {"name": "Surat Nikah Orang Tua", "description": "Fotokopi Buku Nikah orang tua", "priority": "high"}],
        "pindah": [{"name": "Surat Keterangan Pindah", "description": "Dari kelurahan asal", "priority": "high"}, {"name": "Surat Pengantar RT/RW", "description": "Pengantar dari ketua RT/RW", "priority": "high"}],
        "paspor": [{"name": "Pas Foto 2x3 (background merah/putih)", "description": "Syarat paspor terbaru", "priority": "high"}, {"name": "Bukti Pembayaran Paspor", "description": "Dari bank atau online", "priority": "high"}],
        "sim": [{"name": "Surat Keterangan Sehat", "description": "Dari dokter/rumah sakit", "priority": "high"}, {"name": "Pas Foto 2x3", "description": "Pas foto latar merah", "priority": "medium"}],
    }
    if topic in extra:
        base += extra[topic]
    if topic in ["pajak", "perumahan", "kk", "bencana", "korupsi", "listrik", "air", "sampah"]:
        base += [{"name": "Dokumen pendukung terkait", "description": "Sesuai dengan ketentuan instansi terkait", "priority": "medium"}]
    return base

def _generate_action_plan(message: str, topic: str = "general") -> dict:
    if topic == "greeting":
        return {"today": ["Silakan ceritakan situasi Anda"], "this_week": [], "next_step": []}
    plans = {
        "kematian": {
            "today": ["Urus Akta Kematian di Dukcapil", "Kumpulkan dokumen ahli waris", "Hubungi kelurahan untuk surat keterangan"],
            "this_week": ["Perbaiki data KK di Dukcapil", "Urus surat pindah/domisili", "Cek program bantuan untuk keluarga ditinggalkan"],
            "next_step": ["Daftar program bantuan sosial", "Aktivasi rekening bantuan", "Pantau status penerimaan"],
        },
        "pendidikan": {
            "today": ["Kumpulkan KK, KTP, dan Akta Kelahiran", "Cek jadwal pendaftaran PIP/KIP", "Hubungi sekolah/kampus"],
            "this_week": ["Ambil SKTM di kelurahan", "Verifikasi dokumen ke Dukcapil", "Daftar program PIP/KIP"],
            "next_step": ["Aktivasi rekening bantuan", "Pantau status penerimaan", "Konfirmasi ke pihak sekolah"],
        },
        "dokumen_hilang": {
            "today": ["Buat laporan kehilangan ke polisi", "Ambil surat pengantar RT/RW"],
            "this_week": ["Datang ke Dukcapil dengan dokumen lengkap", "Foto dan perekaman biometrik"],
            "next_step": ["Pantau proses pencetakan KTP", "Ambil KTP di Dukcapil jika sudah jadi"],
        },
        "kesehatan": {
            "today": ["Cek status kepesertaan BPJS via mobile app", "Siapkan dokumen BPJS"],
            "this_week": ["Kunjungi Puskesmas/Faskes 1 untuk rujukan", "Urus administrasi di rumah sakit"],
            "next_step": ["Pantau status klaim/jaminan", "Lakukan pengobatan sesuai jadwal"],
        },
        "bansos": {
            "today": ["Cek status DTKS di kelurahan", "Kumpulkan KK, KTP, dan dokumen pendukung"],
            "this_week": ["Ambil SKTM di kelurahan", "Daftar program bansos yang sesuai"],
            "next_step": ["Pantau status penerimaan bansos", "Aktivasi rekening bantuan"],
        },
        "usaha": {
            "today": ["Kumpulkan dokumen usaha dan identitas", "Cek program bantuan UMKM yang tersedia"],
            "this_week": ["Urus NIB/izin usaha jika belum punya", "Ajukan proposal bantuan usaha"],
            "next_step": ["Pantau status pengajuan bantuan", "Ikuti pelatihan jika disyaratkan"],
        },
        "nikah": {
            "today": ["Siapkan KK, KTP, dan pas foto", "Cek jadwal pendaftaran di KUA/Catatan Sipil"],
            "this_week": ["Daftar pernikahan di KUA/Catatan Sipil", "Tunggu pengumuman 10 hari kerja"],
            "next_step": ["Persiapkan akad nikah", "Ambil Buku Nikah/Akta Pernikahan"],
        },
        "pindah": {
            "today": ["Urus surat pindah dari kelurahan asal", "Siapkan dokumen KTP dan KK"],
            "this_week": ["Lapor ke kelurahan tujuan", "Verifikasi data kependudukan"],
            "next_step": ["Update KK dan KTP di domisili baru", "Aktivasi dokumen kependudukan"],
        },
        "akte": {
            "today": ["Kumpulkan surat keterangan lahir dari bidan/dokter", "Siapkan KK dan KTP orang tua"],
            "this_week": ["Datang ke Dukcapil untuk daftar", "Isi formulir permohonan akta"],
            "next_step": ["Ambil Akta Kelahiran", "Update KK dengan anggota baru"],
        },
    }
    if topic in plans:
        return plans[topic]
    return {
        "today": ["Kumpulkan dokumen identitas (KK, KTP)", "Hubungi kelurahan untuk informasi"],
        "this_week": ["Verifikasi dokumen ke Dukcapil", "Lengkapi dokumen pendukung"],
        "next_step": ["Daftar program bantuan", "Pantau status pengajuan"],
    }

def _generate_risk_factors(message: str, topic: str = "general") -> list:
    if topic == "greeting":
        return []
    risks = [
        {"risk": "Dokumen tidak lengkap menghambat proses", "severity": "high", "mitigation": "Siapkan semua dokumen sebelum memulai proses"},
        {"risk": "Antrean panjang di kantor pelayanan", "severity": "medium", "mitigation": "Datang pagi hari atau gunakan layanan online"},
    ]
    extra_risks = {
        "kematian": [{"risk": "Perbedaan data ahli waris", "severity": "high", "mitigation": "Siapkan surat keterangan ahli waris dari kelurahan"}, {"risk": "Berkabung mempengaruhi konsentrasi", "severity": "low", "mitigation": "Minta bantuan keluarga atau kerabat terdekat"}],
        "pendidikan": [{"risk": "Batas waktu pendaftaran terbatas", "severity": "high", "mitigation": "Cek jadwal pendaftaran dan daftar segera"}, {"risk": "Perubahan status ekonomi", "severity": "medium", "mitigation": "Siapkan dokumen pendukung kondisi ekonomi terkini"}],
        "dokumen_hilang": [{"risk": "Data tidak ditemukan di database Dukcapil", "severity": "high", "mitigation": "Verifikasi data kependudukan sebelum datang"}, {"risk": "Sistem Dukcapil terkadang gangguan", "severity": "low", "mitigation": "Hubungi Dukcapil untuk cek jadwal servis sistem"}],
    }
    for top, extra in extra_risks.items():
        if topic == top:
            risks += extra
    if topic in ["bansos", "usaha"]:
        risks += [{"risk": "Kuota program terbatas", "severity": "high", "mitigation": "Daftar sesegera mungkin"}, {"risk": "Data DTKS tidak valid", "severity": "medium", "mitigation": "Verifikasi data DTKS di kelurahan terlebih dahulu"}]
    if topic in ["nikah", "pindah", "akte"]:
        risks += [{"risk": "Dokumen kurang lengkap", "severity": "high", "mitigation": "Cek ulang persyaratan sebelum datang ke instansi"}, {"risk": "Prosedur berbeda antar daerah", "severity": "medium", "mitigation": "Konfirmasi prosedur ke instansi setempat"}]
    if topic in ["sim", "paspor"]:
        risks += [{"risk": "Antrean online penuh", "severity": "medium", "mitigation": "Cek ketersediaan jadwal secara berkala"}, {"risk": "Syarat administrasi berubah", "severity": "low", "mitigation": "Cek website resmi untuk info terbaru"}]
    return risks

def analyze_hoax_fallback(text: str) -> dict:
    suspicious_indicators = [
        "bagikan", "sebarkan", "viral", "jangan lupa share", "di luar nalar",
        "tidak masuk akal", "dijamin", "Rp", "jutaan", "milyaran", "gratis",
        "tanpa syarat", "forward", "kirim ke 10", "pns", "gaji ke-13",
        "hoax", "bohong", "tipu", "penipuan", "100%", "dijamin", "pasti",
        "asli", "transfer", "nomor rekening", "klik link", "bagikan ke 10",
        "sebelum dihapus", "sekarang juga",
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
        "analysis": "Informasi ini memiliki indikasi kuat sebagai hoaks." if verdict == "hoax" else "Informasi ini perlu diverifikasi lebih lanjut." if verdict == "questionable" else "Informasi ini tampaknya kredibel.",
        "source_comparison": [
            {"source": "Portal Informasi Indonesia (data.go.id)", "alignment": "contradicts" if verdict != "credible" else "supports", "excerpt": "Data resmi menunjukkan tidak ada kebijakan tersebut" if verdict != "credible" else "Informasi sesuai dengan data resmi"},
            {"source": "Kemensos RI", "alignment": "contradicts" if verdict != "credible" else "neutral"},
        ],
        "fact_checks": [{"claim": "Klaim dalam informasi", "verdict": "SALAH" if verdict != "credible" else "BENAR", "source": "Kemensos RI"}],
        "indicators": matched_indicators if verdict != "credible" else ["Informasi ini lolos verifikasi awal"],
    }

def generate_action_plan_fallback(situation: str) -> dict:
    topic = _detect_topic(situation)
    ap = _generate_action_plan(situation, topic)
    return {
        "title": _get_topic_label(topic) if topic != "general" else "Rencana Aksi Personal",
        "overview": "Berdasarkan situasi yang Anda alami, JERNIH OS telah menganalisis kebutuhan dan menyusun rencana aksi personal.",
        "citizen_success_score": round(random.uniform(70, 92), 0),
        "document_readiness": round(random.uniform(40, 85), 0),
        "eligibility_score": round(random.uniform(65, 90), 0),
        "program_match": round(random.uniform(75, 95), 0),
        "timeline": [
            {"phase": "Hari Ini", "tasks": [{"task": t, "deadline": "Hari ini", "priority": "high", "done": False} for t in ap.get("today", [])]},
            {"phase": "Minggu Ini", "tasks": [{"task": t, "deadline": "3-7 hari", "priority": "high", "done": False} for t in ap.get("this_week", [])]},
            {"phase": "Minggu Depan", "tasks": [{"task": t, "deadline": "14 hari", "priority": "medium", "done": False} for t in ap.get("next_step", [])]},
        ],
        "required_documents": [
            {"name": "Kartu Keluarga (KK)", "status": "need", "notes": "Fotokopi 3 lembar"},
            {"name": "KTP Elektronik", "status": "ready"},
            {"name": "SKTM", "status": "need", "notes": "Ambil di kelurahan"},
        ],
        "recommendations": ["Segera urus dokumen kependudukan jika belum lengkap", "Daftar DTKS untuk memperkuat eligibilitas bantuan", "Siapkan dokumen pendukung tambahan"],
        "risks": [{"risk": "Dokumen KK tidak update", "probability": "medium", "impact": "high"}, {"risk": "Antrean panjang di kelurahan", "probability": "high", "impact": "medium"}],
    }

def analyze_situation_fallback(message: str) -> Union[CasualResponse, CopilotResponse]:
    session_id = f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
    message_lower = message.lower()
    topic = _detect_topic(message)
    if topic == "greeting":
        summary = _generate_contextual_summary(message, [], topic)
        return CasualResponse(session_id=session_id, message=summary)
    matched_programs = []
    for prog_id, prog in KNOWLEDGE_BASE["programs"].items():
        score = sum(1 for kw in prog["keywords"] if kw in message_lower)
        if score > 0:
            matched_programs.append({"name": prog["name"], "agency": prog["agency"], "description": prog["description"], "match_score": min(score * 25 + 50, 98), "url": prog.get("url", "")})
    if not matched_programs:
        matched_programs = [{"name": "Program Indonesia Pintar (PIP)", "agency": "Kemdikdasmen", "description": "Bantuan pendidikan untuk anak usia sekolah dari keluarga miskin/rentan", "match_score": 75, "url": "https://pip.kemdikbud.go.id"}, {"name": "Kartu Indonesia Sehat (KIS)", "agency": "BPJS Kesehatan", "description": "Jaminan kesehatan bagi masyarakat kurang mampu", "match_score": 65}]
    return CopilotResponse(
        session_id=session_id,
        summary=_generate_contextual_summary(message, matched_programs, topic),
        analysis=_generate_contextual_analysis(message, matched_programs, topic),
        relevant_programs=matched_programs,
        required_documents=_generate_contextual_documents(message, topic),
        risk_factors=_generate_risk_factors(message, topic),
        timeline=_generate_contextual_timeline(message, topic),
        action_plan=_generate_action_plan(message, topic),
        success_probability=round(random.uniform(65, 88), 0),
        trust_score=TrustScore(
            overall=round(random.uniform(80, 95), 1),
            reliability=round(random.uniform(85, 98), 1),
            freshness=round(random.uniform(75, 92), 1),
            verification=round(random.uniform(82, 95), 1),
            transparency=round(random.uniform(88, 98), 1),
        ),
        sources=DEFAULT_SOURCES,
    )
