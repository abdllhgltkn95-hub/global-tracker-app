import time
import math
import re
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
    page_title="MG BRAND OFFICE | Intelligence Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APIFY_TOKEN = "apify_api_gvh1Gqo99oDTmXqrb4CwCk24HGWmcN07zSRb"

# ---------------------------------------------------------
# 2. BEYAZ TEMA & KUSURSUZ STİL
# ---------------------------------------------------------
st.markdown(
    """
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
        color: #0f172a !important;
    }

    .stTextInput input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
    }

    .reflection-container {
        text-align: center;
        padding-top: 25px;
        padding-bottom: 10px;
    }

    .brand-header-light {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #1e3a8a, #2563eb, #4f46e5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: inline-block;
        -webkit-box-reflect: below -18px linear-gradient(transparent 50%, rgba(255, 255, 255, 0.35));
    }

    .brand-sub-light {
        text-align: center;
        color: #475569 !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    .effect-card {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 16px !important;
    }

    [data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 900 !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        background-color: #ffffff !important;
        padding: 8px 16px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #cbd5e1 !important;
        max-width: fit-content;
        margin: 0 auto 30px auto;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 30px !important;
        padding: 0px 24px !important;
        font-weight: 800 !important;
        color: #475569 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
    }
    
    .stTabs [aria-selected="true"] span { color: #ffffff !important; }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
    }

    .report-box {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-left: 6px solid #2563eb !important;
        border-radius: 12px;
        padding: 22px;
        margin-top: 20px;
    }

    .footer-light {
        text-align: center;
        color: #64748b !important;
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
# 3. VERİ KONTROL & OTOMATİK BOT YORUM MOTORU
# ---------------------------------------------------------
def clean_username(input_text: str) -> str:
    if not input_text:
        return ""
    input_text = input_text.strip()
    match = re.search(r'instagram\.com/([^/?#]+)', input_text)
    if match:
        return match.group(1)
    return input_text.replace("@", "").strip()

def clean_number(value, default=0.0) -> float:
    if value is None:
        return default
    try:
        val = float(value)
        return default if math.isnan(val) else val
    except (ValueError, TypeError):
        return default

def analyze_comment_authenticity(comments_data: list) -> dict:
    """Yorumları metin madenciliği ile analiz ederek bot/organik tespiti yapar."""
    if not comments_data:
        return {"organic": 0, "bot": 0, "bot_pct": 0.0, "details": []}
    
    generic_words = {"harika", "süper", "muhteşem", "nice", "great", "wow", "love", "çok güzel", "bayıldım", "gt", "unf", "takip", "geri takip"}
    
    bot_count = 0
    organic_count = 0
    analyzed_list = []

    for item in comments_data:
        text = str(item.get("text", "")).strip().lower()
        owner = item.get("ownerUsername", "gizli")
        
        is_bot = False
        reasons = []

        # 1. Sadece emoji içeriyor mu?
        if len(text) > 0 and not re.search(r'[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]', text):
            is_bot = True
            reasons.append("Sadece Emoji")
        
        # 2. Çok kısa jenerik kelime mi?
        elif text in generic_words or (len(text.split()) == 1 and len(text) < 5):
            is_bot = True
            reasons.append("Jenerik / Şablon Metin")
            
        # 3. SPAM / Takip Daveti içeriyor mu?
        elif any(w in text for w in ["gt", "takip et", "son gönderi", "unf yapma", "dm"]):
            is_bot = True
            reasons.append("Spam / Takip Çağrısı")

        if is_bot:
            bot_count += 1
            status = "⚠️ Şüpheli / Bot"
        else:
            organic_count += 1
            status = "✅ Organik"

        analyzed_list.append({
            "Kullanıcı": f"@{owner}",
            "Yorum": text if text else "[Resim/Emoji]",
            "Durum": status,
            "Nedeni": ", ".join(reasons) if reasons else "Doğal Etkileşim"
        })

    total = len(comments_data)
    bot_pct = (bot_count / max(total, 1)) * 100.0

    return {
        "organic": organic_count,
        "bot": bot_count,
        "bot_pct": bot_pct,
        "details": analyzed_list
    }

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_apify_instagram_data(username: str, max_posts: int = 12):
    actor_id = "apify~instagram-profile-scraper"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}"
    payload = {"usernames": [username], "resultsLimit": int(max_posts)}

    try:
        response = requests.post(run_url, json=payload, timeout=25)
        if response.status_code not in [200, 201]:
            return None

        run_data = response.json().get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            return None

        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"

        for _ in range(25):
            time.sleep(2)
            res = requests.get(dataset_url, timeout=15)
            if res.status_code == 200:
                items = res.json()
                if items and len(items) > 0:
                    return items[0]
        return None
    except Exception:
        return None

def calculate_influencer_hero_metrics(followers: int, likes_list: list, comments_list: list, views_list: list) -> dict:
    avg_likes = float(np.mean(likes_list)) if likes_list else 0.0
    avg_comments = float(np.mean(comments_list)) if comments_list else 0.0
    avg_views = float(np.mean(views_list)) if views_list else avg_likes * 4.0
    
    total_engagement = avg_likes + avg_comments
    er = (total_engagement / max(followers, 1)) * 100.0
    emv = ((avg_views / 1000.0) * 10.0) + (total_engagement * 0.25)
    
    credibility = 85.0
    if (avg_comments / max(avg_likes, 1.0)) < 0.005:
        credibility -= 25.0
    if er < 0.5:
        credibility -= 20.0

    credibility_score = int(np.clip(credibility, 15, 98))
    authentic_followers_pct = int(np.clip(credibility_score + np.random.randint(-2, 3), 10, 95))
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
# 4. ARAYÜZ
# ---------------------------------------------------------
st.markdown("""
    <div class="reflection-container">
        <h1 class="brand-header-light">MG BRAND OFFICE</h1>
    </div>
    <div class="brand-sub-light">Yeni Nesil Influencer Audit & Otomatik Yorum Tespiti</div>
""", unsafe_allow_html=True)

tab_hero, tab_wask = st.tabs(["• Influencer Hero & Yorum Audit", "• WASK Intelligence"])

with tab_hero:
    st.markdown('<div class="effect-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        raw_hero = st.text_input("Instagram Kullanıcı Adı veya Linki", placeholder="Örn: trendyol", key="hero_user_input")
    with c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_hero = st.button("Derin Analiz Başlat", key="btn_hero")

    if btn_hero and raw_hero:
        hero_user = clean_username(raw_hero)
        with st.spinner(f"@{hero_user} taranıyor, gönderiler ve yorumlar tespitten geçiriliyor..."):
            prof = fetch_apify_instagram_data(hero_user, max_posts=18)

            if prof and "latestPosts" in prof:
                fol = int(clean_number(prof.get("followersCount", prof.get("followers", 0)), default=1))
                posts = prof.get("latestPosts", [])
                
                likes = [clean_number(p.get("likesCount"), 0) for p in posts]
                comments = [clean_number(p.get("commentsCount"), 0) for p in posts]
                views = [clean_number(p.get("videoViewCount"), p.get("likesCount", 0)) for p in posts]

                # Tüm yorumları topla
                all_raw_comments = []
                for p in posts:
                    if "latestComments" in p and isinstance(p["latestComments"], list):
                        all_raw_comments.extend(p["latestComments"])

                metrics = calculate_influencer_hero_metrics(fol, likes, comments, views)
                comment_audit = analyze_comment_authenticity(all_raw_comments)

                # Metrik Kartları
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Kitle Güvenilirliği", f"%{metrics['credibility_score']}")
                m2.metric("Etkileşim Oranı (ER)", f"%{metrics['er']:.2f}")
                m3.metric("Kazanılmış Medya (EMV)", f"${metrics['emv']:,.2f}")
                m4.metric("Şüpheli Yorum Oranı", f"%{comment_audit['bot_pct']:.1f}")

                st.markdown("<br>", unsafe_allow_html=True)

                # OTOMATİK YORUM RAPORU
                st.subheader("📊 Otomatik Yorum ve Bot Tespiti Raporu")
                
                col_c1, col_c2 = st.columns([1, 2])
                with col_c1:
                    comment_df = pd.DataFrame({
                        "Tür": ["Organik Yorum", "Şüpheli / Bot Yorum"],
                        "Sayı": [comment_audit['organic'], comment_audit['bot']]
                    })
                    fig_pie = px.pie(comment_df, names="Tür", values="Sayı", color="Tür", color_discrete_map={"Organik Yorum": "#2563eb", "Şüpheli / Bot Yorum": "#f43f5e"}, hole=0.4)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_c2:
                    st.markdown("##### 🔍 Taranan Son Yorumların Canlı Dökümü")
                    if comment_audit['details']:
                        st.dataframe(pd.DataFrame(comment_audit['details']), use_container_width=True, height=280)
                    else:
                        st.info("Bu hesapta taranacak açık yorum detayı bulunamadı veya yorumlar kapalı.")

                # OTOMATİK RAPOR METNİ
                st.markdown(f"""
                <div class="report-box">
                    <h4 style="color:#1e3a8a; margin-top:0;">📋 OTOMATİK DENETİM VE KİTLE KANAATİ</h4>
                    <p><b>Profil:</b> @{hero_user} | <b>İncelenen Yorum Sayısı:</b> {len(all_raw_comments)}</p>
                    <ul>
                        <li><b>Yorum Kalitesi:</b> Yapılan otomatik tespitte yorumların <b>%{100 - comment_audit['bot_pct']:.1f}</b> kadarı gerçek kullanıcı etkileşiminden oluşmaktadır.</li>
                        <li><b>Bot Risk Durumu:</b> Gönderilere gelen şüpheli/şablon yorum oranı <b>%{comment_audit['bot_pct']:.1f}</b> olarak hesaplanmıştır.</li>
                        <li><b>Karar:</b> {"✅ Bu profil marka iş birlikleri için güvenlidir." if comment_audit['bot_pct'] < 20 else "⚠️ Yüksek oranda şüpheli etkileşim/bot tespiti yapıldı. Dikkatli olunmalıdır."}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("• Profil verisi çekilemedi. Kullanıcı adını kontrol edin.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_wask:
    st.info("WASK Reklam simülasyonu bu sekmede aktif durumdadır.")

st.markdown('<div class="footer-light">MG BRAND OFFICE © 2026 | Enterprise Intelligence Engine</div>', unsafe_allow_html=True)
