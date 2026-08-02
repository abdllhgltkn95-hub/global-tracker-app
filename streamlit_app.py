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
# 2. ÖZEL CSS TASARIMI (POPOVER VE BUTON İYİLEŞTİRMELERİ)
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

    /* Sağ Üst Popover Stil Düzeltmesi */
    div[data-testid="stPopover"] > button {
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        font-size: 1rem !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stPopover"] > button:hover {
        background: #f1f5f9 !important;
        border-color: #94a3b8 !important;
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


def fetch_apify_instagram_data(username, max_posts=12):
    """Apify actor vasıtasıyla Instagram ham verisini çeker."""
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

        for _ in range(35):
            time.sleep(2)
            res = requests.get(dataset_url)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0:
                    return items[0]
        return None
    except Exception:
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
# 3. BAŞLIK VE SAĞ ÜST MENÜ
# ---------------------------------------------------------
col_top_left, col_top_right = st.columns([6, 1])

with col_top_right:
    show_algo_menu = st.popover("📐 Algoritma Mantığı")

with show_algo_menu:
    st.markdown("### ⚙️ Sistem Mantığı")
    st.markdown("---")
    st.markdown("**1. HypeAuditor (AQS):** ER, Yorum Oranı ve İçerik İstikrar Bileşimi.")
    st.markdown("**2. Modash:** Takipçi ölçeğine göre beklenen ER sapması ve bot riski tahmini.")
    st.markdown("**3. Kıyaslama:** Çoklu hesapların ER ve etkileşim metriklerinin karşılaştırılması.")

st.markdown('<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-sub">All-in-One Influencer Tracker & Intelligence Suite</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. ARAYÜZ SEKMELERİ
# ---------------------------------------------------------
tab_single, tab_compare = st.tabs(["👤 Tekil Profil Analizi", "⚖️ Kıyaslama Paneli"])

# =========================================================
# SEKMELER 1: TEKİL PROFİL ANALİZİ
# =========================================================
with tab_single:
    c_left, c_mid, c_right = st.columns([1, 2, 1])

    with c_mid:
        target_user = st.text_input(
            "Instagram Kullanıcı Adı",
            placeholder="Örn: visionx_gallery",
            key="single_user_input",
            label_visibility="collapsed",
        ).strip()

        scan_deep = st.checkbox("Derin Profil Analizi Yap (Son 50+ Gönderi)")
        btn_analyze = st.button("Profili Analiz Et ⚡", key="btn_single")

    st.markdown("---")

    if btn_analyze and target_user:
        if target_user.startswith("@"):
            target_user = target_user[1:]

        max_p = 50 if scan_deep else 12

        with st.spinner(f"⏳ @{target_user} profili taranıyor..."):
            profile = fetch_apify_instagram_data(target_user, max_posts=max_p)

            if profile and "latestPosts" in profile:
                raw_followers = profile.get("followersCount", profile.get("followers", 0))
                followers = int(clean_number(raw_followers, default=1000))
                followers = max(followers, 1)

                raw_posts = profile.get("latestPosts", [])
                likes_list, comments_list, views_list = [], [], []

                for p in raw_posts:
                    l = clean_number(p.get("likesCount"), 0)
                    c = clean_number(p.get("commentsCount"), 0)
                    v = clean_number(p.get("videoViewCount"), l)

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

                    st.success(f"**@{target_user}** analizi tamamlandı. (Takipçi: **{followers:,}**)")

                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🎯 HypeAuditor", "🔍 Modash", "📈 Social Blade"])

                    mean_er = float(df["ER (%)"].mean())
                    std_er = float(df["ER (%)"].std()) if len(df) > 1 else 0.0
                    sum_likes = float(df["Beğeni"].sum())
                    sum_comments = float(df["Yorum"].sum())
                    comment_to_like_ratio = sum_comments / max(sum_likes, 1.0)
                    cv = (std_er / mean_er) if mean_er > 0 else 1.0

                    # HypeAuditor
                    with sub_tab1:
                        benchmark_er = 2.0 if followers >= 100000 else 3.5
                        er_score = min(40.0, (mean_er / benchmark_er) * 40.0)
                        comment_score = 40.0 if comment_to_like_ratio >= 0.015 else (comment_to_like_ratio / 0.015) * 40.0
                        stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
                        final_aqs = int(np.clip(er_score + comment_score + stability_score, 10, 99))

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Kalite Skoru (AQS)", f"{final_aqs} / 100")
                        c2.metric("Ortalama ER", f"%{mean_er:.2f}")
                        c3.metric("Yorum / Beğeni", f"%{(comment_to_like_ratio * 100):.2f}")

                        fig_hype = px.bar(df, x="Gönderi", y="Toplam Etkileşim", template="plotly_white")
                        st.plotly_chart(fig_hype, use_container_width=True)

                    # Modash
                    with sub_tab2:
                        bot_penalty = 0.0
                        if mean_er < (benchmark_er * 0.4): bot_penalty += 25.0
                        if comment_to_like_ratio < 0.003: bot_penalty += 20.0
                        estimated_fake_pct = float(np.clip(4.0 + bot_penalty, 3.0, 75.0))

                        m1, m2 = st.columns(2)
                        m1.metric("Tahmini Şüpheli Kitle", f"%{estimated_fake_pct:.1f}")
                        m2.metric("Organik ER", f"%{(df['Toplam Etkileşim'].mean() / max(followers * (1 - estimated_fake_pct/100), 1)) * 100:.2f}")

                    # Social Blade
                    with sub_tab3:
                        grade = "A+" if mean_er >= 3.5 else ("A" if mean_er >= 2.0 else "B")
                        s1, s2 = st.columns(2)
                        s1.metric("Social Blade Skoru", grade)
                        s2.metric("Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}")

            else:
                st.error("❌ Veri çekilemedi.")

# =========================================================
# SEKMELER 2: KIYASLAMA
# =========================================================
with tab_compare:
    st.subheader("⚖️ 4 Hesap Karşılaştırmalı Analiz Paneli")
    st.caption("Kıyaslamak istediğiniz hesapların kullanıcı adlarını girin.")

    col_u1, col_u2, col_u3, col_u4 = st.columns(4)

    with col_u1:
        u1 = st.text_input("1. Kullanıcı Adı", placeholder="kullanici_1", key="u1").strip()
    with col_u2:
        u2 = st.text_input("2. Kullanıcı Adı", placeholder="kullanici_2", key="u2").strip()
    with col_u3:
        u3 = st.text_input("3. Kullanıcı Adı", placeholder="kullanici_3", key="u3").strip()
    with col_u4:
        u4 = st.text_input("4. Kullanıcı Adı", placeholder="kullanici_4", key="u4").strip()

    btn_compare = st.button("Hesapları Kıyasla ⚡", key="btn_comp")

    if btn_compare:
        users_to_compare = [u for u in [u1, u2, u3, u4] if u]
        users_to_compare = [u[1:] if u.startswith("@") else u for u in users_to_compare]

        if len(users_to_compare) < 2:
            st.warning("⚠️ Kıyaslama yapabilmek için lütfen en az 2 kullanıcı adı girin.")
        else:
            comparison_results = []
            progress_bar = st.progress(0)

            for idx, username in enumerate(users_to_compare):
                st.toast(f"@{username} verileri taranıyor...")
                prof = fetch_apify_instagram_data(username, max_posts=12)

                if prof and "latestPosts" in prof:
                    fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                    fol = max(fol, 1)

                    posts = prof.get("latestPosts", [])
                    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
                    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]

                    avg_likes = np.mean(likes) if likes else 0
                    avg_comments = np.mean(comments) if comments else 0
                    tot_eng = avg_likes + avg_comments
                    er = (tot_eng / fol) * 100.0

                    comparison_results.append({
                        "Kullanıcı Adı": f"@{username}",
                        "Takipçi Sayısı": fol,
                        "Ortalama ER (%)": round(er, 2),
                        "Ortalama Beğeni": int(avg_likes),
                        "Ortalama Yorum": int(avg_comments)
                    })

                progress_bar.progress((idx + 1) / len(users_to_compare))

            if comparison_results:
                comp_df = pd.DataFrame(comparison_results)

                st.markdown("### 📊 Karşılaştırma Özeti")
                st.dataframe(
                    comp_df.style.highlight_max(axis=0, subset=["Ortalama ER (%)", "Takipçi Sayısı"], color="#dcfce7"),
                    use_container_width=True,
                )

                fig_comp = px.bar(
                    comp_df,
                    x="Kullanıcı Adı",
                    y="Ortalama ER (%)",
                    color="Kullanıcı Adı",
                    title="Etkileşim Oranı (ER %) Karşılaştırması",
                    text="Ortalama ER (%)",
                    template="plotly_white",
                    color_discrete_sequence=px.colors.qualitative.Prism,
                )
                fig_comp.update_traces(texttemplate='%{text}%', textposition='outside')
                st.plotly_chart(fig_comp, use_container_width=True)

            else:
                st.error("Girilen kullanıcı adlarının verileri çekilemedi.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">MG BRAND OFFICE © Turkey 2026 | Powered by Apify & Streamlit</div>',
    unsafe_allow_html=True,
)
