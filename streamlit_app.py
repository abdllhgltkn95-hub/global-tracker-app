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
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 2. ÖZEL CSS TASARIMI (SADE, KURUMSAL VE BEYAZ TEMA KORUMALI)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    .stApp {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    .brand-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }

    .brand-sub {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Menü Buton Stili */
    div[data-testid="stPopover"] > button {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stPopover"] > button:hover {
        background: #f8fafc !important;
        border-color: #94a3b8 !important;
    }

    /* Metrik Kartları */
    [data-testid="stMetric"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 20px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background-color: #1e293b !important;
        transform: translateY(-1px);
    }

    /* SEKMELER - Beyaz Ekran Okunabilirlik Düzeltmesi */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 16px !important;
        background-color: transparent !important;
    }

    .stTabs [aria-selected="true"] {
        color: #0f172a !important;
        border-bottom: 2px solid #0f172a !important;
        font-weight: 700 !important;
    }

    /* Sub-tabs İçin Özel Belirginleştirme */
    .stTabs [data-baseweb="tab-panel"] [data-baseweb="tab"] {
        color: #334155 !important;
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
        font-size: 0.85rem;
        font-weight: 500;
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
    show_algo_menu = st.popover("Menü")

with show_algo_menu:
    st.markdown("**Sistem Bilgisi**")
    st.markdown("---")
    st.markdown("MG Brand Office Intelligence v2.4")
    st.caption("İçerik verileri Apify altyapısıyla anlık olarak işlenmektedir.")

st.markdown('<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-sub">Influencer Intelligence & Analytics Suite</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. ARAYÜZ SEKMELERİ
# ---------------------------------------------------------
tab_single, tab_compare = st.tabs(["Tekil Profil Analizi", "Kıyaslama & Metrikler"])

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

        scan_deep = st.checkbox("Derin Profil Analizi (Son 50+ Gönderi)")
        btn_analyze = st.button("Profili Analiz Et", key="btn_single")

    st.markdown("---")

    if btn_analyze and target_user:
        if target_user.startswith("@"):
            target_user = target_user[1:]

        max_p = 50 if scan_deep else 12

        with st.spinner(f"@{target_user} profili taranıyor..."):
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

                    st.success(f"@{target_user} analizi tamamlandı. Takipçi Sayısı: {followers:,}")

                    # Alt Sekmeler - Temiz Ve Belirgin
                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["HypeAuditor", "Modash", "Social Blade"])

                    mean_er = float(df["ER (%)"].mean())
                    std_er = float(df["ER (%)"].std()) if len(df) > 1 else 0.0
                    sum_likes = float(df["Beğeni"].sum())
                    sum_comments = float(df["Yorum"].sum())
                    comment_to_like_ratio = sum_comments / max(sum_likes, 1.0)
                    cv = (std_er / mean_er) if mean_er > 0 else 1.0

                    # HypeAuditor Sekmesi
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
                        fig_hype.update_traces(marker_color='#0f172a')
                        st.plotly_chart(fig_hype, use_container_width=True)

                    # Modash Sekmesi
                    with sub_tab2:
                        bot_penalty = 0.0
                        if mean_er < (benchmark_er * 0.4): bot_penalty += 25.0
                        if comment_to_like_ratio < 0.003: bot_penalty += 20.0
                        estimated_fake_pct = float(np.clip(4.0 + bot_penalty, 3.0, 75.0))

                        m1, m2 = st.columns(2)
                        m1.metric("Tahmini Şüpheli Kitle", f"%{estimated_fake_pct:.1f}")
                        m2.metric("Organik ER", f"%{(df['Toplam Etkileşim'].mean() / max(followers * (1 - estimated_fake_pct/100), 1)) * 100:.2f}")

                    # Social Blade Sekmesi
                    with sub_tab3:
                        grade = "A+" if mean_er >= 3.5 else ("A" if mean_er >= 2.0 else "B")
                        s1, s2 = st.columns(2)
                        s1.metric("Social Blade Skoru", grade)
                        s2.metric("Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}")

            else:
                st.error("Veri çekilemedi. Lütfen kullanıcı adını kontrol edip tekrar deneyin.")

# =========================================================
# SEKMELER 2: KIYASLAMA VE ALGORİTMA MANTIĞI
# =========================================================
with tab_compare:
    with st.expander("Algoritma Mantığı ve Hesaplama Modelleri", expanded=False):
        st.markdown("**Hesaplama Detayları**")
        st.markdown("---")
        col_algo1, col_algo2, col_algo3 = st.columns(3)
        with col_algo1:
            st.markdown("**1. HypeAuditor (AQS):** ER, Yorum Oranı ve İçerik İstikrar Bileşimi.")
        with col_algo2:
            st.markdown("**2. Modash:** Takipçi ölçeğine göre beklenen ER sapması ve bot riski tahmini.")
        with col_algo3:
            st.markdown("**3. Kıyaslama:** Çoklu hesapların AQS, Bot Riski, ER ve etkileşim metriklerinin karşılaştırılması.")

    st.subheader("Hesap Karşılaştırma Paneli")
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

    btn_compare = st.button("Hesapları Kıyasla", key="btn_comp")

    if btn_compare:
        users_to_compare = [u for u in [u1, u2, u3, u4] if u]
        users_to_compare = [u[1:] if u.startswith("@") else u for u in users_to_compare]

        if len(users_to_compare) < 2:
            st.warning("Kıyaslama yapabilmek için lütfen en az 2 kullanıcı adı girin.")
        else:
            comparison_results = []
            progress_bar = st.progress(0)

            for idx, username in enumerate(users_to_compare):
                st.toast(f"@{username} verileri işleniyor...")
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

                    std_er = float(np.std([(l + c)/fol * 100.0 for l, c in zip(likes, comments)])) if len(likes) > 1 else 0.0
                    cv = (std_er / er) if er > 0 else 1.0
                    sum_likes = max(sum(likes), 1.0)
                    comment_to_like_ratio = sum(comments) / sum_likes

                    benchmark_er = 2.0 if fol >= 100000 else 3.5

                    er_score = min(40.0, (er / benchmark_er) * 40.0)
                    comment_score = 40.0 if comment_to_like_ratio >= 0.015 else (comment_to_like_ratio / 0.015) * 40.0
                    stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
                    aqs_score = int(np.clip(er_score + comment_score + stability_score, 10, 99))

                    bot_penalty = 0.0
                    if er < (benchmark_er * 0.4): bot_penalty += 25.0
                    if comment_to_like_ratio < 0.003: bot_penalty += 20.0
                    if cv > 1.4: bot_penalty += 10.0
                    bot_risk_pct = float(np.clip(4.0 + bot_penalty, 3.0, 75.0))

                    comparison_results.append({
                        "Kullanıcı Adı": f"@{username}",
                        "AQS Kalite Puanı": f"{aqs_score} / 100",
                        "Bot Riski (%)": f"%{bot_risk_pct:.1f}",
                        "Ortalama ER (%)": round(er, 2),
                        "Takipçi": fol,
                        "Ort. Beğeni": int(avg_likes),
                        "Ort. Yorum": int(avg_comments),
                    })

                progress_bar.progress((idx + 1) / len(users_to_compare))

            if comparison_results:
                comp_df = pd.DataFrame(comparison_results)

                st.markdown("### Karşılaştırma Özeti")

                st.dataframe(
                    comp_df,
                    use_container_width=True,
                )

                col_g1, col_g2 = st.columns(2)

                with col_g1:
                    fig_comp_er = px.bar(
                        comp_df,
                        x="Kullanıcı Adı",
                        y="Ortalama ER (%)",
                        title="Etkileşim Oranı (ER %) Karşılaştırması",
                        text="Ortalama ER (%)",
                        template="plotly_white",
                    )
                    fig_comp_er.update_traces(marker_color='#0f172a', texttemplate='%{text}%', textposition='outside')
                    st.plotly_chart(fig_comp_er, use_container_width=True)

                with col_g2:
                    comp_df_graph = comp_df.copy()
                    comp_df_graph["AQS (Sayısal)"] = comp_df_graph["AQS Kalite Puanı"].apply(lambda x: int(x.split()[0]))

                    fig_comp_aqs = px.bar(
                        comp_df_graph,
                        x="Kullanıcı Adı",
                        y="AQS (Sayısal)",
                        title="AQS Kalite Puanı Karşılaştırması",
                        text="AQS Kalite Puanı",
                        template="plotly_white",
                    )
                    fig_comp_aqs.update_traces(marker_color='#475569', textposition='outside')
                    st.plotly_chart(fig_comp_aqs, use_container_width=True)

            else:
                st.error("Girilen kullanıcı adlarının verileri çekilemedi.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">MG BRAND OFFICE © 2026 | Powered by Apify & Streamlit</div>',
    unsafe_allow_html=True,
)
