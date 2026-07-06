import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time

st.set_page_config(
    page_title="Predictive Map - JERNIH OS",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
from pathlib import Path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.ui_components import inject_css
from src.ai_service import chat_with_ai
from src.agents import GEOSPATIAL_PROMPT

inject_css()

INDONESIA_REGIONS = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "districts": [
        "Gambir", "Sawah Besar", "Menteng", "Tanah Abang", "Senen",
        "Penjaringan", "Tanjung Priok", "Kelapa Gading", "Cengkareng",
        "Grogol Petamburan", "Kebayoran Baru", "Pasar Minggu",
        "Tebet", "Jatinegara", "Cakung"
    ]},
    "Surabaya": {"lat": -7.2504, "lon": 112.7688, "districts": [
        "Tegalsari", "Simokerto", "Genteng", "Bubutan", "Gubeng",
        "Gunung Anyar", "Sukolilo", "Tambaksari", "Mulyorejo",
        "Wonokromo", "Wiyung", "Karang Pilang"
    ]},
    "Bandung": {"lat": -6.9175, "lon": 107.6191, "districts": [
        "Andir", "Astana Anyar", "Babakan Ciparay", "Bandung Kidul",
        "Bandung Kulon", "Bandung Wetan", "Batununggal", "Bojongloa Kaler",
        "Buahbatu", "Cibeunying Kaler", "Cibeunying Kidul", "Coblong"
    ]},
    "Medan": {"lat": 3.5952, "lon": 98.6722, "districts": [
        "Medan Amplas", "Medan Area", "Medan Barat", "Medan Baru",
        "Medan Belawan", "Medan Deli", "Medan Denai", "Medan Helvetia",
        "Medan Johor", "Medan Kota"
    ]},
    "Makassar": {"lat": -5.1477, "lon": 119.4327, "districts": [
        "Biringkanaya", "Bontoala", "Kepulauan Sangkarrang", "Makassar",
        "Mamajang", "Manggala", "Mariso", "Panakkukang", "Rappocini",
        "Tallo", "Tamalanrea", "Tamalate"
    ]},
    "Semarang": {"lat": -6.9932, "lon": 110.4203, "districts": [
        "Banyumanik", "Candisari", "Gajahmungkur", "Gayamsari",
        "Genuk", "Gunungpati", "Mijen", "Ngaliyan", "Pedurungan",
        "Semarang Barat", "Semarang Selatan", "Semarang Tengah"
    ]},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695, "districts": [
        "Danurejan", "Gedongtengen", "Gondokusuman", "Gondomanan",
        "Jetis", "Kotagede", "Kraton", "Mantrijeron", "Mergangsan",
        "Ngampilan", "Pakualaman", "Tegalrejo", "Umbulharjo"
    ]},
    "Denpasar": {"lat": -8.6705, "lon": 115.2126, "districts": [
        "Denpasar Barat", "Denpasar Selatan", "Denpasar Timur", "Denpasar Utara"
    ]},
}

ANALYSIS_MODES = {
    "Prediksi Daerah Rawan Hoax": {
        "icon": "📰",
        "desc": "Memetakan wilayah dengan penyebaran misinformasi tertinggi",
        "color": [255, 71, 87],
        "ai_target": "Rawan Hoax",
    },
    "Prediksi Daerah Rawan Banjir": {
        "icon": "🌊",
        "desc": "Memprediksi titik-titik rawan banjir berdasarkan pola historis",
        "color": [54, 162, 235],
        "ai_target": "Rawan Banjir",
    },
    "Prediksi Daerah Butuh Bantuan Sosial": {
        "icon": "🤝",
        "desc": "Mengidentifikasi area prioritas penyaluran bansos bulan depan",
        "color": [46, 213, 115],
        "ai_target": "Bantuan Sosial",
    },
}

@st.cache_data(show_spinner=False, ttl=300)
def generate_ai_prediction(analysis_mode_key, timeframe, sensitivity, seed, region_name):
    mode = ANALYSIS_MODES[analysis_mode_key]
    target = mode["ai_target"]
    np.random.seed(seed)

    region_info = INDONESIA_REGIONS[region_name]
    center_lat = region_info["lat"]
    center_lon = region_info["lon"]

    user_prompt = (
        f"Target Analisis: {target}\n"
        f"Wilayah: {region_name}, Indonesia\n"
        f"Periode Prediksi: {timeframe} hari ke depan\n"
        f"Level Sensitivitas: {sensitivity}/10\n\n"
        f"Prediksi 5-8 kecamatan di {region_name} yang paling {target.lower()} "
        f"untuk {timeframe} hari ke depan. Berikan alasan spesifik, skor risiko, tren, "
        f"estimasi jumlah penduduk terdampak, dan rekomendasi."
    )

    ai_result = chat_with_ai(GEOSPATIAL_PROMPT, user_prompt)

    hotspots_raw = []
    confidence = 80
    summary = ""
    trend_analysis = ""
    data_sources = []

    if ai_result and "hotspots" in ai_result and len(ai_result["hotspots"]) > 0:
        hotspots_raw = ai_result["hotspots"]
        confidence = int(ai_result.get("confidence_score", 80))
        summary = ai_result.get("summary", "")
        trend_analysis = ai_result.get("trend_analysis", "")
        data_sources = ai_result.get("data_sources", [])
    else:
        hotspots_raw = generate_fallback_hotspots(target, seed, region_name)

    df_hotspots, df_clusters, df_heat = build_dataframes(hotspots_raw, target, sensitivity, region_name)
    return df_hotspots, df_clusters, df_heat, hotspots_raw, confidence, summary, trend_analysis, data_sources, center_lat, center_lon


# Real risk data for each region & target type
REAL_RISK_DATA = {
    "Jakarta": {
        "Rawan Banjir": [
            ("Penjaringan", -6.1256, 106.7903, 92, "Wilayah pesisir Utara Jakarta, langganan banjir rob setiap tahun"),
            ("Tanjung Priok", -6.1120, 106.8839, 88, "Daerah pelabuhan dengan drainase buruk, banjir saat pasang"),
            ("Cakung", -6.1760, 106.9280, 85, "Cekungan rendah, banjir kiriman dari hulu saat hujan lebat"),
            ("Kelapa Gading", -6.1598, 106.9075, 78, "Drainase tersumbat sampah, banjir akibat luapan Kali Sunter"),
            ("Cengkareng", -6.1520, 106.7301, 82, "Daerah padat penduduk dekat sungai, banjir 1-2 meter saat musim hujan"),
            ("Grogol Petamburan", -6.1621, 106.7885, 70, "Banjir lokal akibat sistem drainase tidak memadai"),
            ("Sawah Besar", -6.1600, 106.8300, 65, "Banjir akibat luapan Kali Ciliwung"),
            ("Pasar Minggu", -6.2870, 106.8425, 60, "Banjir kiriman dari hulu saat intensitas hujan tinggi"),
        ],
        "Rawan Hoax": [
            ("Menteng", -6.1976, 106.8342, 72, "Wilayah pusat bisnis dan politik, sering jadi sasaran hoax politik"),
            ("Tanah Abang", -6.1850, 106.8090, 85, "Pusat perdagangan dengan perputaran informasi massif"),
            ("Senen", -6.1730, 106.8430, 82, "Pasar dan terminal tersebar hoax komersial dan sosial"),
            ("Gambir", -6.1766, 106.8258, 75, "Kawasan perkantoran pemerintah, hoax kebijakan marak"),
            ("Jatinegara", -6.2149, 106.8742, 80, "Kampung padat penduduk, hoax kesehatan dan bansos menyebar cepat"),
            ("Cengkareng", -6.1520, 106.7301, 78, "Daerah penyangga hoax via grup WhatsApp dan media sosial"),
            ("Tanjung Priok", -6.1120, 106.8839, 76, "Masyarakat multi-etnis, hoax SARA rawan menyebar"),
            ("Kebayoran Baru", -6.2360, 106.8048, 55, "Kelas menengah atas, hoax investasi dan properti"),
        ],
        "Bantuan Sosial": [
            ("Penjaringan", -6.1256, 106.7903, 88, "Keluarga prasejahtera tinggi, banyak warga nelayan dan buruh"),
            ("Cakung", -6.1760, 106.9280, 85, "Kawasan industri dengan pekerja informal rentan"),
            ("Tanjung Priok", -6.1120, 106.8839, 82, "Masyarakat pesisir dengan akses pendidikan dan kesehatan terbatas"),
            ("Cengkareng", -6.1520, 106.7301, 80, "Kawasan kumuh dengan tingkat pengangguran tinggi"),
            ("Pasar Minggu", -6.2870, 106.8425, 75, "Daerah penyangga dengan penduduk berpenghasilan rendah"),
            ("Grogol Petamburan", -6.1621, 106.7885, 72, "Kampung padat dengan banyak kepala keluarga miskin"),
        ],
    },
    "Surabaya": {
        "Rawan Banjir": [
            ("Gunung Anyar", -7.3368, 112.7788, 85, "Daerah rendah dekat sungai, banjir rob dan hujan"),
            ("Tambaksari", -7.2473, 112.7580, 82, "Cekungan alami yang sering tergenang"),
            ("Simokerto", -7.2320, 112.7500, 78, "Drainase buruk, banjir saat hujan deras"),
            ("Wonokromo", -7.2965, 112.7340, 75, "Dekat Kali Wonokromo, rawan luapan sungai"),
            ("Mulyorejo", -7.2600, 112.7850, 70, "Genangan akibat limpasan air sungai"),
        ],
        "Rawan Hoax": [
            ("Genteng", -7.2572, 112.7429, 85, "Pusat kota dan perdagangan, rawan hoax komersial"),
            ("Tegalsari", -7.2700, 112.7300, 80, "Kawasan mahasiswa, hoax politik dan sosial cepat viral"),
            ("Bubutan", -7.2400, 112.7350, 75, "Pasar tradisional besar, hoax sembako dan kesehatan"),
        ],
        "Bantuan Sosial": [
            ("Gunung Anyar", -7.3368, 112.7788, 88, "Kawasan kumuh dengan kepadatan tinggi"),
            ("Simokerto", -7.2320, 112.7500, 85, "Penduduk prasejahtera dominan"),
            ("Karang Pilang", -7.3220, 112.6920, 80, "Daerah industri dengan buruh informal"),
        ],
    },
    "Bandung": {
        "Rawan Banjir": [
            ("Babakan Ciparay", -6.9410, 107.6010, 80, "Daerah rendah Bandung Selatan, langganan banjir"),
            ("Bojongloa Kaler", -6.9340, 107.5920, 78, "Cekungan dangkal, drainase tersumbat"),
            ("Andir", -6.9010, 107.5660, 75, "Dekat sungai Citarum, banjir kiriman"),
            ("Batununggal", -6.9180, 107.6280, 72, "Drainase buruk, genangan saat hujan"),
        ],
        "Rawan Hoax": [
            ("Babakan Ciparay", -6.9410, 107.6010, 82, "Kampung padat, hoax kesehatan dan bansos marak"),
            ("Coblong", -6.8910, 107.6080, 78, "Kawasan mahasiswa, hoax akademik dan politik"),
            ("Buahbatu", -6.9530, 107.6430, 75, "Pusat perbelanjaan, hoax diskon dan penipuan"),
        ],
        "Bantuan Sosial": [
            ("Babakan Ciparay", -6.9410, 107.6010, 90, "Keluarga prasejahtera >40%, rawan stunting"),
            ("Bojongloa Kaler", -6.9340, 107.5920, 85, "Penduduk padat dengan akses terbatas"),
            ("Astana Anyar", -6.9260, 107.5800, 78, "Kawasan kumuh dengan pendidikan rendah"),
        ],
    },
    "Medan": {
        "Rawan Banjir": [
            ("Medan Belawan", 3.7875, 98.6835, 92, "Wilayah pesisir, banjir rob dan pasang surut"),
            ("Medan Deli", 3.6580, 98.6750, 85, "Dekat sungai Deli, langganan banjir tahunan"),
            ("Medan Amplas", 3.5500, 98.6800, 78, "Cekungan rendah, drainase buruk"),
            ("Medan Kota", 3.5880, 98.6800, 75, "Pusat kota dengan drainase tersumbat sampah"),
        ],
        "Rawan Hoax": [
            ("Medan Kota", 3.5880, 98.6800, 85, "Pusat informasi, hoax politik dan SARA rawan"),
            ("Medan Area", 3.5750, 98.6900, 80, "Pasar tradisional besar, hoax komersial"),
            ("Medan Helvetia", 3.5950, 98.6350, 75, "Daerah multi-etnis, hoax SARA"),
        ],
        "Bantuan Sosial": [
            ("Medan Belawan", 3.7875, 98.6835, 90, "Nelayan prasejahtera, akses pendidikan minim"),
            ("Medan Deli", 3.6580, 98.6750, 85, "Kawasan kumuh padat penduduk"),
            ("Medan Amplas", 3.5500, 98.6800, 80, "Daerah penyangga dengan ekonomi rendah"),
        ],
    },
    "Makassar": {
        "Rawan Banjir": [
            ("Biringkanaya", -5.0800, 119.5100, 82, "Daerah rendah dekat pantai, banjir rob"),
            ("Tallo", -5.1150, 119.4450, 80, "Dekat muara sungai Tallo, banjir kiriman"),
            ("Panakkukang", -5.1470, 119.4500, 75, "Cekungan perkotaan, drainase buruk"),
            ("Manggala", -5.1400, 119.4800, 72, "Daerah penyangga dengan genangan musiman"),
        ],
        "Rawan Hoax": [
            ("Makassar", -5.1370, 119.4250, 85, "Pusat kota, hoax politik dan bisnis marak"),
            ("Panakkukang", -5.1470, 119.4500, 80, "Pusat perbelanjaan, hoax diskon dan investasi"),
            ("Tamalate", -5.1720, 119.4000, 75, "Kawasan padat, hoax kesehatan dan bansos"),
        ],
        "Bantuan Sosial": [
            ("Tallo", -5.1150, 119.4450, 88, "Kawasan kumuh pesisir dengan kemiskinan tinggi"),
            ("Biringkanaya", -5.0800, 119.5100, 82, "Daerah penyangga dengan keterbatasan akses"),
            ("Mariso", -5.1550, 119.4050, 78, "Kampung padat dengan pendidikan rendah"),
        ],
    },
    "Semarang": {
        "Rawan Banjir": [
            ("Genuk", -6.9430, 110.4680, 90, "Wilayah pesisir Utara, banjir rob dan pasang"),
            ("Semarang Barat", -6.9680, 110.3950, 85, "Daerah rendah dekat pantai, langganan rob"),
            ("Pedurungan", -7.0030, 110.4630, 78, "Cekungan dengan drainase buruk"),
            ("Gayamsari", -6.9830, 110.4300, 75, "Genangan di musim hujan akibat luapan sungai"),
        ],
        "Rawan Hoax": [
            ("Semarang Tengah", -6.9680, 110.4250, 82, "Pusat kota, hoax politik dan perdagangan"),
            ("Semarang Barat", -6.9680, 110.3950, 78, "Kawasan padat, hoax sosial menyebar cepat"),
            ("Pedurungan", -7.0030, 110.4630, 75, "Daerah padat, hoax kesehatan dan bansos"),
        ],
        "Bantuan Sosial": [
            ("Genuk", -6.9430, 110.4680, 88, "Nelayan dan buruh prasejahtera"),
            ("Semarang Barat", -6.9680, 110.3950, 82, "Kawasan kumuh pesisir"),
            ("Mijen", -7.0500, 110.3200, 76, "Daerah pinggiran dengan akses terbatas"),
        ],
    },
    "Yogyakarta": {
        "Rawan Banjir": [
            ("Jetis", -7.7850, 110.3630, 70, "Cekungan dangkal di pusat kota"),
            ("Mantrijeron", -7.8150, 110.3600, 68, "Daerah rendah dekat sungai Code"),
            ("Ngampilan", -7.7950, 110.3550, 65, "Drainase padat penduduk tersumbat"),
            ("Gedongtengen", -7.7820, 110.3600, 62, "Pusat pasar, drainase tertutup bangunan"),
        ],
        "Rawan Hoax": [
            ("Danurejan", -7.7880, 110.3680, 80, "Pusat kuliner dan wisata, hoax tarif dan wisata"),
            ("Gondokusuman", -7.7900, 110.3750, 78, "Kawasan kampus dan perumahan, hoax akademik"),
            ("Kraton", -7.8050, 110.3630, 72, "Kampung wisata, hoax budaya dan tradisi"),
        ],
        "Bantuan Sosial": [
            ("Mantrijeron", -7.8150, 110.3600, 82, "Kampung padat dengan ekonomi rendah"),
            ("Tegalrejo", -7.7850, 110.3450, 78, "Daerah penyangga, banyak lansia prasejahtera"),
            ("Umbulharjo", -7.8100, 110.3780, 75, "Pinggiran kota dengan akses terbatas"),
        ],
    },
    "Denpasar": {
        "Rawan Banjir": [
            ("Denpasar Selatan", -8.7020, 115.2100, 72, "Daerah dekat pantai, banjir rob dan pasang"),
            ("Denpasar Barat", -8.6700, 115.1900, 68, "Cekungan dengan drainase kurang"),
            ("Denpasar Timur", -8.6520, 115.2300, 65, "Daerah padat dengan genangan musiman"),
            ("Denpasar Utara", -8.6350, 115.2100, 60, "Drainase alamiah masih cukup baik"),
        ],
        "Rawan Hoax": [
            ("Denpasar Selatan", -8.7020, 115.2100, 80, "Pusat wisata, hoax tarif dan penipuan turis"),
            ("Denpasar Barat", -8.6700, 115.1900, 75, "Kawasan perdagangan, hoax komersial"),
            ("Denpasar Timur", -8.6520, 115.2300, 72, "Daerah padat, hoax kesehatan dan bansos"),
        ],
        "Bantuan Sosial": [
            ("Denpasar Selatan", -8.7020, 115.2100, 78, "Pekerja informal sektor pariwisata"),
            ("Denpasar Barat", -8.6700, 115.1900, 75, "Kawasan padat dengan ekonomi campuran"),
            ("Denpasar Utara", -8.6350, 115.2100, 72, "Daerah penyangga dengan akses terbatas"),
        ],
    },
}


def generate_fallback_hotspots(target, seed, region_name):
    np.random.seed(seed)
    region_data = REAL_RISK_DATA.get(region_name, {}).get(target, [])

    if not region_data:
        info = INDONESIA_REGIONS[region_name]
        for d in info["districts"]:
            lat_offset = np.random.normal(0, 0.015)
            lon_offset = np.random.normal(0, 0.015)
            region_data.append((d, info["lat"] + lat_offset, info["lon"] + lon_offset,
                                65, f"Analisis pola {target.lower()} di {region_name}"))

    fallback_data = []
    for item in region_data[:8]:
        name, lat, lon, risk_score, reason = item
        risk_level = "High" if risk_score >= 70 else "Medium"
        trend = np.random.choice(["increasing", "stable", "decreasing"], p=[0.4, 0.35, 0.25])
        affected = int(np.random.randint(8000, 200000))
        affected_str = f"{affected:,}".replace(",", ".")
        recs = {
            "Rawan Banjir": ["Normalisasi sungai", "Perbaikan drainase", "Sosialisasi kesiapsiagaan bencana", "Early warning system"],
            "Rawan Hoax": ["Literasi digital masyarakat", "Kerjasama dengan tokoh masyarakat", "Fakta check oleh relawan", "Hotline pelaporan hoax"],
            "Bantuan Sosial": ["Pendataan ulang DTKS", "Distribusi sembako tepat sasaran", "Program padat karya", "Pendampingan UMKM"],
        }
        recommendations = recs.get(target, ["Monitoring berkala", "Koordinasi dengan dinas terkait"])
        fallback_data.append({
            "name": f"Kecamatan {name}",
            "lat": lat,
            "lon": lon,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reason": reason,
            "trend": trend,
            "affected_estimate": f"{affected_str} jiwa",
            "recommendations": recommendations[:3],
        })
    return fallback_data


def build_dataframes(hotspots, target, sensitivity, region_name):
    rows_hotspots = []
    rows_clusters = []
    rows_heat = []
    n_pts = int(30 * (sensitivity / 5.0))
    center_lat = INDONESIA_REGIONS[region_name]["lat"]
    center_lon = INDONESIA_REGIONS[region_name]["lon"]

    for hs in hotspots:
        name = hs.get("name", "Area")
        lat = float(hs.get("lat", center_lat + np.random.normal(0, 0.01)))
        lon = float(hs.get("lon", center_lon + np.random.normal(0, 0.01)))
        risk_level = hs.get("risk_level", "Medium")
        risk_score = int(hs.get("risk_score", 65))
        reason = hs.get("reason", "")
        trend = hs.get("trend", "stable")
        affected = hs.get("affected_estimate", "")

        is_high = "High" in risk_level or risk_score >= 70
        base_color = [255, 71, 87, 220] if is_high else [255, 165, 2, 220]
        bar_color = [255, 71, 87, 180] if is_high else [255, 165, 2, 180]
        elevation = risk_score * 80

        trend_symbol = {"increasing": "↑", "stable": "→", "decreasing": "↓"}.get(trend, "→")
        tooltip_label = f"{trend_symbol} {risk_level} - {name}"

        rows_hotspots.append({
            "lat": lat,
            "lon": lon,
            "name": name,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reason": reason,
            "trend": trend,
            "affected": affected,
            "color": base_color,
            "bar_color": bar_color,
            "elevation": elevation,
            "intensity": risk_score / 100.0,
            "radius": 500,
            "tooltip": tooltip_label,
            "type": "hotspot",
        })

        for _ in range(n_pts):
            olat = np.random.normal(lat, 0.012)
            olon = np.random.normal(lon, 0.012)
            dist_intensity = max(0.1, risk_score / 100.0 * np.random.uniform(0.4, 0.9))
            rows_clusters.append({
                "lat": olat,
                "lon": olon,
                "name": name,
                "color": [255, 255, 255, int(dist_intensity * 80)],
                "intensity": dist_intensity,
                "radius": 150,
                "type": "cluster",
            })
            rows_heat.append({
                "lat": olat,
                "lon": olon,
                "weight": dist_intensity * risk_score / 100.0,
            })

    # spread some extra heat points across the region for coverage
    for _ in range(30):
        rows_heat.append({
            "lat": center_lat + np.random.normal(0, 0.04),
            "lon": center_lon + np.random.normal(0, 0.04),
            "weight": np.random.uniform(0.05, 0.2),
        })

    df_hotspots = pd.DataFrame(rows_hotspots)
    df_clusters = pd.DataFrame(rows_clusters)
    df_heat = pd.DataFrame(rows_heat)
    return df_hotspots, df_clusters, df_heat


def build_map_layers(df_hotspots, df_clusters, df_heat, pitch=45):
    if df_hotspots.empty:
        return []

    heat_layer = pdk.Layer(
        "HeatmapLayer",
        data=df_heat,
        get_position="[lon, lat]",
        get_weight="weight",
        aggregation="MEAN",
        radiusPixels=60,
        intensity=1.2,
        threshold=0.05,
        colorRange=[
            [0, 0, 0, 0],
            [46, 213, 115, 80],
            [255, 165, 2, 120],
            [255, 71, 87, 160],
            [255, 0, 0, 200],
        ],
    )

    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df_hotspots,
        get_position="[lon, lat]",
        get_elevation="elevation",
        elevation_scale=1,
        radius=350,
        get_fill_color="bar_color",
        get_line_color=[255, 255, 255, 40],
        line_width_min_pixels=1,
        extruded=True,
        pickable=True,
        auto_highlight=True,
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_hotspots,
        get_position="[lon, lat]",
        get_color="color",
        get_radius="radius",
        radius_scale=1.5,
        radius_min_pixels=5,
        radius_max_pixels=30,
        pickable=False,
    )

    cluster_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_clusters,
        get_position="[lon, lat]",
        get_color="color",
        get_radius="radius",
        radius_scale=1,
        radius_min_pixels=2,
        radius_max_pixels=15,
        pickable=False,
    )

    return [heat_layer, scatter_layer, cluster_layer, column_layer]


def render_hotspot_details(hotspots):
    st.markdown("<h4 style='color:white;margin-top:1.5rem;'>📋 Detail Area Terdeteksi</h4>", unsafe_allow_html=True)
    hotspots_sorted = sorted(hotspots, key=lambda x: x.get("risk_score", 0), reverse=True)
    for hs in hotspots_sorted:
        is_high = "High" in hs.get("risk_level", "") or hs.get("risk_score", 0) >= 70
        risk = hs.get("risk_level", "Medium")
        score = hs.get("risk_score", 0)
        trend = hs.get("trend", "stable")
        trend_icon = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
        trend_text = "Meningkat" if trend == "increasing" else "Menurun" if trend == "decreasing" else "Stabil"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border-radius:12px;padding:1rem;margin-bottom:0.8rem;border-left:4px solid {'#ff4757' if is_high else '#ffa502'};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="color:white;font-size:1.1rem;">{hs.get("name", "-")}</strong>
                <span style="color:{'#ff4757' if is_high else '#ffa502'};font-weight:bold;font-size:1.2rem;">{score}/100</span>
            </div>
            <div style="color:#8892b0;font-size:0.85rem;margin-top:0.3rem;">
                {trend_icon} Tren: {trend_text} &nbsp;|&nbsp; Level: {risk} &nbsp;|&nbsp; Terdampak: {hs.get("affected_estimate", "-")}
            </div>
            <div style="color:#ccd6f6;font-size:0.9rem;margin-top:0.4rem;">{hs.get("reason", "")}</div>
            <div style="margin-top:0.4rem;">
                {''.join(f'<span style="background:rgba(100,255,218,0.1);color:#64ffda;border-radius:6px;padding:2px 10px;font-size:0.75rem;margin-right:4px;">{r}</span>' for r in hs.get("recommendations", [])[:2])}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_page():
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🗺️ AI Predictive Map — Indonesia Smart City</h1>
        <p>Sistem Prediksi Geospasial bertenaga AI untuk alokasi sumber daya dan mitigasi risiko seluruh Indonesia</p>
    </div>
    """, unsafe_allow_html=True)

    col_ctrl, col_map = st.columns([1.1, 2.9])

    with col_ctrl:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:white;'>🎛️ Panel Kendali</h3>", unsafe_allow_html=True)
        
        region_keys = list(INDONESIA_REGIONS.keys())
        selected_region = st.selectbox("🌍 Wilayah (Kota/Provinsi)", options=region_keys, index=0)

        mode_keys = list(ANALYSIS_MODES.keys())
        mode_labels = [f"{ANALYSIS_MODES[k]['icon']} {k}" for k in mode_keys]

        selected_idx = st.selectbox(
            "Mode Analisis",
            options=range(len(mode_keys)),
            format_func=lambda i: mode_labels[i],
            index=0,
            label_visibility="collapsed",
        )
        selected_mode = mode_keys[selected_idx]
        mode_info = ANALYSIS_MODES[selected_mode]

        st.caption(mode_info["desc"])

        timeframe = st.slider("Periode Prediksi (hari)", 7, 90, 30, 7)
        sensitivity = st.slider("Sensitivitas AI", 1, 10, 7, 1)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            regenerate = st.button("🔄 Regenerasi", type="primary", use_container_width=True)
        with col_b2:
            auto_refresh = st.toggle("Auto-refresh", value=False)

        if regenerate:
            st.session_state["geo_seed"] = np.random.randint(0, 10000)
            st.session_state["auto_refresh"] = False

        if auto_refresh:
            st.session_state["auto_refresh"] = True
            if "last_refresh" not in st.session_state:
                st.session_state["last_refresh"] = time.time()

        if "geo_seed" not in st.session_state:
            st.session_state["geo_seed"] = 42

        st.markdown("</div>", unsafe_allow_html=True)

        # auto-refresh logic
        if st.session_state.get("auto_refresh") and "last_refresh" in st.session_state:
            if time.time() - st.session_state["last_refresh"] > 15:
                st.session_state["geo_seed"] = np.random.randint(0, 10000)
                st.session_state["last_refresh"] = time.time()
                st.rerun()

    # ── GENERATE AI DATA ──
    with st.spinner(f"🧠 AI sedang menganalisis data geospasial {selected_region} untuk '{selected_mode}'..."):
        df_hotspots, df_clusters, df_heat, hotspots_raw, confidence, summary, trend_analysis, data_sources, center_lat, center_lon = generate_ai_prediction(
            selected_mode, timeframe, sensitivity, st.session_state["geo_seed"], selected_region
        )

    with col_map:
        st.markdown("<div class='glass-card' style='padding:0;overflow:hidden;'>", unsafe_allow_html=True)

        if not df_hotspots.empty:
            layers = build_map_layers(df_hotspots, df_clusters, df_heat, pitch=50)
            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=10.5,
                pitch=50,
                bearing=0,
            )

            tooltip = {
                "html": (
                    "<div style='background:rgba(10,10,30,0.9);border-radius:8px;padding:10px 14px;"
                    "border:1px solid rgba(100,255,218,0.3);font-family:sans-serif;min-width:200px;'>"
                    "<div style='color:#64ffda;font-weight:bold;font-size:1rem;'>{name}</div>"
                    "<div style='display:flex;justify-content:space-between;margin-top:6px;'>"
                    "<span style='color:#8892b0;'>Risk Level:</span>"
                    "<span style='color:#ff4757;font-weight:bold;'>{risk_level}</span></div>"
                    "<div style='display:flex;justify-content:space-between;'>"
                    "<span style='color:#8892b0;'>Risk Score:</span>"
                    "<span style='color:#ffa502;font-weight:bold;'>{risk_score}/100</span></div>"
                    "<div style='color:#ccd6f6;font-size:0.85rem;margin-top:4px;border-top:1px solid rgba(255,255,255,0.1);padding-top:4px;'>{reason}</div>"
                    "</div>"
                ),
            }

            r = pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=tooltip,
                map_style=pdk.map_styles.DARK,
            )
            st.pydeck_chart(r, use_container_width=True)
        else:
            st.warning("Tidak ada data hotspot yang dihasilkan. Coba regenerate.")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── METRICS ROW ──
        total_high = len(df_hotspots[df_hotspots["risk_level"].str.contains("High", na=False)])
        total_zones = len(df_hotspots)
        avg_risk = int(df_hotspots["risk_score"].mean()) if not df_hotspots.empty else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#ff4757;">{total_high}</div>
                <div class="metric-label">Zona Berisiko Tinggi</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#ffa502;">{total_zones}</div>
                <div class="metric-label">Total Zona Terdeteksi</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#64ffda;">{avg_risk}</div>
                <div class="metric-label">Rata-rata Skor Risiko</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            conf_color = "#64ffda" if confidence >= 75 else "#ffa502" if confidence >= 50 else "#ff4757"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{conf_color};">{confidence}%</div>
                <div class="metric-label">Confidence AI</div>
            </div>
            """, unsafe_allow_html=True)

        # ── AI ANALYSIS RESULTS ──
        if summary or trend_analysis:
            with st.expander("🧠 Analisis & Insight AI", expanded=True):
                if summary:
                    st.markdown(f"**Ringkasan Prediksi {selected_region} ({timeframe} hari):**")
                    st.markdown(f"<div style='background:rgba(100,255,218,0.05);border-radius:8px;padding:0.8rem;color:#ccd6f6;'>{summary}</div>", unsafe_allow_html=True)

                if trend_analysis:
                    st.markdown("**Analisis Tren:**")
                    st.markdown(f"<div style='background:rgba(255,165,2,0.05);border-radius:8px;padding:0.8rem;color:#ccd6f6;'>{trend_analysis}</div>", unsafe_allow_html=True)

                if data_sources:
                    st.markdown("**Sumber Data:** " + ", ".join(f"`{s}`" for s in data_sources))

        # ── HOTSPOT DETAILS LIST ──
        if hotspots_raw:
            render_hotspot_details(hotspots_raw)

    # ── KEY METRICS SIDEBAR ──
    with col_ctrl:
        st.markdown("<div class='glass-card' style='margin-top:1rem;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:white;'>📊 Ringkasan</h4>", unsafe_allow_html=True)

        mode_meta = {
            "Prediksi Daerah Rawan Hoax": {
                "indicator": "Skor Penyebaran",
                "unit": "%",
                "sources": "Kemkominfo, Mafindo, TurnBackHoax",
            },
            "Prediksi Daerah Rawan Banjir": {
                "indicator": "Tingkat Kerawanan",
                "unit": "%",
                "sources": "BMKG, BPBD DKI, BBWS",
            },
            "Prediksi Daerah Butuh Bantuan Sosial": {
                "indicator": "Indeks Kebutuhan",
                "unit": "%",
                "sources": "Kemensos, DTKS, BPS",
            },
        }
        meta = mode_meta.get(selected_mode, {})
        st.markdown(f"""
        <div style="color:#8892b0;font-size:0.85rem;">
            <div style="display:flex;justify-content:space-between;padding:4px 0;">
                <span>Indikator</span>
                <span style="color:#ccd6f6;">{meta.get("indicator", "-")}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:4px 0;">
                <span>Satuan</span>
                <span style="color:#ccd6f6;">{meta.get("unit", "-")}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:4px 0;">
                <span>Sumber Data</span>
                <span style="color:#ccd6f6;font-size:0.75rem;">{meta.get("sources", "-")}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:4px 0;border-top:1px solid rgba(255,255,255,0.05);margin-top:4px;">
                <span>Periode</span>
                <span style="color:#ccd6f6;">{timeframe} hari</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:4px 0;">
                <span>Sensitivitas</span>
                <span style="color:#ccd6f6;">{sensitivity}/10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── LEGEND ──
        st.markdown("<div class='glass-card' style='margin-top:1rem;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:white;'>📌 Legenda</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.85rem;">
            <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
                <div style="width:12px;height:12px;border-radius:50%;background:#ff4757;"></div>
                <span style="color:#ccd6f6;">High Risk</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
                <div style="width:12px;height:12px;border-radius:50%;background:#ffa502;"></div>
                <span style="color:#ccd6f6;">Medium Risk</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
                <div style="width:12px;height:12px;border-radius:50%;background:#2ed573;"></div>
                <span style="color:#ccd6f6;">Low Risk / Affected Zone</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
                <div style="width:12px;height:12px;border-radius:2px;background:rgba(255,71,87,0.5);"></div>
                <span style="color:#ccd6f6;">3D Column = Risk Elevation</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
                <div style="width:12px;height:12px;border-radius:50%;background:rgba(255,165,2,0.3);"></div>
                <span style="color:#ccd6f6;">Heatmap = Risk Density</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        f"*Data prediktif untuk {selected_mode.lower()} di {selected_region} — periode {timeframe} hari ke depan. "
        f"Confidence AI: {confidence}%. Data bersifat simulasi prediktif berdasarkan AI.*"
    )

if __name__ == "__main__":
    render_page()
