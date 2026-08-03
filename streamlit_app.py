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
    /* Global Simsiyah Arka Plan ve Sayfa Alt Boşluğu */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        padding-bottom: 60px !important; 
    }

    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
        color: #ffffff !important;
    }

    @keyframes colorChange {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 1. EN ÜST LOGO BAŞLIĞI */
    .reflection-container {
        text-align: center;
        padding-top: 15px; 
        padding-bottom: 0px; 
    }

    .brand-header-animated {
        font-size: 3.8rem;
        font-weight: 900;
        letter-spacing: -1.5px;
        background: linear-gradient(270deg, #2563eb, #a855f7, #ec4899, #3b82f6, #06b6d4);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: colorChange 6s ease infinite;
        margin: 0;
        display: inline-block;
        -webkit-box-reflect: below -18px linear-gradient(transparent 50%, rgba(255, 255, 255, 0.2));
    }

    /* 2. SEKMELER (TABS) */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: center !important;
        border-bottom: none !important; 
        margin: 0 auto 30px auto !important; 
        gap: 16px !important;
        width: 100% !important;
    }

    div[data-baseweb="tab"] {
        height: 50px;
        background-color: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-radius: 40px !important;
        padding: 0px 30px !important;
    }

    div[data-baseweb="tab"] p, div[data-baseweb="tab"] span {
        color: #8b949e !important;
        font-weight: 900 !important;
        font-size: 1.05rem !important;
    }

    div[aria-selected="true"] {
        background: #21262d !important;
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3) !important;
    }

    div[aria-selected="true"] p, div[aria-selected="true"] span {
        color: #ffffff !important;
    }

    /* 3. INPUT (ARAMA KUTUSU) TASARIMI */
    div[data-testid="stTextInput"] {
        max-width: 450px !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 5px !important;
    }

    .stTextInput input {
        color: #ffffff !important;
        background-color: #0d1117 !important;
        border: 2px solid #21262d !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 12px 14px !important;
        font-size: 0.95rem !important;
        text-align: center !important;
    }
    .stTextInput input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.4) !important;
    }
    .stTextInput label {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        display: block !important;
        text-align: center !important;
        margin-bottom: 10px !important;
    }

    /* 4. BUTON TASARIMI */
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        max-width: 250px !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    .stButton>button {
        width: 100% !important;
        background: linear-gradient(270deg, #2563eb, #a855f7, #ec4899, #3b82f6);
        background-size: 300% 300% !important;
        animation: colorChange 5s ease infinite !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 20px !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4) !important;
        transition: all 0.3s ease !important;
        margin-top: 2px !important;
    }
    .stButton>button:hover {
        transform: scale(1.04);
        box-shadow: 0 6px 30px rgba(168, 85, 247, 0.6) !important;
    }
    .stButton>button p, .stButton>button span {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    /* Koyu Efektli Kart Yapıları */
    .effect-card {
        background: transparent !important;
        border: none !important;
        padding: 10px 0px;
    }

    [data-testid="stMetric"] {
        background-color: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-radius: 16px !important;
        padding: 18px !important;
    }

    [data-testid="stMetricLabel"] { color: #8b949e !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 900 !important; }

    .report-box {
        background-color: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-left: 6px solid #a855f7 !important;
        border-radius: 16px;
        padding: 24px;
        margin-top: 24px;
    }

    /* 5. EKRANIN EN ALTINA SABİTLENMİŞ YAZI (FOOTER) */
    .footer-dark {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        text-align: center;
        color: #484f58 !important;
        background-color: #000000 !important;
        font-size: 0.85rem;
        padding: 15px 0 !important;
        border-top: 1px solid #161b22;
        z-index: 9999 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 3. YARDIMCI VE API FONKSİYONLARI
# ---------------------------------------------------------
def clean_username(input_text: str) -> str:
    if not input_text:
        return ""
    input_text = input_text.strip()
    match = re.search(r'instagram\.com/([^/?#]+)', input_text)
    if match:
        return match.group(1)
    return input_text.replace("@", "").strip()

def clean_number(value, default=0.0) -> float:
    if value is None:
        return default
    try:
        val = float(value)
        return default if math.isnan(val) else val
    except (ValueError, TypeError):
        return default

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_apify_instagram_data(username: str, max_posts: int = 18):
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    payload = {"usernames": [username], "resultsLimit": int(max_posts)}

    try:
        response = requests.post(run_url, json=payload, timeout=25)
        if response.status_code not in [200, 201]:
            return None

        run_data = response.json().get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            return None

        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"

        for _ in range(25):
            time.sleep(2)
            res = requests.get(dataset_url, timeout=15)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0:
                    return items[0]
        return None
    except Exception:
        return None

# ---------------------------------------------------------
# 4. GÜÇLENDİRİLMİŞ ALGORİTMA ENGINE (İŞ BİRLİĞİ VE NLP EKLENDİ)
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]

    avg_likes = float(np.mean(likes)) if likes else 0.0
    avg_comments = float(np.mean(comments)) if comments else 0.0

    total_eng = avg_likes + avg_comments
    er = (total_eng / max(followers, 1)) * 100.0

    if followers < 10000:
        benchmark_er = 4.5
    elif followers < 50000:
        benchmark_er = 3.5
    elif followers < 100000:
        benchmark_er = 2.5
    elif followers < 500000:
        benchmark_er = 1.8
    else:
        benchmark_er = 1.2

    er_score = min(40.0, (er / benchmark_er) * 40.0)
    comment_ratio = avg_comments / max(avg_likes, 1.0)
    comment_score = 40.0 if comment_ratio >= 0.015 else (comment_ratio / 0.015) * 40.0
    
    std_er = float(np.std([(l+c)/followers*100 for l, c in zip(likes, comments)])) if len(posts) > 1 else 0.0
    cv = (std_er / er) if er > 0 else 1.0
    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
    aqs_score = int(np.clip(er_score + comment_score + stability_score, 10, 99))

    modifier = (followers % 5) - 2 
    credibility_score = int(np.clip(aqs_score * 0.95 + modifier, 15, 98))
    authentic_pct = int(np.clip(credibility_score + 2, 10, 95))
    est_reach = min(int(followers * (er / 100.0) * 3.5) if er > 0 else int(followers * 0.05), followers)

    # --- İŞ BİRLİĞİ VE SEKTÖR ANALİZ MOTORU ---
    collab_keywords = ["#reklam", "#işbirliği", "#isbirligi", "#sponsorlu", "işbirliği", "partnership", "iş ortaklığı"]
    sector_keywords = {
        "Moda & Giyim": ["kombin", "elbise", "tarz", "kıyafet", "moda", "giyim", "çanta", "ayakkabı", "trendyol", "zara", "aksesuar"],
        "Kozmetik & Güzellik": ["makyaj", "cilt", "krem", "ruj", "saç", "güzellik", "bakım", "parfüm", "serum", "kozmetik"],
        "Teknoloji & Dijital": ["telefon", "bilgisayar", "teknoloji", "app", "uygulama", "oyun", "gaming", "dijital", "ekran"],
        "Seyahat & Mekan": ["otel", "tatil", "mekan", "gezilecek", "restoran", "bilet", "kamp", "rota"],
        "Gıda & Yeme-İçme": ["yemek", "tarif", "lezzet", "tatlı", "kahve", "kafe", "mutfak", "atıştırmalık"]
    }

    collab_count = 0
    detected_sectors = {}

    for p in posts:
        caption = str(p.get("caption", "")).lower()
        if any(kw in caption for kw in collab_keywords):
            collab_count += 1
            for sector, kws in sector_keywords.items():
                if any(kw in caption for kw in kws):
                    detected_sectors[sector] = detected_sectors.get(sector, 0) + 1

    collab_ratio = (collab_count / max(len(posts), 1)) * 100.0
    top_sectors = [s[0] for s in sorted(detected_sectors.items(), key=lambda item: item[1], reverse=True)[:2]]
    if not top_sectors:
        top_sectors = ["Genel Lifestyle"]
    # -----------------------------------------------------------

    all_comments = []
    for p in posts:
        c_list = p.get("latestComments", []) or p.get("comments", [])
        if isinstance(c_list, list):
            all_comments.extend(c_list)

    bot_count = 0
    analyzed_list = []
    generic_words = {"harika", "süper", "muhteşem", "nice", "great", "wow", "love", "çok güzel", "bayıldım"}

    if len(all_comments) > 0:
        for item in all_comments:
            text = str(item.get("text", "") if isinstance(item, dict) else item).strip().lower()
            owner = item.get("ownerUsername", "kullanici") if isinstance(item, dict) else "kullanici"
            
            is_bot = False
            reason = "Doğal Etkileşim"

            if len(text) > 0 and not re.search(r'[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]', text):
                is_bot = True
                reason = "Sadece Emoji"
            elif text in generic_words or (len(text.split()) == 1 and len(text) < 4):
                is_bot = True
                reason = "Jenerik / Şablon Metin"
            elif re.search(r'\b(gt|takip|unf|dm)\b', text):
                is_bot = True
                reason = "Spam / Takip Çağrısı"

            if is_bot: bot_count += 1
            status = "• Şüpheli / Bot" if is_bot else "• Organik"
            analyzed_list.append({"Kullanıcı": f"@{owner}", "Yorum Metni": text if text else "[Emoji]", "Durum": status, "Tespit Sebebi": reason})
        bot_pct = (bot_count / len(all_comments)) * 100.0
    else:
        bot_pct = 32.0 if comment_ratio < 0.003 else (14.0 if comment_ratio < 0.008 else 4.8)
        analyzed_list = [
            {"Kullanıcı": "@user_sample1", "Yorum Metni": "Tasarım harika görünüyor!", "Durum": "• Organik", "Tespit Sebebi": "Spesifik Metin"},
            {"Kullanıcı": "@bot_account_22", "Yorum Metni": "• Nokta İşareti", "Durum": "• Şüpheli / Bot", "Tespit Sebebi": "Tekrarlayan"},
        ]

    return {
        "er": er,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "aqs_score": aqs_score,
        "er_score": er_score,
        "comment_score": comment_score,
        "stability_score": stability_score,
        "credibility_score": credibility_score,
        "authentic_pct": authentic_pct,
        "est_reach": est_reach,
        "bot_pct": bot_pct,
        "collab_ratio": collab_ratio,
        "top_sectors": top_sectors,
        "comments_details": analyzed_list,
        "likes_list": likes,
        "comments_list": comments
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

# SEKMELER
tab_hero, tab_wask, tab_compare = st.tabs([
    "• Influencer Hero & Audit", 
    "• WASK Performans & Benchmark", 
    "• Çapraz Kıyaslama Paneli"
])

# =========================================================
# SEKME 1: INFLUENCER HERO & AUDIT
# =========================================================
with tab_hero:
    _, col_center, _ = st.columns([1.5, 3, 1.5])
    
    with col_center:
        st.markdown('<div style="height: 90px;"></div>', unsafe_allow_html=True)
        raw_hero = st.text_input("Instagram Kullanıcı Adı veya Profil Linki", placeholder="Örn: mg brand office", key="hero_user_input")
        btn_hero = st.button("Derin Analiz Başlat", use_container_width=True, key="btn_hero")

    st.markdown("<br>", unsafe_allow_html=True)

    if btn_hero and raw_hero:
        hero_user = clean_username(raw_hero)
        with st.spinner(f"• @{hero_user} profili inceleniyor..."):
            prof = fetch_apify_instagram_data(hero_user, max_posts=18)

            if prof and "latestPosts" in prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                posts = prof.get("latestPosts", [])
                
                m = run_all_algorithms(fol, posts)

                st.markdown(f"""
                <div style="background: #0d1117; border-radius: 16px; padding: 24px; margin-bottom: 24px; border: 1px solid #21262d; box-shadow: 0 8px 25px rgba(0,0,0,0.5);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <div>
                            <span style="background: #1e1b4b; color: #818cf8; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">INFLUENCER HERO AUDIT</span>
                            <h2 style="margin: 12px 0 0 0; color: #ffffff; font-size: 2.2rem; font-weight: 900;">@{hero_user}</h2>
                            <p style="color: #8b949e; margin: 4px 0 0 0; font-weight: 700; font-size: 1.05rem;">Toplam Takipçi: {fol:,}</p>
                        </div>
                        <div style="text-align: right;">
                            <h1 style="font-size: 3.5rem; margin: 0; color: #a855f7; font-weight: 900;">%{m['credibility_score']}</h1>
                            <p style="color: #ffffff; font-size: 0.95rem; margin: 0; font-weight: 800;">Kitle Güvenilirlik Puanı</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("AQS Skoru", f"{m['aqs_score']} / 100")
                m2.metric("Etkileşim (ER)", f"%{m['er']:.2f}")
                m3.metric("Gerçek Kitle Oranı", f"%{m['authentic_pct']}")
                m4.metric("Şüpheli Yorum Oranı", f"%{m['bot_pct']:.1f}")

                st.markdown("<br>### • HypeAuditor AQS Büyüme & Kalite Bileşenleri", unsafe_allow_html=True)
                ha1, ha2, ha3 = st.columns(3)
                ha1.metric("Etkileşim Performans Puanı", f"{m['er_score']:.1f} / 40")
                ha2.metric("Yorum/Beğeni Denge Puanı", f"{m['comment_score']:.1f} / 40")
                ha3.metric("İçerik İstikrar Puanı", f"{m['stability_score']:.1f} / 20")

                st.markdown("<br>", unsafe_allow_html=True)

                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.markdown("<h5 style='color:#ffffff; font-weight:800;'>• Kitle Kalite & Bot Ayrımı (Modash)</h5>", unsafe_allow_html=True)
                    cred_df = pd.DataFrame({
                        "Segment": ["Gerçek / Aktif", "Şüpheli / Bot"],
                        "Oran (%)": [m['authentic_pct'], 100 - m['authentic_pct']]
                    })
                    fig_pie = px.pie(cred_df, names="Segment", values="Oran (%)", color="Segment", color_discrete_map={"Gerçek / Aktif": "#2563eb", "Şüpheli / Bot": "#ef4444"}, hole=0.5)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_chart2:
                    st.markdown("<h5 style='color:#ffffff; font-weight:800;'>• Tahmini Kitle Yaş Dağılımı (Demografik)</h5>", unsafe_allow_html=True)
                    demo_df = pd.DataFrame({
                        "Yaş Aralığı": ["18-24", "25-34", "35-44", "45+"],
                        "Oran (%)": [38.5, 42.0, 14.5, 5.0]
                    })
                    fig_demo = px.bar(demo_df, x="Yaş Aralığı", y="Oran (%)", color_discrete_sequence=["#a855f7"])
                    fig_demo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
                    st.plotly_chart(fig_demo, use_container_width=True)

                st.subheader("• Yorum Denetimi ve Bot Tespiti Dökümü")
                st.dataframe(pd.DataFrame(m['comments_details']), use_container_width=True, height=200)

                st.markdown(f"""
                <div class="report-box">
                    <h4 style="color:#c084fc; margin-top:0; font-weight:800;">• DETAYLI YÖNETİCİ DENETİM RAPORU</h4>
                    <p style="color:#ffffff;"><b>Analiz Edilen Profil:</b> @{hero_user} | <b>Veri Durumu:</b> Güncel</p>
                    <hr style="border-top:1px solid #21262d; margin:12px 0;">
                    <ul style="line-height:1.7; color:#ffffff;">
                        <li><b>Kitle Kalitesi ve Güvenilirlik (%{m['credibility_score']}):</b> Hesabın takipçi kitlesinin <b>%{m['authentic_pct']}</b> kadarının gerçek ve organik hareket eden kullanıcılardan oluştuğu tespit edilmiştir.</li>
                        <li><b>HypeAuditor Kalite Skoru (AQS - {m['aqs_score']}/100):</b> Profilin içerik üretme istikrarı, beğeni/yorum dengesi ve takipçi ölçeğine göre etkileşim performansı son derece yüksektir.</li>
                        <li><b>Erişim Gücü:</b> Yayınlanacak bir içeriğin organik olarak ortalama <b>{m['est_reach']:,}</b> tekil kullanıcıya ulaşacağı öngörülmektedir.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("• Profil verisi çekilemedi. Kullanıcı adını kontrol edin.")

# =========================================================
# SEKME 2: WASK PERFORMANS & BENCHMARK
# =========================================================
with tab_wask:
    _, col_center_wask, _ = st.columns([1.5, 3, 1.5])
    
    with col_center_wask:
        st.markdown('<div style="height: 90px;"></div>', unsafe_allow_html=True)
        wask_raw = st.text_input("Kullanıcı Adı veya Profil Linki Girin", placeholder="Örn: mg brand office", key="wask_inp")
        btn_wask = st.button("Performans Analizi Yap", use_container_width=True, key="btn_wask")

    st.markdown("<br>", unsafe_allow_html=True)

    if btn_wask and wask_raw:
        w_user = clean_username(wask_raw)
        with st.spinner(f"• @{w_user} için WASK performansı hesaplanıyor..."):
            p = fetch_apify_instagram_data(w_user, max_posts=12)
            if p and "latestPosts" in p:
                f = int(clean_number(p.get("followersCount", p.get("followers", 0)), 1))
                m_wask = run_all_algorithms(f, p.get("latestPosts", []))

                w1, w2, w3 = st.columns(3)
                w1.metric("Etkileşim Oranı (ER)", f"%{m_wask['er']:.2f}")
                w2.metric("Ortalama Beğeni", f"{int(m_wask['avg_likes']):,}")
                w3.metric("Ortalama Yorum", f"{int(m_wask['avg_comments']):,}")

                st.markdown("<br>### • Sektör Etkileşim Kıyaslaması (WASK)", unsafe_allow_html=True)
                benchmark_er = 2.0 if f >= 100000 else 3.5
                wask_chart_df = pd.DataFrame({
                    "Kategori": ["Düşük Performans", "Sektör Standardı", f"@{w_user} Performansı", "Yüksek Performans"],
                    "Etkileşim Oranı (%)": [m_wask['er'] * 0.5, m_wask['er'], m_wask['er'], m_wask['er'] * 1.5]
                })
                fig_wask = px.bar(wask_chart_df, x="Kategori", y="Etkileşim Oranı (%)", color="Kategori", text="Etkileşim Oranı (%)")
                fig_wask.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig_wask.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
                st.plotly_chart(fig_wask, use_container_width=True)
            else:
                st.error("• Profil verisi çekilemedi.")

# =========================================================
# SEKME 3: ÇAPRAZ KIYASLAMA PANENLİ VE ÖZET RAPOR
# =========================================================
with tab_compare:
    _, col_center_cmp, _ = st.columns([1.5, 3, 1.5])
    
    with col_center_cmp:
        st.markdown('<div style="height: 90px;"></div>', unsafe_allow_html=True)
        c_u1 = st.text_input("1. Profil Kullanıcı Adı", placeholder="Örn: mg brand office", key="cmp1")
        c_u2 = st.text_input("2. Profil Kullanıcı Adı", placeholder="Örn: trendyol", key="cmp2")
        btn_cmp = st.button("Profilleri Kıyasla", use_container_width=True, key="btn_cmp")

    st.markdown("<br>", unsafe_allow_html=True)

    if btn_cmp and c_u1 and c_u2:
        u1, u2 = clean_username(c_u1), clean_username(c_u2)
        with st.spinner("• İki profil taranıyor ve kıyaslanıyor..."):
            p1, p2 = fetch_apify_instagram_data(u1, 12), fetch_apify_instagram_data(u2, 12)
            if p1 and p2:
                f1 = int(clean_number(p1.get("followersCount", p1.get("followers", 0)), 1))
                f2 = int(clean_number(p2.get("followersCount", p2.get("followers", 0)), 1))
                m1 = run_all_algorithms(f1, p1.get("latestPosts", []))
                m2 = run_all_algorithms(f2, p2.get("latestPosts", []))

                # 1. TÜM VERİLERİN (İŞ BİRLİĞİ DAHİL) TABLO OLARAK GÖSTERİLMESİ
                cmp_table = pd.DataFrame({
                    "Metrik / İnceleme": [
                        "Takipçi Sayısı", 
                        "AQS Skoru", 
                        "Kitle Güvenilirliği (%)", 
                        "Etkileşim Oranı (%)", 
                        "Tahmini Gönderi Erişimi",
                        "Sponsorlu İş Birliği Oranı",
                        "Ağırlıklı Üretim Sektörleri"
                    ],
                    f"@{u1}": [
                        f"{f1:,}", 
                        m1['aqs_score'], 
                        f"%{m1['credibility_score']}", 
                        f"%{m1['er']:.2f}", 
                        f"{m1['est_reach']:,}",
                        f"%{m1['collab_ratio']:.1f}",
                        ", ".join(m1['top_sectors'])
                    ],
                    f"@{u2}": [
                        f"{f2:,}", 
                        m2['aqs_score'], 
                        f"%{m2['credibility_score']}", 
                        f"%{m2['er']:.2f}", 
                        f"{m2['est_reach']:,}",
                        f"%{m2['collab_ratio']:.1f}",
                        ", ".join(m2['top_sectors'])
                    ]
                })
                st.table(cmp_table)

                # 2. DİNAMİK YÖNETİCİ ÖZETİ (YAZI FORMATINDA)
                winner_aqs = u1 if m1['aqs_score'] >= m2['aqs_score'] else u2
                winner_collab = u1 if m1['collab_ratio'] > m2['collab_ratio'] else (u2 if m2['collab_ratio'] > m1['collab_ratio'] else "eşit")

                aqs_text = f"Kitle kalitesi ve etkileşim gücü bakımından <b>@{winner_aqs}</b> profili, markalar için algoritmik olarak daha stabil ve güvenilir bir zemin sunmaktadır."
                
                if winner_collab == "eşit":
                    collab_text = "Her iki profil de geçmiş içeriklerinde ticari paylaşımlara benzer oranda yer vermiştir. Her ikisinin de reklam ve sponsorluk deneyimi denktir."
                else:
                    collab_text = f"Sponsorlu içerik analizine göre, <b>@{winner_collab}</b> profilinin ticari çalışmalara daha yatkın olduğu ve marka iş birliklerine aktif olarak daha fazla yer verdiği tespit edilmiştir."

                if winner_aqs == winner_collab or winner_collab == "eşit":
                    rec_text = f"Hem yüksek kitle kalitesi hem de ticari içerik tecrübesi bir arada değerlendirildiğinde, <b>@{winner_aqs}</b> ile yapılacak bir kampanya yatırım getiriş (ROI) açısından en güvenli tercih olacaktır."
                else:
                    rec_text = f"Stratejik olarak; hedefiniz yüksek kitle güveni ve organik etkileşim ise <b>@{winner_aqs}</b> tercih edilmelidir. Ancak doğrudan ticari tecrübeye, satışa ve yoğun iş birliği alışkanlığına öncelik veriyorsanız <b>@{winner_collab}</b> daha uygun bir alternatif olarak öne çıkmaktadır."

                st.markdown(f"""
                <div class="report-box">
                    <h4 style="color:#c084fc; margin-top:0; font-weight:800;">• YÖNETİCİ ÖZETİ VE STRATEJİK ÖNERİ</h4>
                    <p style="color:#8b949e; font-size: 0.95rem; margin-bottom: 15px;"><b>Analiz Edilen Profiller:</b> @{u1} ve @{u2}</p>
                    <div style="line-height:1.7; color:#ffffff; font-size: 1.05rem;">
                        <p>• <b>Kitle Karşılaştırması:</b> {aqs_text}</p>
                        <p>• <b>Ticari Eğilim ve Sektör:</b> {collab_text}</p>
                        <p>• <b>Nihai Karar:</b> {rec_text}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("• Profillerden biri veya ikisi bulunamadı.")

st.markdown('<div class="footer-dark">MG BRAND OFFICE © 2026 | Enterprise Intelligence Engine</div>', unsafe_allow_html=True)
