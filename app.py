import streamlit as st
from asistan import sor

st.title("🌍 Deprem Veri Asistanı")

# Yan yana iki buton için sütun oluşturma
col1, col2 = st.columns(2)
with col1:
    ornek_1 = st.button("2023 Türkiye Depremleri")
with col2:
    ornek_2 = st.button("Tarihteki En Büyük 5 Deprem")

# Kullanıcının kendi sorusu için alan
soru = st.text_input("Veya kendi sorunu yaz:", placeholder="2020'den beri en büyük 5 deprem hangileri?")

# Hangi sorunun işleme alınacağını belirleme
aktif_soru = None
if ornek_1:
    aktif_soru = "2023 yılında Türkiye'de gerçekleşen depremleri getir."
elif ornek_2:
    aktif_soru = "Tarihteki en büyük 5 depremi getir."
elif st.button("Sor") and soru:
    aktif_soru = soru

# Seçilen soruyu yapay zekaya ve veritabanına gönderme
if aktif_soru:
    with st.spinner("Düşünüyorum..."):
        sql, df, cevap = sor(aktif_soru)
        
    st.write(cevap)
    if df is not None:
        st.dataframe(df)
        if {"latitude", "longitude"} <= set(df.columns):
            st.map(df)
            
    with st.expander("Üretilen SQL"):
        st.code(sql, language="sql")
