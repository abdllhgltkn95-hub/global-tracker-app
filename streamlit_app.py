def calculate_wask_er(likes_list, comments_list, follower_count):
    if not likes_list or follower_count <= 0:
        return 0.0, "Veri Yetersiz"
    
    # Son gönderilerin ortalaması
    avg_likes = sum(likes_list) / len(likes_list)
    avg_comments = sum(comments_list) / len(comments_list)
    
    # Ortalama Etkileşim / Takipçi * 100
    total_avg_engagement = avg_likes + avg_comments
    er = (total_avg_engagement / follower_count) * 100
    
    # Sektör Benchmark Değerlendirmesi
    if follower_count < 10000:
        status = "Yüksek" if er > 4.0 else ("Ortalama" if er >= 1.5 else "Düşük")
    elif follower_count < 100000:
        status = "Yüksek" if er > 2.5 else ("Ortalama" if er >= 1.0 else "Düşük")
    else:
        status = "Yüksek" if er > 1.8 else ("Ortalama" if er >= 0.8 else "Düşük")
        
    return round(er, 2), status
