import time
import math
import re
import collections
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI VE SESSION STATE
# ---------------------------------------------------------
st.set_page_config(
    page_title="MG BRAND OFFICE | Executive Intelligence",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'credits' not in st.session_state:
    st.session_state['credits'] = 15
if 'agency_name' not in st.session_state:
    st.session_state['agency_name'] = ""

RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "API_ANAHTARINI_BURAYA_GIR")

# ---------------------------------------------------------
# 2. CSS STİLLERİ (GLOBAL INFLUENCER COLLAGE & GLASSMORPHISM)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #050505 !important; color: #e2e8f0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        padding-bottom: 60px !important; 
    }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #e2e8f0 !important; }
    
    /* GLOBAL INFLUENCER BACKGROUND COLLAGE ANIMATION */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(5, 5, 5, 0.88), rgba(5, 5, 5, 0.92)),
            url('https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1920&auto=format&fit=crop'),
            url('https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1920&auto=format&fit=crop');
        background-size: cover, cover, cover;
        background-position: center, center, center;
        z-index: 0;
        animation: subtleZoom 25s infinite alternate ease-in-out;
        pointer-events: none;
    }

    @keyframes subtleZoom {
        0% { transform: scale(1); }
        100% { transform: scale(1.06); }
    }

    .login-wrapper {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 85vh;
    }

    .login-container { 
        width: 420px; 
        background: rgba(15, 23, 42, 0.75); 
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 45px; 
        border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        text-align: center; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.7); 
    }
    .login-header { font-size: 2.2rem; font-weight: 900; background: linear-gradient(270deg, #f8fafc, #94a3b8, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; letter-spacing: -1px; }
    .login-sub { color: #64748b; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 35px; font-weight: 700; }

    .header-bar { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; border-bottom: 1px solid #1e293b; margin-bottom: 30px; background-color: #0a0f1d; position: relative; z-index: 10; }
    .brand-logo { font-size: 1.5rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.5px; }
    .credit-badge { background: #1e293b; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 700; color: #cbd5e1; border: 1px solid #334155; }
    .credit-highlight { color: #3b82f6; font-weight: 900; }

    [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; border-bottom: 1px solid #1e293b !important; margin: 0 auto 30px auto !important; gap: 15px !important; width: 100% !important; flex-wrap: wrap; }
    [data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-radius: 0 !important; box-shadow: none !important; outline: none !important; padding: 12px 15px !important; margin: 0 !important; }
    [data-baseweb="tab"] p, [data-baseweb="tab"] span { color: #64748b !important; font-weight: 700 !important; font-size: 0.9rem !important; text-transform: uppercase; letter-spacing: 0.5px;}
    [data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3b82f6 !important; }
    [data-baseweb="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"] span { color: #f8fafc !important; font-weight: 800 !important; }

    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 500px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    div[data-testid="stTextArea"] { max-width: 600px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea { background-color: #0f172a !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 14px 16px !important; font-size: 1rem !important; color: #f8fafc !important; transition: all 0.3s; }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important; }
    
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 350px !important; margin: 10px auto 0 auto !important; width: 100% !important; }
    .stButton>button { width: 100% !important; background-color: #2563eb !important; color: #ffffff !important; border: none !important; padding: 12px 24px !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.95rem !important; text-transform: uppercase; letter-spacing: 1px; transition: all 0.2s !important; }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: translateY(-1px); }

    [data-testid="stDownloadButton"] { display: flex !important; justify-content: flex-end !important; margin-bottom: 10px; }
    [data-testid="stDownloadButton"] > button { background-color: #0f172a !important; border: 1px solid #334155 !important; color: #94a3b8 !important; padding: 8px 16px !important; border-radius: 6px !important; font-size: 0.85rem !important; font-weight: 700 !important; }
    [data-testid="stDownloadButton"] > button:hover { border-color: #3b82f6 !important; color: #f8fafc !important; }

    .metric-card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; text-align: left; height: 100%; }
    .metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .metric-value { color: #f8fafc; font-size: 1.8rem; font-weight: 900; margin: 0; }
    .metric-sub { font-size: 0.8rem; margin-top: 5px; font-weight: 600; }
    
    .exec-summary { background: linear-gradient(145deg, #0f172a, #020617); border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .badge-status { padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    
    .ai-summary-box { background-color: #0f172a; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 20px; margin-bottom: 25px; line-height: 1.7; color: #cbd5e1; font-size: 0.95rem; }
    .ai-summary-title { font-weight: 800; color: #f8fafc; font-size: 1.05rem; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }

    .fraud-box { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 18px; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 15px; border-left-width: 4px;}
    .fraud-icon { font-size: 1.5rem; margin-top: 2px; font-weight: 900; }
    .fraud-content h5 { margin: 0 0 5px 0; color: #e2e8f0; font-weight: 800; font-size: 1.05rem; }
    .fraud-content p { margin: 0; color: #94a3b8; font-size: 0.9rem; line-height: 1.5; }

    .footer-dark { position: fixed !important; bottom: 0 !important; left: 0 !important; width: 100% !important; text-align: center; color: #475569 !important; background-color: #050505 !important; font-size: 0.8rem; padding: 15px 0 !important; border-top: 1px solid #1e293b; z-index: 9999 !important; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR VE API
# ---------------------------------------------------------
def clean_username(input_text: str) -> str:
    if not input_text: return ""
    input_text = input_text.strip()
    match = re.search(r'(instagram|tiktok|youtube)\.com/([^/?#]+)', input_text)
    if match: return match.group(2).replace("@", "")
    return input_text.replace("@", "").strip()

def clean_number(value, default=0.0) -> float:
    if value is None: return default
    try: val = float(value)
    except (ValueError, TypeError): return default
    return default if math.isnan(val) else val

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_real_social_data(username: str, platform: str):
    time.sleep(1)
    if platform == "• TikTok":
        return {
            "followersCount": 850000,
            "latestPosts": [
                {"likesCount": 120000, "commentsCount": 1500, "viewsCount": 1500000, "caption": "Yeni akım denemesi #fyp", "type": "Video"},
                {"likesCount": 85000, "commentsCount": 800, "viewsCount": 900000, "caption": "Kamera arkası", "type": "Video"},
                {"likesCount": 250000, "commentsCount": 4200, "viewsCount": 3200000, "caption": "İşbirliği ile harika bir gün @marka", "type": "Video"},
            ]
        }
    elif platform == "• YouTube":
        return {
            "followersCount": 450000,
            "latestPosts": [
                {"likesCount": 25000, "commentsCount": 3500, "viewsCount": 450000, "caption": "VLOG: Seyahat ve Yaşam", "type": "Video"},
                {"likesCount": 18000, "commentsCount": 2100, "viewsCount": 310000, "caption": "Yeni Ekipman İncelemesi #reklam", "type": "Video"},
            ]
        }
    else:
        return {
            "followersCount": 1200000,
            "latestPosts": [
                {"likesCount": 65000, "commentsCount": 850, "caption": "Harika bir çekim oldu! #işbirliği @marka", "type": "Photo"},
                {"likesCount": 62000, "commentsCount": 780, "caption": "Yeni koleksiyon hazır.", "type": "Video"},
                {"likesCount": 140000, "commentsCount": 4500, "caption": "Çekiliş zamanı!", "type": "Sidecar"},
            ]
        }

def generate_html_report(user, data):
    html = f"""
    <html><head><meta charset="utf-8"><style>
        body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1e293b; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
        h2 {{ color: #334155; margin-top: 30px; font-size: 1.2rem; }}
        .box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-bottom: 15px; }}
        .summary-box {{ background: #e0f2fe; border-left: 4px solid #0284c7; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }}
        .metric {{ font-weight: bold; color: #2563eb; }}
    </style></head><body>
    <h1>MG BRAND OFFICE • Kurumsal Denetim Raporu</h1>
    <p><b>Hedef Profil:</b> @{user}</p>
    <p><b>Platform:</b> {data['platform']}</p>
    
    <div class="summary-box">
        <b>• Yapay Zeka Yönetici Özeti:</b><br>{data['ai_summary']}
    </div>

    <div class="box">
        <h2>• Skorlama ve Kalite Metrikleri</h2>
        <p>AQS (Kitle Kalite Skoru): <span class="metric">{data['aqs_score']} / 100</span></p>
        <p>Tahmini Organik Kitle Oranı: <span class="metric">%{data['authentic_pct']:.1f}</span></p>
        <p>Sentetik (Bot) Riski: <span class="metric">%{data['bot_pct']:.1f}</span></p>
    </div>

    <div class="box">
        <h2>• Performans ve Maliyet Projeksiyonu</h2>
        <p>Net Etkileşim Oranı (ER): <span class="metric">%{data['er']:.2f}</span></p>
        <p>Tahmini Tekil Erişim Kapasitesi: <span class="metric">{data['est_reach']:,}</span></p>
        <p>CPE (Etkileşim Başına Maliyet): <span class="metric">₺{data['cpe']:.2f}</span></p>
    </div>
    
    <p style="text-align:center; margin-top:50px; font-size:12px; color:#94a3b8;">Sistem Tarafından Otomatik Üretilmiştir • MG BRAND OFFICE</p>
    </body></html>
    """
    return html

# ---------------------------------------------------------
# 4. ALGORİTMA MOTORU
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list, platform: str, budget: float = 0.0, username: str = ""):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    views = [clean_number(p.get("viewsCount"), 0) for p in posts]
    
    avg_likes = float(np.mean(likes)) if likes else 0.0
    avg_comments = float(np.mean(comments)) if comments else 0.0
    total_eng = avg_likes + avg_comments

    er = (total_eng / max(followers, 1)) * 100.0
    
    if platform == "• TikTok":
        benchmark_er = 12.0 if followers < 100000 else 8.0
        visibility_multiplier = 5.0
    elif platform == "• YouTube":
        benchmark_er = 5.0 if followers < 100000 else 3.5
        visibility_multiplier = 1.2
    else:
        benchmark_er = 3.0 if followers < 100000 else 1.8
        visibility_multiplier = 3.0

    er_score = min(40.0, (er / benchmark_er) * 40.0)
    
    if platform == "• TikTok" or platform == "• YouTube":
        avg_views = float(np.mean(views)) if views else 0.0
        engagement_ratio = avg_likes / max(avg_views, 1.0)
        if engagement_ratio < 0.02: comment_anomaly = 0.40
        elif engagement_ratio > 0.25: comment_anomaly = 0.35
        else: comment_anomaly = 0.00
    else:
        engagement_ratio = avg_comments / max(avg_likes, 1.0)
        if engagement_ratio < 0.008: comment_anomaly = 0.50
        elif engagement_ratio > 0.15: comment_anomaly = 0.30
        else: comment_anomaly = 0.00

    if len(posts) > 1:
        eng_array = [(l+c)/max(followers, 1)*100 for l, c in zip(likes, comments)]
        std_er = float(np.std(eng_array))
        cv = (std_er / er) if er > 0 else 1.0 
    else:
        std_er, cv = 0.0, 1.0
        
    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
    aqs_score = int(np.clip(er_score + 40.0 + stability_score - (comment_anomaly*100), 10, 99))

    er_defect = max(0.0, (benchmark_er - er) / benchmark_er)
    
    if cv < 0.28 and len(posts) > 2: variance_anomaly = 0.40 
    elif cv > 1.2: variance_anomaly = 0.30 
    else: variance_anomaly = 0.00 

    calculated_bot = 10.0 + (er_defect * 50.0) + (comment_anomaly * 100.0) + (variance_anomaly * 100.0)
    bot_pct = float(np.clip(calculated_bot, 3.2, 98.5))
    authentic_pct = float(np.clip(100.0 - bot_pct, 1.5, 96.8))
    
    if bot_pct > 30.0: aqs_score = int(aqs_score * 0.4)
    elif bot_pct > 15.0: aqs_score = int(aqs_score * 0.7)

    ai_summary = f"Sistem {platform} algoritma kurallarına göre @{username} profilini denetlendiğinde; kitlenin yaklaşık %{authentic_pct:.1f}'lik kısmının organik olduğu öngörülmektedir. "
    if bot_pct > 20: ai_summary += f"Ancak, %{bot_pct:.1f} seviyesinde ciddi bir manipülasyon/bot riski mevcuttur. "
    elif bot_pct > 10: ai_summary += f"Bununla birlikte %{bot_pct:.1f} pasif/şüpheli kitle oranı gözlemlenmiştir. "
    else: ai_summary += f"Profilin bot ve manipülasyon riski (%{bot_pct:.1f}) {platform} ekosisteminde oldukça güvenilir seviyededir. "

    if er >= benchmark_er: ai_summary += f"Ortalama %{benchmark_er:.2f} olan etkileşim beklentisi aşılarak %{er:.2f} güçlü bir performans elde edilmiştir."
    else: ai_summary += f"Net etkileşim oranı (%{er:.2f}), {platform} pazar standardının altında seyretmektedir."

    all_captions = ""
    mentions_list = []
    collab_keywords = ["#reklam", "#işbirliği", "#isbirligi", "#sponsorlu", "işbirliği", "partnership"]
    sector_keywords = {
        "Moda & Giyim": ["kombin", "elbise", "tarz", "kıyafet", "moda", "giyim"],
        "Kozmetik & Güzellik": ["makyaj", "cilt", "krem", "ruj", "saç", "güzellik"],
        "Teknoloji & Dijital": ["telefon", "bilgisayar", "teknoloji", "app", "uygulama", "oyun"],
        "Gıda & Mekan": ["yemek", "tarif", "lezzet", "otel", "tatil", "restoran", "mekan"]
    }
    collab_count = 0
    detected_sectors = {}
    
    for p in posts:
        caption = str(p.get("caption", "")).lower()
        all_captions += " " + caption
        if any(kw in caption for kw in collab_keywords): collab_count += 1
        for sector, kws in sector_keywords.items():
            if any(kw in caption for kw in kws): detected_sectors[sector] = detected_sectors.get(sector, 0) + 1
        found_mentions = re.findall(r'@([a-zA-Z0-9_.]+)', caption)
        mentions_list.extend([m for m in found_mentions if m != username])

    collab_ratio = (collab_count / max(len(posts), 1)) * 100.0
    top_sectors = [s[0] for s in sorted(detected_sectors.items(), key=lambda item: item[1], reverse=True)[:2]]
    if not top_sectors: top_sectors = ["Genel Lifestyle"]

    mention_counts = collections.Counter(mentions_list)
    top_mentions = mention_counts.most_common(5)

    stopwords = ["ve", "bir", "bu", "için", "çok", "ile", "de", "da", "daha", "en", "gibi", "kadar", "olan", "olarak", "var", "yok", "ama"]
    words = re.findall(r'\b[a-zçğıöşü]{4,}\b', all_captions)
    filtered_words = [w for w in words if w not in stopwords]
    word_counts = collections.Counter(filtered_words).most_common(8)

    if "Moda & Giyim" in top_sectors or "Kozmetik & Güzellik" in top_sectors:
        gender_data = {"Kadın": 78, "Erkek": 22}
        age_data = {"13-17": 12, "18-24": 45, "25-34": 30, "35+": 13}
    elif "Teknoloji & Dijital" in top_sectors:
        gender_data = {"Kadın": 25, "Erkek": 75}
        age_data = {"13-17": 18, "18-24": 42, "25-34": 35, "35+": 5}
    else:
        gender_data = {"Kadın": 55, "Erkek": 45}
        age_data = {"13-17": 8, "18-24": 32, "25-34": 40, "35+": 20}

    est_reach = min(int(followers * (er / 100.0) * visibility_multiplier), followers * 2)
    if est_reach < followers * 0.05: est_reach = int(followers * 0.05)

    cpe = budget / total_eng if total_eng > 0 else 0.0
    cpm = (budget / est_reach) * 1000.0 if est_reach > 0 else 0.0

    return {
        "followers": followers, "er": er, "avg_likes": avg_likes, "total_eng": total_eng,
        "aqs_score": aqs_score, "cv_value": cv, "engagement_ratio": engagement_ratio,
        "authentic_pct": authentic_pct, "est_reach": est_reach,
        "bot_pct": bot_pct, "collab_ratio": collab_ratio, "top_sectors": top_sectors,
        "cpe": cpe, "cpm": cpm, "benchmark_er": benchmark_er,
        "top_mentions": top_mentions, "word_counts": word_counts, "gender_data": gender_data, "age_data": age_data,
        "ai_summary": ai_summary, "platform": platform
    }

# ---------------------------------------------------------
# 5. GİRİŞ VE ANA UYGULAMA YÖNETİMİ
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    st.markdown('<div class="login-wrapper"><div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">ENTERPRISE INTELLIGENCE</div>', unsafe_allow_html=True)
    
    username_input = st.text_input("Kurumsal Kimlik", placeholder="Ajans / Kullanıcı Adı")
    password_input = st.text_input("Şifre", type="password", placeholder="••••••••")
    
    if st.button("SİSTEME GİRİŞ YAP", use_container_width=True):
        if username_input == "admin" and password_input == "12345":
            st.session_state['logged_in'] = True
            st.session_state['agency_name'] = "MG Ajans Yöneticisi"
            st.rerun()
        else:
            st.error("• Hatalı kimlik bilgisi. Lütfen tekrar deneyin.")
    st.markdown('</div></div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
        <div class="header-bar">
            <div class="brand-logo">MG BRAND OFFICE <span style="color:#64748b; font-size:0.9rem; font-weight:600;">| EXECUTIVE SUITE</span></div>
            <div class="credit-badge">Hoş Geldiniz, {st.session_state['agency_name']} • Kalan Kredi: <span class="credit-highlight">{st.session_state['credits']}</span></div>
        </div>
    """, unsafe_allow_html=True)

    tab_report, tab_bulk, tab_demo, tab_finance, tab_compare = st.tabs([
        "• OMNICHANNEL DENETİM", 
        "• TOPLU KAMPANYA (BULK)",
        "• İÇGÖRÜ & AFİNİTE",
        "• MALİYET VE ROI", 
        "• ÇAPRAZ İSTİHBARAT"
    ])

    with tab_report:
        _, col_center_rep, _ = st.columns([1, 4, 1])
        with col_center_rep:
            selected_platform = st.radio("Analiz Edilecek Platform", ["• Instagram", "• TikTok", "• YouTube"], horizontal=True)
            rep_raw = st.text_input(f"{selected_platform.replace('• ', '')} Profil Bağlantısı veya Kullanıcı Adı", key="rep_inp")
            btn_rep = st.button("KAPSAMLI DENETİMİ BAŞLAT", use_container_width=True, key="btn_rep")

        st.markdown("<br>", unsafe_allow_html=True)

        if btn_rep and rep_raw:
            if st.session_state['credits'] <= 0:
                st.error("• Analiz krediniz tükenmiştir.")
            else:
                st.session_state['credits'] -= 1
                r_user = clean_username(rep_raw)
                with st.spinner(f"• @{r_user} ({selected_platform.replace('• ', '')}) algoritmalarıyla denetleniyor..."):
                    p_rep = fetch_real_social_data(r_user, selected_platform)
                    if p_rep and "latestPosts" in p_rep:
                        f_rep = int(clean_number(p_rep.get("followersCount", 0), 1))
                        m_r = run_all_algorithms(f_rep, p_rep.get("latestPosts", []), selected_platform, username=r_user)
                        
                        st.session_state['report_data'] = m_r
                        st.session_state['report_user'] = r_user

                        html_report = generate_html_report(r_user, m_r)
                        st.download_button("• KURUMSAL RAPORU İNDİR", data=html_report, file_name=f"{r_user}_mg_denetim.html", mime="text/html")

                        if m_r['bot_pct'] > 20 or m_r['cv_value'] < 0.28:
                            exec_decision, exec_color, exec_badge = "RİSKLİ (YATIRIM ONAYLANMADI)", "#ef4444", "background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);"
                        elif m_r['bot_pct'] > 10 or m_r['cv_value'] < 0.35:
                            exec_decision, exec_color, exec_badge = "ŞÜPHELİ (KONTROLLÜ YATIRIM)", "#f59e0b", "background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3);"
                        else:
                            exec_decision, exec_color, exec_badge = "GÜVENİLİR (YATIRIM ONAYLANDI)", "#10b981", "background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);"

                        st.markdown(f"""
                        <div class="exec-summary">
                            <div>
                                <p style="color:#64748b; font-size:0.85rem; font-weight:700; margin:0 0 5px 0; text-transform:uppercase;">Profİl İstİhbaratı ({selected_platform.replace('• ', '')})</p>
                                <h2 style="margin: 0 0 5px 0; color: #f8fafc; font-size: 2.2rem; font-weight: 900; letter-spacing:-1px;">@{r_user}</h2>
                                <p style="color: #94a3b8; margin: 0; font-size: 0.95rem; font-weight: 500;">{f_rep:,} Toplam Takipçi/Abone</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="color:#64748b; font-size:0.85rem; font-weight:700; margin:0 0 10px 0; text-transform:uppercase;">Algorİtmİk Karar</p>
                                <span class="badge-status" style="{exec_badge}">• {exec_decision}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="ai-summary-box">
                            <div class="ai-summary-title">• Yapay Zeka Yönetici Özeti</div>
                            {m_r['ai_summary']}
                        </div>
                        """, unsafe_allow_html=True)

                        m1, m2, m3, m4 = st.columns(4)
                        m1.markdown(f"<div class='metric-card'><div class='metric-title'>AQS Kalite Skoru</div><div class='metric-value'>{m_r['aqs_score']} <span style='font-size:1rem;color:#64748b'>/ 100</span></div><div class='metric-sub' style='color:#64748b'>Standart: %{m_r['benchmark_er']}</div></div>", unsafe_allow_html=True)
                        m2.markdown(f"<div class='metric-card'><div class='metric-title'>Etkileşim (ER)</div><div class='metric-value'>%{m_r['er']:.2f}</div><div class='metric-sub' style='color:#64748b'>Ort. Reaksiyon: {int(m_r['total_eng']):,}</div></div>", unsafe_allow_html=True)
                        m3.markdown(f"<div class='metric-card'><div class='metric-title'>Organik Kapasite</div><div class='metric-value' style='color:#3b82f6'>%{m_r['authentic_pct']:.1f}</div><div class='metric-sub' style='color:#64748b'>Maks. Erişim: {m_r['est_reach']:,}</div></div>", unsafe_allow_html=True)
                        m4.markdown(f"<div class='metric-card'><div class='metric-title'>Sentetik (Bot) Riski</div><div class='metric-value' style='color:#ef4444'>%{m_r['bot_pct']:.1f}</div><div class='metric-sub' style='color:#64748b'>Manipülasyon Oranı</div></div>", unsafe_allow_html=True)

                        st.markdown("<br><h4 style='color:#f8fafc; font-weight:800; font-size:1.2rem; border-bottom:1px solid #1e293b; padding-bottom:10px; margin-bottom:20px;'>• ANTI-FRAUD (SAHTEKARLIK) KARNESİ</h4>", unsafe_allow_html=True)

                        e_ratio = m_r['engagement_ratio']
                        if selected_platform == "• Instagram":
                            if e_ratio < 0.008: s1, c1, d1 = "AĞIR İHLAL", "#ef4444", f"Yorum/Beğeni dengesi (%{(e_ratio*100):.2f}) mantıksız. Panel kullanılmış."
                            elif e_ratio > 0.15: s1, c1, d1 = "ŞÜPHELİ", "#f59e0b", f"Aşırı yüksek yorum oranı (%{(e_ratio*100):.2f})."
                            else: s1, c1, d1 = "GÜVENİLİR", "#10b981", f"Denge (%{(e_ratio*100):.2f}) organik standartlardadır."
                        else:
                            if e_ratio < 0.02: s1, c1, d1 = "AĞIR İHLAL", "#ef4444", f"İzlenme/Beğeni oranı (%{(e_ratio*100):.2f}) çok düşük."
                            elif e_ratio > 0.25: s1, c1, d1 = "ŞÜPHELİ", "#f59e0b", f"İzlenmeye kıyasla çok fazla beğeni."
                            else: s1, c1, d1 = "GÜVENİLİR", "#10b981", f"İzlenme ve reaksiyon tutarlılığı uygun."

                        st.markdown(f"""
                        <div class="fraud-box" style="border-left-color: {c1};">
                            <div class="fraud-icon" style="color:{c1};">•</div>
                            <div class="fraud-content"><h5>Reaksiyon / İzlenme Dengesizliği - <span style="color:{c1}">{s1}</span></h5><p>{d1}</p></div>
                        </div>
                        """, unsafe_allow_html=True)

                        cv_val = m_r['cv_value']
                        if cv_val < 0.28: s2, c2, d2 = "AĞIR İHLAL", "#ef4444", f"Gönderiler arası etkileşim stabilitesi suni."
                        elif cv_val > 1.2: s2, c2, d2 = "ŞÜPHELİ", "#f59e0b", f"İçerikler arası uçurumlar var."
                        else: s2, c2, d2 = "GÜVENİLİR", "#10b981", f"İçerik etkileşimleri doğal dalgalanma gösteriyor."

                        st.markdown(f"""
                        <div class="fraud-box" style="border-left-color: {c2};">
                            <div class="fraud-icon" style="color:{c2};">•</div>
                            <div class="fraud-content"><h5>İstatistiksel Varyans (CV) - <span style="color:{c2}">{s2}</span></h5><p>{d2}</p></div>
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.error("• Profil verisi çekilemedi.")

    with tab_bulk:
        st.markdown("<h4 style='color:#f8fafc; font-weight:800; border-bottom:1px solid #1e293b; padding-bottom:10px;'>• TOPLU KAMPANYA FİZİBİLİTESİ (BULK SEARCH)</h4>", unsafe_allow_html=True)
        _, col_bulk_center, _ = st.columns([1, 4, 1])
        with col_bulk_center:
            bulk_raw = st.text_area("Influencer Aday Listesi", placeholder="leyakirsan\nmerrtdmrcii", height=120)
            bulk_budget = st.number_input("Toplam Kampanya Bütçesi (₺)", min_value=1000, step=10000, value=250000)
            btn_bulk = st.button("LİSTEYİ ANALİZ ET", use_container_width=True)

        if btn_bulk and bulk_raw:
            usernames = [clean_username(u) for u in re.split(r'[,\n]+', bulk_raw) if u.strip()]
            if usernames:
                results = []
                for user in usernames:
                    p_data = fetch_real_social_data(user, "• Instagram")
                    if p_data:
                        f_count = int(clean_number(p_data.get("followersCount", 0), 1))
                        m_data = run_all_algorithms(f_count, p_data.get("latestPosts", []), "• Instagram", username=user)
                        m_data['username'] = user
                        results.append(m_data)
                if results:
                    total_reach = sum([r['est_reach'] for r in results])
                    avg_aqs = np.mean([r['aqs_score'] for r in results])
                    st.markdown(f"<div class='exec-summary'><div><h2 style='color:#f8fafc; margin:0;'>Toplam Erişim: {total_reach:,}</h2></div><div style='text-align:right;'><span class='badge-status' style='background:rgba(59,130,246,0.1); color:#3b82f6; font-size:1.3rem;'>Ort. AQS: {int(avg_aqs)}</span></div></div>", unsafe_allow_html=True)
                    df_res = pd.DataFrame([{"Kullanıcı": f"@{r['username']}", "Takipçi": f"{r['followers']:,}", "AQS": r['aqs_score'], "Bot Riski": f"%{r['bot_pct']:.1f}", "ER": f"%{r['er']:.2f}"} for r in results])
                    st.dataframe(df_res, use_container_width=True, hide_index=True)

    with tab_demo:
        if 'report_data' in st.session_state:
            d = st.session_state['report_data']
            u = st.session_state['report_user']
            st.markdown(f"<h4 style='color:#f8fafc; font-weight:800; font-size:1.2rem; border-bottom:1px solid #1e293b; padding-bottom:10px; margin-bottom:20px;'>• @{u} KİTLE DEMOGRAFİSİ & MARKA AFİNİTESİ</h4>", unsafe_allow_html=True)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                gen_df = pd.DataFrame(list(d['gender_data'].items()), columns=['Cinsiyet', 'Oran'])
                fig_g = px.pie(gen_df, names='Cinsiyet', values='Oran', hole=0.7, color_discrete_sequence=["#ec4899", "#3b82f6"])
                fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"), title=dict(text="Cinsiyet Dağılımı", font=dict(color="#f8fafc", size=15)), margin=dict(t=40, b=10, l=10, r=10))
                st.plotly_chart(fig_g, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col_d2:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                age_df = pd.DataFrame(list(d['age_data'].items()), columns=['Yaş Grubu', 'Oran'])
                fig_a = px.bar(age_df, x='Yaş Grubu', y='Oran', color_discrete_sequence=["#a855f7"])
                fig_a.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"), title=dict(text="Yaş Dağılımı", font=dict(color="#f8fafc", size=15)), margin=dict(t=40, b=10, l=10, r=10))
                st.plotly_chart(fig_a, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#f8fafc; font-weight:800;'>• Rakip Radarı (Marka Afinitesi)</h5>", unsafe_allow_html=True)
                if d['top_mentions']:
                    for mention, count in d['top_mentions']:
                        st.markdown(f"<div style='background:#1e293b; padding:10px 15px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between;'><span style='color:#3b82f6; font-weight:700;'>@{mention}</span><span style='color:#94a3b8;'>{count} Kez</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#94a3b8;'>Veri yok.</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col_w2:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#f8fafc; font-weight:800;'>• Konu Analizi (Kelime Frekansı)</h5>", unsafe_allow_html=True)
                if d['word_counts']:
                    w_df = pd.DataFrame(d['word_counts'], columns=['Kelime', 'Frekans'])
                    fig_w = px.bar(w_df, y='Kelime', x='Frekans', orientation='h', color_discrete_sequence=["#06b6d4"])
                    fig_w.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"), margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_w, use_container_width=True)
                else:
                    st.markdown("<p style='color:#94a3b8;'>Veri yok.</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("• Lütfen önce 'OMNICHANNEL DENETİM' sekmesinden bir profili taratın.")

    with tab_finance:
        _, col_center_fin, _ = st.columns([1, 4, 1])
        with col_center_fin:
            fin_raw = st.text_input("Hedef Profil", placeholder="Örn: leyakirsan", key="fin_inp")
            fin_budget = st.number_input("Kampanya Bütçesi (₺)", min_value=1000, step=5000, value=50000, key="fin_budget_single")
            btn_fin = st.button("FİZİBİLİTE HESAPLA", use_container_width=True, key="btn_fin")

        st.markdown("<br>", unsafe_allow_html=True)
        if btn_fin and fin_raw:
            f_user = clean_username(fin_raw)
            with st.spinner("• Finansal metrikler hesaplanıyor..."):
                p_fin = fetch_real_social_data(f_user, "• Instagram")
                if p_fin:
                    fol_f = int(clean_number(p_fin.get("followersCount", 0), 1))
                    m_f = run_all_algorithms(fol_f, p_fin.get("latestPosts", []), "• Instagram", budget=fin_budget)
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<div class='metric-card'><div class='metric-title'>CPE</div><div class='metric-value' style='color:#3b82f6'>₺{m_f['cpe']:.2f}</div></div>", unsafe_allow_html=True)
                    c2.markdown(f"<div class='metric-card'><div class='metric-title'>CPM</div><div class='metric-value' style='color:#10b981'>₺{m_f['cpm']:.2f}</div></div>", unsafe_allow_html=True)
                    c3.markdown(f"<div class='metric-card'><div class='metric-title'>Erişim</div><div class='metric-value'>{m_f['est_reach']:,}</div></div>", unsafe_allow_html=True)

    with tab_compare:
        _, col_center_cmp, _ = st.columns([1, 4, 1])
        with col_center_cmp:
            c_u1 = st.text_input("1. Profil", placeholder="Örn: rakip1", key="cmp1")
            c_u2 = st.text_input("2. Profil", placeholder="Örn: rakip2", key="cmp2")
            btn_cmp = st.button("KIYASLA", use_container_width=True, key="btn_cmp")

        if btn_cmp and c_u1 and c_u2:
            u1, u2 = clean_username(c_u1), clean_username(c_u2)
            p1, p2 = fetch_real_social_data(u1, "• Instagram"), fetch_real_social_data(u2, "• Instagram")
            if p1 and p2:
                f1 = int(clean_number(p1.get("followersCount", 0), 1))
                f2 = int(clean_number(p2.get("followersCount", 0), 1))
                m1 = run_all_algorithms(f1, p1.get("latestPosts", []), "• Instagram")
                m2 = run_all_algorithms(f2, p2.get("latestPosts", []), "• Instagram")
                cmp_df = pd.DataFrame({
                    "Metrik": ["Takipçi", "AQS", "Bot Riski", "ER", "Erişim"],
                    f"@{u1}": [f"{f1:,}", m1['aqs_score'], f"%{m1['bot_pct']:.1f}", f"%{m1['er']:.2f}", f"%{m1['est_reach']:,}"],
                    f"@{u2}": [f"{f2:,}", m2['aqs_score'], f"%{m2['bot_pct']:.1f}", f"%{m2['er']:.2f}", f"%{m2['est_reach']:,}"]
                })
                st.dataframe(cmp_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="footer-dark">MG BRAND OFFICE EXECUTIVE SUITE © 2026 | ENTERPRISE INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
