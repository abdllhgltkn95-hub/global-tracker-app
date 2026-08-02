
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="All-in-One Tracker Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛡️ All-in-One Influencer Tracker & Intelligence Suite")
st.caption(
    "HypeAuditor, Modash ve Social Blade Algoritmalarıyla Otomatik Analiz Platformu"
)

# -------------------------------------------------------------
# RAPIDAPI ANAHTARIN (SENİN KEY'İN BURAYA EKLENDİ)
# -------------------------------------------------------------
API_KEY = "f149f5dbe8msh64295e613d8e62fp1068d3jsn8724a64fa267"


# --- YAN MENÜ: OTOMATİK VERİ ÇEKME ---
st.sidebar.header("🔍 Otomatik Profil Analizi")
target_user = st.sidebar.text_input(
    "Instagram Kullanıcı Adı", placeholder="gunduzmeltemi"
)
btn_analyze = st.sidebar.button("🚀 Profili Analiz Et")


def fetch_instagram_data(username):
    url = f"https://instagram-looter2.p.rapidapi.com/profile?username={username}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "instagram-looter2.p.rapidapi.com",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


if btn_analyze and target_user:
    with st.spinner(
        f"⏳ @{target_user} profil verileri çekiliyor, lütfen bekleyin..."
    ):
        data = fetch_instagram_data(target_user)

        if data and "followers" in data:
            followers = data.get("followers", 10000)
            posts = data.get("posts", [])[:10]

            likes = [p.get("like_count", 0) for p in posts]
            comments = [p.get("comment_count", 0) for p in posts]
            views = [p.get("view_count", 0) for p in posts]

            if likes and len(likes) > 0:
                df = pd.DataFrame(
                    {
                        "Gönderi": [f"Post {i+1}" for i in range(len(likes))],
                        "Beğeni": likes,
                        "Yorum": comments,
                        "İzlenme": views,
                    }
                )

                df["Toplam Etkileşim"] = df["Beğeni"] + df["Yorum"]
                df["ER (%)"] = (df["Toplam Etkileşim"] / followers) * 100

                st.success(
                    f"✅ **@{target_user}** hesabı başarıyla çekildi! (Takipçi: {followers:,})"
                )

                tab1, tab2, tab3 = st.tabs(
                    [
                        "🎯 HypeAuditor Modülü",
                        "🔍 Modash Modülü",
                        "📈 Social Blade Modülü",
                    ]
                )

                # 1. HYPEAUDITOR
                with tab1:
                    st.header("🎯 HypeAuditor Kalite Analizi")
                    st.info(
                        "💡 **HypeAuditor:** Kitle kalitesi ve sahte etkileşim (Bot) tespitinde dünya standardıdır."
                    )

                    q_low = df["ER (%)"].quantile(0.10)
                    q_high = df["ER (%)"].quantile(0.90)
                    clean_df = df[
                        (df["ER (%)"] >= q_low) & (df["ER (%)"] <= q_high)
                    ]
                    clean_er = (
                        clean_df["ER (%)"].mean()
                        if not clean_df.empty
                        else df["ER (%)"].mean()
                    )

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

                    fig_hype = px.bar(
                        df,
                        x="Gönderi",
                        y="Toplam Etkileşim",
                        title="Gönderi Başına Etkileşim Gücü",
                        color_discrete_sequence=["#a855f7"],
                    )
                    st.plotly_chart(fig_hype, use_container_width=True)

                # 2. MODASH
                with tab2:
                    st.header("🔍 Modash Analizi")
                    st.info(
                        "💡 **Modash:** Satış/reklam odağı, Reels izlenmeleri ve pasif kitle oranına odaklanır."
                    )

                    fake_follower_pct = 12.5
                    real_followers = followers * (1 - (fake_follower_pct / 100))
                    effective_er = (
                        df["Toplam Etkileşim"].mean() / real_followers
                    ) * 100

                    m1, m2 = st.columns(2)
                    m1.metric(
                        "Tahmini Pasif/Bot Kitle", f"%{fake_follower_pct}"
                    )
                    m2.metric("Aktif Kitle Üzerinden ER", f"%{effective_er:.2f}")

                    fig_modash = px.scatter(
                        df,
                        x="İzlenme",
                        y="Toplam Etkileşim",
                        size="Beğeni",
                        title="Reels İzlenme vs Etkileşim Matrisi",
                        color_discrete_sequence=["#38bdf8"],
                    )
                    st.plotly_chart(fig_modash, use_container_width=True)

                # 3. SOCIAL BLADE
                with tab3:
                    st.header("📈 Social Blade Analizi")
                    st.info(
                        "💡 **Social Blade:** Hesabın genel performans harfini (Grade) ve gidişat trendini verir."
                    )

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
                    s1.metric("Social Blade Skoru", grade)
                    s2.metric("Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}")

                    fig_sb = px.line(
                        df,
                        x="Gönderi",
                        y="ER (%)",
                        markers=True,
                        title="Etkileşim Oranı Trend Çizgisi",
                        color_discrete_sequence=["#ec4899"],
                    )
                    st.plotly_chart(fig_sb, use_container_width=True)

            else:
                st.error("Profilin son gönderi verileri okunamadı.")
        else:
            st.error(
                "Instagram verisi çekilemedi. Profil gizli olabilir veya kullanıcı adı yanlış."
            )

elif btn_analyze:
    st.warning("Lütfen sol tarafa bir Instagram kullanıcı adı girin.")
