import streamlit as st
import time
import math
import re
import collections
import numpy as np
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# SAYFA AYARLARI
# ---------------------------------------------------------
st.set_page_config(page_title="MG BRAND OFFICE", layout="wide")

# ---------------------------------------------------------
# GÜÇLÜ CSS (Görseli Garantiye Alıyoruz)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* ARKA PLAN - DAHA GÜÇLÜ VE SABİT */
    .stApp {
        background: linear-gradient(135deg, #050505 0%, #0a0f1d 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* GLASSMORPHISM - PROFESYONEL AJANS GÖRÜNÜMÜ */
    .glass-card {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 30px !important;
    }
    
    /* YAZI TİPLERİ */
    h1, h2, h3, h4 { color: #f8fafc !important; font-family: 'Inter', sans-serif !important; }
    .stTextInput input { border: 2px solid #2563eb !important; background: #0f172a !important; color: white !important; }
    
    /* BUTONLAR */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        transition: transform 0.2s !important;
    }
    .stButton>button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TEST ARAYÜZÜ (KOD ÇALIŞIYOR MU KONTROLÜ)
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.title("MG BRAND OFFICE • Executive Suite")
st.markdown("### Sistem Durumu: <span style='color: #10b981;'>AKTİF</span>", unsafe_allow_html=True)
st.write("• Eğer bu yazıyı görüyorsan sistem çalışıyor demektir.")

if st.button("SİSTEMİ TEST ET"):
    st.balloons()
    st.success("• Görsel efekt motoru başarıyla çalıştırıldı.")
st.markdown("</div>", unsafe_allow_html=True)
