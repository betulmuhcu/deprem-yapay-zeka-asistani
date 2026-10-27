
import os
import re

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors
from sqlalchemy import create_engine


# .env dosyasındaki güncel ayarları yükle
load_dotenv(override=True)

MODEL = "gemini-3.5-flash-lite"

# Gemini API istemcisini oluştur
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY bulunamadı. .env dosyanı kontrol et."
    )

client = genai.Client(api_key=api_key)


# SQL Server bağlantısını oluştur
engine = create_engine(
    f"mssql+pyodbc://@{os.getenv('SQL_SERVER')}/{os.getenv('SQL_DB')}"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)


# Veritabanı şeması ve Gemini için kurallar
SCHEMA = """
Tablo: deprem_verileri (Microsoft SQL Server, T-SQL)

Sütunlar:
- earthquake_id: deprem kimliği
- date: deprem zamanı (UTC)
- magnitude: deprem büyüklüğü
- place: tam yer açıklaması (İngilizce)
- region: place içindeki bölge veya ülke adı (İngilizce)
- longitude, latitude: koordinatlar
- depth_km: derinlik (km)

Veri: Tüm dünya, 2000-01-01'den itibaren yaklaşık 188 bin deprem.

Kurallar:
- Yalnızca tek bir SELECT sorgusu üret.
- Açıklama veya Markdown kod bloğu ekleme.
- Microsoft SQL Server T-SQL kullan.
- LIMIT yerine TOP kullan.
- Yıl filtresinde YEAR(date) kullan.
- Yer filtresinde İngilizce adlarla LIKE kullan.
- Japonya için region LIKE '%Japan%' kullan.
- Türkiye için region LIKE '%Turkey%' OR region LIKE '%T_rkiye%' kullan.
- Satır döndüren sorgularda en fazla TOP 100 kullan.
- Kullanıcıdan gelen metni SQL kodu olarak doğrudan çalıştırma.
- Sadece belirtilen deprem tablosunu ve sütunlarını kullan.
"""

# Tehlikeli SQL ifadelerini engelle
YASAK = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|exec|execute|"
    r"merge|grant|into|union|backup|restore|"
    r"waitfor|openrowset|opendatasource)\b|;|--|/\*|\*/",
    re.IGNORECASE
)


def hata_mesaji(e):
    """Gemini API hatalarını anlaşılır mesajlara dönüştür."""

    if isinstance(e, errors.ClientError):
        if e.code == 429:
            return (
                "Gemini API ücretsiz kullanım kotası doldu. "
                "Kota yenilendiğinde tekrar deneyebilirsin. "
            )

        if e.code == 400:
            return (
                "Gemini isteği kabul etmedi. "
                "Model ayarlarını ve gönderilen isteği kontrol et."
            )

        if e.code == 401 or e.code == 403:
            return (
                "Gemini API erişim hatası. "
                "API anahtarını ve erişim ayarlarını kontrol et."
            )

        return f"Gemini API hatası oluştu (HTTP {e.code})."

    if isinstance(e, errors.ServerError):
        return (
            "Gemini sunucusu şu anda yanıt veremiyor. "
            "Bir süre sonra tekrar dene."
        )

    return "Beklenmeyen bir hata oluştu. Ayrıntılar terminalde görüntülenebilir."


def sql_uret(istek):
    """Kullanıcı sorusunu SQL sorgusuna dönüştür."""

    yanit = client.models.generate_content(
        model=MODEL,
        contents=istek,
        config=types.GenerateContentConfig(
            system_instruction=SCHEMA,
            temperature=0,
        ),
    )

    if not yanit.text:
        raise RuntimeError("Gemini boş bir SQL yanıtı döndürdü.")

    sql = re.sub(
        r"^\s*```(?:sql)?\s*|\s*```\s*$",
        "",
        yanit.text,
        flags=re.IGNORECASE,
    ).strip()

    # Sonlandırıcı noktalı virgülü kaldır
    sql = sql.rstrip(";").strip()

    return sql


def guvenli_mi(sql):
    """Sorgunun güvenli ve tek bir SELECT olup olmadığını kontrol et."""

    temiz_sql = sql.strip()

    # Yalnızca SELECT ile başlayan sorgular kabul edilir
    if not re.match(r"^select\b", temiz_sql, re.IGNORECASE):
        return False

    # Yasaklı SQL ifadelerini ve çoklu sorgu işaretlerini engelle
    if YASAK.search(temiz_sql):
        return False

    # Yalnızca izin verilen tabloyu kullan
    tablo_eslesmeleri = re.findall(
        r"\b(?:from|join)\s+([a-zA-Z0-9_.\[\]]+)",
        temiz_sql,
        re.IGNORECASE,
    )

    if not tablo_eslesmeleri:
        return False

    for tablo in tablo_eslesmeleri:
        tablo_adi = tablo.replace("[", "").replace("]", "").split(".")[-1]

        if tablo_adi.lower() != "deprem_verileri":
            return False

    return True


def yorumla(soru, df):
    """SQL sonucunu Gemini ile Türkçe açıkla."""

    # Sonuç boşsa ikinci bir API çağrısı yapma
    if df.empty:
        return "Bu koşullara uygun deprem kaydı bulunamadı."

    sonuc = df.head(30).to_string(index=False)

    yanit = client.models.generate_content(
        model=MODEL,
        contents=(
            f"Kullanıcı sorusu: {soru}\n\n"
            f"SQL sorgusunun sonucu:\n{sonuc}\n\n"
            "Sonuçları 1-3 cümleyle Türkçe açıkla. "
            "Yalnızca verilen sonuçlardaki bilgileri kullan. "
            "Sonuçta olmayan bilgi veya sayı uydurma."
        ),
        config=types.GenerateContentConfig(
            temperature=0,
        ),
    )

    if not yanit.text:
        return "Sorgu çalıştı ancak sonuç açıklaması oluşturulamadı."

    return yanit.text.strip()


@st.cache_data(show_spinner=False, ttl=300)
def sor(soru):
    """Soruyu işle, SQL sorgusunu çalıştır ve sonucu döndür."""

    soru = soru.strip()

    if not soru:
        return "", None, "Lütfen bir soru yaz."

    try:
        # İlk SQL sorgusunu oluştur
        istek = soru
        sql = sql_uret(istek)

        # Güvenlik kontrolünü geçemeyen sorguyu çalıştırma
        if not guvenli_mi(sql):
            return (
                sql,
                None,
                "Oluşturulan sorgu güvenlik kontrolünden geçemedi. "
                "Lütfen sorunu farklı şekilde ifade et.",
            )

        # SQL sorgusunu en fazla iki kez dene.
        # İkinci deneme yalnızca veritabanı sorguyu reddederse yapılır.
        for deneme in range(2):
            try:
                df = pd.read_sql(sql, engine)

                # SQL sonucu alındıktan sonra Türkçe açıklama üret
                cevap = yorumla(soru, df)

                return sql, df, cevap

            except (errors.ClientError, errors.ServerError):
                # Gemini hatalarında yeni istek gönderme
                raise

            except Exception as e:
                # İlk SQL denemesi başarısızsa düzeltme iste
                if deneme == 0:
                    istek = (
                        f"Kullanıcı sorusu: {soru}\n"
                        f"Önceki SQL sorgusu: {sql}\n"
                        f"Veritabanı hatası: {str(e)[:1000]}\n"
                        "Hataları düzelt ve yalnızca yeni SELECT "
                        "sorgusunu döndür."
                    )

                    sql = sql_uret(istek)

                    if not guvenli_mi(sql):
                        return (
                            sql,
                            None,
                            "Düzeltilen sorgu güvenlik kontrolünden geçemedi.",
                        )
                else:
                    return (
                        sql,
                        None,
                        "SQL sorgusu iki denemede de çalıştırılamadı. "
                        "Soruyu farklı şekilde ifade etmeyi dene.",
                    )

        return sql, None, "Sorgu çalıştırılamadı."

    except (errors.ClientError, errors.ServerError) as e:
        mesaj = hata_mesaji(e)
        return "", None, mesaj

    except Exception as e:
        # Teknik ayrıntıları terminale yaz; arayüzde anlaşılır mesaj göster
        print(f"Deprem asistanı hatası: {type(e).__name__}: {e}")

        return (
            "",
            None,
            "Bir hata oluştu. Terminaldeki hata mesajını kontrol et.",
        )
