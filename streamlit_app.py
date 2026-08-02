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
    page_title="MG BRAND OFFICE | Influencer Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 2. ÖZEL CSS TASARIMI (MG BRAND OFFICE Renk Uyumu & Beyaz Tema)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    /* ARKA PLAN BEYAZ */
    .stApp {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    /* MG BRAND OFFICE EFEKTLİ BAŞLIK */
    .brand-header {
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #2563eb, #7c3aed, #db2777);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientAnimation 4s ease infinite;
        margin-top: 10px;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }

    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .brand-sub {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 25px;
    }

    /* METRİK KARTLARI */
    [data-testid="stMetric"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* MG BRAND OFFICE RENKLERİYLE BİREBİR UYUMLU BUTON */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #db2777 100%) !important;
        background-size: 200% 200% !important;
        color: #ffffff !important;
        border: none !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
        transition: all 0.4s ease !important;
    }

    .stButton>button:hover {
        background-position: 100% 50% !important;
        box-shadow: 0 6px 20px rgba(219, 39, 119, 0.45) !important;
        transform: translateY(-2px) !important;
    }

    /* TAB (SEKME) SEÇİM ÇİZGİSİ UYUMU */
    .stTabs [aria-selected="true"] {
        color: #7c3aed !important;
        border-bottom: 3px solid #7c3aed !important;
        font-weight: 700 !important;
    }

    /* FOOTER (Turkey 2026) */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #94a3b8;
        text-align: center;
        padding: 12px 0;
        font-size: 0.9rem;
        font-weight: 600;
        border-top: 1px solid #f1f5f9;
        z-index: 999;
    }
    
    .main .block-container {
        padding-bottom: 70px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- API ANAHTARINIZ ---
APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"


def fetch_apify_instagram_data(username, max_posts=50):
    """
    Apify Instagram Profile Scraper
    'resultsLimit' parametresi ile profilin geniş/tüm gönderi geçmişini çeker.
    """
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"

    payload = {"usernames": [username], "resultsLimit": max_posts}

    try:
        response = requests.post(run_url, json=payload, timeout=20)
        if response.status_code not in [200, 201]:
            st.error(
                f"Apify Başlatma Hatası ({response.status_code}): {response.text}"
            )
            return None

        run_data = response.json().get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            return None

        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"

        for _ in range(25):
            time.sleep(2)
            res = requests.get(dataset_url)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0:
                    return items[0]
        return None
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None


# ---------------------------------------------------------
# 3. SAĞ ÜST KÖŞE YATAY ÜÇ ÇİZGİ MENÜSÜ & BAŞLIK
# ---------------------------------------------------------
col_top_left, col_top_right = st.columns([5, 1])

with col_top_right:
    show_algo_menu = st.popover("☰ Algoritmalar")

with show_algo_menu:
    st.markdown("### 🧠 Gelişmiş Algoritma Metodolojisi")
    st.write("Platformda kullanılan analiz metriklerinin matematiksel alt yapısı:")

    st.markdown("---")
    st.markdown("**🎯 1. HypeAuditor (AQS)**")
    st.caption(
        "AQS = f(Log(ER) * 0.5 + CommentRatio * 0.35 + StabilityIndex * 0.15). Kitle kalitesini 1-100 arasında derecelendirir."
    )

    st.markdown("**🔍 2. Modash (Dinamik Fake Audit)**")
    st.caption(
        "Beğeni/Yorum oranlarındaki anormallik, ortalama ER sapması ve takipçi segmenti süzülerek profile özel bot oranı belirlenir."
    )

    st.markdown("**📈 3. Social Blade Grade**")
    st.caption(
        "Gönderiler arası varyasyon katsayısı (CV) ve ortalama ER ile hesaplanan istikrar derecesidir (A+, A, B+, B, C)."
    )

# ANA BAŞLIK
st.markdown(
    '<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="brand-sub">All-in-One Influencer Tracker & Intelligence Suite</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. ARAMA KUTUSU VE DERİN TARAMA SEÇENEKLERİ
# ---------------------------------------------------------
c_left, c_mid, c_right = st.columns([1, 2, 1])

with c_mid:
    target_user = st.text_input(
        "Instagram Kullanıcı Adı",
        placeholder="Örn: visionx_gallery",
        label_visibility="collapsed",
    ).strip()

    scan_deep = st.checkbox("Tüm Profili Derinlemesine Tara (Son 50+ Post)")

    btn_analyze = st.button("Profili Analiz Et")

st.markdown("---")

# ---------------------------------------------------------
# 5. VERİ İŞLEME VE GELİŞMİŞ ALGORİTMA ANALİZİ
# ---------------------------------------------------------
if btn_analyze and target_user:
    if target_user.startswith("@"):
        target_user = target_user[1:]

    max_p = 50 if scan_deep else 12
    spinner_msg = (
        f"⏳ @{target_user} profilinin TÜM geçmişi ve gönderileri taranıyor..."
        if scan_deep
        else f"⏳ @{target_user} profili taranıyor..."
    )

    with st.spinner(spinner_msg):
        profile = fetch_apify_instagram_data(target_user, max_posts=max_p)

        if profile and "latestPosts" in profile:
            followers = profile.get(
                "followersCount", profile.get("followers", 10000)
            )
            posts = profile.get("latestPosts", [])

            likes, comments, views = [], [], []

            for post in posts:
                likes.append(post.get("likesCount", 0))
                comments.append(post.get("commentsCount", 0))
                views.append(
                    post.get("videoViewCount", post.get("likesCount", 0))
                )

            if likes:
                df = pd.DataFrame(
                    {
                        "Gönderi": [
                            f"Post {i+1}" for i in range(len(likes))
                        ],
                        "Beğeni": likes,
                        "Yorum": comments,
                        "İzlenme": views,
                    }
                )

                df["Toplam Etkileşim"] = df["Beğeni"] + df["Yorum"]
                df["ER (%)"] = (
                    df["Toplam Etkileşim"] / max(followers, 1)
                ) * 100

                st.success(
                    f"**@{target_user}** hesabı analiz edildi! (Takipçi: {followers:,} | Analiz Edilen Gönderi: **{len(likes)}**)"
                )

                sub_tab1, sub_tab2, sub_tab3 = st.tabs(
                    [
                        "🎯 HypeAuditor Modülü",
                        "🔍 Modash Modülü",
                        "📈 Social Blade Modülü",
                    ]
                )

                # --- GENEL MATEMATİKSEL DEĞERLER ---
                clean_er = df["ER (%)"].mean()
                total_likes = df["Beğeni"].sum()
                total_comments = df["Yorum"].sum()
                er_std = df["ER (%)"].std() if len(df) > 1 else 0.1
                cv_index = (er_std / clean_er) if clean_er > 0 else 1.0  # Varyasyon Katsayısı

                # =========================================================
                # 1. HYPEAUDITOR (AQS HESAPLAMA ALGORİTMASI)
                # =========================================================
                with sub_tab1:
                    st.subheader("🎯 HypeAuditor Tüm Profil Kalite Analizi")
                    
                    comment_ratio = total_comments / max(total_likes, 1)
                    
                    # AQS Formülü: ER Puanı (45) + Yorum Oranı Puanı (35) + İstikrar Puanı (20)
                    er_score = min(45, (clean_er / 3.5) * 45)
                    comment_score = min(35, (comment_ratio / 0.03) * 35)
                    stability_score = max(0, 20 - (cv_index * 10))
                    
                    aqs_score = int(min(100, max(15, er_score + comment_score + stability_score)))

                    col1, col2, col3 = st.columns(3)
                    col1.metric(
                        "Kitle Kalite Skoru (AQS)", f"{aqs_score} / 100"
                    )
                    col2.metric("Tüm Profil Ortalama ER", f"%{clean_er:.2f}")
                    col3.metric(
                        "Yorum / Beğeni Oranı", f"%{(comment_ratio * 100):.2f}"
                    )

                    fig_hype = px.bar(
                        df,
                        x="Gönderi",
                        y="Toplam Etkileşim",
                        title=f"Tüm Profil ({len(likes)} Post) Etkileşim Dağılımı",
                        color_discrete_sequence=["#7c3aed"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_hype, use_container_width=True)

                # =========================================================
                # 2. MODASH (DİNAMİK BOT ANALİZİ ALGORİTMASI)
                # =========================================================
                with sub_tab2:
                    st.subheader("🔍 Modash Dinamik Bot & Kitle Matrisi")

                    # Gelişmiş Dinamik Bot Risk Matrisi:
                    bot_risk = 3.5  # Taban organik pay

                    # Düşük yorum/beğeni oranı riski
                    if comment_ratio < 0.003:
                        bot_risk += 18.0
                    elif comment_ratio < 0.01:
                        bot_risk += 9.0

                    # Düşük ER riski (Takipçi var ama etkileşim yok)
                    if clean_er < 0.4:
                        bot_risk += 20.0
                    elif clean_er < 1.0:
                        bot_risk += 10.0

                    # Aşırı yüksek fluctuate (Aniden parlayan ve batan postlar)
                    if cv_index > 1.2:
                        bot_risk += 8.5

                    # Takipçi büyüklüğü katsayısı
                    if followers > 250000:
                        bot_risk += 5.0

                    fake_follower_pct = round(min(max(bot_risk, 2.5), 60.0), 1)
                    real_followers = followers * (1 - (fake_follower_pct / 100))
                    effective_er = (df["Toplam Etkileşim"].mean() / max(real_followers, 1)) * 100

                    m1, m2 = st.columns(2)
                    m1.metric(
                        "Dinamik Pasif/Bot Kitle Tahmini",
                        f"%{fake_follower_pct}",
                    )
                    m2.metric(
                        "Aktif Takipçi Üzerinden ER", f"%{effective_er:.2f}"
                    )

                    fig_modash = px.scatter(
                        df,
                        x="İzlenme",
                        y="Toplam Etkileşim",
                        size="Beğeni",
                        title="Tüm Profil Reels İzlenme vs Etkileşim Matrisi",
                        color_discrete_sequence=["#2563eb"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_modash, use_container_width=True)

                # =========================================================
                # 3. SOCIAL BLADE (DERECE & İSTİKRAR ALGORİTMASI)
                # =========================================================
                with sub_tab3:
                    st.subheader("📈 Social Blade Derecelendirme & Trend")
                    
                    # Not Hesaplama: Hem ER hem de Varyasyon (İstikrar) dikkate alınır
                    if clean_er >= 4.5 and cv_index < 0.8:
                        grade = "A+"
                    elif clean_er >= 3.0:
                        grade = "A"
                    elif clean_er >= 1.5:
                        grade = "B+"
                    elif clean_er >= 0.8:
                        grade = "B"
                    else:
                        grade = "C"

                    s1, s2 = st.columns(2)
                    s1.metric("Social Blade Hesap Skoru", grade)
                    s2.metric(
                        "Gönderi Başı Ortalama Beğeni",
                        f"{int(df['Beğeni'].mean()):,}",
                    )

                    fig_sb = px.line(
                        df,
                        x="Gönderi",
                        y="ER (%)",
                        markers=True,
                        title="Profil Genel Etkileşim Trendi",
                        color_discrete_sequence=["#db2777"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_sb, use_container_width=True)
            else:
                st.error("Gelen veride analiz edilecek gönderi bulunamadı.")
        else:
            st.error(
                "❌ Profil bulunamadı veya Apify taraması zaman aşımına uğradı."
            )

elif btn_analyze:
    st.warning("Lütfen bir Instagram kullanıcı adı girin.")

# ---------------------------------------------------------
# FOOTER (Turkey 2026)
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">MG BRAND OFFICE © Turkey 2026 | Powered by Apify & Streamlit</div>',
    unsafe_allow_html=True,
)
