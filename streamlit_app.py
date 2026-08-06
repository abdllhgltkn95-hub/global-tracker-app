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
RAPIDAPI_HOST = "instagram-scraper-api2.p.rapidapi.com"

# ---------------------------------------------------------
# 2. CSS STİLLERİ (HIGH-END ENTERPRISE DESIGN & NO EMOJI)
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
    @keyframes colorChange { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    .login-container { max-width: 400px; margin: 100px auto; background: #0f172a; padding: 40px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .login-header { font-size: 2rem; font-weight: 900; background: linear-gradient(270deg, #f8fafc, #94a3b8, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .login-sub { color: #64748b; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 30px; }

    .header-bar { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; border-bottom: 1px solid #1e293b; margin-bottom: 30px; background-color: #0a0f1d; }
    .brand-logo { font-size: 1.5rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.5px; }
    .credit-badge { background: #1e293b; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 700; color: #cbd5e1; border: 1px solid #334155; }
    .credit-highlight { color: #3b82f6; font-weight: 900; }

    [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; border-bottom: 1px solid #1e293b !important; margin: 0 auto 30px auto !important; gap: 20px !important; width: 100% !important; flex-wrap: wrap; }
    [data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-radius: 0 !important; box-shadow: none !important; outline: none !important; padding: 12px 15px !important; margin: 0 !important; }
    [data-baseweb="tab"] p, [data-baseweb="tab"] span { color: #64748b !important; font-weight: 700 !important; font-size: 0.95rem !important; text-transform: uppercase; letter-spacing: 0.5px;}
    [data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3b82f6 !important; }
    [data-baseweb="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"] span { color: #f8fafc !important; font-weight: 800 !important; }

    div[data-testid="stRadio"] > div { display: flex; justify-content: center; gap: 20px; margin-bottom: 15px; }
    
    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 500px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    div[data-testid="stTextArea"] { max-width: 600px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea { background-color: #0f172a !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 14px 16px !important; font-size: 1rem !important; color: #f8fafc !important; transition: all 0.3s; }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important; }
    
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 350px !important; margin: 10px auto 0 auto !important; width: 100% !important; }
    .stButton>button { width: 100% !important; background-color: #2563eb !important; color: #ffffff !important; border: none !important; padding: 12px 24px !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.95rem !important; text-transform: uppercase; letter-spacing: 1px; transition: all 0.2s !important; }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: translateY(-1px); }

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
    """
    Çoklu Platform Veri Simülatörü / API Entegrasyon Noktası
    Gerçek API eklendiğinde platform parametresine göre TikTok veya YouTube endpointleri çağrılacaktır.
    """
    time.sleep(1)
    
    # Platforma göre farklı hacimlerde sentetik/gerçekçi test verisi üretimi
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
                {"likesCount": 25000, "commentsCount": 3500, "viewsCount": 450000, "caption": "VLOG: Tokyo Seyahati", "type": "Video"},
                {"likesCount": 18000, "commentsCount": 2100, "viewsCount": 310000, "caption": "Yeni Ekipman İncelemesi #reklam", "type": "Video"},
            ]
        }
    else: # Instagram
        return {
            "followersCount": 1200000,
            "latestPosts": [
                {"likesCount": 65000, "commentsCount": 850, "caption": "Harika bir çekim oldu! #işbirliği @marka", "type": "Photo"},
                {"likesCount": 62000, "commentsCount": 780, "caption": "Yeni koleksiyon hazır.", "type": "Video"},
                {"likesCount": 140000, "commentsCount": 4500, "caption": "Çekiliş zamanı!", "type": "Sidecar"},
            ]
        }

# ---------------------------------------------------------
# 4. ÇOKLU PLATFORM (OMNICHANNEL) ANTI-FRAUD ALGORİTMASI
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list, platform: str, budget: float = 0.0, username: str = ""):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    views = [clean_number(p.get("viewsCount"), 0) for p in posts] # Sadece TikTok/YT için geçerli
    
    avg_likes = float(np.mean(likes)) if likes else 0.0
    avg_comments = float(np.mean(comments)) if comments else 0.0
    avg_views = float(np.mean(views)) if views else 0.0
    total_eng = avg_likes + avg_comments

    er = (total_eng / max(followers, 1)) * 100.0
    
    # Platforma Özel Sektör Standartları (Benchmark)
    if platform == "• TikTok":
        benchmark_er = 12.0 if followers < 100000 else 8.0
        visibility_multiplier = 5.0 # TikTok FYP Algoritması
    elif platform == "• YouTube":
        benchmark_er = 5.0 if followers < 100000 else 3.5
        visibility_multiplier = 1.2
    else: # Instagram
        benchmark_er = 3.0 if followers < 100000 else 1.8
        visibility_multiplier = 3.0

    er_score = min(40.0, (er / benchmark_er) * 40.0)
    
    # Platforma Özel Manipülasyon Analizi
    if platform == "• TikTok" or platform == "• YouTube":
        # Video platformlarında İzlenme / Beğeni oranı çok kritiktir.
        engagement_ratio = avg_likes / max(avg_views, 1.0)
        if engagement_ratio < 0.02: comment_anomaly = 0.40 # Çok izlenip az beğenilme (View Bot)
        elif engagement_ratio > 0.25: comment_anomaly = 0.35 # Az izlenip çok beğenilme (Like Bot)
        else: comment_anomaly = 0.00
    else:
        # Instagram'da Yorum / Beğeni oranı geçerlidir.
        engagement_ratio = avg_comments / max(avg_likes, 1.0)
        if engagement_ratio < 0.008: comment_anomaly = 0.50 # Sadece beğeni basılmış
        elif engagement_ratio > 0.15: comment_anomaly = 0.30 # Yorum botu
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

    # Yapay Zeka Özeti
    ai_summary = f"Sistem {platform} algoritma kurallarına göre @{username} profilini denetlediğinde; kitlenin yaklaşık %{authentic_pct:.1f}'lik kısmının organik olduğu öngörülmektedir. "
    if bot_pct > 20: ai_summary += f"Ancak, %{bot_pct:.1f} seviyesinde ciddi bir manipülasyon/bot riski mevcuttur. Platform içi algoritmik sapmalar yüksek risk taşıyor. "
    elif bot_pct > 10: ai_summary += f"Bununla birlikte %{bot_pct:.1f} pasif/şüpheli kitle oranı gözlemlenmiştir. "
    else: ai_summary += f"Profilin bot ve manipülasyon riski (%{bot_pct:.1f}) {platform} ekosisteminde oldukça güvenilir seviyededir. "

    if er >= benchmark_er: ai_summary += f"Platformun ortalama %{benchmark_er:.2f} olan etkileşim beklentisi aşılarak %{er:.2f} güçlü bir performans elde edilmiştir."
    else: ai_summary += f"Net etkileşim oranı (%{er:.2f}), {platform} pazar standardının (%{benchmark_er:.2f}) altında seyretmektedir."

    est_reach = min(int(followers * (er / 100.0) * visibility_multiplier), followers * 2) # Viral kapasite eklendi
    if est_reach < followers * 0.05: est_reach = int(followers * 0.05)

    cpe = budget / total_eng if total_eng > 0 else 0.0
    cpm = (budget / est_reach) * 1000.0 if est_reach > 0 else 0.0

    return {
        "er": er, "avg_likes": avg_likes, "total_eng": total_eng,
        "aqs_score": aqs_score, "cv_value": cv, "engagement_ratio": engagement_ratio,
        "authentic_pct": authentic_pct, "est_reach": est_reach,
        "bot_pct": bot_pct, "cpe": cpe, "cpm": cpm, "benchmark_er": benchmark_er,
        "ai_summary": ai_summary, "platform": platform
    }

# ---------------------------------------------------------
# 5. GİRİŞ VE ANA UYGULAMA YÖNETİMİ
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">ENTERPRISE INTELLIGENCE LOGIN</div>', unsafe_allow_html=True)
    
    username_input = st.text_input("Kurumsal Kimlik", placeholder="Ajans / Kullanıcı Adı")
    password_input = st.text_input("Şifre", type="password", placeholder="••••••••")
    
    if st.button("SİSTEME GİRİŞ YAP", use_container_width=True):
        if username_input == "admin" and password_input == "12345":
            st.session_state['logged_in'] = True
            st.session_state['agency_name'] = "MG Ajans Yöneticisi"
            st.rerun()
        else:
            st.error("• Hatalı kimlik bilgisi. Lütfen tekrar deneyin.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- ANA UYGULAMA (GİRİŞ YAPILDIKTAN SONRA) ---
    st.markdown(f"""
        <div class="header-bar">
            <div class="brand-logo">MG BRAND OFFICE <span style="color:#64748b; font-size:0.9rem; font-weight:600;">| EXECUTIVE SUITE</span></div>
            <div class="credit-badge">Hoş Geldiniz, {st.session_state['agency_name']} • Kalan Kredi: <span class="credit-highlight">{st.session_state['credits']}</span></div>
        </div>
    """, unsafe_allow_html=True)

    tab_report, tab_bulk, tab_finance = st.tabs([
        "• OMNICHANNEL DENETİM", 
        "• TOPLU KAMPANYA (BULK)",
        "• MALİYET VE ROI"
    ])

    with tab_report:
        _, col_center_rep, _ = st.columns([1, 4, 1])
        with col_center_rep:
            # ÇOKLU PLATFORM SEÇİCİ
            selected_platform = st.radio("Analiz Edilecek Platform", ["• Instagram", "• TikTok", "• YouTube"], horizontal=True)
            rep_raw = st.text_input(f"{selected_platform.replace('• ', '')} Profil Bağlantısı veya Kullanıcı Adı", key="rep_inp")
            btn_rep = st.button("KAPSAMLI DENETİMİ BAŞLAT", use_container_width=True, key="btn_rep")

        st.markdown("<br>", unsafe_allow_html=True)

        if btn_rep and rep_raw:
            if st.session_state['credits'] <= 0:
                st.error("• Analiz krediniz tükenmiştir. Lütfen Enterprise paketinizi yükseltin.")
            else:
                st.session_state['credits'] -= 1 # Kredi düşüşü
                r_user = clean_username(rep_raw)
                with st.spinner(f"• @{r_user} ({selected_platform.replace('• ', '')}) algoritmalarıyla denetleniyor..."):
                    p_rep = fetch_real_social_data(r_user, selected_platform)
                    if p_rep and "latestPosts" in p_rep:
                        f_rep = int(clean_number(p_rep.get("followersCount", 0), 1))
                        m_r = run_all_algorithms(f_rep, p_rep.get("latestPosts", []), selected_platform, username=r_user)

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
                            elif e_ratio > 0.15: s1, c1, d1 = "ŞÜPHELİ", "#f59e0b", f"Aşırı yüksek yorum oranı (%{(e_ratio*100):.2f}). Yorum havuzu şüphesi."
                            else: s1, c1, d1 = "GÜVENİLİR", "#10b981", f"Denge (%{(e_ratio*100):.2f}) organik standartlardadır."
                        else:
                            if e_ratio < 0.02: s1, c1, d1 = "AĞIR İHLAL", "#ef4444", f"İzlenme/Beğeni oranı (%{(e_ratio*100):.2f}) çok düşük. İzlenme botu (View Bot) şüphesi."
                            elif e_ratio > 0.25: s1, c1, d1 = "ŞÜPHELİ", "#f59e0b", f"İzlenmeye kıyasla çok fazla beğeni (%{(e_ratio*100):.2f}). Şişirilmiş reaksiyon."
                            else: s1, c1, d1 = "GÜVENİLİR", "#10b981", f"İzlenme ve reaksiyon tutarlılığı (%{(e_ratio*100):.2f}) algoritma standartlarına uygun."

                        st.markdown(f"""
                        <div class="fraud-box" style="border-left-color: {c1};">
                            <div class="fraud-icon" style="color:{c1};">•</div>
                            <div class="fraud-content"><h5>Reaksiyon / İzlenme Dengesizliği - <span style="color:{c1}">{s1}</span></h5><p>{d1}</p></div>
                        </div>
                        """, unsafe_allow_html=True)

                        cv_val = m_r['cv_value']
                        if cv_val < 0.28: s2, c2, d2 = "AĞIR İHLAL", "#ef4444", f"Gönderiler arası etkileşim stabilitesi (Sapma: {cv_val:.2f}) suni."
                        elif cv_val > 1.2: s2, c2, d2 = "ŞÜPHELİ", "#f59e0b", f"İçerikler arası uçurumlar var (Sapma: {cv_val:.2f}). Reklamlara özel dış müdahale olabilir."
                        else: s2, c2, d2 = "GÜVENİLİR", "#10b981", f"İçerik etkileşimleri (Sapma: {cv_val:.2f}) doğal dalgalanma gösteriyor."

                        st.markdown(f"""
                        <div class="fraud-box" style="border-left-color: {c2};">
                            <div class="fraud-icon" style="color:{c2};">•</div>
                            <div class="fraud-content"><h5>İstatistiksel Varyans (CV) - <span style="color:{c2}">{s2}</span></h5><p>{d2}</p></div>
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.error("• Profil verisi çekilemedi.")

    with tab_bulk:
        st.info("• Kredi harcaması yapmamak adına Toplu Tarama Modülü şimdilik tekil analiz tarafına yönlendirilmiştir.")
        
    with tab_finance:
        st.info("• Bütçe ve maliyet analizleri, çoklu platform güncellemeleri doğrultusunda yapılandırılmaktadır.")

    st.markdown('<div class="footer-dark">MG BRAND OFFICE EXECUTIVE SUITE © 2026 | ENTERPRISE INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
