import time
import math
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="MG BRAND OFFICE | Enterprise Intelligence Suite",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb")

# ---------------------------------------------------------
# 2. CSS STİLLERİ
# ---------------------------------------------------------
st.markdown(
    """
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #000000 !important; color: #ffffff !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        padding-bottom: 60px !important; 
    }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #ffffff !important; }
    @keyframes colorChange { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .reflection-container { text-align: center; padding-top: 15px; padding-bottom: 0px; }
    .brand-header-animated {
        font-size: 3.8rem; font-weight: 900; letter-spacing: -1.5px;
        background: linear-gradient(270deg, #2563eb, #a855f7, #ec4899, #3b82f6, #06b6d4);
        background-size: 400% 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: colorChange 6s ease infinite; margin: 0; display: inline-block;
        -webkit-box-reflect: below -18px linear-gradient(transparent 50%, rgba(255, 255, 255, 0.2));
    }
    [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; border-bottom: 1px solid #161b22 !important; margin: 0 auto 30px auto !important; gap: 16px !important; width: 100% !important; }
    [data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-radius: 0 !important; box-shadow: none !important; outline: none !important; padding: 10px 15px !important; margin: 0 !important; }
    [data-baseweb="tab"] p, [data-baseweb="tab"] span { color: #8b949e !important; font-weight: 800 !important; font-size: 1.05rem !important; }
    [data-baseweb="tab"][aria-selected="true"] { border-bottom: 2px solid #ef4444 !important; }
    [data-baseweb="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"] span { color: #ffffff !important; font-weight: 900 !important; }
    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 450px !important; width: 100% !important; margin: 0 auto 5px auto !important; }
    .stTextInput input, .stNumberInput input { color: #ffffff !important; background-color: #0d1117 !important; border: 2px solid #21262d !important; border-radius: 12px !important; font-weight: 700 !important; padding: 12px 14px !important; font-size: 0.95rem !important; text-align: center !important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: #a855f7 !important; box-shadow: 0 0 15px rgba(168, 85, 247, 0.4) !important; }
    .stTextInput label, .stNumberInput label { color: #ffffff !important; font-weight: 800 !important; font-size: 1rem !important; display: block !important; text-align: center !important; margin-bottom: 8px !important; }
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 250px !important; margin: 5px auto 0 auto !important; width: 100% !important; }
    .stButton>button { width: 100% !important; background: linear-gradient(270deg, #2563eb, #a855f7, #ec4899, #3b82f6); background-size: 300% 300% !important; animation: colorChange 5s ease infinite !important; color: #ffffff !important; border: none !important; padding: 10px 20px !important; border-radius: 20px !important; font-weight: 900 !important; font-size: 0.95rem !important; box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4) !important; transition: all 0.3s ease !important; }
    .stButton>button:hover { transform: scale(1.04); box-shadow: 0 6px 30px rgba(168, 85, 247, 0.6) !important; }
    [data-testid="stDownloadButton"] > button { background: #0d1117 !important; border: 1px solid #21262d !important; box-shadow: none !important; animation: none !important; color: #818cf8 !important; border-radius: 12px !important; }
    [data-testid="stDownloadButton"] > button:hover { border-color: #818cf8 !important; background: #161b22 !important; }
    [data-testid="stMetric"] { background-color: #0d1117 !important; border: 1px solid #21262d !important; border-radius: 16px !important; padding: 18px !important; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 900 !important; }
    .report-box { background-color: #0d1117 !important; border: 1px solid #21262d !important; border-left: 6px solid #a855f7 !important; border-radius: 16px; padding: 24px; margin-top: 24px; }
    .anomaly-box { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 16px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
    .footer-dark { position: fixed !important; bottom: 0 !important; left: 0 !important; width: 100% !important; text-align: center; color: #484f58 !important; background-color: #000000 !important; font-size: 0.85rem; padding: 15px 0 !important; border-top: 1px solid #161b22; z-index: 9999 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR
# ---------------------------------------------------------
def clean_username(input_text: str) -> str:
    if not input_text: return ""
    input_text = input_text.strip()
    match = re.search(r'instagram\.com/([^/?#]+)', input_text)
    if match: return match.group(1)
    return input_text.replace("@", "").strip()

def clean_number(value, default=0.0) -> float:
    if value is None: return default
    try: val = float(value)
    except (ValueError, TypeError): return default
    return default if math.isnan(val) else val

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_apify_instagram_data(username: str, max_posts: int = 24):
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    payload = {"usernames": [username], "resultsLimit": int(max_posts)}
    try:
        response = requests.post(run_url, json=payload, timeout=25)
        if response.status_code not in [200, 201]: return None
        run_data = response.json().get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id: return None
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
        for _ in range(25):
            time.sleep(2)
            res = requests.get(dataset_url, timeout=15)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0: return items[0]
        return None
    except Exception: return None

# ---------------------------------------------------------
# 4. ACIMASIZ (PANDORA-STYLE) ANTI-FRAUD ALGORİTMASI
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list, budget: float = 0.0):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    
    avg_likes = float(np.mean(likes)) if likes else 0.0
    avg_comments = float(np.mean(comments)) if comments else 0.0
    total_eng = avg_likes + avg_comments

    er = (total_eng / max(followers, 1)) * 100.0
    
    if followers < 5000: benchmark_er = 5.0
    elif followers < 20000: benchmark_er = 4.0
    elif followers < 100000: benchmark_er = 2.8
    elif followers < 500000: benchmark_er = 2.0
    elif followers < 1000000: benchmark_er = 1.5
    else: benchmark_er = 1.0

    er_score = min(40.0, (er / benchmark_er) * 40.0)
    comment_ratio = avg_comments / max(avg_likes, 1.0)
    comment_score = 40.0 if comment_ratio >= 0.015 else (comment_ratio / 0.015) * 40.0
    
    if len(posts) > 1:
        eng_array = [(l+c)/max(followers, 1)*100 for l, c in zip(likes, comments)]
        std_er = float(np.std(eng_array))
        cv = (std_er / er) if er > 0 else 1.0 
    else:
        std_er, cv = 0.0, 1.0
        
    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
    aqs_score = int(np.clip(er_score + comment_score + stability_score, 10, 99))

    # --- PANDORA STRICT MODE: DİNAMİK BOT VE HAYALET HESAPLAMA ---
    er_defect = max(0.0, (benchmark_er - er) / benchmark_er)
    
    # Eskiden 0.002'ydi. Artık %0.8 altı Yorum/Beğeni direkt ağır ceza!
    if comment_ratio < 0.008: comment_anomaly = 0.50 # Aşırı sessizlik (Bot panel beğenisi)
    elif comment_ratio < 0.012: comment_anomaly = 0.25 # Şüpheli dengesizlik
    elif comment_ratio > 0.15: comment_anomaly = 0.30 # Yorum botu / Çekiliş basması
    else: comment_anomaly = 0.00 # Temiz

    # Eskiden 0.10'du. Artık 0.28 altı zeki bot panellerini yakalar!
    if cv < 0.28 and len(posts) > 4: variance_anomaly = 0.40 # Akıllı Paket Bot
    elif cv > 1.2: variance_anomaly = 0.30 # Sıçramalı Sponsorluk Botu
    else: variance_anomaly = 0.00 # Doğal dalgalanma

    # Acımasız Bot Hesaplama Formülü
    calculated_bot = 10.0 + (er_defect * 50.0) + (comment_anomaly * 100.0) + (variance_anomaly * 100.0)
    bot_pct = float(np.clip(calculated_bot, 3.2, 98.5))
    authentic_pct = float(np.clip(100.0 - bot_pct, 1.5, 96.8))
    
    # AQS'i bot oranına göre çökert
    if bot_pct > 30.0: aqs_score = int(aqs_score * 0.4)
    elif bot_pct > 15.0: aqs_score = int(aqs_score * 0.7)
    credibility_score = int(np.clip(authentic_pct * 0.90 + (er_score * 0.1), 5, 98))

    sentiment_data = pd.DataFrame({"Duygu": ["Pozitif", "Nötr", "Negatif"], "Oran (%)": [65.0, 25.0, 10.0]})
    collab_keywords = ["#reklam", "#işbirliği", "#isbirligi", "#sponsorlu", "işbirliği", "partnership"]
    sector_keywords = {
        "Moda & Giyim": ["kombin", "elbise", "tarz", "kıyafet", "moda", "giyim"],
        "Kozmetik & Güzellik": ["makyaj", "cilt", "krem", "ruj", "saç", "güzellik"],
        "Teknoloji & Dijital": ["telefon", "bilgisayar", "teknoloji", "app", "uygulama"],
        "Gıda & Seyahat": ["yemek", "tarif", "lezzet", "otel", "tatil", "restoran"]
    }
    collab_count = 0
    detected_sectors = {}
    for p in posts:
        caption = str(p.get("caption", "")).lower()
        if any(kw in caption for kw in collab_keywords): collab_count += 1
        for sector, kws in sector_keywords.items():
            if any(kw in caption for kw in kws): detected_sectors[sector] = detected_sectors.get(sector, 0) + 1
                
    collab_ratio = (collab_count / max(len(posts), 1)) * 100.0
    top_sectors = [s[0] for s in sorted(detected_sectors.items(), key=lambda item: item[1], reverse=True)[:2]]
    if not top_sectors: top_sectors = ["Genel Lifestyle / Belirsiz"]

    format_stats = {"Reels/Video": [], "Carousel": [], "Tekil Fotoğraf": []}
    for p in posts:
        l = clean_number(p.get("likesCount"), 0)
        c = clean_number(p.get("commentsCount"), 0)
        if p.get("isVideo") or p.get("type") == "Video": format_stats["Reels/Video"].append(l+c)
        elif p.get("type") == "Sidecar": format_stats["Carousel"].append(l+c)
        else: format_stats["Tekil Fotoğraf"].append(l+c)
            
    format_data = [{"Format": k, "Ortalama Etkileşim": np.mean(v)} for k, v in format_stats.items() if v]
    if not format_data: format_data = [{"Format": "Veri Yok", "Ortalama Etkileşim": 0}]

    visibility_multiplier = 3.5 if er > 2.0 else 2.5
    est_reach = min(int(followers * (er / 100.0) * visibility_multiplier), followers)
    if est_reach < followers * 0.05: est_reach = int(followers * 0.05)

    cpe = budget / total_eng if total_eng > 0 else 0.0
    cpm = (budget / est_reach) * 1000.0 if est_reach > 0 else 0.0

    return {
        "er": er, "avg_likes": avg_likes, "avg_comments": avg_comments, "total_eng": total_eng,
        "aqs_score": aqs_score, "er_score": er_score, "comment_score": comment_score, "stability_score": stability_score,
        "cv_value": cv, "comment_ratio": comment_ratio, "er_defect": er_defect,
        "credibility_score": credibility_score, "authentic_pct": authentic_pct, "est_reach": est_reach,
        "bot_pct": bot_pct, "collab_ratio": collab_ratio, "top_sectors": top_sectors,
        "cpe": cpe, "cpm": cpm, "benchmark_er": benchmark_er, "format_data": format_data, "sentiment_data": sentiment_data
    }

# ---------------------------------------------------------
# 5. ARAYÜZ YAPISI
# ---------------------------------------------------------
st.markdown("""
    <div class="reflection-container">
        <h1 class="brand-header-animated">MG BRAND OFFICE</h1>
    </div>
    <div style="height: 70px;"></div>
""", unsafe_allow_html=True)

tab_hero, tab_wask, tab_compare, tab_report = st.tabs([
    "• Influencer Hero & Audit", 
    "• WASK Performans & Benchmark", 
    "• Çapraz Kıyaslama Paneli",
    "• Kurumsal Denetim Raporu"
])

# =========================================================
# SEKME 1: INFLUENCER HERO & AUDIT
# =========================================================
with tab_hero:
    _, col_center, _ = st.columns([1.5, 3, 1.5])
    with col_center:
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        raw_hero = st.text_input("Instagram Kullanıcı Adı veya Profil Linki", placeholder="Örn: mg brand office", key="hero_user_input")
        budget_hero = st.number_input("Tahmini Kampanya Bütçesi (₺) - İsteğe Bağlı", min_value=0, step=1000, key="hero_budget")
        btn_hero = st.button("Derin Analiz Başlat", use_container_width=True, key="btn_hero")

    if btn_hero and raw_hero:
        hero_user = clean_username(raw_hero)
        with st.spinner(f"• @{hero_user} profili acımasız filtrelerden geçiriliyor..."):
            prof = fetch_apify_instagram_data(hero_user, max_posts=24)
            if prof and "latestPosts" in prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                m = run_all_algorithms(fol, prof.get("latestPosts", []), budget=budget_hero)

                st.markdown(f"""
                <div style="background: #0d1117; border-radius: 16px; padding: 24px; margin-bottom: 24px; border: 1px solid #21262d;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <div>
                            <span style="background: #1e1b4b; color: #818cf8; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">INFLUENCER HERO AUDIT</span>
                            <h2 style="margin: 12px 0 0 0; color: #ffffff; font-size: 2.2rem; font-weight: 900;">@{hero_user}</h2>
                            <p style="color: #8b949e; margin: 4px 0 0 0; font-weight: 700;">Toplam Takipçi: {fol:,}</p>
                        </div>
                        <div style="text-align: right;">
                            <h1 style="font-size: 3.5rem; margin: 0; color: #a855f7; font-weight: 900;">{m['aqs_score']}</h1>
                            <p style="color: #ffffff; font-size: 0.95rem; margin: 0; font-weight: 800;">AQS (Kalite Skoru)</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Ortalama Beğeni", f"{int(m['avg_likes']):,}")
                m2.metric("Etkileşim (ER)", f"%{m['er']:.2f}")
                m3.metric("Gerçek Kitle Oranı", f"%{m['authentic_pct']:.1f}")
                m4.metric("Şüpheli/Bot Oranı", f"%{m['bot_pct']:.1f}")

                st.markdown("<br>", unsafe_allow_html=True)
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    cred_df = pd.DataFrame({"Segment": ["Gerçek / Aktif", "Şüpheli / Bot"], "Oran (%)": [m['authentic_pct'], m['bot_pct']]})
                    fig_pie = px.pie(cred_df, names="Segment", values="Oran (%)", color="Segment", color_discrete_map={"Gerçek / Aktif": "#2563eb", "Şüpheli / Bot": "#ef4444"}, hole=0.5, title="Kitle Kalite Dağılımı")
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
                    st.plotly_chart(fig_pie, use_container_width=True)

                with row1_col2:
                    fmt_df = pd.DataFrame(m['format_data'])
                    fig_fmt = px.bar(fmt_df, x="Format", y="Ortalama Etkileşim", color_discrete_sequence=["#3b82f6"], title="Format Performansı")
                    fig_fmt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
                    st.plotly_chart(fig_fmt, use_container_width=True)
            else:
                st.error("• Profil verisi çekilemedi. Kullanıcı adını kontrol edin.")

# =========================================================
# SEKME 2: WASK PERFORMANS & BENCHMARK
# =========================================================
with tab_wask:
    _, col_center_wask, _ = st.columns([1.5, 3, 1.5])
    with col_center_wask:
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        wask_raw = st.text_input("Kullanıcı Adı veya Profil Linki", placeholder="Örn: mg brand office", key="wask_inp")
        btn_wask = st.button("WASK Analizi", use_container_width=True, key="btn_wask")

    if btn_wask and wask_raw:
        w_user = clean_username(wask_raw)
        with st.spinner(f"• @{w_user} WASK standartlarında ölçülüyor..."):
            p = fetch_apify_instagram_data(w_user, max_posts=24)
            if p and "latestPosts" in p:
                f = int(clean_number(p.get("followersCount", p.get("followers", 0)), 1))
                m_wask = run_all_algorithms(f, p.get("latestPosts", []))
                
                benchmark_er = m_wask['benchmark_er']
                wask_chart_df = pd.DataFrame({
                    "Kategori": ["Düşük Performans", "Sektör Standardı", f"@{w_user} Performansı", "Yüksek Performans"],
                    "Etkileşim Oranı (%)": [benchmark_er * 0.5, benchmark_er, m_wask['er'], benchmark_er * 1.5]
                })
                fig_wask = px.bar(wask_chart_df, x="Kategori", y="Etkileşim Oranı (%)", color="Kategori", text="Etkileşim Oranı (%)")
                fig_wask.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig_wask.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
                st.plotly_chart(fig_wask, use_container_width=True)
            else:
                st.error("• Profil verisi çekilemedi.")

# =========================================================
# SEKME 3: ÇAPRAZ KIYASLAMA
# =========================================================
with tab_compare:
    _, col_center_cmp, _ = st.columns([1.5, 3, 1.5])
    with col_center_cmp:
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        c_u1 = st.text_input("1. Profil Kullanıcı Adı", placeholder="Örn: mg brand office", key="cmp1")
        c_u2 = st.text_input("2. Profil Kullanıcı Adı", placeholder="Örn: trendyol", key="cmp2")
        btn_cmp = st.button("Profilleri Kıyasla", use_container_width=True, key="btn_cmp")

    if btn_cmp and c_u1 and c_u2:
        u1, u2 = clean_username(c_u1), clean_username(c_u2)
        with st.spinner("• İki profil acımasızca kıyaslanıyor..."):
            p1, p2 = fetch_apify_instagram_data(u1, 24), fetch_apify_instagram_data(u2, 24)
            if p1 and p2:
                f1 = int(clean_number(p1.get("followersCount", p1.get("followers", 0)), 1))
                f2 = int(clean_number(p2.get("followersCount", p2.get("followers", 0)), 1))
                m1 = run_all_algorithms(f1, p1.get("latestPosts", []))
                m2 = run_all_algorithms(f2, p2.get("latestPosts", []))

                cmp_table = pd.DataFrame({
                    "Metrik / İnceleme": ["Takipçi Sayısı", "AQS Skoru", "Bot Oranı (%)", "Etkileşim Oranı (%)"],
                    f"@{u1}": [f"{f1:,}", m1['aqs_score'], f"%{m1['bot_pct']:.1f}", f"%{m1['er']:.2f}"],
                    f"@{u2}": [f"{f2:,}", m2['aqs_score'], f"%{m2['bot_pct']:.1f}", f"%{m2['er']:.2f}"]
                })
                st.table(cmp_table)
            else:
                st.error("• Profiller bulunamadı.")

# =========================================================
# SEKME 4: KURUMSAL DENETİM RAPORU (ACIMASIZ ANTI-FRAUD)
# =========================================================
with tab_report:
    _, col_center_rep, _ = st.columns([1.5, 3, 1.5])
    with col_center_rep:
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        rep_raw = st.text_input("Kurumsal Denetim İçin Profil Linki", placeholder="Örn: mg brand office", key="rep_inp")
        btn_rep = st.button("Denetim Raporunu Çıkart", use_container_width=True, key="btn_rep")

    st.markdown("<br>", unsafe_allow_html=True)

    if btn_rep and rep_raw:
        r_user = clean_username(rep_raw)
        with st.spinner(f"• @{r_user} Pandora seviyesi filtrelerden geçiriliyor..."):
            p_rep = fetch_apify_instagram_data(r_user, max_posts=24)
            if p_rep and "latestPosts" in p_rep:
                f_rep = int(clean_number(p_rep.get("followersCount", p_rep.get("followers", 0)), 1))
                m_r = run_all_algorithms(f_rep, p_rep.get("latestPosts", []))

                st.markdown(f"<h3 style='text-align:center; color:#ffffff; font-weight:900;'>@{r_user} • Algoritmik Risk & İstihbarat Raporu</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#8b949e; margin-bottom:40px;'>MG BRAND OFFICE Enterprise V4 (Strict Mode), profilin olası zeki bot panelleri kullanıp kullanmadığını acımasızca denetler.</p>", unsafe_allow_html=True)

                # YENİ ACIMASIZ RİSK LİMİTLERİ (Pandora Mode)
                if m_r['bot_pct'] > 20 or m_r['cv_value'] < 0.28:
                    risk_status, risk_color = "YÜKSEK RİSK (RED FLAG)", "#ef4444"
                elif m_r['bot_pct'] > 10 or m_r['cv_value'] < 0.35:
                    risk_status, risk_color = "ORTA RİSK (Şüpheli)", "#f59e0b"
                else:
                    risk_status, risk_color = "DÜŞÜK RİSK (Güvenilir)", "#10b981"

                c_g1, c_g2, c_g3 = st.columns(3)
                c_g1.metric("AQS (Kalite Endeksi)", f"{m_r['aqs_score']} / 100")
                c_g2.markdown(f"<div style='text-align:center; padding:18px; border-radius:16px; background:#0d1117; border:1px solid #21262d;'><p style='color:#8b949e; margin:0; font-weight:800; font-size:14px;'>Algoritmik Risk Seviyesi</p><p style='color:{risk_color}; margin:0; font-size:1.5rem; font-weight:900;'>{risk_status}</p></div>", unsafe_allow_html=True)
                c_g3.metric("Spam/Bot Oranı", f"% {m_r['bot_pct']:.1f}")

                st.markdown("<br><h4 style='color:#ffffff; font-weight:800;'>• Manipülasyon & Anomali Testleri (Bot Tespiti)</h4>", unsafe_allow_html=True)

                # SENARYO 1: Yorum/Beğeni Dengesizliği (Giyotin)
                c_ratio = m_r['comment_ratio']
                if c_ratio < 0.008: 
                    stat1, clr1, icon1 = "KRİTİK RİSK (Beğeni Botu Şüphesi)", "#ef4444", "🚨"
                    desc1 = f"Hesabın Beğeni/Yorum dengesi insan doğasına aykırı şekilde kopuk (%{(c_ratio*100):.2f}). Profil ucuz beğeni paneli veya hayalet beğeni kullanmış."
                elif c_ratio > 0.15:
                    stat1, clr1, icon1 = "RİSKLİ (Şablon Yorum Şüphesi)", "#f59e0b", "⚠️"
                    desc1 = f"Aşırı yüksek yorum oranı tespit edildi (%{(c_ratio*100):.2f}). Yorum paneli veya çekiliş hesapları kullanılmış."
                else:
                    stat1, clr1, icon1 = "DOĞAL DENGE (Temiz)", "#10b981", "✅"
                    desc1 = f"Yorum ve beğeni arasındaki oran (%{(c_ratio*100):.2f}) sağlıklı insan davranışlarına ve organik reaksiyona uygundur."

                st.markdown(f"""
                <div class="anomaly-box" style="border-left: 4px solid {clr1};">
                    <div>
                        <h5 style="margin:0; color:#ffffff; font-weight:800;">1. Yorum ve Beğeni Orijinalliği Denetimi</h5>
                        <p style="margin:5px 0 0 0; color:#8b949e; font-size:0.9rem;">{desc1}</p>
                    </div>
                    <div style="text-align:right;"><span style="color:{clr1}; font-weight:800; font-size:1rem;">{icon1} {stat1}</span></div>
                </div>
                """, unsafe_allow_html=True)

                # SENARYO 2: Gönderi Varyansı (Zeki Paket Bot Yakalayıcı)
                cv_val = m_r['cv_value']
                if cv_val < 0.28:
                    stat2, clr2, icon2 = "KRİTİK RİSK (Paket Bot / Suni Düzenlilik)", "#ef4444", "🚨"
                    desc2 = f"Gönderiler arası dalgalanma (Sapma: {cv_val:.2f}) imkansız denecek kadar düşük. Profil her postuna sabit rastgeleli 'Zeki Beğeni Paketi' basıyor."
                elif cv_val > 1.2:
                    stat2, clr2, icon2 = "RİSKLİ (Sıçramalı Sponsorluk Botu)", "#f59e0b", "⚠️"
                    desc2 = f"İçerikler arası çok sert uçurumlar var (Sapma: {cv_val:.2f}). Reklamlı içeriklere manipülatif dış bot basılmış olabilir."
                else:
                    stat2, clr2, icon2 = "DOĞAL DALGALANMA (Temiz)", "#10b981", "✅"
                    desc2 = f"Gönderi etkileşimleri (Sapma: {cv_val:.2f}) insan davranışına uygun, organik dalgalanmalar gösteriyor."

                st.markdown(f"""
                <div class="anomaly-box" style="border-left: 4px solid {clr2};">
                    <div>
                        <h5 style="margin:0; color:#ffffff; font-weight:800;">2. İstatistiksel Varyans (CV) Denetimi</h5>
                        <p style="margin:5px 0 0 0; color:#8b949e; font-size:0.9rem;">{desc2}</p>
                    </div>
                    <div style="text-align:right;"><span style="color:{clr2}; font-weight:800; font-size:1rem;">{icon2} {stat2}</span></div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("• Profil verisi çekilemedi.")

st.markdown('<div class="footer-dark">MG BRAND OFFICE © 2026 | Enterprise Intelligence Engine</div>', unsafe_allow_html=True)
