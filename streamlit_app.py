# TIKTOK MATEMATİKSEL KONTROL BLOGU (Önizleme)
if platform == "TikTok":
    # 1. LVR (Like-to-View Ratio) Kontrolü
    avg_views = np.mean(views)
    lvr = avg_likes / max(avg_views, 1.0)
    
    if lvr < 0.01: 
        fraud_type = "AĞIR İHLAL: İzlenme Botu"
        bot_risk += 60.0
    elif lvr > 0.40:
        fraud_type = "AĞIR İHLAL: Suni Beğeni Şişirmesi"
        bot_risk += 50.0

    # 2. Viralite Skoru
    viral_score = avg_views / max(followers, 1)
    
    # 3. Ters Varyans Kontrolü (Stabilite = Sahtekarlık)
    if cv < 0.15: # Tüm videolar aynı izlenmeye sahipse
        fraud_type = "AĞIR İHLAL: Otomatik Paket İzlenme"
        bot_risk += 70.0
