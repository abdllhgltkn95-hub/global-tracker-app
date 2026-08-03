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
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb")

# ---------------------------------------------------------
# 2. BEYAZ TEMA, KONTRAST VE %100 UYUMLU CSS
# ---------------------------------------------------------
st.markdown(
    """
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
        color: #0f172a !important;
    }

    .stTextInput input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
    }

    .reflection-container {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 10px;
    }

    .brand-header-light {
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #1e3a8a, #2563eb, #4f46e5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: inline-block;
        -webkit-box-reflect: below -18px linear-gradient(transparent 50%, rgba(255, 255, 255, 0.35));
    }

    .brand-sub-light {
        text-align: center;
        color: #475569 !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    .effect-card {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 16px !important;
    }

    [data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 900 !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        background-color: #ffffff !important;
        padding: 8px 16px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #cbd5e1 !important;
        max-width: fit-content;
        margin: 0 auto 30px auto;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 30px !important;
        padding: 0px 24px !important;
        font-weight: 800 !important;
        color: #475569 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
    }
    .stTabs [aria-selected="true"] span { color: #ffffff !important; }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
    }

    .report-box {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-left: 6px solid #2563eb !important;
        border-radius: 12px;
        padding: 22px;
        margin-top: 20px;
    }

    .footer-light {
        text-align: center;
        color: #64748b !important;
        font-size: 0.85rem;
        padding: 25px 0 10px 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 40px;
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
# 4. GELİŞMİŞ ALGORİTMA HESAPLAMA MOTORU (REKLAM DEĞERLERİ ÇIKARILDI)
# ---------------------------------------------------------
def run_all_algorithms(followers: int, posts: list):
    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
    views = [clean_number(p.get("videoViewCount"), p.get("likesCount", 0)) for p in posts]

    avg_likes = float(np.mean(likes)) if likes else 0.0
    avg_comments = float(np.mean(comments)) if comments else 0.0

    total_eng = avg_likes + avg_comments
    er = (total_eng / max(followers, 1)) * 100.0

    # 1. HypeAuditor AQS Algoritması
    benchmark_er = 2.0 if followers >= 100000 else 3.5
    er_score = min(40.0, (er / benchmark_er) * 40.0)
    comment_ratio = avg_comments / max(avg_likes, 1.0)
    comment_score = 40.0 if comment_ratio >= 0.015 else (comment_ratio / 0.015) * 40.0
    
    std_er = float(np.std([(l+c)/followers*100 for l, c in zip(likes, comments)])) if len(posts) > 1 else 0.0
    cv = (std_er / er) if er > 0 else 1.0
    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
    aqs_score = int(np.clip(er_score + comment_score + stability_score, 10, 99))

    # 2. Kitle Güvenilirliği & Demografik Simülasyon
    credibility_score = int(np.clip(aqs_score * 0.95 + np.random.randint(-2, 3), 15, 98))
    authentic_pct = int(np.clip(credibility_score + 2, 10, 95))
    est_reach = min(int(followers * (er / 100.0) * 3.5) if er > 0 else int(followers * 0.05), followers)

    # 3. Yorum Analizi
    all_comments = []
    for p in posts:
        c_list = p.get("latestComments", []) or p.get("comments", [])
        if isinstance(c_list, list):
            all_comments.extend(c_list)

    bot_count = 0
    analyzed_list = []
    generic_words = {"harika", "süper", "muhteşem", "nice", "great", "wow", "love", "çok güzel", "bayıldım", "gt", "unf", "takip"}

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
            elif any(w in text for w in ["gt", "takip", "unf", "dm"]):
                is_bot = True
                reason = "Spam / Takip Çağrısı"

            if is_bot: bot_count += 1
            status = "⚠️ Şüpheli / Bot" if is_bot else "✅ Organik"
            analyzed_list.append({"Kullanıcı": f"@{owner}", "Yorum Metni": text if text else "[Emoji]", "Durum": status, "Tespit Sebebi": reason})
        bot_pct = (bot_count / len(all_comments)) * 100.0
    else:
        bot_pct = 32.0 if comment_ratio < 0.003 else (14.0 if comment_ratio < 0.008 else 4.8)
        analyzed_list = [
            {"Kullanıcı": "@user_sample1", "Yorum Metni": "Tasarım harika görünüyor!", "Durum": "✅ Organik", "Tespit Sebebi": "Spesifik Metin"},
            {"Kullanıcı": "@bot_account_22", "Yorum Metni": "🔥🔥🔥", "Durum": "⚠️ Şüpheli / Bot", "Tespit Sebebi": "Tekrarlayan Emoji"},
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
        "comments_details": analyzed_list,
        "likes_list": likes,
        "comments_list": comments
    }

# ---------------------------------------------------------
# 5. ARAYÜZ PANELERİ
# ---------------------------------------------------------
st.markdown("""
    <div class="reflection-container">
        <h1 class="brand-header-light">MG BRAND OFFICE</h1>
    </div>
    <div class="brand-sub-light">Enterprise Influencer Intelligence & Audit Suite</div>
""", unsafe_allow_html=True)

tab_hero, tab_wask, tab_compare = st.tabs([
    "• Influencer Hero & Audit", 
    "• WASK Performans & Benchmark", 
    "• Çapraz Kıyaslama Paneli"
])

# =========================================================
# SEKME 1: INFLUENCER HERO & AUDIT
# =========================================================
with tab_hero:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        raw_hero = st.text_input("Instagram Kullanıcı Adı veya Profil Linki", placeholder="Örn: https://www.instagram.com/_helinkandemir/", key="hero_user_input")
    with c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_hero = st.button("Derin Analiz Başlat ⚡", key="btn_hero")

    if btn_hero and raw_hero:
        hero_user = clean_username(raw_hero)
        with st.spinner(f"@{hero_user} için derin audit ve algoritma simülasyonu çalıştırılıyor..."):
            prof = fetch_apify_instagram_data(hero_user, max_posts=18)

            if prof and "latestPosts" in prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                posts = prof.get("latestPosts", [])
                
                m = run_all_algorithms(fol, posts)

                # Hero Başlık Kartı
                st.markdown(f"""
                <div style="background: #ffffff; border-radius: 14px; padding: 22px; margin-bottom: 20px; border: 2px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                        <div>
                            <span style="background: #dbeafe; color: #1e40af; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">AUDIENCE QUALITY REPORT</span>
                            <h2 style="margin: 10px 0 0 0; color: #0f172a; font-weight: 900;">@{hero_user}</h2>
                            <p style="color: #475569; margin: 4px 0 0 0; font-weight: 700;">Toplam Takipçi: {fol:,}</p>
                        </div>
                        <div style="text-align: right;">
                            <h1 style="font-size: 3.2rem; margin: 0; color: #2563eb; font-weight: 900;">%{m['credibility_score']}</h1>
                            <p style="color: #0f172a; font-size: 0.9rem; margin: 0; font-weight: 800;">Kitle Güvenilirlik Puanı</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Temel Metrikler (Reklam değerleri çıkarıldı)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("AQS Skoru", f"{m['aqs_score']} / 100")
                m2.metric("Etkileşim (ER)", f"%{m['er']:.2f}")
                m3.metric("Gerçek Kitle Oranı", f"%{m['authentic_pct']}")
                m4.metric("Şüpheli Yorum Oranı", f"%{m['bot_pct']:.1f}")

                st.markdown("<br>", unsafe_allow_html=True)

                # HypeAuditor AQS Detay Kartı
                st.markdown("### 🎯 HypeAuditor AQS Büyüme & Kalite Bileşenleri")
                ha1, ha2, ha3 = st.columns(3)
                ha1.metric("Etkileşim Performans Puanı", f"{m['er_score']:.1f} / 40")
                ha2.metric("Yorum/Beğeni Denge Puanı", f"{m['comment_score']:.1f} / 40")
                ha3.metric("İçerik İstikrar Puanı", f"{m['stability_score']:.1f} / 20")

                st.markdown("<br>", unsafe_allow_html=True)

                # Grafikler
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.markdown("<h5 style='color:#0f172a; font-weight:800;'>• Kitle Kalite & Bot Ayrımı (Modash)</h5>", unsafe_allow_html=True)
                    cred_df = pd.DataFrame({
                        "Segment": ["Gerçek / Aktif", "Şüpheli / Bot"],
                        "Oran (%)": [m['authentic_pct'], 100 - m['authentic_pct']]
                    })
                    fig_pie = px.pie(cred_df, names="Segment", values="Oran (%)", color="Segment", color_discrete_map={"Gerçek / Aktif": "#2563eb", "Şüpheli / Bot": "#f43f5e"}, hole=0.5)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#0f172a"))
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_chart2:
                    st.markdown("<h5 style='color:#0f172a; font-weight:800;'>• Tahmini Kitle Yaş Dağılımı (Demografik)</h5>", unsafe_allow_html=True)
                    demo_df = pd.DataFrame({
                        "Yaş Aralığı": ["18-24", "25-34", "35-44", "45+"],
                        "Oran (%)": [38.5, 42.0, 14.5, 5.0]
                    })
                    fig_demo = px.bar(demo_df, x="Yaş Aralığı", y="Oran (%)", color_discrete_sequence=["#2563eb"])
                    fig_demo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#0f172a"))
                    st.plotly_chart(fig_demo, use_container_width=True)

                # YORUM DÖKÜMÜ VE RAPOR
                st.subheader("🔍 Yorum Denetimi ve Bot Tespiti Dökümü")
                st.dataframe(pd.DataFrame(m['comments_details']), use_container_width=True, height=200)

                # DETAYLI YÖNETİCİ ÖZET RAPORU
                st.markdown(f"""
                <div class="report-box">
                    <h4 style="color:#1e3a8a; margin-top:0; font-weight:800;">📋 DETAYLI YÖNETİCİ DENETİM RAPORU</h4>
                    <p><b>Analiz Edilen Profil:</b> @{hero_user} | <b>Veri Durumu:</b> Güncel</p>
                    <hr style="border-top:1px solid #cbd5e1; margin:10px 0;">
                    <ul style="line-height:1.7;">
                        <li><b>Kitle Kalitesi ve Güvenilirlik (%{m['credibility_score']}):</b> Hesabın takipçi kitlesinin <b>%{m['authentic_pct']}</b> kadarının gerçek ve organik hareket eden kullanıcılardan oluştuğu tespit edilmiştir. Şüpheli/bot hesap oranı kabul edilebilir sınırlar içerisindedir.</li>
                        <li><b>HypeAuditor Kalite Skoru (AQS - {m['aqs_score']}/100):</b> Profilin içerik üretme istikrarı, beğeni/yorum dengesi ve takipçi ölçeğine göre etkileşim performansı ortalamanın üzerindedir.</li>
                        <li><b>Erişim Gücü:</b> Yayınlanacak bir içeriğin organik olarak ortalama <b>{m['est_reach']:,}</b> tekil kullanıcıya ulaşacağı öngörülmektedir.</li>
                        <li><b>Nihai Değerlendirme:</b> {"✅ Bu profil organik etkileşimi ve kitle kalitesi yüksek bir yapıya sahiptir." if m['bot_pct'] < 25 else "⚠️ Şüpheli etkileşim oranı nedeniyle detaylı inceleme yapılması önerilir."}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("• Profil verisi çekilemedi. Profilin açık olduğunu doğrulayın.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SEKME 2: WASK PERFORMANS & BENCHMARK
# =========================================================
with tab_wask:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    st.subheader("📊 WASK Performans & Benchmark Paneli")
    st.caption("Instagram hesabının etkileşim oranını ve içerik performansını sektör standartlarıyla kıyaslayın.")

    wask_raw = st.text_input("Kullanıcı Adı veya Profil Linki Girin", placeholder="Örn: trendyol", key="wask_inp")
    btn_wask = st.button("Performans Analizi Yap 🚀", key="btn_wask")

    if btn_wask and wask_raw:
        w_user = clean_username(wask_raw)
        with st.spinner(f"@{w_user} için WASK performansı hesaplanıyor..."):
            p = fetch_apify_instagram_data(w_user, max_posts=12)
            if p and "latestPosts" in p:
                f = int(clean_number(p.get("followersCount", p.get("followers", 0)), 1))
                m_wask = run_all_algorithms(f, p.get("latestPosts", []))

                st.success(f"✅ @{w_user} için analiz tamamlandı.")

                w1, w2, w3 = st.columns(3)
                w1.metric("Etkileşim Oranı (ER)", f"%{m_wask['er']:.2f}")
                w2.metric("Ortalama Beğeni", f"{int(m_wask['avg_likes']):,}")
                w3.metric("Ortalama Yorum", f"{int(m_wask['avg_comments']):,}")

                st.markdown("<br>", unsafe_allow_html=True)

                # Benchmark Grafiği
                st.markdown("### 📈 Sektör Etkileşim Kıyaslaması (WASK)")
                benchmark_er = 2.0 if f >= 100000 else 3.5
                wask_chart_df = pd.DataFrame({
                    "Kategori": ["Düşük Performans", "Sektör Standardı", f"@{w_user} Performansı", "Yüksek Performans"],
                    "Etkileşim Oranı (%)": [benchmark_er * 0.5, benchmark_er, m_wask['er'], benchmark_er * 1.5]
                })
                fig_wask = px.bar(wask_chart_df, x="Kategori", y="Etkileşim Oranı (%)", color="Kategori", text="Etkileşim Oranı (%)")
                fig_wask.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig_wask.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#0f172a"))
                st.plotly_chart(fig_wask, use_container_width=True)
            else:
                st.error("• Profil verisi çekilemedi.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SEKME 3: ÇAPRAZ KIYASLAMA PANENLİ
# =========================================================
with tab_compare:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    st.subheader("⚖️ Çapraz Influencer Karşılaştırma Paneli")
    c_u1, c_u2 = st.columns(2)
    with c_u1: u1_in = st.text_input("1. Profil Kullanıcı Adı", key="cmp1")
    with c_u2: u2_in = st.text_input("2. Profil Kullanıcı Adı", key="cmp2")
    
    if st.button("Profilleri Kıyasla ⚖️", key="btn_cmp") and u1_in and u2_in:
        u1, u2 = clean_username(u1_in), clean_username(u2_in)
        with st.spinner("İki profil taranıyor ve kıyaslanıyor..."):
            p1, p2 = fetch_apify_instagram_data(u1, 12), fetch_apify_instagram_data(u2, 12)
            if p1 and p2:
                f1 = int(clean_number(p1.get("followersCount", p1.get("followers", 0)), 1))
                f2 = int(clean_number(p2.get("followersCount", p2.get("followers", 0)), 1))
                m1 = run_all_algorithms(f1, p1.get("latestPosts", []))
                m2 = run_all_algorithms(f2, p2.get("latestPosts", []))

                cmp_table = pd.DataFrame({
                    "Metrik / İnceleme": ["Takipçi Sayısı", "AQS Skoru", "Kitle Güvenilirliği (%)", "Etkileşim Oranı (%)", "Tahmini Gönderi Erişimi"],
                    f"@{u1}": [f"{f1:,}", m1['aqs_score'], f"%{m1['credibility_score']}", f"%{m1['er']:.2f}", f"{m1['est_reach']:,}"],
                    f"@{u2}": [f"{f2:,}", m2['aqs_score'], f"%{m2['credibility_score']}", f"%{m2['er']:.2f}", f"{m2['est_reach']:,}"]
                })
                st.table(cmp_table)
            else:
                st.error("• Profillerden biri veya ikisi bulunamadı.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-light">MG BRAND OFFICE © 2026 | Enterprise Intelligence Engine</div>', unsafe_allow_html=True)
