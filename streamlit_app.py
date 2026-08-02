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
# 2. ÖZEL CSS TASARIMI
# ---------------------------------------------------------
st.markdown(
    """
<style>
    .stApp {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

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

    .stTabs [aria-selected="true"] {
        color: #7c3aed !important;
        border-bottom: 3px solid #7c3aed !important;
        font-weight: 700 !important;
    }

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

# --- API CONFIGURATION ---
APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"


def fetch_apify_instagram_data(username, max_posts=50):
    """Apify actor vasıtasıyla Instagram ham verisini çeker ve izole eder."""
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"

    payload = {"usernames": [username], "resultsLimit": int(max_posts)}

    try:
        response = requests.post(run_url, json=payload, timeout=20)
        if response.status_code not in [200, 201]:
            st.error(f"API Hatası ({response.status_code}): {response.text}")
            return None

        run_data = response.json().get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            return None

        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"

        # Polling döngüsü
        for _ in range(35):
            time.sleep(2)
            res = requests.get(dataset_url)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0:
                    return items[0]
        return None
    except Exception as e:
        st.error(f"Baglanti Hatasi: {e}")
        return None


def clean_number(value, default=0):
    """Veri tipini garanti altına alan sanitleştirici."""
    if value is None:
        return default
    try:
        val = float(value)
        return default if math.isnan(val) else val
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------
# 3. KONTROL PANELI VE POP-OVER
# ---------------------------------------------------------
col_top_left, col_top_right = st.columns([5, 1])

with col_top_right:
    show_algo_menu = st.popover("☰ Algoritma Mantığı")

with show_algo_menu:
    st.markdown("### 📐 Tam Doğruluklu Hesaplama Modeli")
    st.markdown("---")
    st.markdown("**1. HypeAuditor (AQS):**")
    st.caption("AQS = 100 * [ (ER_Score * 0.40) + (CommentRatio_Score * 0.40) + (Stability_Score * 0.20) ]")
    st.markdown("**2. Modash (Bot / Fake Audit):**")
    st.caption("Takipçi skalasına bağlı beklenen ER ile gerçekleşen ER farkı + Yorum/Beğeni anormallik varyansı.")
    st.markdown("**3. Social Blade Grade:**")
    st.caption("Medyan ER ve Varyasyon Katsayısı (CV) matrisi üzerinden harf derecelemesi.")

st.markdown('<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-sub">All-in-One Influencer Tracker & Intelligence Suite</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. ARAMA VE TARAMA BÖLÜMÜ
# ---------------------------------------------------------
c_left, c_mid, c_right = st.columns([1, 2, 1])

with c_mid:
    target_user = st.text_input(
        "Instagram Kullanıcı Adı",
        placeholder="Örn: visionx_gallery",
        label_visibility="collapsed",
    ).strip()

    scan_deep = st.checkbox("Derin Profil Analizi Yap (Son 50+ Gönderi)")
    btn_analyze = st.button("Profili Analiz Et")

st.markdown("---")

# ---------------------------------------------------------
# 5. GERÇEKÇİ HESAPLAMA MOTORU
# ---------------------------------------------------------
if btn_analyze and target_user:
    if target_user.startswith("@"):
        target_user = target_user[1:]

    max_p = 50 if scan_deep else 12
    spinner_msg = f"⏳ @{target_user} profili çekiliyor ve matematiksel doğrulamadan geçiriliyor..."

    with st.spinner(spinner_msg):
        profile = fetch_apify_instagram_data(target_user, max_posts=max_p)

        if profile and "latestPosts" in profile:
            # 1. Takipçi Sayısını Kesinleştir
            raw_followers = profile.get("followersCount", profile.get("followers", 0))
            followers = int(clean_number(raw_followers, default=1000))
            followers = max(followers, 1) # Division by zero engeli

            raw_posts = profile.get("latestPosts", [])
            
            likes_list = []
            comments_list = []
            views_list = []

            for p in raw_posts:
                l = clean_number(p.get("likesCount"), 0)
                c = clean_number(p.get("commentsCount"), 0)
                v = clean_number(p.get("videoViewCount"), l) # Video değilse izlenmeyi beğeniye eşitleme, direkt l alıyoruz
                
                likes_list.append(l)
                comments_list.append(c)
                views_list.append(v)

            if len(likes_list) > 0:
                df = pd.DataFrame({
                    "Gönderi": [f"Post {i+1}" for i in range(len(likes_list))],
                    "Beğeni": likes_list,
                    "Yorum": comments_list,
                    "İzlenme": views_list
                })

                df["Toplam Etkileşim"] = df["Beğeni"] + df["Yorum"]
                df["ER (%)"] = (df["Toplam Etkileşim"] / followers) * 100.0

                st.success(
                    f"**@{target_user}** analizi tamamlandı. "
                    f"(Takipçi: **{followers:,}** | İşlenen Gönderi: **{len(df)}**)"
                )

                sub_tab1, sub_tab2, sub_tab3 = st.tabs(
                    [
                        "🎯 HypeAuditor Modülü",
                        "🔍 Modash Modülü",
                        "📈 Social Blade Modülü",
                    ]
                )

                # --- TEMEL İSTATİSTİKİ VERİLER ---
                mean_er = float(df["ER (%)"].mean())
                median_er = float(df["ER (%)"].median())
                std_er = float(df["ER (%)"].std()) if len(df) > 1 else 0.0
                
                sum_likes = float(df["Beğeni"].sum())
                sum_comments = float(df["Yorum"].sum())
                
                comment_to_like_ratio = sum_comments / max(sum_likes, 1.0)
                
                # Variation Coefficient (CV) - İstikrar Endeksi
                cv = (std_er / mean_er) if mean_er > 0 else 1.0

                # =========================================================
                # 1. HYPEAUDITOR (AQS REALISTIC SCORE)
                # =========================================================
                with sub_tab1:
                    st.subheader("🎯 HypeAuditor Kitle Kalite Analizi (AQS)")

                    # Takipçi Büyüklüğüne Göre Hedef ER (Benchmark)
                    if followers < 20000:
                        benchmark_er = 3.5
                    elif followers < 100000:
                        benchmark_er = 2.0
                    elif followers < 1000000:
                        benchmark_er = 1.2
                    else:
                        benchmark_er = 0.8

                    # 1. ER Puanı (Max 40)
                    er_score = min(40.0, (mean_er / benchmark_er) * 40.0)
                    
                    # 2. Yorum Kalitesi Puanı (Ideal yorum/beğeni %1.5 - %4.0 arası) (Max 40)
                    if comment_to_like_ratio >= 0.015:
                        comment_score = 40.0
                    else:
                        comment_score = (comment_to_like_ratio / 0.015) * 40.0

                    # 3. İçerik İstikrar Puanı (CV yükseldikçe puan düşer) (Max 20)
                    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))

                    # Toplam AQS
                    final_aqs = int(np.clip(er_score + comment_score + stability_score, 10, 99))

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Gerçek Kalite Skoru (AQS)", f"{final_aqs} / 100")
                    c2.metric("Ortalama ER", f"%{mean_er:.2f}")
                    c3.metric("Yorum / Beğeni Oranı", f"%{(comment_to_like_ratio * 100):.2f}")

                    fig_hype = px.bar(
                        df,
                        x="Gönderi",
                        y="Toplam Etkileşim",
                        title="Gönderi Başına Etkileşim Miktarı",
                        color_discrete_sequence=["#7c3aed"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_hype, use_container_width=True)

                # =========================================================
                # 2. MODASH (MATEMATİKSEL BOT/GÜVENİLİRLİK HESABI)
                # =========================================================
                with sub_tab2:
                    st.subheader("🔍 Modash Gerçekçi Kitle Matrisi")

                    # Bot Oranı Tespiti İçin 3 Parametreli Model
                    bot_penalty = 0.0

                    # A) Düşük ER Cezası
                    if mean_er < (benchmark_er * 0.4):
                        bot_penalty += 25.0
                    elif mean_er < (benchmark_er * 0.7):
                        bot_penalty += 12.0

                    # B) Anormal Düşük Yorum Cezası (Sadece Beğeni Satın Alınmış Olabilir)
                    if comment_to_like_ratio < 0.003:
                        bot_penalty += 20.0
                    elif comment_to_like_ratio < 0.008:
                        bot_penalty += 8.0

                    # C) Aşırı Düzensiz Etkileşim Dalgalanması
                    if cv > 1.4:
                        bot_penalty += 10.0

                    # Doğal Pasif Kitle Tabanı: %4.0
                    estimated_fake_pct = float(np.clip(4.0 + bot_penalty, 3.0, 75.0))
                    
                    real_audience = int(followers * (1.0 - (estimated_fake_pct / 100.0)))
                    real_er = (df["Toplam Etkileşim"].mean() / max(real_audience, 1)) * 100.0

                    m1, m2 = st.columns(2)
                    m1.metric("Tahmini Pasif / Şüpheli Kitle", f"%{estimated_fake_pct:.1f}")
                    m2.metric("Organik Kitle Üzerinden ER", f"%{real_er:.2f}")

                    fig_modash = px.scatter(
                        df,
                        x="İzlenme",
                        y="Toplam Etkileşim",
                        size="Beğeni",
                        title="İzlenme - Etkileşim Dağılım Matrisi",
                        color_discrete_sequence=["#2563eb"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_modash, use_container_width=True)

                # =========================================================
                # 3. SOCIAL BLADE (GRADE METRİĞİ)
                # =========================================================
                with sub_tab3:
                    st.subheader("📈 Social Blade Derecelendirmesi")

                    # Not Skalası (Medyan ER ve Varyasyon Katsayısı Bileşimi)
                    if median_er >= (benchmark_er * 1.5) and cv < 0.8:
                        grade = "A+"
                    elif median_er >= benchmark_er:
                        grade = "A"
                    elif median_er >= (benchmark_er * 0.6):
                        grade = "B+"
                    elif median_er >= (benchmark_er * 0.3):
                        grade = "B"
                    else:
                        grade = "C"

                    s1, s2 = st.columns(2)
                    s1.metric("Social Blade Hesap Skoru", grade)
                    s2.metric("Ortalama Beğeni / Post", f"{int(df['Beğeni'].mean()):,}")

                    fig_sb = px.line(
                        df,
                        x="Gönderi",
                        y="ER (%)",
                        markers=True,
                        title="Gönderi Bazlı Performans Çizgisi",
                        color_discrete_sequence=["#db2777"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_sb, use_container_width=True)
            else:
                st.error("Gelen veride işlenebilir gönderi sayısı 0. Profil gizli veya boş olabilir.")
        else:
            st.error("❌ Profil verisi çekilemedi. Apify taraması zaman aşımına uğramış olabilir.")

elif btn_analyze:
    st.warning("Lütfen analiz etmek istediğiniz kullanıcı adını girin.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">MG BRAND OFFICE © Turkey 2026 | Powered by Apify & Streamlit</div>',
    unsafe_allow_html=True,
)
