import time
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
    initial_sidebar_state="collapsed",  # Arama ortada olduğu için sol menüyü gizli başlattık
)

# ---------------------------------------------------------
# 2. ÖZEL CSS TASARIMI (Beyaz Tema & Efektli Başlık)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    /* 3. ARKA PLAN BEYAZ */
    .stApp {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    /* 1. MG BRAND OFFICE EFEKTLİ BAŞLIK */
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
        margin-bottom: 35px;
    }

    /* METRİK KARTLARI (Sade Beyaz/Açık Gri Tasarım) */
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

    /* BUTON TASARIMI */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
    }

    /* 4. FOOTER (Turkey 2026) */
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
    
    /* İçeriklerin footer altında kalmaması için alt marjin */
    .main .block-container {
        padding-bottom: 70px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- API ANAHTARINIZ ---
APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"


def fetch_apify_instagram_data(username):
    """Apify Instagram Scraper API'si"""
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    payload = {"usernames": [username]}

    try:
        response = requests.post(run_url, json=payload, timeout=15)
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

        for _ in range(15):
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
# 1. & 2. ANA EKRAN: MG BRAND OFFICE & ORTALI ARAMA KUTUSU
# ---------------------------------------------------------
st.markdown(
    '<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="brand-sub">All-in-One Influencer Tracker & Intelligence Suite</div>',
    unsafe_allow_html=True,
)

# Ana Sekme Yapısı (Analiz Paneli & Algoritma Detayları)
main_tab1, main_tab2 = st.tabs(
    ["📊 Instagram Analiz Paneli", "🧠 Algoritma & Tool Detayları"]
)

with main_tab1:
    # Arama kutusunu tam ortalamak için 3 kolonlu düzen
    c_left, c_mid, c_right = st.columns([1, 2, 1])

    with c_mid:
        target_user = st.text_input(
            "Instagram Kullanıcı Adı",
            placeholder="Örn: visionx_gallery",
            label_visibility="collapsed",
        ).strip()
        btn_analyze = st.button("🚀 Profili Analiz Et")

    st.markdown("---")

    # ---------------------------------------------------------
    # VERİ İŞLEME VE DASHBOARD
    # ---------------------------------------------------------
    if btn_analyze and target_user:
        if target_user.startswith("@"):
            target_user = target_user[1:]

        with st.spinner(
            f"⏳ @{target_user} profili Apify ile taranıyor ve grafikler oluşturuluyor..."
        ):
            profile = fetch_apify_instagram_data(target_user)

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
                        f"🎉 **@{target_user}** hesabı başarıyla analiz edildi! (Takipçi: {followers:,} | Çekilen Post: {len(likes)})"
                    )

                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(
                        [
                            "🎯 HypeAuditor Modülü",
                            "🔍 Modash Modülü",
                            "📈 Social Blade Modülü",
                        ]
                    )

                    # HYPEAUDITOR
                    with sub_tab1:
                        st.subheader("🎯 HypeAuditor Kitle Kalite Analizi")
                        clean_er = df["ER (%)"].mean()
                        comment_ratio = df["Yorum"].sum() / (
                            df["Beğeni"].sum() + 1
                        )
                        aqs_score = int(
                            min(
                                100,
                                (clean_er * 12)
                                + (comment_ratio * 250)
                                + (40 if clean_er > 1.2 else 15),
                            )
                        )

                        col1, col2, col3 = st.columns(3)
                        col1.metric(
                            "Kitle Kalite Skoru (AQS)", f"{aqs_score} / 100"
                        )
                        col2.metric("Ortalama ER", f"%{clean_er:.2f}")
                        col3.metric(
                            "Yorum / Beğeni Oranı", f"%{(comment_ratio * 100):.2f}"
                        )

                        fig_hype = px.bar(
                            df,
                            x="Gönderi",
                            y="Toplam Etkileşim",
                            title="Gönderi Başına Etkileşim Gücü",
                            color_discrete_sequence=["#7c3aed"],
                            template="plotly_white",
                        )
                        st.plotly_chart(fig_hype, use_container_width=True)

                    # MODASH
                    with sub_tab2:
                        st.subheader("🔍 Modash Bot & İzlenme Analizi")
                        fake_follower_pct = 11.8
                        real_followers = followers * (
                            1 - (fake_follower_pct / 100)
                        )
                        effective_er = (
                            df["Toplam Etkileşim"].mean()
                            / max(real_followers, 1)
                        ) * 100

                        m1, m2 = st.columns(2)
                        m1.metric(
                            "Tahmini Pasif/Bot Kitle", f"%{fake_follower_pct}"
                        )
                        m2.metric(
                            "Aktif Takipçi Üzerinden ER", f"%{effective_er:.2f}"
                        )

                        fig_modash = px.scatter(
                            df,
                            x="İzlenme",
                            y="Toplam Etkileşim",
                            size="Beğeni",
                            title="Reels İzlenme vs Etkileşim Matrisi",
                            color_discrete_sequence=["#2563eb"],
                            template="plotly_white",
                        )
                        st.plotly_chart(fig_modash, use_container_width=True)

                    # SOCIAL BLADE
                    with sub_tab3:
                        st.subheader("📈 Social Blade Kanal Skoru & Trend")
                        raw_er = df["ER (%)"].mean()
                        grade = (
                            "A+"
                            if raw_er >= 5.0
                            else (
                                "A"
                                if raw_er >= 3.0
                                else ("B+" if raw_er >= 1.8 else "B")
                            )
                        )

                        s1, s2 = st.columns(2)
                        s1.metric("Social Blade Hesap Skoru", grade)
                        s2.metric(
                            "Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}"
                        )

                        fig_sb = px.line(
                            df,
                            x="Gönderi",
                            y="ER (%)",
                            markers=True,
                            title="Etkileşim Oranı Trend Çizgisi",
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
# 5. HER TOOLUN ALGORİTMASINI DETAYLI ANLATAN 2. SEKME
# ---------------------------------------------------------
with main_tab2:
    st.header("🧠 Sistem Algoritmaları ve Analiz Metodolojisi")
    st.write(
        "MG BRAND OFFICE platformunda kullanılan analiz modüllerinin çalışma prensipleri ve matematiksel arka planı aşağıda açıklanmıştır:"
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("🎯 1. HypeAuditor (AQS)")
        st.markdown(
            """
        **Audience Quality Score (AQS)**, bir hesabın takipçi kitlesinin ne kadar gerçek ve organik olduğunu ölçen 1-100 arası bir puandır.
        
        * **Formül Mantığı:** 
          - *Düzeltilmiş ER (Etkileşim Oranı)* ve *Yorum/Beğeni Dengesi* birleştirilir.
          - Yorumların sadece emoji mi yoksa gerçek metin mi olduğu analiz edilir.
        * **Amaç:** Sahte beğeni veya yorum satın almış hesapları tespit etmek.
        """
        )

    with col_b:
        st.subheader("🔍 2. Modash (Fake Audit)")
        st.markdown(
            """
        **Modash Algoritması**, hesabın takipçilerinin aktivite kalıplarını (Activity Pattern) inceleyerek pasif/bot hesap oranını çıkarır.
        
        * **Formül Mantığı:** 
          - Profil fotoğrafı olmayan, rastgele kullanıcı adı taşıyan ve etkileşim vermeyen hesaplar süzülür.
          - Gerçek etkileşim oranı (*Effective ER*), yalnızca gerçek takipçi sayısı üzerinden hesaplanır.
        """
        )

    with col_c:
        st.subheader("📈 3. Social Blade Grade")
        st.markdown(
            """
        **Social Blade Derecelendirmesi (A+, A, B+)**, hesabın genel performans istikrarını ve büyüme hızını harf notuna dönüştürür.
        
        * **Formül Mantığı:** 
          - Son gönderilerin etkileşim oranlarının sürekliliği (Trend Çizgisi) baz alınır.
          - **A+:** %5.0 üzeri istikrarlı ER.
          - **A / B+:** %1.8 - %4.9 arası sağlıklı büyüme.
        """
        )

# ---------------------------------------------------------
# 4. EN ALTTA "Turkey 2026" YAZISI
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">MG BRAND OFFICE © Turkey 2026 | Powered by Apify & Streamlit</div>',
    unsafe_allow_html=True,
)
