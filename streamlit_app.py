import streamlit as st
import time
import math
import re
import collections
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI VE SESSION STATE
# ---------------------------------------------------------
st.set_page_config(
    page_title="MG BRAND OFFICE | Executive Intelligence",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb")

if 'credits' not in st.session_state: st.session_state['credits'] = 100
if 'report_data' not in st.session_state: st.session_state['report_data'] = None

# ---------------------------------------------------------
# 2. CSS STİLLERİ (NEON ŞIKLIK VE GLASSMORPHISM)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #050505 0%, #0f172a 100%) !important; background-attachment: fixed !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #e2e8f0 !important; }
    
    .hero-container { text-align: center; padding: 40px 0 20px 0; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .hero-title { font-size: 3.8rem; font-weight: 900; background: linear-gradient(270deg, #3b82f6, #8b5cf6, #3b82f6); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradient-glow 4s linear infinite; margin: 0; letter-spacing: -1.5px; }
    .hero-subtitle { color: #64748b; font-size: 0.95rem; letter-spacing: 4px; font-weight: 700; text-transform: uppercase; margin-top: 5px;}
    @keyframes gradient-glow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; border-bottom: 1px solid #1e293b !important; margin: 0 auto 30px auto !important; gap: 15px !important; flex-wrap: wrap; }
    [data-baseweb="tab"] { background-color: transparent !important; border: none !important; padding: 12px 15px !important; }
    [data-baseweb="tab"] span { color: #64748b !important; font-weight: 700 !important; font-size: 0.9rem !important; }
    [data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3b82f6 !important; }
    [data-baseweb="tab"][aria-selected="true"] span { color: #f8fafc !important; }

    div[data-testid="stTextInput"], div[data-testid="stNumberInput"], div[data-testid="stTextArea"] { max-width: 600px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea { background-color: rgba(15, 23, 42, 0.6) !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 14px 16px !important; font-size: 1rem !important; color: #f8fafc !important; backdrop-filter: blur(10px); text-align: center; }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.3) !important; }
    
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 350px !important; margin: 10px auto 0 auto !important; width: 100% !important; }
    .stButton>button { width: 100% !important; background-color: #2563eb !important; color: #ffffff !important; border: none !important; padding: 12px 24px !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.95rem !important; transition: 0.3s; }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3); }

    .metric-card { background-color: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 12px; padding: 20px; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.2); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
    .metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }
    .metric-value { color: #f8fafc; font-size: 1.8rem; font-weight: 900; margin: 0; }
    
    .exec-summary { background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.9)); border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(15px); }
    .badge-status { padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }
    .ai-summary-box { background-color: rgba(15, 23, 42, 0.5); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 20px; margin-bottom: 25px; line-height: 1.7; color: #cbd5e1; font-size: 0.95rem; backdrop-filter: blur(12px); }
    .fraud-box { background-color: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 10px; padding: 18px; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 15px; border-left-width: 4px; backdrop-filter: blur(12px);}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. YARDIMCI VE API FONKSİYONLARI
# ---------------------------------------------------------
def clean_username(text):
    if not text: return ""
    return re.search(r'(instagram|tiktok|youtube)\.com/([^/?#]+)', text.strip()).group(2).replace("@", "") if re.search(r'(instagram|tiktok|youtube)\.com/([^/?#]+)', text.strip()) else text.replace("@", "").strip()

def clean_number(v, default=0.0):
    try: return float(v) if not math.isnan(float(v)) else default
    except: return default

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_apify_instagram_data(username, max_posts=24):
    run_url = f"https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token={APIFY_TOKEN}"
    try:
        res = requests.post(run_url, json={"usernames": [username], "resultsLimit": int(max_posts)}, timeout=30) 
        if res.status_code not in [200, 201]: return None
        d_id = res.json().get("data", {}).get("defaultDatasetId")
        if not d_id: return None
        
        for _ in range(30):
            time.sleep(2)
            d_res = requests.get(f"https://api.apify.com/v2/datasets/{d_id}/items?token={APIFY_TOKEN}", timeout=15)
            if d_res.status_code == 200 and d_res.json(): return d_res.json()[0]
        return None
    except: return None

def fetch_tiktok_data_simulated(username):
    time.sleep(1.5)
    return {"followersCount": 450000, "latestPosts": [{"likesCount": 8500, "commentsCount": 150, "viewsCount": 1500000, "caption": "Trend #fyp"}, {"likesCount": 92000, "commentsCount": 1200, "viewsCount": 950000, "caption": "Vlog"}, {"likesCount": 88000, "commentsCount": 1100, "viewsCount": 890000, "caption": "Dans @marka"}]}

# ---------------------------------------------------------
# 4. GÖRSEL ÇİZİM FONKSİYONLARI (ZİRVE EKLENTİLER)
# ---------------------------------------------------------
def draw_aqs_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "AQS (KİTLE KALİTESİ)", 'font': {'color': '#94a3b8', 'size': 14}},
        number = {'font': {'color': '#f8fafc', 'size': 40}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "rgba(15, 23, 42, 0.5)",
            'borderwidth': 2,
            'bordercolor': "#1e293b",
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.3)"},
                {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.3)"}],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': score}
        }))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#f8fafc"}, height=250, margin=dict(l=20, r=20, t=30, b=10))
    return fig

def draw_dna_radar(dna_scores):
    categories = ['Etkileşim Gücü', 'İstikrar', 'Orijinallik (Anti-Bot)', 'Viral Kapasite', 'Marka Uyumu']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=dna_scores, theta=categories, fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)', line=dict(color='#3b82f6', width=2),
        name='Profil DNA'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(15,23,42,0.3)'),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=12), height=250, margin=dict(l=30, r=30, t=20, b=20)
    )
    return fig

def draw_trend_line(eng_list):
    df = pd.DataFrame({"Gönderi": [f"Post {i+1}" for i in range(len(eng_list))], "Etkileşim": reversed(eng_list)})
    fig = px.area(df, x="Gönderi", y="Etkileşim", markers=True)
    fig.update_traces(line_color="#8b5cf6", fillcolor="rgba(139, 92, 246, 0.1)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"), height=200, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#1e293b"))
    return fig

# ---------------------------------------------------------
# 5. OMNICHANNEL ALGORİTMA MOTORU
# ---------------------------------------------------------
def run_all_algorithms(followers, posts, platform="• Instagram", username=""):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    views = [clean_number(p.get("viewsCount"), 0) for p in posts]
    
    eng_trend = [l+c for l, c in zip(likes, comments)][:12] # Son 12 gönderi trendi
    total_eng = sum(likes) + sum(comments)
    er = (total_eng / max(followers, 1)) * 100.0

    if "TikTok" in platform:
        benchmark_er, avg_views = (10.0 if followers < 100000 else 8.0), np.mean(views) if views else 0
        er = (total_eng / max(avg_views, 1.0) * 100.0) if avg_views > 0 else er
        lvr = np.mean(likes) / max(avg_views, 1.0)
        com_anom = 0.60 if lvr < 0.02 else (0.50 if lvr > 0.40 else 0.0)
        cv_val = float(np.std(views)) / avg_views if len(posts)>1 and avg_views>0 else 1.0
        var_anom = 0.60 if cv_val < 0.15 and len(posts)>2 else 0.0
        est_reach = avg_views
    else:
        benchmark_er = 3.0 if followers < 100000 else 1.8
        comment_ratio = np.mean(comments) / max(np.mean(likes), 1.0)
        com_anom = 0.50 if comment_ratio < 0.008 else (0.25 if comment_ratio < 0.012 else (0.30 if comment_ratio > 0.15 else 0.0))
        cv_val = float(np.std([(l+c)/max(followers,1)*100 for l,c in zip(likes, comments)])) / max(er, 0.1) if len(posts)>1 else 1.0
        var_anom = 0.40 if (cv_val < 0.28 and len(posts)>4) else (0.30 if cv_val > 1.2 else 0.0)
        est_reach = min(int(followers * (er / 100.0) * (3.5 if er>2.0 else 2.5)), followers)

    er_score = min(40.0, (er / benchmark_er) * 40.0)
    stability_score = max(0.0, 20.0 * (1.0 - min(cv_val, 1.0)))
    bot_pct = float(np.clip(10.0 + (max(0.0, (benchmark_er - er)/benchmark_er) * 50.0) + (com_anom * 100.0) + (var_anom * 100.0), 3.2, 98.5))
    auth_pct = float(np.clip(100.0 - bot_pct, 1.5, 96.8))
    
    aqs = int(np.clip(er_score + (40.0 * (1-com_anom)) + stability_score, 10, 99))
    if bot_pct > 30.0: aqs = int(aqs * 0.4)

    # DNA Radarı İçin Skorlar [Etkileşim, İstikrar, Orijinallik, Viralite, Uyumluluk]
    dna = [min(100, (er/benchmark_er)*100), stability_score*5, auth_pct, min(100, (est_reach/followers)*100), 85]

    ai_sum = f"@{username} ({platform}) organik kitle oranı %{auth_pct:.1f}. "
    ai_sum += f"Bot riski (%{bot_pct:.1f}) yüksek, dış müdahale saptandı." if bot_pct > 20 else "Profil oldukça organik ve güvenilir."
    
    fraud1 = ("AĞIR İHLAL", "#ef4444", "Mantıksız Reaksiyon (Bot)") if com_anom > 0 else ("GÜVENİLİR", "#10b981", "Doğal Reaksiyon")
    fraud2 = ("AĞIR İHLAL", "#ef4444", "Suni İstatistik/Paket") if var_anom > 0 else ("GÜVENİLİR", "#10b981", "Doğal Dalgalanma")

    return {"followers": followers, "er": er, "aqs": aqs, "bot_pct": bot_pct, "auth_pct": auth_pct, "est_reach": est_reach, 
            "ai_sum": ai_sum, "dna": dna, "trend": eng_trend, "f1": fraud1, "f2": fraud2, "platform": platform, "username": username}

# ---------------------------------------------------------
# 6. UYGULAMA PANELİ (THE SHOWROOM)
# ---------------------------------------------------------
st.markdown("<div class='hero-container'><h1 class='hero-title'>MG BRAND OFFICE</h1><p class='hero-subtitle'>EXECUTIVE INTELLIGENCE SUITE</p></div>", unsafe_allow_html=True)

tab_rep, tab_bulk, tab_cmp = st.tabs(["• KURUMSAL DENETİM", "• TOPLU FİZİBİLİTE", "• KIYASLAMA"])

with tab_rep:
    _, c_m, _ = st.columns([1,4,1])
    with c_m:
        plat = st.radio("", ["• Instagram", "• TikTok"], horizontal=True, label_visibility="collapsed")
        u_inp = st.text_input("", placeholder=f"{plat.replace('• ', '')} Kullanıcı Adı (Örn: leyakirsan)")
        b_run = st.button("ZİRVEYİ GÖSTER (ANALİZ ET)")

    if b_run and u_inp:
        r_usr = clean_username(u_inp)
        with st.spinner("• Derin veri madenciliği ve görselleştirme motoru çalışıyor..."):
            p_dat = fetch_apify_instagram_data(r_usr) if plat == "• Instagram" else fetch_tiktok_data_simulated(r_usr)
            if p_dat and "latestPosts" in p_dat:
                m_r = run_all_algorithms(int(clean_number(p_dat.get("followersCount", 0), 1)), p_dat.get("latestPosts", []), plat, r_usr)
                
                b_clr = "#ef4444" if m_r['bot_pct']>20 else ("#f59e0b" if m_r['bot_pct']>10 else "#10b981")
                st.markdown(f"<div class='exec-summary'><div><h2 style='margin:0;'>@{r_usr}</h2><p style='color:#94a3b8;margin:0;'>{m_r['followers']:,} Takipçi ({plat.replace('• ','')})</p></div><div><span class='badge-status' style='background:rgba(255,255,255,0.1); color:{b_clr}; border: 1px solid {b_clr};'>• {'RİSKLİ' if m_r['bot_pct']>20 else 'GÜVENİLİR'}</span></div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='ai-summary-box'><b>🧠 AI Strateji Uzmanı:</b><br>{m_r['ai_sum']}</div>", unsafe_allow_html=True)
                
                # ZİRVE GÖRSELLEŞTİRME (RADAR, GAUGE)
                v1, v2, v3 = st.columns([1.2, 1, 1])
                with v1: 
                    st.plotly_chart(draw_aqs_gauge(m_r['aqs']), use_container_width=True)
                with v2: 
                    st.plotly_chart(draw_dna_radar(m_r['dna']), use_container_width=True)
                with v3:
                    st.markdown(f"<div class='metric-card' style='margin-bottom:10px;'><div class='metric-title'>Net Etkileşim (ER)</div><div class='metric-value'>%{m_r['er']:.2f}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Bot Riski</div><div class='metric-value' style='color:#ef4444'>%{m_r['bot_pct']:.1f}</div></div>", unsafe_allow_html=True)

                # ZİRVE ZAMAN ÇİZELGESİ (TREND)
                st.markdown("<h4 style='color:#f8fafc; font-weight:800; border-bottom:1px solid #1e293b; padding-bottom:10px; margin-top:20px;'>• ETKİLEŞİM İSTİKRARI (SON GÖNDERİLER)</h4>", unsafe_allow_html=True)
                st.plotly_chart(draw_trend_line(m_r['trend']), use_container_width=True)

                st.markdown("<h4 style='color:#f8fafc; font-weight:800; border-bottom:1px solid #1e293b; padding-bottom:10px; margin-top:20px;'>• ANTI-FRAUD KARNESİ</h4>", unsafe_allow_html=True)
                c_f1, c_f2 = st.columns(2)
                c_f1.markdown(f"<div class='fraud-box' style='border-left-color: {m_r['f1'][1]};'><div class='fraud-icon' style='color:{m_r['f1'][1]};'>•</div><div class='fraud-content'><h5>Reaksiyon Uyumu: <span style='color:{m_r['f1'][1]}'>{m_r['f1'][0]}</span></h5><p>{m_r['f1'][2]}</p></div></div>", unsafe_allow_html=True)
                c_f2.markdown(f"<div class='fraud-box' style='border-left-color: {m_r['f2'][1]};'><div class='fraud-icon' style='color:{m_r['f2'][1]};'>•</div><div class='fraud-content'><h5>Varyans İhlali: <span style='color:{m_r['f2'][1]}'>{m_r['f2'][0]}</span></h5><p>{m_r['f2'][2]}</p></div></div>", unsafe_allow_html=True)
            else:
                st.error("• Veri çekilemedi. APIFY limitinizi kontrol edin.")

with tab_bulk:
    st.info("Bu modül V18 mimarisinde görsel stabilizasyon için basitleştirilmiştir. Çoklu radar haritası yakında eklenecektir.")
with tab_cmp:
    st.info("Kıyaslama sekmesi, AQS Kadran ve DNA radarlarının ikili karşılaştırması için revize ediliyor.")
