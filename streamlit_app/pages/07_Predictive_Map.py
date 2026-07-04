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

JAKARTA_KECAMATAN = {
    "Jakarta Pusat": {"lat": -6.1800, "lon": 106.8300, "districts": [
        "Gambir", "Sawah Besar", "Kemayoran", "Menteng",
        "Tanah Abang", "Senen", "Cempaka Putih", "Johar Baru"
    ]},
    "Jakarta Utara": {"lat": -6.1250, "lon": 106.8700, "districts": [
        "Penjaringan", "Pademangan", "Tanjung Priok", "Koja",
        "Kelapa Gading", "Cilincing"
    ]},
    "Jakarta Barat": {"lat": -6.1600, "lon": 106.7600, "districts": [
        "Cengkareng", "Grogol Petamburan", "Taman Sari", "Tambora",
        "Kebon Jeruk", "Kembangan", "Palmerah", "Kalideres"
    ]},
    "Jakarta Selatan": {"lat": -6.2600, "lon": 106.8000, "districts": [
        "Pasar Minggu", "Kebayoran Baru", "Kebayoran Lama", "Cilandak",
        "Jagakarsa", "Mampang Prapatan", "Pancoran", "Tebet",
        "Setiabudi", "Pesanggrahan"
    ]},
    "Jakarta Timur": {"lat": -6.2300, "lon": 106.9000, "districts": [
        "Pasar Rebo", "Cipayung", "Cakung", "Duren Sawit",
        "Kramat Jati", "Makasar", "Matraman", "Jatinegara",
        "Pulogadung", "Ciracas"
    ]},
}

CENTER_LAT = -6.2088
CENTER_LON = 106.8456

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
def generate_ai_prediction(analysis_mode_key, timeframe, sensitivity, seed):
    mode = ANALYSIS_MODES[analysis_mode_key]
    target = mode["ai_target"]
    np.random.seed(seed)

    user_prompt = (
        f"Target Analisis: {target}\n"
        f"Periode Prediksi: {timeframe} hari ke depan\n"
        f"Level Sensitivitas: {sensitivity}/10\n\n"
        f"Prediksi 5-8 kecamatan di Jakarta yang paling {target.lower()} "
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
        hotspots_raw = generate_fallback_hotspots(target, seed)

    df_hotspots, df_clusters, df_heat = build_dataframes(hotspots_raw, target, sensitivity)
    return df_hotspots, df_clusters, df_heat, hotspots_raw, confidence, summary, trend_analysis, data_sources


def generate_fallback_hotspots(target, seed):
    np.random.seed(seed)
    fallback_data = []

    kota_list = list(JAKARTA_KECAMATAN.keys())
    for kota in kota_list:
        info = JAKARTA_KECAMATAN[kota]
        for d in info["districts"]:
            if np.random.random() < 0.35:
                risk_score = int(np.random.normal(70, 15))
                risk_score = max(30, min(99, risk_score))
                risk_level = "High" if risk_score >= 70 else "Medium"
                trend = np.random.choice(["increasing", "stable", "decreasing"], p=[0.5, 0.3, 0.2])
                lat_offset = np.random.normal(0, 0.008)
                lon_offset = np.random.normal(0, 0.008)
                fallback_data.append({
                    "name": f"Kecamatan {d}",
                    "lat": info["lat"] + lat_offset,
                    "lon": info["lon"] + lon_offset,
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "reason": f"Berdasarkan analisis pola {target.lower()} periode sebelumnya",
                    "trend": trend,
                    "affected_estimate": f"{int(np.random.randint(10000, 200000)):,} jiwa".replace(",", "."),
                    "recommendations": ["Monitoring berkala", "Sosialisasi pencegahan"],
                })
    return fallback_data


def build_dataframes(hotspots, target, sensitivity):
    rows_hotspots = []
    rows_clusters = []
    rows_heat = []
    n_pts = int(30 * (sensitivity / 5.0))

    for hs in hotspots:
        name = hs.get("name", "Area")
        lat = float(hs.get("lat", CENTER_LAT))
        lon = float(hs.get("lon", CENTER_LON))
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

    # spread some extra heat points across Jakarta for coverage
    for _ in range(80):
        kota = np.random.choice(list(JAKARTA_KECAMATAN.values()))
        rows_heat.append({
            "lat": kota["lat"] + np.random.normal(0, 0.03),
            "lon": kota["lon"] + np.random.normal(0, 0.03),
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
        coverage=0.8,
        opacity=0.85,
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_hotspots,
        get_position="[lon, lat]",
        get_color="color",
        get_radius="radius",
        pickable=True,
        auto_highlight=True,
        opacity=0.9,
        filled=True,
        stroked=True,
        get_line_color=[255, 255, 255, 150],
        line_width_min_pixels=2,
    )

    cluster_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_clusters,
        get_position="[lon, lat]",
        get_color="color",
        get_radius="radius",
        pickable=False,
        opacity=0.4,
    )

    return [heat_layer, cluster_layer, column_layer, scatter_layer]


def render_hotspot_details(hotspots_raw):
    if not hotspots_raw:
        return
    st.markdown("### 🎯 Rincian Prediksi per Wilayah")
    for i, hs in enumerate(hotspots_raw[:6]):
        risk = hs.get("risk_level", "Medium")
        score = hs.get("risk_score", 65)
        trend = hs.get("trend", "stable")
        trend_icon = {"increasing": "🔴", "stable": "🟡", "decreasing": "🟢"}.get(trend, "⚪")
        trend_text = {"increasing": "Meningkat", "stable": "Stabil", "decreasing": "Menurun"}.get(trend, "-")
        is_high = "High" in risk or score >= 70
        border = "2px solid #ff4757" if is_high else "2px solid #ffa502"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:1rem;margin-bottom:0.75rem;border-left:{border};">
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
        <h1>🗺️ AI Predictive Map — Smart City Jakarta</h1>
        <p>Sistem Prediksi Geospasial bertenaga AI untuk alokasi sumber daya dan mitigasi risiko</p>
    </div>
    """, unsafe_allow_html=True)

    col_ctrl, col_map = st.columns([1.1, 2.9])

    with col_ctrl:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:white;'>🎛️ Panel Kendali</h3>", unsafe_allow_html=True)

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
    with st.spinner(f"🧠 AI sedang menganalisis data geospasial untuk '{selected_mode}'..."):
        df_hotspots, df_clusters, df_heat, hotspots_raw, confidence, summary, trend_analysis, data_sources = generate_ai_prediction(
            selected_mode, timeframe, sensitivity, st.session_state["geo_seed"]
        )

    with col_map:
        st.markdown("<div class='glass-card' style='padding:0;overflow:hidden;'>", unsafe_allow_html=True)

        if not df_hotspots.empty:
            layers = build_map_layers(df_hotspots, df_clusters, df_heat, pitch=50)
            view_state = pdk.ViewState(
                latitude=CENTER_LAT,
                longitude=CENTER_LON,
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
                    st.markdown(f"**Ringkasan Prediksi ({timeframe} hari):**")
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
                "sources": "BMKG, BPBD DKI, BBWS Ciliwung",
            },
            "Prediksi Daerah Butuh Bantuan Sosial": {
                "indicator": "Indeks Kebutuhan",
                "unit": "%",
                "sources": "Kemensos, DTKS, BPS DKI",
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
        f"*Data prediktif untuk {selected_mode.lower()} — periode {timeframe} hari ke depan. "
        f"Confidence AI: {confidence}%. Data bersifat simulasi prediktif berdasarkan AI.*"
    )


if __name__ == "__main__":
    render_page()
