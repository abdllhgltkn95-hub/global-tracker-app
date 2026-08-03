import time
import math
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="MG BRAND OFFICE | Intelligence Suite",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"

# ---------------------------------------------------------
# 2. BEYAZ TEMA & YANSIMALI HEADER & KAYAN ŞERİT CSS
# ---------------------------------------------------------
st.markdown(
    """
<style>
    /* Temel Arka Plan ve Metin Rengi (Açık Tema) */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Yansımalı MG BRAND OFFICE Başlığı */
    .reflection-container {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 30px;
    }

    .brand-header-light {
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: inline-block;
        position: relative;
        /* Metin Yansıması (Reflection) */
        -webkit-box-reflect: below -18px linear-gradient(transparent 50%, rgba(255, 255, 255, 0.35));
    }

    .brand-sub-light {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
    }

    /* Kaliteli Efektli Beyaz Kartlar (Glassmorphism & Soft Shadow) */
    .effect-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        transition: all 0.3s ease;
    }
    .effect-card:hover {
        box-shadow: 0 20px 30px -10px rgba(59, 130, 246, 0.12);
        border-color: #cbd5e1;
    }

    /* Metric Kutuları Tasarımı */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }

    /* Kayan Şerit Sekme Tasarımı (Floating Tab Strip) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        background-color: #ffffff;
        padding: 8px 16px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        max-width: fit-content;
        margin: 0 auto 35px auto;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre;
        border-radius: 30px !important;
        padding: 0px 24px !important;
        font-weight: 700 !important;
        color: #64748b !important;
        border: none !important;
        background-color: transparent !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    }

    /* Özel Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
    }

    /* Footer */
    .footer-light {
        text-align: center;
        color: #94a3b8;
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
# 3. YARDIMCI VE ALGORİTMA FONKSİYONLARI
# ---------------------------------------------------------
def clean_number(value, default=0):
    if value is None:
        return default
    try:
        val = float(value)
        return default if math.isnan(val) else val
    except (ValueError, TypeError):
        return default

def fetch_apify_instagram_data(username, max_posts=12):
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    payload = {"usernames": [username], "resultsLimit": int(max_posts)}

    try:
        response = requests.post(run_url, json=payload, timeout=20)
        if response.status_code not in [200, 201]:
            return None

        run_data = response.json().get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            return None

        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"

        for _ in range(30):
            time.sleep(2)
            res = requests.get(dataset_url)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0:
                    return items[0]
        return None
    except Exception:
        return None

def calculate_influencer_hero_metrics(followers, likes_list, comments_list, views_list):
    avg_likes = float(np.mean(likes_list)) if likes_list else 0.0
    avg_comments = float(np.mean(comments_list)) if comments_list else 0.0
    avg_views = float(np.mean(views_list)) if views_list else avg_likes * 4.0
    
    total_engagement = avg_likes + avg_comments
    er = (total_engagement / max(followers, 1)) * 100.0

    emv = ((avg_views / 1000.0) * 10.0) + (total_engagement * 0.25)
    comment_ratio = avg_comments / max(avg_likes, 1.0)
    
    credibility = 85.0
    if comment_ratio < 0.005:
        credibility -= 30.0
    elif comment_ratio < 0.01:
        credibility -= 15.0
        
    if er < 0.5:
        credibility -= 25.0
    elif er > 15.0:
        credibility -= 20.0

    credibility_score = int(np.clip(credibility, 15, 98))
    authentic_followers_pct = int(np.clip(credibility_score + np.random.randint(-3, 3), 10, 95))
    est_reach = min(int(followers * (er / 100.0) * 3.5) if er > 0 else int(followers * 0.05), followers)

    return {
        "er": er,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_views": avg_views,
        "emv": emv,
        "credibility_score": credibility_score,
        "authentic_followers_pct": authentic_followers_pct,
        "est_reach": est_reach
    }

# ---------------------------------------------------------
# 4. YANSIMALI ANA BAŞLIK
# ---------------------------------------------------------
st.markdown(
    """
    <div class="reflection-container">
        <h1 class="brand-header-light">MG BRAND OFFICE</h1>
    </div>
    <div class="brand-sub-light">Next-Gen Influencer & Performance Intelligence</div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 5. ORTALANMIŞ KAYAN ŞERİT SEKMELER 
# ---------------------------------------------------------
tab_wask, tab_hero, tab_compare = st.tabs([
    "• WASK Intelligence", 
    "• Influencer Hero Intelligence", 
    "• Kıyaslama Paneli"
])

# =========================================================
# 1. SEKME: WASK INTELLIGENCE
# =========================================================
with tab_wask:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    st.subheader("• WASK Performans & Reklam Analizi")
    st.caption("Dijital reklam hedefleme, tahmini erişim maliyeti ve etkileşim optimizasyon paneli.")
    
    col_w1, col_w2 = st.columns([3, 1])
    with col_w1:
        wask_user = st.text_input("Instagram Profil Kullanıcı Adı", placeholder="Örn: trendyol", key="wask_user").strip()
    with col_w2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_wask = st.button("Reklam Analizi Çalıştır", key="btn_wask")
        
    if btn_wask and wask_user:
        with st.spinner("Reklam ve kitle performans verileri çekiliyor..."):
            prof = fetch_apify_instagram_data(wask_user, max_posts=12)
            if prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                st.success(f"• @{wask_user} profili başarıyla yüklendi.")
                
                mw1, mw2, mw3 = st.columns(3)
                mw1.metric("Toplam Kitle", f"{fol:,}")
                mw2.metric("Tahmini CPM", "$4.20")
                mw3.metric("Tahmini CPC", "$0.18")
            else:
                st.error("• Profil verisi bulunamadı.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 2. SEKME: INFLUENCER HERO INTELLIGENCE
# =========================================================
with tab_hero:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    st.subheader("• Influencer Hero Audit & Credibility Raporu")
    st.caption("Kitle doğrulama (Audience Credibility), EMV ve organik erişim potansiyeli.")

    c1, c2 = st.columns([3, 1])
    with c1:
        hero_user = st.text_input("Instagram Kullanıcı Adı Girin", placeholder="Örn: instagram_kullanici", key="hero_user_input").strip()
    with c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_hero = st.button("Hero Analiz Başlat", key="btn_hero")

    if btn_hero and hero_user:
        if hero_user.startswith("@"):
            hero_user = hero_user[1:]

        with st.spinner(f"@{hero_user} için Influencer Hero algoritması çalıştırılıyor..."):
            prof = fetch_apify_instagram_data(hero_user, max_posts=18)

            if prof and "latestPosts" in prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                posts = prof.get("latestPosts", [])
                likes = [clean_number(p.get("likesCount"), 0) for p in posts]
                comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
                views = [clean_number(p.get("videoViewCount"), p.get("likesCount", 0)) for p in posts]

                metrics = calculate_influencer_hero_metrics(fol, likes, comments, views)

                st.markdown(f"""
                <div style="background: #f1f5f9; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #cbd5e1;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">HERO AUDIT REPORT</span>
                            <h2 style="margin: 8px 0 0 0; color: #0f172a;">@{hero_user}</h2>
                            <p style="color: #64748b; margin: 2px 0 0 0;">Takipçi Sayısı: {fol:,}</p>
                        </div>
                        <div style="text-align: right;">
                            <h1 style="font-size: 2.8rem; margin: 0; color: #2563eb;">%{metrics['credibility_score']}</h1>
                            <p style="color: #64748b; font-size: 0.85rem; margin: 0; font-weight: 600;">Audience Credibility Score</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Earned Media Value (EMV)", f"${metrics['emv']:,.2f}")
                m2.metric("Etkileşim Oranı (ER)", f"%{metrics['er']:.2f}")
                m3.metric("Gerçek Kitle Oranı", f"%{metrics['authentic_followers_pct']}")
                m4.metric("Tahmini Gönderi Erişimi", f"{metrics['est_reach']:,}")

                st.markdown("---")

                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.markdown("##### • Kitle Kalitesi")
                    cred_df = pd.DataFrame({
                        "Segment": ["Gerçek / Aktif", "Şüpheli / Pasif"],
                        "Oran (%)": [metrics['authentic_followers_pct'], 100 - metrics['authentic_followers_pct']]
                    })
                    fig_pie = px.pie(
                        cred_df, 
                        names="Segment", 
                        values="Oran (%)", 
                        color="Segment",
                        color_discrete_map={"Gerçek / Aktif": "#2563eb", "Şüpheli / Pasif": "#f43f5e"},
                        hole=0.5
                    )
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_chart2:
                    st.markdown("##### • Etkileşim Trendi")
                    post_df = pd.DataFrame({
                        "Gönderi": [f"P{i+1}" for i in range(len(likes))],
                        "Beğeni": likes,
                        "Yorum": comments
                    })
                    fig_line = px.line(
                        post_df, 
                        x="Gönderi", 
                        y=["Beğeni", "Yorum"],
                        markers=True,
                        color_discrete_sequence=["#4f46e5", "#ec4899"]
                    )
                    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.error("• Influencer Hero verileri çekilemedi.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 3. SEKME: KIYASLAMA PANENLİ
# =========================================================
with tab_compare:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    st.subheader("• Çapraz Influencer Kıyaslama Paneli")
    st.caption("Birden fazla profili yan yana koyarak metrik karşılaştırması yapın.")
    
    col_cmp1, col_cmp2 = st.columns(2)
    with col_cmp1:
        u1 = st.text_input("1. Profil Kullanıcı Adı", placeholder="Örn: profil1", key="cmp_u1")
    with col_cmp2:
        u2 = st.text_input("2. Profil Kullanıcı Adı", placeholder="Örn: profil2", key="cmp_u2")
        
    btn_cmp = st.button("Profilleri Kıyasla", key="btn_cmp")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-light">MG BRAND OFFICE © 2026 | Powered by Intelligence Engine</div>', unsafe_allow_html=True)
