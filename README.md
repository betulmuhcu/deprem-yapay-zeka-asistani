# 🌍 Deprem Veri Analitiği ve Yapay Zekâ Asistanı (Text-to-SQL)

2000–2026 yılları arasındaki yaklaşık **188.000 küresel deprem kaydını** sorgulamak, analiz etmek ve görselleştirmek için geliştirilen yapay zekâ destekli bir veri analitiği web uygulaması.

Proje; USGS Earthquake API üzerinden elde edilen deprem verilerini Python ile işler, Microsoft SQL Server üzerinde depolar ve kullanıcıların doğal dilde yazdığı soruları SQL sorgularına dönüştürür. Sorgu sonuçları Streamlit arayüzünde tablolar, harita görselleştirmeleri ve yapay zekâ tarafından oluşturulan Türkçe açıklamalarla sunulur.

## ✨ Temel Özellikler

- **Text-to-SQL:** Doğal dildeki soruları T-SQL sorgularına dönüştürme.
- **SQL Server entegrasyonu:** Deprem verilerini doğrudan veritabanından sorgulama.
- **Yapay zekâ ile sonuç yorumlama:** Sorgu sonuçlarını kısa ve anlaşılır Türkçe açıklamalarla sunma.
- **Otomatik hata düzeltme:** Sorgu hatalarını modele ileterek sınırlı sayıda yeniden deneme yapma.
- **Veri görselleştirme:** Sorgu sonuçlarını tablolar ve koordinat tabanlı haritalarla inceleme.
- **Hazır analiz senaryoları:** Örnek sorular üzerinden hızlıca sorgu yapabilme.
- **Önbellekleme:** Tekrarlanan işlemlerde gereksiz API ve veritabanı çağrılarını azaltma.

## 🏗️ Sistem Mimarisi ve Veri Akışı

1. **Veri toplama:** USGS Earthquake API üzerinden deprem verileri alınır.
2. **Veri işleme:** Python ve Pandas ile veriler temizlenir ve analize hazırlanır.
3. **Veri depolama:** Veriler Microsoft SQL Server'daki `deprem_verileri` tablosuna aktarılır.
4. **Text-to-SQL:** Kullanıcının doğal dildeki sorusu, veritabanı şeması dikkate alınarak T-SQL sorgusuna dönüştürülür.
5. **Sorgu güvenliği:** Üretilen sorgular, çalıştırılmadan önce temel güvenlik kontrollerinden geçirilir.
6. **Sorgu yürütme:** SQLAlchemy ve pyodbc aracılığıyla sorgu SQL Server üzerinde çalıştırılır.
7. **Sonuçların sunulması:** Sonuçlar Pandas ile işlenir; Streamlit arayüzünde tablo, harita ve yapay zekâ destekli Türkçe açıklama olarak gösterilir.

## 🛠️ Kullanılan Teknolojiler

- **Programlama dili:** Python
- **Veri toplama:** USGS Earthquake API
- **Veri işleme:** Pandas
- **Veritabanı:** Microsoft SQL Server, T-SQL
- **Veritabanı bağlantısı:** SQLAlchemy, pyodbc
- **Web arayüzü:** Streamlit
- **Yapay zekâ:** Google Gemini API — Gemini 3.5 Flash Lite
- **Diğer araçlar:** python-dotenv, RegEx

## 🚀 Kurulum ve Çalıştırma


### 2. Projeyi bilgisayarınıza indirin

GitHub deposunu bilgisayarınıza klonlayın:

```bash
git clone REPOSITORY_URL
cd REPOSITORY_FOLDER
```

`REPOSITORY_URL` ve `REPOSITORY_FOLDER` ifadelerini kendi GitHub depo adresiniz ve klasör adınızla değiştirin. Alternatif olarak GitHub üzerinden **Code → Download ZIP** seçeneğini kullanabilirsiniz.

### 3. Sanal ortam oluşturun

```bash
python -m venv .venv
```

Sanal ortamı etkinleştirin.

**Windows:**

```bash
.venv\Scripts\activate
```

### 4. Gerekli kütüphaneleri yükleyin

```bash
pip install pandas sqlalchemy pyodbc streamlit python-dotenv google-genai
```

### 5. Ortam değişkenlerini ayarlayın

Proje klasöründeki `.env.example` dosyasını `.env` adıyla kopyalayın. Ardından `.env` dosyasını kendi bilgilerinizle doldurun:

- `GEMINI_API_KEY`: Google AI Studio üzerinden alınan Gemini API anahtarı.
- `SQL_SERVER`: SQL Server sunucu adı veya bağlantı adresi.
- `SQL_DB`: Deprem verilerinin bulunduğu veritabanının adı.

### 6. Veritabanını hazırlayın

Microsoft SQL Server üzerinde proje verilerinizin bulunduğu veritabanını oluşturun veya mevcut veritabanınıza bağlanın.

Uygulamanın beklediği `deprem_verileri` tablosunun oluşturulmuş ve deprem verileriyle doldurulmuş olması gerekir. Proje dosyalarınızda veri toplama veya SQL'e aktarma betikleri bulunuyorsa bunları da kendi sırasına göre çalıştırın.

### 7. Uygulamayı başlatın

Proje klasöründe aşağıdaki komutu çalıştırın:

```bash
streamlit run app.py
```

## 👩‍💻 Geliştirici

**Betül Muhcu**  
