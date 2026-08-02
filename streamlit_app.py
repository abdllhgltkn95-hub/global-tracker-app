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
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"

    payload = {"usernames": [username], "resultsLimit": int(max_posts)}

    try:
        response = requests.post(run_url, json=payload, timeout=20)
        if response.status_code not in [200, 201]:
            st.error(f"Apify Başlatma Hatası ({response.status_code}): {response.text}")
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
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None


# Helper safe converter
def safe_int(val, default=0):
    try:
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------
# 3. SAĞ ÜST KÖŞE POP-OVER MENÜ VE BAŞLIK
# ---------------------------------------------------------
col_top_left, col_top_right = st.columns([5, 1])

with col_top_right:
    show_algo_menu = st.popover("☰ Algoritmalar")

with show_algo_menu:
    st.markdown("### 🧠 Revize Edilmiş Algoritma Modeli")
    st.write("Performans ve doğruluk odaklı matematiksel güncellemeler:")

    st.markdown("---")
    st.markdown("**🎯 1. HypeAuditor (AQS)**")
    st.caption("AQS = Sigmoid(Normalized ER) * 40 + Comment/Like Quality * 40 + Stability * 20. Ölçek 1-100 arasında sınırlandırılmıştır.")

    st.markdown("**🔍 2. Modash (Dinamik Bot Analizi)**")
    st.caption("Takipçi skalasına göre normalize edilmiş ER beklentisi ve yorum/beğeni uyumsuzluk katsayısı ile dinamik risk oranlanır.")

    st.markdown("**📈 3. Social Blade Grade**")
    st.caption("Düzeltilmiş Medyan ER ve Varyasyon Katsayısı (CV = Std/Mean) bileşimiyle harf notlandırması yapılır.")

# ANA BAŞLIK
st.markdown('<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
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
# 5. GELİŞMİŞ VE REVİZE EDİLMİŞ ALGORİTMA ANALİZİ
# ---------------------------------------------------------
if btn_analyze and target_user:
    if target_user.startswith("@"):
        target_user = target_user[1:]

    max_p = 50 if scan_deep else 12
    spinner_msg = (
        f"⏳ @{target_user} profilinin detaylı geçmiş verileri taranıyor..."
        if scan_deep
        else f"⏳ @{target_user} profili taranıyor..."
    )

    with st.spinner(spinner_msg):
        profile = fetch_apify_instagram_data(target_user, max_posts=max_p)

        if profile and "latestPosts" in profile:
            followers = safe_int(profile.get("followersCount", profile.get("followers", 0)), default=1000)
            followers = max(followers, 1) # Sıfıra bölünmeyi önle

            raw_posts = profile.get("latestPosts", [])

            likes, comments, views = [], [], []

            for post in raw_posts:
                l = safe_int(post.get("likesCount", 0))
                c = safe_int(post.get("commentsCount", 0))
                v = safe_int(post.get("videoViewCount", l))
                likes.append(l)
                comments.append(c)
                views.append(v)

            if len(likes) > 0:
                df = pd.DataFrame({
                    "Gönderi": [f"Post {i+1}" for i in range(len(likes))],
                    "Beğeni": likes,
                    "Yorum": comments,
                    "İzlenme": views,
                })

                df["Toplam Etkileşim"] = df["Beğeni"] + df["Yorum"]
                df["ER (%)"] = (df["Toplam Etkileşim"] / followers) * 100

                st.success(
                    f"**@{target_user}** hesabı başarıyla doğrulandı ve analiz edildi! "
                    f"(Takipçi: {followers:,} | İncelenen Post Sayısı: **{len(likes)}**)"
                )

                sub_tab1, sub_tab2, sub_tab3 = st.tabs(
                    [
                        "🎯 HypeAuditor Modülü",
                        "🔍 Modash Modülü",
                        "📈 Social Blade Modülü",
                    ]
                )

                # --- GENEL MATEMATİKSEL DEĞERLER (REVİZE EDİLDİ) ---
                mean_er = float(df["ER (%)"].mean())
                median_er = float(df["ER (%)"].median())
                total_likes = sum(likes)
                total_comments = sum(comments)
                
                # Standart Sapma ve Varyasyon Katsayısı (CV)
                std_er = float(df["ER (%)"].std()) if len(df) > 1 else 0.0
                cv_index = (std_er / mean_er) if mean_er > 0 else 0.0

                # Yorum / Beğeni Dengesi
                comment_like_ratio = (total_comments / max(total_likes, 1))

                # =========================================================
                # 1. HYPEAUDITOR (SİGMOİD VE LOGARİTMİK AQS REVIZYONU)
                # =========================================================
                with sub_tab1:
                    st.subheader("🎯 HypeAuditor Profil Kalite Analizi (AQS)")

                    # Sigmoidal ER Skoru (Sektör Standartı Benchmark: ~%2.0 ER ideal kabul edilir)
                    er_norm = 1 / (1 + math.exp(-1.2 * (mean_er - 2.0)))
                    er_part = er_norm * 40.0

                    # Yorum Kalitesi Skoru (Ideali %2 ile %5 arası yorum/beğeni oranıdır)
                    comm_norm = min(1.0, comment_like_ratio / 0.03)
                    comm_part = comm_norm * 40.0

                    # İstikrar Skoru (Düşük varyasyon daha yüksek puan getirir)
                    stab_part = max(0.0, 20.0 * (1.0 - min(cv_index, 1.0)))

                    # Toplam AQS
                    aqs_score = int(np.clip(er_part + comm_part + stab_part, 10, 99))

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Kitle Kalite Skoru (AQS)", f"{aqs_score} / 100")
                    col2.metric("Ortalama ER", f"%{mean_er:.2f}")
                    col3.metric("Yorum / Beğeni Oranı", f"%{(comment_like_ratio * 100):.2f}")

                    fig_hype = px.bar(
                        df,
                        x="Gönderi",
                        y="Toplam Etkileşim",
                        title=f"Gönderi Başına Etkileşim Dağılımı ({len(likes)} Post)",
                        color_discrete_sequence=["#7c3aed"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_hype, use_container_width=True)

                # =========================================================
                # 2. MODASH (DİNAMİK RİSK VE BOT SKORU REVIZYONU)
                # =========================================================
                with sub_tab2:
                    st.subheader("🔍 Modash Dinamik Bot & Kitle Matrisi")

                    # Büyüklüğe göre beklenen ideal ER hesabı (Takipçi arttıkça ER doğal düşer)
                    if followers < 10000:
                        expected_er = 3.0
                    elif followers < 100000:
                        expected_er = 1.8
                    elif followers < 1000000:
                        expected_er = 1.2
                    else:
                        expected_er = 0.8

                    bot_risk_score = 3.0  # Doğal taban pasif kitle payı

                    # Risk 1: ER beklentinin çok altındaysa
                    if mean_er < (expected_er * 0.3):
                        bot_risk_score += 22.0
                    elif mean_er < (expected_er * 0.6):
                        bot_risk_score += 12.0

                    # Risk 2: Yorum oranı aşırı düşükse (sadece bot beğeni basılmış riski)
                    if comment_like_ratio < 0.002:
                        bot_risk_score += 18.0
                    elif comment_like_ratio < 0.008:
                        bot_risk_score += 8.0

                    # Risk 3: Düzenli değil, aşırı dengesiz dalgalanma varsa
                    if cv_index > 1.5:
                        bot_risk_score += 10.0

                    fake_follower_pct = round(float(np.clip(bot_risk_score, 2.5, 65.0)), 1)
                    real_followers = int(followers * (1.0 - (fake_follower_pct / 100.0)))
                    
                    # Gerçek takipçi üzerinden efektif ER
                    effective_er = (df["Toplam Etkileşim"].mean() / max(real_followers, 1)) * 100.0

                    m1, m2 = st.columns(2)
                    m1.metric("Tahmini Pasif / Bot Takipçi Oranı", f"%{fake_follower_pct}")
                    m2.metric("Organik Kitle Üzerinden ER", f"%{effective_er:.2f}")

                    fig_modash = px.scatter(
                        df,
                        x="İzlenme",
                        y="Toplam Etkileşim",
                        size="Beğeni",
                        title="İzlenme vs Toplam Etkileşim Korelasyonu",
                        color_discrete_sequence=["#2563eb"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_modash, use_container_width=True)

                # =========================================================
                # 3. SOCIAL BLADE (DERECE ALGORİTMASI REVIZYONU)
                # =========================================================
                with sub_tab3:
                    st.subheader("📈 Social Blade Derecelendirme & Trend")

                    # Düzeltilmiş Derecelendirme Mantığı (Aykırı Değerlerden Arındırılmış Medyan ER Esas Alınır)
                    if median_er >= 3.5 and cv_index < 0.9:
                        grade = "A+"
                    elif median_er >= 2.0:
                        grade = "A"
                    elif median_er >= 1.0:
                        grade = "B+"
                    elif median_er >= 0.5:
                        grade = "B"
                    else:
                        grade = "C"

                    s1, s2 = st.columns(2)
                    s1.metric("Social Blade Hesap Skoru", grade)
                    s2.metric("Gönderi Başı Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}")

                    fig_sb = px.line(
                        df,
                        x="Gönderi",
                        y="ER (%)",
                        markers=True,
                        title="Gönderi Bazlı Etkileşim Oranı Trendi",
                        color_discrete_sequence=["#db2777"],
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_sb, use_container_width=True)
            else:
                st.error("Gelen profilde analiz edilecek geçerli bir gönderi bulunamadı.")
        else:
            st.error("❌ Profil bulunamadı veya Apify taraması zaman aşımına uğradı.")

elif btn_analyze:
    st.warning("Lütfen geçerli bir Instagram kullanıcı adı girin.")

# ---------------------------------------------------------
# FOOTER (Turkey 2026)
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">MG BRAND OFFICE © Turkey 2026 | Powered by Apify & Streamlit</div>',
    unsafe_allow_html=True,
)
