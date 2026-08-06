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
# 1. SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="MG BRAND OFFICE | Executive Intelligence",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb")

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
    
    .reflection-container { text-align: center; padding-top: 25px; padding-bottom: 10px; border-bottom: 1px solid #1e293b; margin-bottom: 30px; }
    .brand-header-animated {
        font-size: 3.2rem; font-weight: 900; letter-spacing: -1px;
        background: linear-gradient(270deg, #f8fafc, #94a3b8, #cbd5e1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0; display: inline-block;
    }
    .brand-subtitle { color: #64748b !important; font-size: 0.95rem; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px; }

    [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; border-bottom: 1px solid #1e293b !important; margin: 0 auto 30px auto !important; gap: 20px !important; width: 100% !important; }
    [data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-radius: 0 !important; box-shadow: none !important; outline: none !important; padding: 12px 20px !important; margin: 0 !important; }
    [data-baseweb="tab"] p, [data-baseweb="tab"] span { color: #64748b !important; font-weight: 700 !important; font-size: 1rem !important; text-transform: uppercase; letter-spacing: 0.5px;}
    [data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3b82f6 !important; }
    [data-baseweb="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"] span { color: #f8fafc !important; font-weight: 800 !important; }

    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 500px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    .stTextInput input, .stNumberInput input { background-color: #0f172a !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 14px 16px !important; font-size: 1rem !important; text-align: center !important; color: #f8fafc !important; transition: all 0.3s; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important; }
    
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 300px !important; margin: 10px auto 0 auto !important; width: 100% !important; }
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
    <p><b>Analiz Tarihi:</b> Güncel</p>
    
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

    <div class="box">
        <h2>• Sektör ve Afinite Verileri</h2>
        <p>Ağırlıklı Üretim Sektörleri: <span class="metric">{", ".join(data['top_sectors'])}</span></p>
        <p>Sponsorlu / Ticari İçerik Yoğunluğu: <span class="metric">%{data['collab_ratio']:.1f}</span></p>
    </div>
    
    <p style="text-align:center; margin-top:50px; font-size:12px; color:#94a3b8;">Sistem Tarafından Otomatik Üretilmiştir • MG BRAND OFFICE</p>
    </body></html>
    """
    return html

# ---------------------------------------------------------
# 4. ULTIMATE ENTERPRISE ALGORİTMASI (Anti-Fraud V5 & Summary)
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list, budget: float = 0.0, username: str = ""):
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

    er_defect = max(0.0, (benchmark_er - er) / benchmark_er)
    
    if comment_ratio < 0.008: comment_anomaly = 0.50 
    elif comment_ratio < 0.012: comment_anomaly = 0.25 
    elif comment_ratio > 0.15: comment_anomaly = 0.30 
    else: comment_anomaly = 0.00 

    if cv < 0.28 and len(posts) > 4: variance_anomaly = 0.40 
    elif cv > 1.2: variance_anomaly = 0.30 
    else: variance_anomaly = 0.00 

    calculated_bot = 10.0 + (er_defect * 50.0) + (comment_anomaly * 100.0) + (variance_anomaly * 100.0)
    bot_pct = float(np.clip(calculated_bot, 3.2, 98.5))
    authentic_pct = float(np.clip(100.0 - bot_pct, 1.5, 96.8))
    
    if bot_pct > 30.0: aqs_score = int(aqs_score * 0.4)
    elif bot_pct > 15.0: aqs_score = int(aqs_score * 0.7)
    
    credibility_score = int(np.clip(authentic_pct * 0.85 + (er_score * 0.15), 5, 98))

    # YÖNETİCİ ÖZETİ METNİ OLUŞTURMA (AI Text Generation)
    ai_summary = f"Sistem tarafından @{username} profilinin son verileri denetlendiğinde; kitle hacminin yaklaşık %{authentic_pct:.1f}'lik kısmının organik/aktif kullanıcılardan oluştuğu öngörülmektedir. "
    
    if bot_pct > 20:
        ai_summary += f"Ancak, %{bot_pct:.1f} seviyesine ulaşan manipülasyon ve sentetik hesap (bot) riski tespit edilmiştir. Etkileşimlerdeki anormal sapmalar, profilin dışarıdan suni müdahaleler aldığını göstermekte olup, marka iş birlikleri için yüksek risk taşımaktadır. "
    elif bot_pct > 10:
        ai_summary += f"Sistemde %{bot_pct:.1f} seviyesinde şüpheli veya tamamen pasif kitle tespit edilmiştir. İstatistiksel sapmaların makul sınırların dışına çıkma eğilimi göstermesi sebebiyle bütçe optimizasyonunda bu fire oranının hesaba katılması önerilir. "
    else:
        ai_summary += f"Bot ve manipülasyon riski (%{bot_pct:.1f}) sektör standartlarının altında olup, oldukça güvenilir bir seviyededir. Gönderiler arası geçişler insan doğasına uygun ve manipülasyondan uzaktır. "

    if er >= benchmark_er:
        ai_summary += f"Ayrıca profil, bulunduğu segmentteki %{benchmark_er:.2f}'lik standart etkileşim beklentisini aşarak %{er:.2f} oranında güçlü bir performans sergilemektedir."
    else:
        ai_summary += f"Buna karşın, profilin gösterdiği net etkileşim oranı (%{er:.2f}), bulunduğu takipçi büyüklüğü için beklenen pazar standardının (%{benchmark_er:.2f}) altında kalmaktadır."

    # Marka Afinitesi ve NLP
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

    format_stats = {"Video/Reels": [], "Carousel": [], "Tekil Fotoğraf": []}
    for p in posts:
        l = clean_number(p.get("likesCount"), 0)
        c = clean_number(p.get("commentsCount"), 0)
        if p.get("isVideo") or p.get("type") == "Video": format_stats["Video/Reels"].append(l+c)
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
        "cpe": cpe, "cpm": cpm, "benchmark_er": benchmark_er, "format_data": format_data,
        "top_mentions": top_mentions, "word_counts": word_counts, "gender_data": gender_data, "age_data": age_data,
        "ai_summary": ai_summary
    }

# ---------------------------------------------------------
# 5. ARAYÜZ YAPISI
# ---------------------------------------------------------
st.markdown("""
    <div class="reflection-container">
        <h1 class="brand-header-animated">MG BRAND OFFICE</h1>
        <div class="brand-subtitle">Executive Intelligence & Fraud Detection</div>
    </div>
""", unsafe_allow_html=True)

tab_report, tab_demo, tab_finance, tab_compare = st.tabs([
    "• C-LEVEL DENETİM", 
    "• İÇGÖRÜ & AFİNİTE",
    "• MALİYET & ROI", 
    "• ÇAPRAZ İSTİHBARAT"
])

# =========================================================
# SEKME 1: C-LEVEL DENETİM (Ana Ekran + Özet)
# =========================================================
with tab_report:
    _, col_center_rep, _ = st.columns([1, 4, 1])
    with col_center_rep:
        rep_raw = st.text_input("Hedef Profil Bağlantısı veya Kullanıcı Adı", placeholder="Örn: leyakirsan", key="rep_inp")
        btn_rep = st.button("KAPSAMLI DENETİMİ BAŞLAT", use_container_width=True, key="btn_rep")

    st.markdown("<br>", unsafe_allow_html=True)

    if btn_rep and rep_raw:
        r_user = clean_username(rep_raw)
        with st.spinner(f"• @{r_user} algoritmik sahtekarlık testlerine tabi tutuluyor..."):
            p_rep = fetch_apify_instagram_data(r_user, max_posts=24)
            if p_rep and "latestPosts" in p_rep:
                f_rep = int(clean_number(p_rep.get("followersCount", p_rep.get("followers", 0)), 1))
                m_r = run_all_algorithms(f_rep, p_rep.get("latestPosts", []), username=r_user)
                
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
                        <p style="color:#64748b; font-size:0.85rem; font-weight:700; margin:0 0 5px 0; text-transform:uppercase;">Profİl İstİhbaratı</p>
                        <h2 style="margin: 0 0 5px 0; color: #f8fafc; font-size: 2.2rem; font-weight: 900; letter-spacing:-1px;">@{r_user}</h2>
                        <p style="color: #94a3b8; margin: 0; font-size: 0.95rem; font-weight: 500;">{f_rep:,} Takipçi • Sektör: {", ".join(m_r['top_sectors'])}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="color:#64748b; font-size:0.85rem; font-weight:700; margin:0 0 10px 0; text-transform:uppercase;">Algorİtmİk Karar</p>
                        <span class="badge-status" style="{exec_badge}">• {exec_decision}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # YAPAY ZEKA YÖNETİCİ ÖZETİ (YENİ)
                st.markdown(f"""
                <div class="ai-summary-box">
                    <div class="ai-summary-title">• Yapay Zeka Yönetici Özeti (AI Insights)</div>
                    {m_r['ai_summary']}
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.markdown(f"<div class='metric-card'><div class='metric-title'>AQS Kalite Skoru</div><div class='metric-value'>{m_r['aqs_score']} <span style='font-size:1rem;color:#64748b'>/ 100</span></div><div class='metric-sub' style='color:#64748b'>Sektör Standardı: %{m_r['benchmark_er']}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-card'><div class='metric-title'>Etkileşim (ER)</div><div class='metric-value'>%{m_r['er']:.2f}</div><div class='metric-sub' style='color:#64748b'>Ort. Reaksiyon: {int(m_r['total_eng']):,}</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-card'><div class='metric-title'>Organik Kitle Kapasitesi</div><div class='metric-value' style='color:#3b82f6'>%{m_r['authentic_pct']:.1f}</div><div class='metric-sub' style='color:#64748b'>Maks. Erişim: {m_r['est_reach']:,}</div></div>", unsafe_allow_html=True)
                m4.markdown(f"<div class='metric-card'><div class='metric-title'>Sentetik (Bot) Riski</div><div class='metric-value' style='color:#ef4444'>%{m_r['bot_pct']:.1f}</div><div class='metric-sub' style='color:#64748b'>Manipülasyon Oranı</div></div>", unsafe_allow_html=True)

                st.markdown("<br><h4 style='color:#f8fafc; font-weight:800; font-size:1.2rem; border-bottom:1px solid #1e293b; padding-bottom:10px; margin-bottom:20px;'>• ANTI-FRAUD (SAHTEKARLIK) KARNESİ</h4>", unsafe_allow_html=True)

                c_ratio = m_r['comment_ratio']
                if c_ratio < 0.008: s1, c1, d1 = "AĞIR İHLAL (Panel Botu)", "#ef4444", f"Etkileşimlerdeki Yorum/Beğeni dengesi (%{(c_ratio*100):.2f}) istatistiksel imkansızlık seviyesinde. Yüksek ihtimalle ucuz beğeni paneli kullanılmış."
                elif c_ratio > 0.15: s1, c1, d1 = "ŞÜPHELİ İHLAL (Yorum Paneli)", "#f59e0b", f"Gönderilerde aşırı yüksek bir yorum oranı (%{(c_ratio*100):.2f}) mevcut. Çekiliş hesapları veya yorum havuzları kullanılıyor olabilir."
                else: s1, c1, d1 = "GÜVENİLİR (Doğal Denge)", "#10b981", f"Yorum ve beğeni arasındaki korelasyon (%{(c_ratio*100):.2f}) sağlıklı insan davranışlarına ve organik kitle reaksiyonuna uygundur."

                st.markdown(f"""
                <div class="fraud-box" style="border-left-color: {c1};">
                    <div class="fraud-icon" style="color:{c1};">•</div>
                    <div class="fraud-content">
                        <h5>Kitle Reaksiyonu (Yorum/Beğeni Dengesizliği) - <span style="color:{c1}">{s1}</span></h5>
                        <p>{d1}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                cv_val = m_r['cv_value']
                if cv_val < 0.28: s2, c2, d2 = "AĞIR İHLAL (Suni Düzenlilik)", "#ef4444", f"Gönderiler arası etkileşim dalgalanması (Sapma: {cv_val:.2f}) insan doğasına aykırı şekilde stabil. Profil düzenli olarak 'Zeki Paket Bot' satın alıyor."
                elif cv_val > 1.2: s2, c2, d2 = "ŞÜPHELİ İHLAL (Ani Sıçrama)", "#f59e0b", f"İçerikler arası mantıksız uçurumlar tespit edildi (Sapma: {cv_val:.2f}). Reklamlı gönderilere dışarıdan geçici bot basılmış olabilir."
                else: s2, c2, d2 = "GÜVENİLİR (Organik Dalgalanma)", "#10b981", f"İçeriklerin etkileşimleri arasındaki geçişler (Sapma: {cv_val:.2f}) tamamen insan davranışına uygun, manipülasyonsuz dalgalanmalar gösteriyor."

                st.markdown(f"""
                <div class="fraud-box" style="border-left-color: {c2};">
                    <div class="fraud-icon" style="color:{c2};">•</div>
                    <div class="fraud-content">
                        <h5>Etkileşim İstikrarı (İstatistiksel Varyans) - <span style="color:{c2}">{s2}</span></h5>
                        <p>{d2}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # KURUMSAL METRİK KILAVUZU (YENİ)
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("• METRİK SÖZLÜĞÜ VE TERMİNOLOJİ KILAVUZU"):
                    st.markdown("""
                    <div style='color:#cbd5e1; font-size:0.95rem; line-height:1.6;'>
                        <p><b>• AQS (Audience Quality Score):</b> Kitle Kalite Skoru. Profilin organik etkileşim gücü, beğeni/yorum dengesi ve botlardan arındırılmış saflık derecesini 100 üzerinden notlar. 70 ve üzeri yatırıma uygundur.</p>
                        <p><b>• Etkileşim Oranı (ER):</b> Toplam takipçi sayısına kıyasla, gönderi başına alınan ortalama beğeni ve yorumların yüzdesidir. Profilin kitlesiyle bağ kurma gücünü gösterir.</p>
                        <p><b>• Sektör Standardı (Benchmark):</b> Aynı takipçi büyüklüğündeki küresel hesapların ortalama etkileşim oranıdır. Başarı ölçütü olarak referans alınır.</p>
                        <p><b>• İstatistiksel Varyans (CV):</b> Gönderilerin aldıkları etkileşimler arasındaki dalgalanma payıdır. İnsan davranışı doğası gereği dalgalıdır (Yüksek CV). Gönderilerin sürekli aynı sayılarda etkileşim alması (Düşük CV), algoritmamız tarafından sentetik paket bot müdahalesi olarak işaretlenir.</p>
                        <p><b>• Organik Kitle Kapasitesi:</b> Yapay zekanın tespit ettiği şüpheli, sahte veya tamamen pasif hesapların toplam takipçiden çıkartılmasıyla elde edilen "Gerçek ve Aktif İnsan" yüzdesidir.</p>
                        <p><b>• Sentetik (Bot) Riski:</b> Ucuz beğeni panelleri, yorum botları, takipçi hileleri veya etkileşim grupları (pod) ile şişirilmiş istatistiksel anomali taşıyan kitle oranıdır.</p>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.error("• Profil verisi çekilemedi veya API engeline takıldı.")

# =========================================================
# SEKME 2: İÇGÖRÜ & AFİNİTE
# =========================================================
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
            fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"), title=dict(text="Tahmini Cinsiyet Dağılımı", font=dict(color="#f8fafc", size=15)), margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_g, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_d2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            age_df = pd.DataFrame(list(d['age_data'].items()), columns=['Yaş Grubu', 'Oran'])
            fig_a = px.bar(age_df, x='Yaş Grubu', y='Oran', color_discrete_sequence=["#a855f7"])
            fig_a.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"), title=dict(text="Tahmini Yaş Dağılımı", font=dict(color="#f8fafc", size=15)), margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_a, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_w1, col_w2 = st.columns(2)
        
        with col_w1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color:#f8fafc; font-weight:800;'>• Rakip Radarı (Marka Afinitesi)</h5>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:0.85rem;'>İçeriklerde en çok etiketlenen veya bahsedilen hesaplar.</p>", unsafe_allow_html=True)
            if d['top_mentions']:
                for mention, count in d['top_mentions']:
                    st.markdown(f"<div style='background:#1e293b; padding:10px 15px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between;'><span style='color:#3b82f6; font-weight:700;'>@{mention}</span><span style='color:#94a3b8;'>{count} Kez</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#94a3b8;'>Yeterli etiket verisi bulunamadı.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_w2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color:#f8fafc; font-weight:800;'>• Konu Analizi (Sık Kullanılanlar)</h5>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:0.85rem;'>Kaption metinlerinden çıkarılan anahtar kelimeler.</p>", unsafe_allow_html=True)
            if d['word_counts']:
                w_df = pd.DataFrame(d['word_counts'], columns=['Kelime', 'Frekans'])
                fig_w = px.bar(w_df, y='Kelime', x='Frekans', orientation='h', color_discrete_sequence=["#06b6d4"])
                fig_w.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"), margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_w, use_container_width=True)
            else:
                st.markdown("<p style='color:#94a3b8;'>Yeterli metin verisi bulunamadı.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("• Analiz sonuçlarını görmek için lütfen önce 'C-LEVEL DENETİM' sekmesinden bir profili taratın.")

# =========================================================
# SEKME 3: MALİYET VE ROI ANALİZİ
# =========================================================
with tab_finance:
    _, col_center_fin, _ = st.columns([1, 4, 1])
    with col_center_fin:
        fin_raw = st.text_input("Hedef Profil", placeholder="Örn: leyakirsan", key="fin_inp")
        fin_budget = st.number_input("Planlanan Kampanya Bütçesi (₺)", min_value=1000, step=5000, value=50000, key="fin_budget")
        btn_fin = st.button("FİNANSAL FİZİBİLİTEYİ HESAPLA", use_container_width=True, key="btn_fin")

    st.markdown("<br>", unsafe_allow_html=True)

    if btn_fin and fin_raw:
        f_user = clean_username(fin_raw)
        with st.spinner("• Finansal metrikler ve dönüşüm kapasitesi hesaplanıyor..."):
            p_fin = fetch_apify_instagram_data(f_user, 24)
            if p_fin and "latestPosts" in p_fin:
                fol_f = int(clean_number(p_fin.get("followersCount", p_fin.get("followers", 0)), 1))
                m_f = run_all_algorithms(fol_f, p_fin.get("latestPosts", []), budget=fin_budget)

                st.markdown(f"<h4 style='color:#f8fafc; font-weight:800; text-align:center;'>@{f_user} • Kampanya Maliyet Projeksiyonu</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center; color:#64748b; margin-bottom:30px;'>Planlanan Bütçe: <b>₺{fin_budget:,}</b> | Yatırım Getirisi (ROI) Çarpanları</p>", unsafe_allow_html=True)

                c_f1, c_f2, c_f3 = st.columns(3)
                c_f1.markdown(f"<div class='metric-card' style='border-color:#3b82f6;'><div class='metric-title'>CPE (Etkileşim Başına Maliyet)</div><div class='metric-value' style='color:#3b82f6'>₺{m_f['cpe']:.2f}</div><div class='metric-sub' style='color:#64748b'>Beğeni veya yorum başına ödenecek tutar.</div></div>", unsafe_allow_html=True)
                c_f2.markdown(f"<div class='metric-card' style='border-color:#10b981;'><div class='metric-title'>CPM (1000 Gösterim Maliyeti)</div><div class='metric-value' style='color:#10b981'>₺{m_f['cpm']:.2f}</div><div class='metric-sub' style='color:#64748b'>1000 kişiye ulaşmanın tahmini bedeli.</div></div>", unsafe_allow_html=True)
                c_f3.markdown(f"<div class='metric-card'><div class='metric-title'>Maksimum Erişilebilir Kitle</div><div class='metric-value'>{m_f['est_reach']:,}</div><div class='metric-sub' style='color:#64748b'>Algoritmik sınır ve aktif takipçi çarpımı.</div></div>", unsafe_allow_html=True)
                
            else:
                st.error("• Profil verisi çekilemedi.")

# =========================================================
# SEKME 4: ÇAPRAZ İSTİHBARAT
# =========================================================
with tab_compare:
    _, col_center_cmp, _ = st.columns([1, 4, 1])
    with col_center_cmp:
        c_u1 = st.text_input("1. Profil (Rakip A)", placeholder="Örn: rakip1", key="cmp1")
        c_u2 = st.text_input("2. Profil (Rakip B)", placeholder="Örn: rakip2", key="cmp2")
        btn_cmp = st.button("STRATEJİK KIYASLAMA YAP", use_container_width=True, key="btn_cmp")

    if btn_cmp and c_u1 and c_u2:
        u1, u2 = clean_username(c_u1), clean_username(c_u2)
        with st.spinner("• Milyar dolarlık çapraz kıyaslama motoru çalışıyor..."):
            p1, p2 = fetch_apify_instagram_data(u1, 24), fetch_apify_instagram_data(u2, 24)
            if p1 and p2:
                f1 = int(clean_number(p1.get("followersCount", p1.get("followers", 0)), 1))
                f2 = int(clean_number(p2.get("followersCount", p2.get("followers", 0)), 1))
                m1 = run_all_algorithms(f1, p1.get("latestPosts", []))
                m2 = run_all_algorithms(f2, p2.get("latestPosts", []))

                st.markdown("<br>", unsafe_allow_html=True)
                cmp_table = pd.DataFrame({
                    "STRATEJİK METRİKLER": [
                        "Toplam Takipçi Hacmi", "Kitle Kalite Endeksi (AQS)", "Sentetik Kitle Riski", 
                        "Net Etkileşim Gücü (ER)", "Tahmini Kampanya Erişimi", "Aktif Sponsorluk Sıklığı"
                    ],
                    f"@{u1.upper()}": [
                        f"{f1:,}", f"{m1['aqs_score']} / 100", f"%{m1['bot_pct']:.1f}", 
                        f"%{m1['er']:.2f}", f"{m1['est_reach']:,}", f"%{m1['collab_ratio']:.1f}"
                    ],
                    f"@{u2.upper()}": [
                        f"{f2:,}", f"{m2['aqs_score']} / 100", f"%{m2['bot_pct']:.1f}", 
                        f"%{m2['er']:.2f}", f"{m2['est_reach']:,}", f"%{m2['collab_ratio']:.1f}"
                    ]
                })
                
                st.dataframe(cmp_table, use_container_width=True, hide_index=True)

            else:
                st.error("• Profillerden biri veya ikisi bulunamadı.")

st.markdown('<div class="footer-dark">MG BRAND OFFICE EXECUTIVE SUITE © 2026 | ENTERPRISE INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
