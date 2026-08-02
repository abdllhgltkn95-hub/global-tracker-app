import time
import math
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
    page_title="MG BRAND OFFICE | Influencer Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- API CONFIGURATION ---
APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"

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
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #2563eb, #7c3aed, #db2777);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .brand-sub {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 25px;
    }

    div[data-testid="stPopover"] > button {
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
    }

    [data-testid="stMetric"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }

    .wask-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .wask-status-high {
        background-color: #dcfce7;
        color: #166534;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .wask-status-avg {
        background-color: #fef9c3;
        color: #854d0e;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .wask-status-low {
        background-color: #fee2e2;
        color: #991b1b;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #7c3aed, #db2777) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
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
        padding: 10px 0;
        font-size: 0.85rem;
        border-top: 1px solid #f1f5f9;
        z-index: 999;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR
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

def calculate_wask_metrics(followers, likes_list, comments_list):
    avg_likes = np.mean(likes_list) if likes_list else 0
    avg_comments = np.mean(comments_list) if comments_list else 0
    total_eng = avg_likes + avg_comments
    er = (total_eng / max(followers, 1)) * 100.0

    if followers < 10000:
        benchmark = {"düşük": 1.5, "yuksek": 4.0, "seviye": "Micro-Influencer"}
    elif followers < 100000:
        benchmark = {"düşük": 1.0, "yuksek": 2.5, "seviye": "Mid-Influencer"}
    else:
        benchmark = {"düşük": 0.8, "yuksek": 1.8, "seviye": "Macro/Mega-Influencer"}

    if er >= benchmark["yuksek"]:
        status = "Yüksek (İyi)"
        status_class = "wask-status-high"
    elif er >= benchmark["düşük"]:
        status = "Ortalama"
        status_class = "wask-status-avg"
    else:
        status = "Düşük"
        status_class = "wask-status-low"

    return {
        "er": er,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "status": status,
        "status_class": status_class,
        "benchmark": benchmark
    }

# ---------------------------------------------------------
# 4. ARAYÜZ BAŞLIĞI VE SİSTEM BİLGİSİ
# ---------------------------------------------------------
col_top_left, col_top_right = st.columns([6, 1])

with col_top_right:
    show_algo_menu = st.popover("📐 Algoritma Mantığı")
    with show_algo_menu:
        st.markdown("### ⚙️ Sistem Mantığı")
        st.markdown("---")
        st.markdown("**1. HypeAuditor (AQS):** ER, Yorum Oranı ve İçerik İstikrarı.")
        st.markdown("**2. Modash:** Takipçi ölçeğine göre beklenen ER sapması.")
        st.markdown("**3. WASK Calculator:** Takipçi ölçeğine göre benchmark kıyası ve etkileşim performansı.")

st.markdown('<div class="brand-header">MG BRAND OFFICE</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">All-in-One Influencer Tracker & Intelligence Suite</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. SEKMELER (WASK ARAYÜZÜ DAHİL EDİLDİ)
# ---------------------------------------------------------
tab_single, tab_wask, tab_compare = st.tabs([
    "👤 Tekil Profil Analizi", 
    "📊 WASK Etkileşim Hesaplayıcı", 
    "⚖️ Kıyaslama Paneli"
])

# =========================================================
# SEKMELER 1: TEKİL PROFİL ANALİZİ
# =========================================================
with tab_single:
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    with c_mid:
        target_user = st.text_input("Instagram Kullanıcı Adı", placeholder="Örn: visionx_gallery", key="single_user_input").strip()
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

                    sub1, sub2, sub3 = st.tabs(["🎯 HypeAuditor", "🔍 Modash", "📈 Social Blade"])

                    mean_er = float(df["ER (%)"].mean())
                    std_er = float(df["ER (%)"].std()) if len(df) > 1 else 0.0
                    sum_likes = float(df["Beğeni"].sum())
                    sum_comments = float(df["Yorum"].sum())
                    comment_ratio = sum_comments / max(sum_likes, 1.0)
                    cv = (std_er / mean_er) if mean_er > 0 else 1.0

                    with sub1:
                        benchmark_er = 2.0 if followers >= 100000 else 3.5
                        er_score = min(40.0, (mean_er / benchmark_er) * 40.0)
                        comment_score = 40.0 if comment_ratio >= 0.015 else (comment_ratio / 0.015) * 40.0
                        stability_score = max(0.0, 20.0 * (1.0 - min(cv, 1.0)))
                        final_aqs = int(np.clip(er_score + comment_score + stability_score, 10, 99))

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Kalite Skoru (AQS)", f"{final_aqs} / 100")
                        c2.metric("Ortalama ER", f"%{mean_er:.2f}")
                        c3.metric("Yorum / Beğeni", f"%{(comment_ratio * 100):.2f}")

                        fig_hype = px.bar(df, x="Gönderi", y="Toplam Etkileşim", template="plotly_white")
                        st.plotly_chart(fig_hype, use_container_width=True)

                    with sub2:
                        bot_penalty = 0.0
                        if mean_er < (benchmark_er * 0.4): bot_penalty += 25.0
                        if comment_ratio < 0.003: bot_penalty += 20.0
                        estimated_fake_pct = float(np.clip(4.0 + bot_penalty, 3.0, 75.0))

                        m1, m2 = st.columns(2)
                        m1.metric("Tahmini Şüpheli Kitle", f"%{estimated_fake_pct:.1f}")
                        m2.metric("Organik ER", f"%{(df['Toplam Etkileşim'].mean() / max(followers * (1 - estimated_fake_pct/100), 1)) * 100:.2f}")

                    with sub3:
                        grade = "A+" if mean_er >= 3.5 else ("A" if mean_er >= 2.0 else "B")
                        s1, s2 = st.columns(2)
                        s1.metric("Social Blade Skoru", grade)
                        s2.metric("Ortalama Beğeni", f"{int(df['Beğeni'].mean()):,}")
            else:
                st.error("❌ Profil bulunamadı veya veriler çekilemedi.")

# =========================================================
# SEKMELER 2: WASK ETKİLEŞİM HESAPLAYICI (UYARLANAN ARAYÜZ)
# =========================================================
with tab_wask:
    st.subheader("📊 WASK Tarzı Etkileşim Oranı Hesaplayıcı")
    st.caption("Instagram hesabının takipçi ve etkileşim verilerine göre benchmark durum analizi.")

    wask_user = st.text_input("Analiz Edilecek Kullanıcı Adı", placeholder="Örn: instagram_kullanici", key="wask_user_input").strip()
    btn_wask = st.button("WASK Metriklerini Hesapla ⚡", key="btn_wask")

    if btn_wask and wask_user:
        if wask_user.startswith("@"):
            wask_user = wask_user[1:]

        with st.spinner(f"⏳ @{wask_user} hesabı için WASK verileri taranıyor..."):
            prof = fetch_apify_instagram_data(wask_user, max_posts=12)

            if prof and "latestPosts" in prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                fol = max(fol, 1)

                posts = prof.get("latestPosts", [])
                likes = [clean_number(p.get("likesCount"), 0) for p in posts]
                comments = [clean_number(p.get("commentsCount"), 0) for p in posts]

                metrics = calculate_wask_metrics(fol, likes, comments)

                col_w1, col_w2 = st.columns([1, 1])

                with col_w1:
                    st.markdown(f"""
                    <div class="wask-card">
                        <h3>@{wask_user}</h3>
                        <p><strong>Kategori:</strong> {metrics['benchmark']['seviye']}</p>
                        <p><strong>Takipçi Sayısı:</strong> {fol:,}</p>
                        <p><strong>Etkileşim Statüsü:</strong> <span class="{metrics['status_class']}">{metrics['status']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

                    wm1, wm2, wm3 = st.columns(3)
                    wm1.metric("Etkileşim Oranı (ER)", f"%{metrics['er']:.2f}")
                    wm2.metric("Ort. Beğeni", f"{int(metrics['avg_likes']):,}")
                    wm3.metric("Ort. Yorum", f"{int(metrics['avg_comments']):,}")

                with col_w2:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=metrics['er'],
                        title={'text': "WASK Etkileşim Seviyesi (ER %)"},
                        gauge={
                            'axis': {'range': [0, max(5.0, metrics['er'] * 1.5)]},
                            'bar': {'color': "#2563eb"},
                            'steps': [
                                {'range': [0, metrics['benchmark']['düşük']], 'color': "#fee2e2"},
                                {'range': [metrics['benchmark']['düşük'], metrics['benchmark']['yuksek']], 'color': "#fef9c3"},
                                {'range': [metrics['benchmark']['yuksek'], 10], 'color': "#dcfce7"}
                            ]
                        }
                    ))
                    fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                st.markdown("### 📈 Sektör Benchmark Karşılaştırması")
                benchmark_data = pd.DataFrame({
                    "Kategori": ["Düşük Performans", "Ortalama (Sektör Standardı)", "Hesabınızın Performansı", "Yüksek Performans"],
                    "Etkileşim Oranı (ER %)": [
                        metrics['benchmark']['düşük'] * 0.5,
                        metrics['benchmark']['düşük'],
                        metrics['er'],
                        metrics['benchmark']['yuksek']
                    ]
                })

                fig_bmark = px.bar(
                    benchmark_data,
                    x="Kategori",
                    y="Etkileşim Oranı (ER %)",
                    color="Kategori",
                    text="Etkileşim Oranı (ER %)",
                    template="plotly_white"
                )
                fig_bmark.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                st.plotly_chart(fig_bmark, use_container_width=True)

            else:
                st.error("❌ WASK hesabı için veriler çekilemedi.")

# =========================================================
# SEKMELER 3: KIYASLAMA PANENLİ
# =========================================================
with tab_compare:
    st.subheader("⚖️ 4 Hesap Karşılaştırmalı Analiz Paneli")
    col_u1, col_u2, col_u3, col_u4 = st.columns(4)

    with col_u1: u1 = st.text_input("1. Kullanıcı", key="u1").strip()
    with col_u2: u2 = st.text_input("2. Kullanıcı", key="u2").strip()
    with col_u3: u3 = st.text_input("3. Kullanıcı", key="u3").strip()
    with col_u4: u4 = st.text_input("4. Kullanıcı", key="u4").strip()

    btn_compare = st.button("Hesapları Kıyasla ⚡", key="btn_comp")

    if btn_compare:
        users = [u for u in [u1, u2, u3, u4] if u]
        users = [u[1:] if u.startswith("@") else u for u in users]

        if len(users) < 2:
            st.warning("⚠️ Lütfen en az 2 kullanıcı adı girin.")
        else:
            comp_results = []
            p_bar = st.progress(0)

            for idx, username in enumerate(users):
                st.toast(f"@{username} taranıyor...")
                prof = fetch_apify_instagram_data(username, max_posts=12)

                if prof and "latestPosts" in prof:
                    fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                    fol = max(fol, 1)

                    posts = prof.get("latestPosts", [])
                    likes = [clean_number(p.get("likesCount"), 0) for p in posts]
                    comments = [clean_number(p.get("commentsCount"), 0) for p in posts]

                    avg_likes = np.mean(likes) if likes else 0
                    avg_comments = np.mean(comments) if comments else 0
                    er = ((avg_likes + avg_comments) / fol) * 100.0

                    comp_results.append({
                        "Kullanıcı Adı": f"@{username}",
                        "Takipçi Sayısı": fol,
                        "Ortalama ER (%)": round(er, 2),
                        "Ortalama Beğeni": int(avg_likes),
                        "Ortalama Yorum": int(avg_comments)
                    })

                p_bar.progress((idx + 1) / len(users))

            if comp_results:
                comp_df = pd.DataFrame(comp_results)
                st.markdown("### 📊 Karşılaştırma Özeti")
                st.dataframe(comp_df, use_container_width=True)

                fig_comp = px.bar(
                    comp_df, x="Kullanıcı Adı", y="Ortalama ER (%)",
                    color="Kullanıcı Adı", title="Etkileşim Oranı (ER %) Karşılaştırması",
                    template="plotly_white"
                )
                st.plotly_chart(fig_comp, use_container_width=True)

st.markdown('<div class="footer">MG BRAND OFFICE © 2026 | Powered by Apify & Streamlit</div>', unsafe_allow_html=True)
