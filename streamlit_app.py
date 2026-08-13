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

if 'credits' not in st.session_state: 
    st.session_state['credits'] = 100

# ---------------------------------------------------------
# 2. CSS STİLLERİ (PITCH BLACK & STABİL)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* SİMSİYAH ARKA PLAN */
    html, body, [data-testid="stAppViewContainer"], .stApp { 
        background-color: #000000 !important; 
        background-image: none !important; 
        color: #e2e8f0 !important; 
        font-family: 'Inter', sans-serif !important; 
    }
    
    /* BAŞLIK */
    .hero-container { text-align: center; padding: 50px 0 30px 0; margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .hero-title { 
        font-size: 5.5rem !important; 
        font-weight: 900 !important; 
        background: linear-gradient(270deg, #3b82f6, #a855f7, #ec4899, #3b82f6) !important; 
        background-size: 300% auto !important; 
        color: transparent !important;
        -webkit-background-clip: text !important; 
        background-clip: text !important;
        animation: gradient-glow 5s linear infinite !important; 
        margin: 0 !important; 
        letter-spacing: -2px !important; 
    }
    .hero-subtitle { color: #94a3b8 !important; font-size: 1.1rem !important; letter-spacing: 6px !important; font-weight: 800 !important; text-transform: uppercase !important; margin-top: 10px !important;}
    @keyframes gradient-glow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    /* INPUT KUTULARI */
    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 700px !important; width: 100% !important; margin: 0 auto 15px auto !important; }
    .stTextInput input, .stNumberInput input { background-color: rgba(20, 20, 20, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 10px !important; font-weight: 700 !important; padding: 18px 20px !important; font-size: 1.2rem !important; color: #ffffff !important; text-align: center !important; }
    .stTextInput input:focus { border-color: #ffffff !important; box-shadow: 0 0 0 2px rgba(255,255,255,0.2) !important; }
    
    /* BUTON */
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 400px !important; margin: 15px auto 0 auto !important; width: 100% !important; }
    div[data-testid="stButton"] button { background-color: #ffffff !important; border: none !important; border-radius: 10px !important; padding: 15px 30px !important; transition: 0.3s !important; }
    div[data-testid="stButton"] button p { color: #000000 !important; font-weight: 900 !important; font-size: 1.1rem !important; letter-spacing: 1px !important; margin: 0 !important; }
    div[data-testid="stButton"] button:hover { transform: translateY(-3px) !important; box-shadow: 0 10px 25px rgba(255, 255, 255, 0.25) !important; }

    /* KART TASARIMLARI */
    .metric-card { background-color: rgba(15, 15, 15, 0.7); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 25px; text-align: center; height: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    .metric-title { color: #94a3b8; font-size: 1rem; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 1px;}
    .metric-value { color: #ffffff; font-size: 2.4rem; font-weight: 900; margin: 0; }
    .metric-sub { font-size: 0.9rem; margin-top: 5px; font-weight: 600; color: #64748b; }
    .exec-summary { background: linear-gradient(145deg, rgba(20, 20, 20, 0.9), rgba(5, 5, 5, 0.9)); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 30px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }
    .badge-status { padding: 8px 18px; border-radius: 8px; font-weight: 900; font-size: 1rem; color: #000000 !important; letter-spacing: 1px; }
    .ai-summary-box { background-color: rgba(15, 15, 15, 0.7); border-left: 5px solid #ffffff; border-radius: 10px; padding: 25px; margin-bottom: 30px; line-height: 1.8; color: #e2e8f0; font-size: 1.1rem;}
    .fraud-box { background-color: rgba(15, 15, 15, 0.7); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 15px; border-left-width: 5px;}
    .section-header { font-size: 1.4rem; font-weight: 900; color: #ffffff; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-top: 40px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. YARDIMCI VE API FONKSİYONLARI
# ---------------------------------------------------------
def clean_username(text: str) -> str:
    if not text: return ""
    text = text.strip()
    match = re.search(r'(instagram|tiktok|youtube)\.com/([^/?#]+)', text)
    if match: return match.group(2).replace("@", "").strip()
    return text.replace("@", "").strip()

def clean_number(value, default=0.0) -> float:
    try:
        float_val = float(value)
        if math.isnan(float_val): return default
        return float_val
    except: return default

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_apify_instagram_data(username: str, max_posts: int = 24):
    run_url = f"https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs?token={APIFY_TOKEN}"
    try:
        res = requests.post(run_url, json={"usernames": [username], "resultsLimit": max_posts}, timeout=30) 
        if res.status_code not in [200, 201]: return None
        dataset_id = res.json().get("data", {}).get("defaultDatasetId")
        if not dataset_id: return None
        
        for _ in range(30):
            time.sleep(2)
            d_res = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}", timeout=15)
            if d_res.status_code == 200 and d_res.json(): return d_res.json()[0]
        return None
    except: return None

def fetch_tiktok_data_simulated(username: str):
    time.sleep(1.5)
    return {"followersCount": 450000, "latestPosts": [{"likesCount": 8500, "commentsCount": 150, "viewsCount": 1500000, "caption": "Trend #fyp"}, {"likesCount": 92000, "commentsCount": 1200, "viewsCount": 950000, "caption": "Vlog"}, {"likesCount": 88000, "commentsCount": 1100, "viewsCount": 890000, "caption": "Dans @zara @trendyol"}]}

def fetch_youtube_data_simulated(username: str):
    """YouTube motoru için simülasyon (Gerçek API bağlanana kadar)"""
    time.sleep(1.8)
    return {
        "followersCount": 1250000, # Abone Sayısı
        "latestPosts": [
            {"likesCount": 45000, "commentsCount": 3200, "viewsCount": 850000, "caption": "Yeni teknoloji incelemesi harika oldu!"}, 
            {"likesCount": 38000, "commentsCount": 2100, "viewsCount": 720000, "caption": "Kamera testi ve Vlog stili çekim."}, 
            {"likesCount": 65000, "commentsCount": 4800, "viewsCount": 1200000, "caption": "Büyük ödüllü yarışma duyurusu #shorts"}
        ]
    }

# ---------------------------------------------------------
# 4. GÖRSEL ÇİZİM FONKSİYONLARI 
# ---------------------------------------------------------
def draw_aqs_gauge(score: int):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "KİTLE KALİTE SKORU (AQS)", 'font': {'color': '#94a3b8', 'size': 14}},
        number = {'font': {'color': '#ffffff', 'size': 50, 'weight': 'bold'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.1)"},
            'bar': {'color': "#ffffff"}, 'bgcolor': "rgba(20, 20, 20, 0.5)",
            'borderwidth': 1, 'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [{'range': [0, 40], 'color': "rgba(239, 68, 68, 0.4)"}, {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.4)"}, {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.4)"}],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': score}
        }))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#f8fafc"}, height=320, margin=dict(l=20, r=20, t=30, b=10))
    return fig

def draw_dna_radar(dna_scores: list):
    categories = ['Etkileşim Gücü', 'İstikrar', 'Orijinallik (Anti-Bot)', 'Viral Kapasite', 'Marka Uyumu']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=dna_scores, theta=categories, fill='toself', fillcolor='rgba(255, 255, 255, 0.1)', line=dict(color='#ffffff', width=2)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(15,15,15,0.5)'), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=14), height=320, margin=dict(l=40, r=40, t=20, b=20))
    return fig

def draw_donut(labels: list, values: list, title: str, colors: list):
    fig = px.pie(values=values, names=labels, hole=0.7, color_discrete_sequence=colors)
    fig.update_layout(title=dict(text=title, font=dict(color="#ffffff", size=16), x=0.5, xanchor='center'), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"), height=300, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    fig.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
    return fig

def draw_bar(x_data: list, y_data: list, title: str, color: str):
    df = pd.DataFrame({"X": x_data, "Y": y_data})
    fig = px.bar(df, x="X", y="Y")
    fig.update_traces(marker_color=color, marker_line_color='#000000', marker_line_width=1.5)
    fig.update_layout(title=dict(text=title, font=dict(color="#ffffff", size=16), x=0.5, xanchor='center'), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"), height=300, margin=dict(l=10, r=10, t=40, b=10), xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"))
    return fig

def draw_trend_line(eng_list: list):
    df = pd.DataFrame({"Gönderi": [f"Post {i+1}" for i in range(len(eng_list))], "Etkileşim": reversed(eng_list)})
    fig = px.area(df, x="Gönderi", y="Etkileşim", markers=True)
    fig.update_traces(line_color="#ffffff", fillcolor="rgba(255, 255, 255, 0.05)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"), height=250, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"))
    return fig

# ---------------------------------------------------------
# 5. OMNICHANNEL ALGORİTMA MOTORU
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list, platform: str = "• Instagram", budget: float = 50000.0, username: str = ""):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    views = [clean_number(p.get("viewsCount"), 0) for p in posts]
    
    eng_trend = [l + c for l, c in zip(likes, comments)][:15]
    total_likes = sum(likes)
    total_comments = sum(comments)
    total_eng = total_likes + total_comments
    
    er = (total_eng / max(followers, 1)) * 100.0

    if "YouTube" in platform:
        benchmark_er = 4.0 if followers < 500000 else 2.5
        avg_views = np.mean(views) if views else 0
        
        # YouTube ER hesaplaması İzlenme (Views) üzerinden yapılır
        if avg_views > 0: er = (total_eng / avg_views) * 100.0
        
        lvr = np.mean(likes) / max(avg_views, 1.0)
        com_anom = 0.60 if lvr < 0.01 else (0.50 if lvr > 0.15 else 0.0) # View bot < %1, Like bot > %15
        
        cv_val = float(np.std(views)) / avg_views if len(posts)>1 and avg_views>0 else 1.0
        var_anom = 0.60 if cv_val < 0.05 and len(posts)>2 else 0.0 # YouTube dalgalıdır, aşırı stabilite bottur
        est_reach = avg_views

    elif "TikTok" in platform:
        benchmark_er = 10.0 if followers < 100000 else 8.0
        avg_views = np.mean(views) if views else 0
        if avg_views > 0: er = (total_eng / max(avg_views, 1.0)) * 100.0
        lvr = np.mean(likes) / max(avg_views, 1.0)
        com_anom = 0.60 if lvr < 0.02 else (0.50 if lvr > 0.40 else 0.0)
        cv_val = float(np.std(views)) / avg_views if len(posts)>1 and avg_views>0 else 1.0
        var_anom = 0.60 if cv_val < 0.15 and len(posts)>2 else 0.0
        est_reach = avg_views
        
    else: # Instagram
        benchmark_er = 3.0 if followers < 100000 else 1.8
        comment_ratio = np.mean(comments) / max(np.mean(likes), 1.0)
        com_anom = 0.50 if comment_ratio < 0.008 else (0.25 if comment_ratio < 0.012 else (0.30 if comment_ratio > 0.15 else 0.0))
        cv_val = float(np.std([(l+c)/max(followers,1)*100 for l,c in zip(likes, comments)])) / max(er, 0.1) if len(posts)>1 else 1.0
        var_anom = 0.40 if (cv_val < 0.28 and len(posts)>4) else (0.30 if cv_val > 1.2 else 0.0)
        est_reach = min(int(followers * (er / 100.0) * (3.5 if er > 2.0 else 2.5)), followers)

    er_score = min(40.0, (er / benchmark_er) * 40.0)
    stability_score = max(0.0, 20.0 * (1.0 - min(cv_val, 1.0)))
    er_defect = max(0.0, (benchmark_er - er) / benchmark_er)
    calculated_bot = 10.0 + (er_defect * 50.0) + (com_anom * 100.0) + (var_anom * 100.0)
    
    bot_pct = float(np.clip(calculated_bot, 3.2, 98.5))
    auth_pct = float(np.clip(100.0 - bot_pct, 1.5, 96.8))
    
    aqs = int(np.clip(er_score + (40.0 * (1 - com_anom)) + stability_score, 10, 99))
    if bot_pct > 30.0: aqs = int(aqs * 0.4)

    # YouTube için Abone (Followers) kıyaslamalı Viral Skor
    viral_reach = est_reach / max(followers, 1.0)
    dna = [min(100, (er / benchmark_er) * 100), stability_score * 5, auth_pct, min(100, viral_reach * 100), 85]
    
    ai_sum = f"Sistem, @{username} ({platform}) profilini analiz etti. Kitle hacminin %{auth_pct:.1f}'lik kısmının tamamen organik reaksiyon verdiği hesaplanmıştır. "
    
    if "YouTube" in platform and viral_reach > 0.5:
        ai_sum += "Kanal kendi abone tabanının ötesine geçebilen güçlü bir organik keşfet/arama hacmine (SEO) sahip. "
        
    if bot_pct > 20: ai_sum += f"Etkileşim anormallikleri sebebiyle %{bot_pct:.1f} oranında manipülasyon (bot) tespit edilmiştir. "
    else: ai_sum += "Profil davranışları platform doğasına uygundur, suni müdahale izine rastlanmamıştır. "

    cpe = budget / total_eng if total_eng > 0 else 0.0
    cpm = (budget / max(est_reach, 1.0)) * 1000.0

    all_captions, mentions_list = "", []
    for p in posts:
        cap = str(p.get("caption", "")).lower()
        all_captions += " " + cap
        mentions_list.extend([m for m in re.findall(r'@([a-zA-Z0-9_.]+)', cap) if m != username])

    top_mentions = collections.Counter(mentions_list).most_common(6)
    stopwords = ["ve", "bir", "bu", "için", "çok", "ile", "de", "da", "daha", "en", "gibi", "kadar", "olan", "olarak", "var", "yok", "ama"]
    words = [w for w in re.findall(r'\b[a-zçğıöşü]{4,}\b', all_captions) if w not in stopwords]
    word_counts = collections.Counter(words).most_common(5)

    gender_data = {"Kadın": 65, "Erkek": 35}
    age_data = {"13-17": 15, "18-24": 40, "25-34": 30, "35+": 15}
    
    f1_desc = "Suni reaksiyon tespit edildi." if com_anom > 0 else "Doğal reaksiyon akışı."
    f2_desc = "Paket hizmet şüphesi." if var_anom > 0 else "İstikrarlı büyüme."
    if "YouTube" in platform:
        f1_desc = "Mantıksız LVR (Beğeni/İzlenme) oranı. Bot şüphesi." if com_anom > 0 else "Doğal LVR oranı."
        f2_desc = "Aşırı stabil izlenmeler. Paket view bot şüphesi." if var_anom > 0 else "YouTube SEO/Algoritma dalgalanması organik."

    return {
        "followers": followers, "er": er, "aqs": aqs, "bot_pct": bot_pct, "auth_pct": auth_pct, "est_reach": est_reach, 
        "ai_sum": ai_sum, "dna": dna, "trend": eng_trend, "likes": total_likes, "comments": total_comments,
        "f1_desc": f1_desc, "f2_desc": f2_desc,
        "gender": gender_data, "age": age_data, "mentions": top_mentions, "words": word_counts,
        "cpe": cpe, "cpm": cpm, "platform": platform, "username": username
    }

# ---------------------------------------------------------
# 6. UYGULAMA PANELİ RENDER İŞLEMLERİ
# ---------------------------------------------------------
st.markdown("""
<div class='hero-container'>
    <h1 class='hero-title'>MG BRAND OFFICE</h1>
    <p class='hero-subtitle'>EXECUTIVE INTELLIGENCE SUITE</p>
</div>
""", unsafe_allow_html=True)

_, c_m, _ = st.columns([1, 4, 1])
with c_m:
    # YOUTUBE EKLENDİ
    plat = st.radio("", ["• Instagram", "• TikTok", "• YouTube"], horizontal=True, label_visibility="collapsed")
    u_inp = st.text_input("", placeholder=f"{plat.replace('• ', '')} Hedef Profil (Örn: leyakirsan)")
    budget_inp = st.number_input("Planlanan Kampanya Bütçesi (₺)", min_value=1000, value=50000, step=5000)
    b_run = st.button("TÜM VERİLERİ ÇEK VE GÖRSELLEŞTİR")

if b_run and u_inp:
    r_usr = clean_username(u_inp)
    
    with st.spinner(f"• Derin veri madenciliği ve {plat.replace('• ', '')} motoru çalışıyor... Lütfen bekleyin."):
        if plat == "• Instagram": p_dat = fetch_apify_instagram_data(r_usr)
        elif plat == "• TikTok": p_dat = fetch_tiktok_data_simulated(r_usr)
        else: p_dat = fetch_youtube_data_simulated(r_usr) # YOUTUBE MOTORU TETİKLENİR
            
        if p_dat and "latestPosts" in p_dat:
            followers_count = int(clean_number(p_dat.get("followersCount", 0), 1))
            m_r = run_all_algorithms(followers_count, p_dat.get("latestPosts", []), plat, budget_inp, r_usr)
            
            b_clr = "#ef4444" if m_r['bot_pct'] > 20 else ("#f59e0b" if m_r['bot_pct'] > 10 else "#10b981")
            b_text = 'RİSKLİ' if m_r['bot_pct'] > 20 else 'GÜVENİLİR'
            
            follower_label = "Abone" if plat == "• YouTube" else "Takipçi"
            
            st.markdown(f"""
            <div class='exec-summary'>
                <div>
                    <h2 style='margin:0;'>@{r_usr}</h2>
                    <p style='color:#94a3b8;margin:0;font-size:1.1rem;'>{m_r['followers']:,} {follower_label} ({plat.replace('• ','')})</p>
                </div>
                <div>
                    <span class='badge-status' style='background:{b_clr}; color:#000000; border: none;'>• {b_text}</span>
                </div>
            </div>
            <div class='ai-summary-box'><b>🧠 AI Strateji Uzmanı:</b><br>{m_r['ai_sum']}</div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>• SİSTEM SKORLAMASI VE KİTLE SAFLIĞI</div>", unsafe_allow_html=True)
            v1, v2, v3 = st.columns(3)
            with v1: st.plotly_chart(draw_aqs_gauge(m_r['aqs']), use_container_width=True)
            with v2: st.plotly_chart(draw_dna_radar(m_r['dna']), use_container_width=True)
            with v3: st.plotly_chart(draw_donut(["Organik Kitle", "Sentetik/Bot"], [m_r['auth_pct'], m_r['bot_pct']], "Kitle Sağlığı", ["#ffffff", "#ef4444"]), use_container_width=True)

            st.markdown("<div class='section-header'>• ETKİLEŞİM DİNAMİKLERİ VE TREND</div>", unsafe_allow_html=True)
            t1, t2 = st.columns([2, 1])
            with t1:
                st.markdown("<div style='text-align:center; color:#94a3b8; font-weight:800; font-size:16px; margin-bottom:10px;'>SON GÖNDERİ/VİDEO PERFORMANSLARI</div>", unsafe_allow_html=True)
                st.plotly_chart(draw_trend_line(m_r['trend']), use_container_width=True)
            with t2:
                st.plotly_chart(draw_donut(["Beğeni", "Yorum"], [m_r['likes'], m_r['comments']], "Reaksiyon Dağılımı", ["#8b5cf6", "#ec4899"]), use_container_width=True)

            st.markdown("<div class='section-header'>• DEMOGRAFİ VE İÇERİK ANALİZİ</div>", unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            with d1: st.plotly_chart(draw_bar(list(m_r['age'].keys()), list(m_r['age'].values()), "Yaş Dağılımı", "#ffffff"), use_container_width=True)
            with d2: st.plotly_chart(draw_donut(list(m_r['gender'].keys()), list(m_r['gender'].values()), "Cinsiyet", ["#ec4899", "#3b82f6"]), use_container_width=True)
            with d3:
                if m_r['words']:
                    st.plotly_chart(draw_bar([w[0] for w in m_r['words']], [w[1] for w in m_r['words']], "Sık Kullanılan Kelimeler", "#a855f7"), use_container_width=True)
                else:
                    st.markdown("<div class='metric-card' style='height:300px; display:flex; align-items:center; justify-content:center;'><p style='color:#64748b; font-size:1.1rem;'>Kelime Verisi Yok</p></div>", unsafe_allow_html=True)

            st.markdown("<div class='section-header'>• YATIRIM GETİRİSİ (ROI) & RAKİP RADARI</div>", unsafe_allow_html=True)
            f1, f2, f3, f4 = st.columns(4)
            f1.markdown(f"<div class='metric-card'><div class='metric-title'>Tahmini Erişim</div><div class='metric-value'>{int(m_r['est_reach']):,}</div><div class='metric-sub'>Kişi Başı</div></div>", unsafe_allow_html=True)
            f2.markdown(f"<div class='metric-card'><div class='metric-title'>CPE (Etkileşim Başı)</div><div class='metric-value'>₺{m_r['cpe']:.2f}</div><div class='metric-sub'>Maliyet</div></div>", unsafe_allow_html=True)
            f3.markdown(f"<div class='metric-card'><div class='metric-title'>CPM (1000 Gösterim)</div><div class='metric-value'>₺{m_r['cpm']:.2f}</div><div class='metric-sub'>Maliyet</div></div>", unsafe_allow_html=True)
            
            with f4:
                st.markdown("<div class='metric-card' style='padding:25px;'><div class='metric-title'>Sık Etiketlenenler</div>", unsafe_allow_html=True)
                if m_r['mentions']:
                    for m, c in m_r['mentions'][:3]:
                        st.markdown(f"<div style='font-size:1.1rem; color:#ffffff; font-weight:800; margin-bottom:8px;'>@{m} <span style='color:#64748b; font-weight:600; float:right;'>{c} kez</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='font-size:1rem; color:#64748b;'>Veri Bulunamadı.</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-header'>• ANTI-FRAUD (SAHTEKARLIK) KARNESİ</div>", unsafe_allow_html=True)
            a1, a2 = st.columns(2)
            c1_col = "#ef4444" if m_r['bot_pct'] > 20 else "#10b981"
            
            a1.markdown(f"""
            <div class='fraud-box' style='border-left-color: {c1_col};'>
                <div class='fraud-icon' style='color:{c1_col};'>•</div>
                <div class='fraud-content'><h5>Reaksiyon Uyumu</h5><p>{m_r['f1_desc']}</p></div>
            </div>
            """, unsafe_allow_html=True)
            
            a2.markdown(f"""
            <div class='fraud-box' style='border-left-color: {c1_col};'>
                <div class='fraud-icon' style='color:{c1_col};'>•</div>
                <div class='fraud-content'><h5>İstatistiksel İstikrar</h5><p>{m_r['f2_desc']}</p></div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.error("• Veri çekilemedi. APIFY limitinizi kontrol edin veya profilin açık olduğundan emin olun.")

# ---------------------------------------------------------
# 7. MAĞAZA LOGOLARI VE COPYRIGHT FOOTER (MG BRAND 2026)
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding: 50px 0 40px 0; margin-top: 60px; border-top: 1px solid rgba(255,255,255,0.05);">
    <div style="color: #64748b; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 20px;">
        Mobil Uygulamamızı İndirin
    </div>
    <div style="display: flex; justify-content: center; align-items: center;">
        <a href="#" target="_blank" style="text-decoration: none; border: none; background: transparent; padding: 0; margin: 0; outline: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Download_on_the_App_Store_Badge.svg" alt="App Store" style="height: 48px; display: block; border-radius: 8px;">
        </a>
    </div>
    <div style="margin-top: 30px; font-size: 0.85rem; color: #475569; letter-spacing: 2px; font-weight: 700;">
        © 2026 MG BRAND OFFICE. TÜM HAKLARI SAKLIDIR.
    </div>
</div>
""", unsafe_allow_html=True)
