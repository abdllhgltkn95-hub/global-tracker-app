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

# ---------------------------------------------------------
# 2. CSS STİLLERİ (BÜYÜTÜLMÜŞ FONTLAR & MAĞAZA LOGOLARI)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* SİMSİYAH (PITCH BLACK) ARKA PLAN VE GENEL BÜYÜTME */
    html, body, [data-testid="stAppViewContainer"], .stApp { 
        background-color: #000000 !important; 
        background-image: none !important; 
        background-attachment: fixed !important; 
        color: #e2e8f0 !important; 
        font-family: 'Inter', sans-serif !important; 
        font-size: 16px !important; 
    }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #e2e8f0 !important; }
    
    /* YANSIMASI KALDIRILMIŞ, DEĞİŞKEN EFEKTLİ DEV HERO BAŞLIK */
    .hero-container { text-align: center; padding: 50px 0 30px 0; margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .hero-title { 
        font-size: 5.5rem; 
        font-weight: 900; 
        background: linear-gradient(270deg, #3b82f6, #a855f7, #ec4899, #3b82f6); 
        background-size: 300% auto; 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        animation: gradient-glow 5s linear infinite; 
        margin: 0; 
        letter-spacing: -2px; 
    }
    .hero-subtitle { color: #94a3b8; font-size: 1.1rem; letter-spacing: 6px; font-weight: 800; text-transform: uppercase; margin-top: 10px;}
    
    @keyframes gradient-glow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* INPUT VE BUTONLAR (BÜYÜTÜLDÜ) */
    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 700px !important; width: 100% !important; margin: 0 auto 15px auto !important; }
    .stTextInput input, .stNumberInput input { background-color: rgba(20, 20, 20, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 10px !important; font-weight: 700 !important; padding: 18px 20px !important; font-size: 1.2rem !important; color: #ffffff !important; backdrop-filter: blur(10px); text-align: center; transition: 0.3s; }
    .stTextInput input:focus { border-color: #ffffff !important; box-shadow: 0 0 0 2px rgba(255,255,255,0.2) !important; }
    
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 400px !important; margin: 15px auto 0 auto !important; width: 100% !important; }
    .stButton>button { background: #ffffff !important; color: #000000 !important; border: none !important; border-radius: 10px !important; font-weight: 900 !important; font-size: 1.1rem !important; padding: 15px 30px !important; transition: 0.3s; letter-spacing: 1px;}
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(255, 255, 255, 0.25); }

    /* METRİK KARTLARI VE YAZILAR (BÜYÜTÜLDÜ) */
    .metric-card { background-color: rgba(15, 15, 15, 0.7); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 25px; text-align: center; height: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.5); backdrop-filter: blur(12px); transition: border 0.3s; }
    .metric-card:hover { border: 1px solid rgba(255, 255, 255, 0.15); }
    .metric-title { color: #94a3b8; font-size: 1rem; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 1px;}
    .metric-value { color: #ffffff; font-size: 2.4rem; font-weight: 900; margin: 0; text-shadow: 0 0 10px rgba(255,255,255,0.1); }
    .metric-sub { font-size: 0.9rem; margin-top: 5px; font-weight: 600; color: #64748b; }
    
    .exec-summary { background: linear-gradient(145deg, rgba(20, 20, 20, 0.9), rgba(5, 5, 5, 0.9)); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 30px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(15px); }
    .exec-summary h2 { font-size: 2.5rem !important; }
    .badge-status { padding: 8px 18px; border-radius: 8px; font-weight: 900; font-size: 1rem; color: #000000 !important; letter-spacing: 1px; }
    
    .ai-summary-box { background-color: rgba(15, 15, 15, 0.7); border-left: 5px solid #ffffff; border-radius: 10px; padding: 25px; margin-bottom: 30px; line-height: 1.8; color: #e2e8f0; font-size: 1.1rem; backdrop-filter: blur(12px); font-weight: 500;}
    .fraud-box { background-color: rgba(15, 15, 15, 0.7); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 15px; border-left-width: 5px; backdrop-filter: blur(12px);}
    .fraud-content h5 { font-size: 1.2rem !important; }
    .fraud-content p { font-size: 1rem !important; }
    
    .section-header { font-size: 1.4rem; font-weight: 900; color: #ffffff; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-top: 40px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px; }

    /* MAĞAZA LOGOLARI (APP STORE & PLAY STORE) */
    .store-footer {
        text-align: center;
        padding: 50px 0 30px 0;
        margin-top: 60px;
        border-top: 1px solid rgba(255,255,255,0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
    }
    .store-footer-text {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .store-badges {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    .store-badges img {
        height: 55px;
        cursor: pointer;
        transition: transform 0.2s, opacity 0.2s;
        opacity: 0.9;
    }
    .store-badges img:hover {
        transform: scale(1.05);
        opacity: 1;
    }
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
    return {"followersCount": 450000, "latestPosts": [{"likesCount": 8500, "commentsCount": 150, "viewsCount": 1500000, "caption": "Trend #fyp"}, {"likesCount": 92000, "commentsCount": 1200, "viewsCount": 950000, "caption": "Vlog"}, {"likesCount": 88000, "commentsCount": 1100, "viewsCount": 890000, "caption": "Dans @zara @trendyol"}]}

# ---------------------------------------------------------
# 4. GÖRSEL ÇİZİM FONKSİYONLARI 
# ---------------------------------------------------------
def draw_aqs_gauge(score):
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

def draw_dna_radar(dna_scores):
    categories = ['Etkileşim Gücü', 'İstikrar', 'Orijinallik (Anti-Bot)', 'Viral Kapasite', 'Marka Uyumu']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=dna_scores, theta=categories, fill='toself',
        fillcolor='rgba(255, 255, 255, 0.1)', line=dict(color='#ffffff', width=2), name='Profil DNA'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(15,15,15,0.5)'),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=14), height=320, margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

def draw_donut(labels, values, title, colors):
    fig = px.pie(values=values, names=labels, hole=0.7, color_discrete_sequence=colors)
    fig.update_layout(
        title=dict(text=title, font=dict(color="#ffffff", size=16), x=0.5, xanchor='center'),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
        font=dict(color="#94a3b8"), height=300, margin=dict(l=10, r=10, t=40, b=10), showlegend=False
    )
    fig.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
    return fig

def draw_bar(x, y, title, color):
    df = pd.DataFrame({"X": x, "Y": y})
    fig = px.bar(df, x="X", y="Y")
    fig.update_traces(marker_color=color, marker_line_color='#000000', marker_line_width=1.5)
    fig.update_layout(
        title=dict(text=title, font=dict(color="#ffffff", size=16), x=0.5, xanchor='center'),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
        font=dict(color="#94a3b8"), height=300, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title=None, yaxis_title=None, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    )
    return fig

def draw_trend_line(eng_list):
    df = pd.DataFrame({"Gönderi": [f"Post {i+1}" for i in range(len(eng_list))], "Etkileşim": reversed(eng_list)})
    fig = px.area(df, x="Gönderi", y="Etkileşim", markers=True)
    fig.update_traces(line_color="#ffffff", fillcolor="rgba(255, 255, 255, 0.05)")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"), 
        height=250, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    )
    return fig

# ---------------------------------------------------------
# 5. OMNICHANNEL ALGORİTMA MOTORU
# ---------------------------------------------------------
def run_all_algorithms(followers, posts, platform="• Instagram", budget=50000.0, username=""):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    views = [clean_number(p.get("viewsCount"), 0) for p in posts]
    
    eng_trend = [l+c for l, c in zip(likes, comments)][:15]
    total_likes = sum(likes)
    total_comments = sum(comments)
    total_eng = total_likes + total_comments
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

    dna = [min(100, (er/benchmark_er)*100), stability_score*5, auth_pct, min(100, (est_reach/followers)*100), 85]
    ai_sum = f"Sistem, @{username} ({platform}) profilini analiz etti. Kitle hacminin %{auth_pct:.1f}'lik kısmının tamamen organik reaksiyon verdiği hesaplanmıştır. "
    ai_sum += f"Ancak etkileşim anormallikleri sebebiyle %{bot_pct:.1f} oranında manipülasyon (bot) tespit edilmiştir. " if bot_pct > 20 else "Profil davranışları platform doğasına uygundur, suni müdahale izine rastlanmamıştır. "

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

    return {"followers": followers, "er": er, "aqs": aqs, "bot_pct": bot_pct, "auth_pct": auth_pct, "est_reach": est_reach, 
            "ai_sum": ai_sum, "dna": dna, "trend": eng_trend, "likes": total_likes, "comments": total_comments,
            "f1_desc": "Suni reaksiyon tespit edildi." if com_anom > 0 else "Doğal reaksiyon akışı.",
            "f2_desc": "Paket hizmet şüphesi." if var_anom > 0 else "İstikrarlı büyüme.",
            "gender": gender_data, "age": age_data, "mentions": top_mentions, "words": word_counts,
            "cpe": cpe, "cpm": cpm, "platform": platform, "username": username}

# ---------------------------------------------------------
# 6. UYGULAMA PANELİ
# ---------------------------------------------------------
st.markdown("""
<div class='hero-container'>
    <h1 class='hero-title'>MG BRAND OFFICE</h1>
    <p class='hero-subtitle'>EXECUTIVE INTELLIGENCE SUITE</p>
</div>
""", unsafe_allow_html=True)

_, c_m, _ = st.columns([1,4,1])
with c_m:
    plat = st.radio("", ["• Instagram", "• TikTok"], horizontal=True, label_visibility="collapsed")
    u_inp = st.text_input("", placeholder=f"{plat.replace('• ', '')} Hedef Profil (Örn: leyakirsan)")
    budget_inp = st.number_input("Planlanan Kampanya Bütçesi (₺)", min_value=1000, value=50000, step=5000)
    b_run = st.button("TÜM VERİLERİ ÇEK VE GÖRSELLEŞTİR")

if b_run and u_inp:
    r_usr = clean_username(u_inp)
    with st.spinner("• Derin veri madenciliği ve görselleştirme motoru çalışıyor... Lütfen bekleyin."):
        p_dat = fetch_apify_instagram_data(r_usr) if plat == "• Instagram" else fetch_tiktok_data_simulated(r_usr)
        if p_dat and "latestPosts" in p_dat:
            m_r = run_all_algorithms(int(clean_number(p_dat.get("followersCount", 0), 1)), p_dat.get("latestPosts", []), plat, budget_inp, r_usr)
            
            b_clr = "#ef4444" if m_r['bot_pct']>20 else ("#f59e0b" if m_r['bot_pct']>10 else "#10b981")
            
            # --- YÖNETİCİ ÖZETİ ---
            st.markdown(f"<div class='exec-summary'><div><h2 style='margin:0;'>@{r_usr}</h2><p style='color:#94a3b8;margin:0;font-size:1.1rem;'>{m_r['followers']:,} Takipçi ({plat.replace('• ','')})</p></div><div><span class='badge-status' style='background:{b_clr}; color:#000000; border: none;'>• {'RİSKLİ' if m_r['bot_pct']>20 else 'GÜVENİLİR'}</span></div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ai-summary-box'><b>🧠 AI Strateji Uzmanı:</b><br>{m_r['ai_sum']}</div>", unsafe_allow_html=True)
            
            # --- 1. SATIR: CORE DNA (GAUGE, RADAR, DONUT) ---
            st.markdown("<div class='section-header'>• SİSTEM SKORLAMASI VE KİTLE SAFLIĞI</div>", unsafe_allow_html=True)
            v1, v2, v3 = st.columns(3)
            with v1: st.plotly_chart(draw_aqs_gauge(m_r['aqs']), use_container_width=True)
            with v2: st.plotly_chart(draw_dna_radar(m_r['dna']), use_container_width=True)
            with v3: st.plotly_chart(draw_donut(["Organik Kitle", "Sentetik/Bot"], [m_r['auth_pct'], m_r['bot_pct']], "Kitle Sağlığı", ["#ffffff", "#ef4444"]), use_container_width=True)

            # --- 2. SATIR: ETKİLEŞİM DİNAMİKLERİ ---
            st.markdown("<div class='section-header'>• ETKİLEŞİM DİNAMİKLERİ VE TREND</div>", unsafe_allow_html=True)
            t1, t2 = st.columns([2, 1])
            with t1:
                st.markdown("<div style='text-align:center; color:#94a3b8; font-weight:800; font-size:16px; margin-bottom:10px;'>SON GÖNDERİ PERFORMANSLARI</div>", unsafe_allow_html=True)
                st.plotly_chart(draw_trend_line(m_r['trend']), use_container_width=True)
            with t2:
                st.plotly_chart(draw_donut(["Beğeni", "Yorum"], [m_r['likes'], m_r['comments']], "Reaksiyon Dağılımı", ["#8b5cf6", "#ec4899"]), use_container_width=True)

            # --- 3. SATIR: DEMOGRAFİ VE NLP ---
            st.markdown("<div class='section-header'>• DEMOGRAFİ VE İÇERİK ANALİZİ</div>", unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            with d1: st.plotly_chart(draw_bar(list(m_r['age'].keys()), list(m_r['age'].values()), "Yaş Dağılımı", "#ffffff"), use_container_width=True)
            with d2: st.plotly_chart(draw_donut(list(m_r['gender'].keys()), list(m_r['gender'].values()), "Cinsiyet", ["#ec4899", "#3b82f6"]), use_container_width=True)
            with d3:
                if m_r['words']:
                    w_labels = [w[0] for w in m_r['words']]
                    w_vals = [w[1] for w in m_r['words']]
                    st.plotly_chart(draw_bar(w_labels, w_vals, "Sık Kullanılan Kelimeler", "#a855f7"), use_container_width=True)
                else:
                    st.markdown("<div class='metric-card' style='height:300px; display:flex; align-items:center; justify-content:center;'><p style='color:#64748b; font-size:1.1rem;'>Kelime Verisi Yok</p></div>", unsafe_allow_html=True)

            # --- 4. SATIR: FİNANS & AFİNİTE ---
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

            # --- 5. SATIR: ANTI-FRAUD UYARILARI ---
            st.markdown("<div class='section-header'>• ANTI-FRAUD (SAHTEKARLIK) KARNESİ</div>", unsafe_allow_html=True)
            a1, a2 = st.columns(2)
            c1_col = "#ef4444" if m_r['bot_pct'] > 20 else "#10b981"
            a1.markdown(f"<div class='fraud-box' style='border-left-color: {c1_col};'><div class='fraud-icon' style='color:{c1_col};'>•</div><div class='fraud-content'><h5>Reaksiyon Uyumu</h5><p>{m_r['f1_desc']}</p></div></div>", unsafe_allow_html=True)
            a2.markdown(f"<div class='fraud-box' style='border-left-color: {c1_col};'><div class='fraud-icon' style='color:{c1_col};'>•</div><div class='fraud-content'><h5>İstatistiksel İstikrar</h5><p>{m_r['f2_desc']}</p></div></div>", unsafe_allow_html=True)

        else:
            st.error("• Veri çekilemedi. APIFY limitinizi kontrol edin veya profilin açık olduğundan emin olun.")

# ---------------------------------------------------------
# 7. MAĞAZA LOGOLARI (APP STORE & GOOGLE PLAY)
# ---------------------------------------------------------
st.markdown("""
<div class="store-footer">
    <div class="store-footer-text">Mobil Uygulamamızı İndirin</div>
    <div class="store-badges">
        <a href="#" target="_blank"><img src="https://developer.apple.com/app-store/marketing/guidelines/images/badge-download-on-the-app-store.svg" alt="Download on the App Store"></a>
        <a href="#" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/7/78/Google_Play_Store_badge_EN.svg" alt="Get it on Google Play"></a>
    </div>
</div>
""", unsafe_allow_html=True)
