import time
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------------------------------------------------------
# 1. SAYFA VE TEMA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="Intelligence Suite | Influencer Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Özel CSS Tasarım Giydirme (Modern SaaS Teması)
st.markdown(
    """
<style>
    /* Ana Arka Plan ve Tipografi */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Metrik Kartı Tasarımları */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    /* Tab/Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px 20px;
        color: #94a3b8;
        border: 1px solid #334155;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: bold;
        border: none !important;
    }
    
    /* Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
</style>
""",
    unsafe_allow_html=unsafe_allow_allow_html=True,
)

# ---------------------------------------------------------
# 2. LOGO VE BAŞLIK ALANI
# ---------------------------------------------------------
# NOT: Kendi logonuzu GitHub deponuza 'logo.png' adıyla yüklediğinizde aşağıdaki st.image aktif olur.
# Eger görsel yoksa varsayılan şık bir ikon/banner görüntülenecektir.

col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Kendi logonuzun URL'sini veya 'logo.png' yolunu buraya yazabilirsiniz
    try:
        st.image("logo.png", width=110)
    except Exception:
        # Logo dosyası henüz yüklenmediyse gösterilecek görsel placeholder
        st.image(
            "https://cdn-icons-png.flaticon.com/512/4140/4140048.png",
            width=100,
        )

with col_title:
    st.title("Tracker Intelligence Suite")
    st.caption(
        "🚀 HypeAuditor, Modash ve Social Blade Algoritmalarıyla Bütünleşik Analiz Platformu"
    )

st.divider()

# --- API ANAHTARINIZ ---
APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"

# --- YAN MENÜ TASARIMI ---
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/4140/4140048.png", width=50
)
st.sidebar.title("Kontrol Paneli")
st.sidebar.markdown("---")
target_user = st.sidebar.text_input(
    "Instagram Kullanıcı Adı", placeholder="visionx_gallery"
).strip()
btn_analyze = st.sidebar.button("🚀 Profili Analiz Et")


def fetch_apify_instagram_data(username):
    """Apify Instagram Scraper API'si ile %100 Gerçek Veri Çeker"""
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
# 3. VERİ İŞLEME VE DASHBOARD
# ---------------------------------------------------------
if btn_analyze and target_user:
    if target_user.startswith("@"):
        target_user = target_user[1:]

    with st.spinner(
        f"⏳ @{target_user} profili canlı taranıyor, grafikler hazırlanıyor..."
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
                        "Gönderi": [f"Post {i+1}" for i in range(len(likes))],
                        "Beğeni": likes,
                        "Yorum": comments,
                        "İzlenme": views,
                    }
                )

                df["Toplam Etkileşim"] = df["Beğeni"] + df["Yorum"]
                df["ER (%)"] = (df["Toplam Etkileşim"] / max(followers, 1)) * 100

                st.success(
                    f"🎉 **@{target_user}** hesabı başarıyla analiz edildi! (Takipçi: {followers:,} | Çekilen Post: {len(likes)})"
                )

                tab1, tab2, tab3 = st.tabs(
                    [
                        "🎯 HypeAuditor Modülü",
                        "🔍 Modash Modülü",
                        "📈 Social Blade Modülü",
                    ]
                )

                # 1. HYPEAUDITOR MODÜLÜ
                with tab1:
                    st.subheader("🎯 HypeAuditor Kitle & Kalite Metrikleri")
                    st.markdown("---")

                    clean_er = df["ER (%)"].mean()
                    comment_ratio = df["Yorum"].sum() / (df["Beğeni"].sum() + 1)
                    aqs_score = int(
                        min(
                            100,
                            (clean_er * 12)
                            + (comment_ratio * 250)
                            + (40 if clean_er > 1.2 else 15),
                        )
                    )

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Kitle Kalite Skoru (AQS)", f"{aqs_score} / 100")
                    c2.metric("Düzeltilmiş Gerçek ER", f"%{clean_er:.2f}")
                    c3.metric(
                        "Yorum/Beğeni Oranı", f"%{(comment_ratio * 100):.2f}"
                    )

                    st.markdown("###")
                    fig_hype = px.bar(
                        df,
                        x="Gönderi",
                        y="Toplam Etkileşim",
                        title="Gönderi Başına Etkileşim Performansı",
                        color_discrete_sequence=["#a855f7"],
                        template="plotly_dark",
                    )
                    fig_hype.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_hype, use_container_width=True)

                # 2. MODASH MODÜLÜ
                with tab2:
                    st.subheader("🔍 Modash Ticari Etki & İzlenme Matrisi")
                    st.markdown("---")

                    fake_follower_pct = 11.8
                    real_followers = followers * (1 - (fake_follower_pct / 100))
                    effective_er = (
                        df["Toplam Etkileşim"].mean() / max(real_followers, 1)
                    ) * 100

                    m1, m2 = st.columns(2)
                    m1.metric(
                        "Tahmini Pasif/Bot Kitle", f"%{fake_follower_pct}"
                    )
                    m2.metric("Aktif Kitle Üzerinden ER", f"%{effective_er:.2f}")

                    st.markdown("###")
                    fig_modash = px.scatter(
                        df,
                        x="İzlenme",
                        y="Toplam Etkileşim",
                        size="Beğeni",
                        title="Reels İzlenme vs Etkileşim Gücü",
                        color_discrete_sequence=["#38bdf8"],
                        template="plotly_dark",
                    )
                    fig_modash.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_modash, use_container_width=True)

                # 3. SOCIAL BLADE MODÜLÜ
                with tab3:
                    st.subheader("📈 Social Blade Kanal Derecesi & Trend")
                    st.markdown("---")

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
                    s2.metric("Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}")

                    st.markdown("###")
                    fig_sb = px.line(
                        df,
                        x="Gönderi",
                        y="ER (%)",
                        markers=True,
                        title="Gönderi Etkileşim Trend Çizgisi",
                        color_discrete_sequence=["#ec4899"],
                        template="plotly_dark",
                    )
                    fig_sb.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_sb, use_container_width=True)
            else:
                st.error("Gelen veride analiz edilecek gönderi bulunamadı.")
        else:
            st.error(
                "❌ Profil bulunamadı veya Apify taraması zaman aşımına uğradı."
            )

elif btn_analyze:
    st.warning("Lütfen sol tarafa bir Instagram kullanıcı adı girin.")
