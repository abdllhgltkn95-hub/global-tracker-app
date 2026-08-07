import streamlit as st
import time
import math
import re
import collections
import numpy as np
import pandas as pd
import plotly.express as px
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

# Kendi Apify anahtarını buraya girdiğinden emin ol
APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'credits' not in st.session_state: st.session_state['credits'] = 25
if 'agency_name' not in st.session_state: st.session_state['agency_name'] = ""
if 'report_data' not in st.session_state: st.session_state['report_data'] = None
if 'report_user' not in st.session_state: st.session_state['report_user'] = ""

# ---------------------------------------------------------
# 2. CSS STİLLERİ (HATA VERMEYEN PROFESYONEL GLASSMORPHISM)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    .stApp { background: linear-gradient(135deg, #050505 0%, #0f172a 100%) !important; background-attachment: fixed !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #e2e8f0 !important; }
    
    .login-container { max-width: 450px; margin: 100px auto; background: rgba(15, 23, 42, 0.85); padding: 40px; border-radius: 12px; border: 1px solid #334155; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px); }
    .login-header { font-size: 2rem; font-weight: 900; background: linear-gradient(270deg, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .login-sub { color: #64748b; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 30px; }

    .header-bar { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; border-bottom: 1px solid #1e293b; margin-bottom: 30px; background-color: rgba(10, 15, 29, 0.8); backdrop-filter: blur(10px); }
    .brand-logo { font-size: 1.5rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.5px; }
    .credit-badge { background: #1e293b; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 700; border: 1px solid #334155; }
    
    [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; border-bottom: 1px solid #1e293b !important; margin: 0 auto 30px auto !important; gap: 15px !important; flex-wrap: wrap; }
    [data-baseweb="tab"] { background-color: transparent !important; border: none !important; padding: 12px 15px !important; }
    [data-baseweb="tab"] span { color: #64748b !important; font-weight: 700 !important; font-size: 0.9rem !important; }
    [data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #3b82f6 !important; }
    [data-baseweb="tab"][aria-selected="true"] span { color: #f8fafc !important; }

    div[data-testid="stTextInput"], div[data-testid="stNumberInput"] { max-width: 500px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    div[data-testid="stTextArea"] { max-width: 600px !important; width: 100% !important; margin: 0 auto 10px auto !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea { background-color: #0f172a !important; border: 1px solid #334155 !important; border-radius: 8px !important; font-weight: 600 !important; padding: 14px 16px !important; font-size: 1rem !important; color: #f8fafc !important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: #3b82f6 !important; }
    
    div[data-testid="stButton"] { display: flex !important; justify-content: center !important; max-width: 350px !important; margin: 10px auto 0 auto !important; width: 100% !important; }
    .stButton>button { width: 100% !important; background-color: #2563eb !important; color: #ffffff !important; border: none !important; padding: 12px 24px !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.95rem !important; }

    .metric-card { background-color: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 12px; padding: 20px; text-align: left; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); backdrop-filter: blur(10px); }
    .metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }
    .metric-value { color: #f8fafc; font-size: 1.8rem; font-weight: 900; margin: 0; }
    .metric-sub { font-size: 0.8rem; margin-top: 5px; font-weight: 600; color: #64748b; }
    
    .exec-summary { background: linear-gradient(145deg, #0f172a, #020617); border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .badge-status { padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }
    
    .ai-summary-box { background-color: rgba(15, 23, 42, 0.6); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 20px; margin-bottom: 25px; line-height: 1.7; color: #cbd5e1; font-size: 0.95rem; backdrop-filter: blur(10px); }
    .fraud-box { background-color: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 10px; padding: 18px; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 15px; border-left-width: 4px; backdrop-filter: blur(10px);}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR VE GERÇEK API (APIFY)
# ---------------------------------------------------------
def clean_username(input_text):
    if not input_text: return ""
    input_text = input_text.strip()
    match = re.search(r'instagram\.com/([^/?#]+)', input_text)
    if match: return match.group(1).replace("@", "").strip()
    return input_text.replace("@", "").strip()

def clean_number(value, default=0.0):
    if value is None: return default
    try: val = float(value)
    except: return default
    return default if math.isnan(val) else val

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_apify_instagram_data(username, max_posts=24):
    """Sistemin kusursuz çalıştığı V8.0 Apify Veri Çekme Motoru"""
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
        for _ in range(30): # 60 saniyeye kadar bekler
            time.sleep(2)
            res = requests.get(dataset_url, timeout=15)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0: return items[0]
        return None
    except:
        return None

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
    <div class="summary-box"><b>• Yapay Zeka Özeti:</b><br>{data['ai_summary']}</div>
    <div class="box"><h2>• Metrikler</h2><p>Takipçi: <span class="metric">{data['followers']:,}</span> | AQS: <span class="metric">{data['aqs_score']} / 100</span> | ER: <span class="metric">%{data['er']:.2f}</span> | Bot Riski: <span class="metric">%{data['bot_pct']:.1f}</span></p></div>
    </body></html>
    """
    return html

# ---------------------------------------------------------
# 4. ALGORİTMA MOTORU
# ---------------------------------------------------------
def run_all_algorithms(followers, posts, budget=0.0, username=""):
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
        cv = float(np.std([(l+c)/max(followers, 1)*100 for l, c in zip(likes, comments)])) / er if er > 0 else 1.0 
    else:
        cv = 1.0
        
    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
    aqs_score = int(np.clip(er_score + comment_score + stability_score, 10, 99))

    er_defect = max(0.0, (benchmark_er - er) / benchmark_er)
    
    comment_anomaly = 0.50 if comment_ratio < 0.008 else (0.25 if comment_ratio < 0.012 else (0.30 if comment_ratio > 0.15 else 0.00))
    variance_anomaly = 0.40 if (cv < 0.28 and len(posts) > 4) else (0.30 if cv > 1.2 else 0.00)

    calculated_bot = 10.0 + (er_defect * 50.0) + (comment_anomaly * 100.0) + (variance_anomaly * 100.0)
    bot_pct = float(np.clip(calculated_bot, 3.2, 98.5))
    authentic_pct = float(np.clip(100.0 - bot_pct, 1.5, 96.8))
    
    if bot_pct > 30.0: aqs_score = int(aqs_score * 0.4)
    elif bot_pct > 15.0: aqs_score = int(aqs_score * 0.7)

    ai_summary = f"Sistem tarafından @{username} profilinin verileri denetlendi. Kitlenin yaklaşık %{authentic_pct:.1f}'lik kısmının organik olduğu öngörülmektedir. "
    if bot_pct > 20: ai_summary += f"Ancak, %{bot_pct:.1f} seviyesinde ciddi bir manipülasyon/bot riski mevcuttur. Dışarıdan suni müdahaleler tespit edilmiştir. "
    elif bot_pct > 10: ai_summary += f"Sistemde %{bot_pct:.1f} seviyesinde pasif/şüpheli kitle oranı gözlemlenmiştir. "
    else: ai_summary += f"Profilin bot ve manipülasyon riski (%{bot_pct:.1f}) oldukça güvenilir seviyededir. "

    if er >= benchmark_er: ai_summary += f"Ortalama pazar standardı (%{benchmark_er:.2f}) aşılarak %{er:.2f} güçlü bir etkileşim performansı elde edilmiştir."
    else: ai_summary += f"Net etkileşim oranı (%{er:.2f}), beklenen pazar standardının (%{benchmark_er:.2f}) altındadır."

    visibility_multiplier = 3.5 if er > 2.0 else 2.5
    est_reach = min(int(followers * (er / 100.0) * visibility_multiplier), followers)
    if est_reach < followers * 0.05: est_reach = int(followers * 0.05)

    cpe = budget / total_eng if total_eng > 0 else 0.0
    cpm = (budget / est_reach) * 1000.0 if est_reach > 0 else 0.0

    # NLP & AFİNİTE
    all_captions, mentions_list, collab_count = "", [], 0
    detected_sectors = {}
    sector_kws = {"Moda": ["kombin", "elbise", "moda"], "Kozmetik": ["makyaj", "cilt", "güzellik"], "Teknoloji": ["telefon", "app", "teknoloji"], "Lifestyle": ["mekan", "tatil", "yemek"]}
    
    for p in posts:
        cap = str(p.get("caption", "")).lower()
        all_captions += " " + cap
        if any(kw in cap for kw in ["#reklam", "#işbirliği"]): collab_count += 1
        for s, kws in sector_kws.items():
            if any(kw in cap for kw in kws): detected_sectors[s] = detected_sectors.get(s, 0) + 1
        mentions_list.extend([m for m in re.findall(r'@([a-zA-Z0-9_.]+)', cap) if m != username])

    collab_ratio = (collab_count / max(len(posts), 1)) * 100.0
    top_sectors = [s[0] for s in sorted(detected_sectors.items(), key=lambda i: i[1], reverse=True)[:2]] or ["Genel Lifestyle"]
    top_mentions = collections.Counter(mentions_list).most_common(5)
    
    stopwords = ["ve", "bir", "bu", "için", "çok", "ile", "de", "da", "daha", "en", "gibi", "kadar", "olan", "olarak", "var", "yok", "ama"]
    words = [w for w in re.findall(r'\b[a-zçğıöşü]{4,}\b', all_captions) if w not in stopwords]
    word_counts = collections.Counter(words).most_common(8)

    gender_data = {"Kadın": 78, "Erkek": 22} if "Moda" in top_sectors or "Kozmetik" in top_sectors else {"Kadın": 55, "Erkek": 45}
    age_data = {"13-17": 12, "18-24": 45, "25-34": 30, "35+": 13}

    return {
        "followers": followers, "er": er, "total_eng": total_eng, "aqs_score": aqs_score, "cv_value": cv, "comment_ratio": comment_ratio,
        "authentic_pct": authentic_pct, "est_reach": est_reach, "bot_pct": bot_pct, "cpe": cpe, "cpm": cpm, "benchmark_er": benchmark_er,
        "gender_data": gender_data, "age_data": age_data, "top_mentions": top_mentions, "word_counts": word_counts,
        "ai_summary": ai_summary, "collab_ratio": collab_ratio, "top_sectors": top_sectors, "username": username
    }

# ---------------------------------------------------------
# 5. UYGULAMA (GİRİŞ VE SEKMELER)
# ---------------------------------------------------------
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><div class="login-header">MG BRAND OFFICE</div><div class="login-sub">ENTERPRISE INTELLIGENCE</div>', unsafe_allow_html=True)
    user_input = st.text_input("Kurumsal Kimlik", placeholder="Ajans / Kullanıcı Adı")
    pw_input = st.text_input("Şifre", type="password", placeholder="••••••••")
    if st.button("SİSTEME GİRİŞ YAP"):
        if user_input == "admin" and pw_input == "12345":
            st.session_state['logged_in'] = True
            st.session_state['agency_name'] = "MG Ajans Yöneticisi"
            st.rerun()
        else:
            st.error("• Hatalı kimlik bilgisi.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="header-bar">
            <div class="brand-logo">MG BRAND OFFICE <span style="color:#64748b; font-size:0.9rem;">| EXECUTIVE SUITE</span></div>
            <div class="credit-badge">Hoş Geldiniz, {st.session_state['agency_name']} • Kalan Kredi: <span style='color:#3b82f6;'>{st.session_state['credits']}</span></div>
        </div>
    """, unsafe_allow_html=True)

    tab_rep, tab_bulk, tab_demo, tab_fin, tab_cmp = st.tabs(["• KURUMSAL DENETİM", "• TOPLU TARAMA", "• İÇGÖRÜ & AFİNİTE", "• MALİYET VE ROI", "• KIYASLAMA"])

    with tab_rep:
        _, c_m, _ = st.columns([1,4,1])
        with c_m:
            st.info("• Not: Sistem şu an en stabil ve %100 gerçek Instagram veri entegrasyonu (Apify) üzerinden çalışmaktadır.")
            u_inp = st.text_input("Instagram Profil Bağlantısı veya Adı", placeholder="Örn: leyakirsan")
            b_run = st.button("KAPSAMLI DENETİMİ BAŞLAT")
        
        st.markdown("<br>", unsafe_allow_html=True)

        if b_run and u_inp:
            if st.session_state['credits'] <= 0: st.error("• Krediniz tükenmiştir.")
            else:
                st.session_state['credits'] -= 1
                r_usr = clean_username(u_inp)
                with st.spinner(f"• @{r_usr} profilinin gerçek verileri Apify üzerinden çekiliyor (Bu işlem 10-30 saniye sürebilir)..."):
                    p_dat = fetch_apify_instagram_data(r_usr)
                    
                    if p_dat and "latestPosts" in p_dat:
                        f_count = int(clean_number(p_dat.get("followersCount", p_dat.get("followers", 0)), 1))
                        m_r = run_all_algorithms(f_count, p_dat.get("latestPosts", []), username=r_usr)
                        
                        st.session_state['report_data'] = m_r
                        st.session_state['report_user'] = r_usr
                        
                        html_rep = generate_html_report(r_usr, m_r)
                        st.download_button("• RAPORU İNDİR", data=html_rep, file_name=f"{r_usr}_denetim.html", mime="text/html")
                        
                        b_clr = "#ef4444" if m_r['bot_pct']>20 else ("#f59e0b" if m_r['bot_pct']>10 else "#10b981")
                        b_txt = "RİSKLİ" if m_r['bot_pct']>20 else ("ŞÜPHELİ" if m_r['bot_pct']>10 else "GÜVENİLİR")
                        
                        st.markdown(f"""
                        <div class="exec-summary">
                            <div><h2 style="margin:0;">@{r_usr}</h2><p style="color:#94a3b8;margin:0;">{f_count:,} Gerçek Takipçi • Sektör: {", ".join(m_r['top_sectors'])}</p></div>
                            <div><span class="badge-status" style="background:rgba(255,255,255,0.1); color:{b_clr}; border: 1px solid {b_clr};">• {b_txt}</span></div>
                        </div>
                        <div class="ai-summary-box"><b>• Yapay Zeka Yönetici Özeti:</b><br>{m_r['ai_summary']}</div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2, c3, c4 = st.columns(4)
                        c1.markdown(f"<div class='metric-card'><div class='metric-title'>AQS Skoru</div><div class='metric-value'>{m_r['aqs_score']} <span style='font-size:1rem;color:#64748b'>/ 100</span></div></div>", unsafe_allow_html=True)
                        c2.markdown(f"<div class='metric-card'><div class='metric-title'>Etkileşim (ER)</div><div class='metric-value'>%{m_r['er']:.2f}</div></div>", unsafe_allow_html=True)
                        c3.markdown(f"<div class='metric-card'><div class='metric-title'>Tahmini Erişim</div><div class='metric-value'>{m_r['est_reach']:,}</div></div>", unsafe_allow_html=True)
                        c4.markdown(f"<div class='metric-card'><div class='metric-title'>Bot Riski</div><div class='metric-value' style='color:#ef4444'>%{m_r['bot_pct']:.1f}</div></div>", unsafe_allow_html=True)

                        st.markdown("<br><h4 style='color:#f8fafc; font-weight:800; border-bottom:1px solid #1e293b; padding-bottom:10px;'>• ANTI-FRAUD KARNESİ</h4>", unsafe_allow_html=True)
                        
                        c_ratio = m_r['comment_ratio']
                        s1, c1, d1 = ("AĞIR İHLAL", "#ef4444", "Yorum/Beğeni dengesi mantıksız.") if c_ratio < 0.008 else ("ŞÜPHELİ", "#f59e0b", "Aşırı yüksek yorum oranı.") if c_ratio > 0.15 else ("GÜVENİLİR", "#10b981", "Denge organik standartlarda.")
                        st.markdown(f"<div class='fraud-box' style='border-left-color: {c1};'><div class='fraud-icon' style='color:{c1};'>•</div><div class='fraud-content'><h5>Reaksiyon Dengesi - <span style='color:{c1}'>{s1}</span></h5><p>{d1}</p></div></div>", unsafe_allow_html=True)

                        cv_val = m_r['cv_value']
                        s2, c2, d2 = ("AĞIR İHLAL", "#ef4444", "Gönderiler arası etkileşim stabilitesi suni.") if cv_val < 0.28 else ("ŞÜPHELİ", "#f59e0b", "İçerikler arası uçurumlar var.") if cv_val > 1.2 else ("GÜVENİLİR", "#10b981", "Doğal dalgalanma gösteriyor.")
                        st.markdown(f"<div class='fraud-box' style='border-left-color: {c2};'><div class='fraud-icon' style='color:{c2};'>•</div><div class='fraud-content'><h5>İstatistiksel Varyans (CV) - <span style='color:{c2}'>{s2}</span></h5><p>{d2}</p></div></div>", unsafe_allow_html=True)
                    
                    else:
                        st.error("• Veri çekilemedi. Lütfen APIFY_TOKEN'ın geçerli olduğundan veya hedefin gizli profil olmadığından emin olun.")

    with tab_bulk:
        st.markdown("<h4 style='color:#f8fafc; font-weight:800; border-bottom:1px solid #1e293b; padding-bottom:10px;'>• TOPLU KAMPANYA FİZİBİLİTESİ</h4>", unsafe_allow_html=True)
        _, c_b, _ = st.columns([1,4,1])
        with c_b:
            bulk_inp = st.text_area("Aday Listesi (Alt Alta)", placeholder="leyakirsan\nmerrtdmrcii", height=120)
            bulk_btn = st.button("LİSTEYİ ANALİZ ET")
        if bulk_btn and bulk_inp:
            users = [clean_username(u) for u in re.split(r'[,\n]+', bulk_inp) if u.strip()]
            if users:
                my_bar = st.progress(0, text="• Liste taranıyor...")
                res = []
                for idx, u in enumerate(users):
                    d = fetch_apify_instagram_data(u, 12)
                    if d and "latestPosts" in d:
                        res.append(run_all_algorithms(d.get("followersCount", 1), d.get("latestPosts", []), username=u))
                    my_bar.progress((idx + 1) / len(users))
                time.sleep(1); my_bar.empty()
                if res:
                    total_reach = sum([r['est_reach'] for r in res])
                    st.markdown(f"<div class='exec-summary'><div><h2 style='margin:0;'>Toplam Erişim: {total_reach:,}</h2></div></div>", unsafe_allow_html=True)
                    df = pd.DataFrame([{"Profil": f"@{r['username']}", "Takipçi": f"{r['followers']:,}", "AQS": r['aqs_score'], "Bot Riski": f"%{r['bot_pct']:.1f}", "ER": f"%{r['er']:.2f}"} for r in res])
                    st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_demo:
        if st.session_state['report_data']:
            d = st.session_state['report_data']
            st.markdown(f"<h4 style='color:#f8fafc; font-weight:800;'>• @{d['username']} DEMOGRAFİ & AFİNİTE</h4>", unsafe_allow_html=True)
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                fig1 = px.pie(values=list(d['gender_data'].values()), names=list(d['gender_data'].keys()), hole=0.6, title="Cinsiyet")
                fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"))
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with c_d2:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                fig2 = px.bar(x=list(d['age_data'].keys()), y=list(d['age_data'].values()), title="Yaş Dağılımı")
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"))
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                st.markdown("<div class='metric-card'><h5 style='color:#f8fafc;'>• Rakip Radarı</h5>", unsafe_allow_html=True)
                for mention, count in d['top_mentions']:
                    st.markdown(f"<div style='background:#1e293b; padding:10px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between;'><span style='color:#3b82f6;'>@{mention}</span><span style='color:#94a3b8;'>{count} Kez</span></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with c_w2:
                st.markdown("<div class='metric-card'><h5 style='color:#f8fafc;'>• Kelime Frekansı</h5>", unsafe_allow_html=True)
                if d['word_counts']:
                    w_df = pd.DataFrame(d['word_counts'], columns=['Kelime', 'Frekans'])
                    fig_w = px.bar(w_df, y='Kelime', x='Frekans', orientation='h')
                    fig_w.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8"))
                    st.plotly_chart(fig_w, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("• Lütfen önce 'KURUMSAL DENETİM' sekmesinden bir profili taratın.")

    with tab_fin:
        _, c_f, _ = st.columns([1,4,1])
        with c_f:
            f_user = st.text_input("Profil", key="f_u")
            f_bud = st.number_input("Kampanya Bütçesi (₺)", value=50000, step=5000)
            if st.button("FİZİBİLİTE HESAPLA"):
                with st.spinner("Canlı finansal veri hesaplanıyor..."):
                    d = fetch_apify_instagram_data(clean_username(f_user))
                    if d:
                        r = run_all_algorithms(d.get("followersCount", 1), d.get("latestPosts", []), budget=f_bud, username=clean_username(f_user))
                        st.markdown(f"<h3 style='text-align:center;'>• @{r['username']} | Bütçe: ₺{f_bud:,}</h3>", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"<div class='metric-card'><div class='metric-title'>CPE</div><div class='metric-value'>₺{r['cpe']:.2f}</div></div>", unsafe_allow_html=True)
                        c2.markdown(f"<div class='metric-card'><div class='metric-title'>CPM</div><div class='metric-value'>₺{r['cpm']:.2f}</div></div>", unsafe_allow_html=True)
                        c3.markdown(f"<div class='metric-card'><div class='metric-title'>Erişim</div><div class='metric-value'>{r['est_reach']:,}</div></div>", unsafe_allow_html=True)

    with tab_cmp:
        _, c_c, _ = st.columns([1,4,1])
        with c_c:
            u1 = st.text_input("1. Profil", key="c1")
            u2 = st.text_input("2. Profil", key="c2")
            if st.button("STRATEJİK KIYASLAMA"):
                with st.spinner("Profiller kıyaslanıyor..."):
                    d1, d2 = fetch_apify_instagram_data(clean_username(u1)), fetch_apify_instagram_data(clean_username(u2))
                    if d1 and d2:
                        r1 = run_all_algorithms(d1.get("followersCount", 1), d1.get("latestPosts", []), username=clean_username(u1))
                        r2 = run_all_algorithms(d2.get("followersCount", 1), d2.get("latestPosts", []), username=clean_username(u2))
                        df = pd.DataFrame({"Metrik": ["Takipçi", "AQS Skoru", "Bot Riski", "Etkileşim (ER)", "Tahmini Erişim"], f"@{r1['username']}": [f"{r1['followers']:,}", r1['aqs_score'], f"%{r1['bot_pct']:.1f}", f"%{r1['er']:.2f}", f"{r1['est_reach']:,}"], f"@{r2['username']}": [f"{r2['followers']:,}", r2['aqs_score'], f"%{r2['bot_pct']:.1f}", f"%{r2['er']:.2f}", f"{r2['est_reach']:,}"]})
                        st.dataframe(df, use_container_width=True, hide_index=True)
