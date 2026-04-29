import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import json
import os
from fpdf import FPDF
from ortools.sat.python import cp_model

st.set_page_config(
    page_title="SBMYO Sınav Sistemi",
    page_icon=":material/calendar_month:",
    layout="wide"
)

KULLANICI_ADI = "Sbmy"
SIFRE = "sbmy2026.0"

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = ""

if not st.session_state.giris_yapildi:
    st.title("Giriş Yap")

    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    ad_soyad = st.text_input("Adınız Soyadınız")

    if st.button("Giriş"):
        if kullanici == KULLANICI_ADI and sifre == SIFRE:
            if not ad_soyad.strip():
                st.warning("Lütfen adınızı ve soyadınızı girin.")
            else:
                st.session_state.giris_yapildi = True
                st.session_state.aktif_kullanici = ad_soyad.strip()
                st.success("Giriş başarılı")
                st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı")

    st.stop()

ust_sol, ust_sag = st.columns([6, 1])

with ust_sol:
    st.title("SBMYO Sınav Programı Sistemi")
    st.caption("Hacettepe Üniversitesi Sosyal Bilimler Meslek Yüksekokulu")

with ust_sag:
    st.caption(f"Kullanıcı: {st.session_state.aktif_kullanici}")
    if st.button("Çıkış Yap"):
        st.session_state.giris_yapildi = False
        st.session_state.aktif_kullanici = ""
        st.rerun()

st.write("Ders, tarih, saat, derslik ve gözetmen bilgilerini kullanarak sınav programı oluşturun.")

GOZETMENLER = [
    "Doç. Dr. Volkan Işık",
    "Doç. Dr. Demet Çakıroğlu",
    "Doç. Dr. Özlem Zerrin Keyvan",
    "Öğr.Gör. Dr. Mehmet Akif Ayarlıoğlu",
    "Öğr. Gör. Dr. Ali Bertan Savaş",
    "Öğr. Gör. Dr. Ayşe Usta",
    "Öğr. Gör. Dr. Pınar Anaforoğlu",
    "Öğr. Gör. Dr. Şule Tarım",
    "Öğr. Gör. Meltem Demir",
    "Öğr. Gör. Nazlı Itır Boso",
    "Öğr. Gör. Esra Kirazlı Korkmaz",
    "Öğr. Gör. Zelal Karabulut",
    "Öğr. Gör. Özgün Eroğlu",
    "Öğr. Gör. Derya Seylan Akkurt",
    "Öğr. Gör. İpek Eröz",
    "Öğr. Gör. Tuna Gamze Taşcıoğlu",
    "Öğr. Gör. Salih Özer",
    "Öğr. Gör. E. Emel Eroğlu Gelir",
    "Dr. Öğr. Üyesi İbrahim Ceyhan Koç",
    "Öğr.Gör. Memduh YAZAR",
    "Öğr.Gör. Orhan KARATAŞ",
    "Öğr.Gör. İbrahim ÜSTÜN",
    "Dr. Faruk KAYADELEN",
    "Araş. Gör. Dr. Güven Şimşek",
    "Öğr.Gör Asuman BAYRAM",
]

DERSLER = {
    "BYA": [
        ("BYA 105", "Ticari Matematik"),
        ("BYA 106", "İletişim"),
        ("BYA 107", "Temel Hukuk"),
        ("BYA 108", "Örgütsel Davranış"),
        ("BYA 109", "Protokol ve Sosyal Davranış Kuralları"),
        ("BYA 110", "Mesleki Yazışmalar"),
        ("BYA 111", "Klavye Teknikleri"),
        ("BYA 112", "Dosyalama ve Arşivleme"),
        ("BYA 113", "Bilgi ve İletişim Teknolojileri"),
        ("BYA 114", "Bilgisayar Büro Programları"),
        ("BYA 115", "Genel İşletme"),
        ("BYA 116", "Genel Ekonomi"),
        ("BYA 201", "Büro Yönetimi"),
        ("BYA 202", "Yönetici Asistanlığı"),
        ("BYA 204", "Halkla İlişkiler"),
        ("BYA 205", "Genel Muhasebe"),
        ("BYA 207", "İş ve Sosyal Güvenlik Hukuku"),
        ("BYA 208", "Meslek Etiği"),
        ("BYA 209", "Müşteri İlişkileri Yönetimi"),
        ("BYA 210", "Etkili ve Güzel Konuşma"),
        ("BYA 211", "Mesleki İngilizce I"),
        ("BYA 212", "Mesleki İngilizce II"),
        ("BYA 217", "Kriz ve Stres Yönetimi"),
        ("BYA 218", "Zaman Yönetimi"),
        ("BYA 219", "Kalite Yönetim Sistemleri"),
        ("BYA 220", "Toplantı Yönetimi"),
        ("BYA 221", "Çevre Koruma"),
        ("BYA 222", "Araştırma Yöntem ve Teknikleri"),
        ("BYA 223", "İnsan Kaynakları Yönetimi"),
    ],
    "MVU": [
        ("MVU 101", "İşletme Yönetimi I"),
        ("MVU 102", "İşletme Yönetimi II"),
        ("MVU 103", "Mikro Ekonomi"),
        ("MVU 104", "Makro Ekonomi"),
        ("MVU 105", "Mesleki Matematik"),
        ("MVU 106", "Ticari Matematik"),
        ("MVU 107", "Temel Hukuk"),
        ("MVU 108", "Ticaret Hukuk Bilgisi"),
        ("MVU 109", "Genel Muhasebe I"),
        ("MVU 110", "Genel Muhasebe II"),
        ("MVU 111", "Ofis Programları I"),
        ("MVU 112", "Ofis Programları II"),
        ("MVU 113", "İletişim"),
        ("MVU 116", "Mesleki Mevzuat ve Etik"),
        ("MVU 201", "Maliyet Muhasebesi"),
        ("MVU 202", "Mali Tablolar Analizi"),
        ("MVU 207", "Finansal Yönetim"),
        ("MVU 208", "Finansal Yatırım Araçları"),
        ("MVU 209", "Dış Ticaret İşlemleri"),
        ("MVU 210", "Dış Ticaret İşlemleri Muhasebesi"),
        ("MVU 211", "Vergi Hukuku"),
        ("MVU 212", "Vergi Sistemi"),
        ("MVU 213", "Kamu Maliyesi"),
        ("MVU 214", "İş ve Sosyal Güvenlik Hukuku"),
        ("MVU 215", "Şirketler Muhasebesi"),
        ("MVU 216", "Paket Programlar"),
        ("MVU 217", "Banka Muhasebesi"),
        ("MVU 219", "Konaklama İşletmeleri Muhasebesi"),
        ("MVU 220", "Vergi Muhasebesi"),
        ("MVU 221", "Borçlar Hukuku"),
        ("MVU 222", "Muhasebe Denetimi"),
        ("MVU 223", "Bilgi ve İletişim Teknolojileri"),
        ("MVU 230", "Kalite Yönetim Sistemleri"),
        ("MVU 232", "Çevre Koruma"),
    ],
    "SGP": [
        ("SGP 101", "Temel Ses Bilgisi"),
        ("SGP 102", "Işık Uygulamaları"),
        ("SGP 103", "Temel Işık Bilgisi"),
        ("SGP 104", "Ses Uygulamaları"),
        ("SGP 105", "Tiyatro Akım ve Özellikleri I"),
        ("SGP 106", "Tiyatro Akımları ve Özellikleri II"),
        ("SGP 107", "Doğru Akım Analizi"),
        ("SGP 108", "Alternatif Akım Devre Analizi"),
        ("SGP 109", "Matematik"),
        ("SGP 110", "Analog Elektronik II"),
        ("SGP 111", "Analog Elektronik I"),
        ("SGP 112", "Işık Teknolojileri"),
        ("SGP 201", "Sinema Tarihi, Kuramı ve Dili I"),
        ("SGP 202", "Sinema Tarihi, Kuramı ve Dili II"),
        ("SGP 203", "Metin Çözümlemesi I"),
        ("SGP 204", "Metin Çözümlemesi II"),
        ("SGP 208", "İleri Ses Bilgisi II"),
        ("SGP 209", "Akustik"),
        ("SGP 210", "Temel Fotoğrafçılık"),
        ("SGP 213", "Sahne Tasarımı I"),
        ("SGP 214", "İleri Işık Bilgisi II"),
        ("SGP 215", "İleri Ses Bilgisi I"),
        ("SGP 216", "İleri Ses Uygulamaları II"),
        ("SGP 217", "İleri Işık Bilgisi I"),
        ("SGP 220", "Ses Stüdyo Teknikleri II"),
        ("SGP 221", "İleri Ses Uygulamaları I"),
        ("SGP 223", "TV. Film Seslendirmesi"),
        ("SGP 225", "İleri Işık Uygulamaları I"),
        ("SGP 227", "Ses Stüdyo Teknikleri I"),
        ("SGP 230", "Sahne Tasarımı II"),
        ("SGP 232", "TV. Film Işıklandırması"),
    ],
    "TOT": [
        ("TOT 103", "Genel Turizm"),
        ("TOT 104", "Otel İşletmeciliği"),
        ("TOT 106", "Menü Planlama"),
        ("TOT 109", "Turizm Ekonomisi"),
        ("TOT 110", "Genel Muhasebe"),
        ("TOT 111", "İletişim"),
        ("TOT 112", "Konukla İletişim"),
        ("TOT 113", "Bilgi ve İletişim Teknolojileri"),
        ("TOT 114", "İş Organizasyonu"),
        ("TOT 115", "Genel İşletme"),
        ("TOT 116", "Kat Hizmetleri Yönetimi"),
        ("TOT 117", "Ön Büro Hizmetleri"),
        ("TOT 204", "İnsan Kaynakları Yönetimi"),
        ("TOT 205", "Seyahat Acentacılığı ve Tur Operatörlüğü"),
        ("TOT 206", "Dekorasyon Hizmetleri"),
        ("TOT 207", "Turizm Coğrafyası"),
        ("TOT 208", "İşçi Sağlığı ve İş Güvenliği"),
        ("TOT 210", "Kalite Yönetim Sistemleri"),
        ("TOT 211", "Mesleki İngilizce I"),
        ("TOT 212", "Mesleki İngilizce II"),
        ("TOT 213", "Otelcilik Otomasyon Sistemleri I"),
        ("TOT 214", "Otelcilik Otomasyon Sistemleri II"),
        ("TOT 215", "Turizm Pazarlaması"),
        ("TOT 216", "Turizm İşletmelerinde Maliyet Analizi"),
        ("TOT 217", "Ziyafet Servis Yönetimi"),
        ("TOT 218", "Ticari Matematik"),
        ("TOT 219", "Türk Mutfak Kültürü"),
        ("TOT 220", "Kongre ve Fuar Yönetimi"),
        ("TOT 222", "Rekreasyon Yönetimi"),
        ("TOT 223", "Yatırım Proje Analizi"),
        ("TOT 224", "Satış Yönetimi"),
        ("TOT 226", "Meslek Etiği"),
        ("TOT 227", "Örgütsel Davranış"),
        ("TOT 229", "Araştırma Yöntem ve Teknikleri"),
        ("TOT 231", "Çevre Koruma"),
    ],
    "ORTAK": [
        ("AİT 103", "Atatürk İlkeleri ve İnkılap Tarihi I"),
        ("AİT 104", "Atatürk İlkeleri ve İnkılap Tarihi II"),
        ("TKD 103", "Türk Dili I"),
        ("TKD 104", "Türk Dili II"),
        ("İNG 127", "Temel İngilizce I"),
        ("İNG 128", "Temel İngilizce II"),
        ("ÜNİ 101", "Üniversite Yaşamına Giriş"),
        ("SBY 202", "Girişimcilik"),
    ],
}

BOLUMLER = [b for b in DERSLER.keys() if b != "ORTAK"]

# Tüm dersleri düz liste olarak hazırla
TUM_DERSLER = []
for bolum, dersler in DERSLER.items():
    for kod, ad in dersler:
        TUM_DERSLER.append((kod, ad, bolum))

# Ders seçimi için options
def get_ders_options(bolum=None):
    if bolum and bolum in DERSLER:
        return [f"{kod} - {ad}" for kod, ad in DERSLER[bolum]]
    return [f"{kod} - {ad}" for kod, ad, _ in TUM_DERSLER]

DERSLIKLER = [
    {"ad": "Derslik B02", "kapasite": 20},
    {"ad": "Derslik B03 Işık Laboratuvarı", "kapasite": 30},
    {"ad": "Derslik B01 Ses Laboratuvarı", "kapasite": 30},
    {"ad": "Derslik Z04", "kapasite": 16},
    {"ad": "Derslik Z03", "kapasite": 16},
    {"ad": "Derslik Z02", "kapasite": 64},
    {"ad": "Derslik Z01", "kapasite": 30},
    {"ad": "Derslik Z05 LAB I", "kapasite": 30},
    {"ad": "Derslik 105", "kapasite": 36},
    {"ad": "Derslik 103", "kapasite": 20},
    {"ad": "Derslik 101", "kapasite": 30},
    {"ad": "Derslik 205", "kapasite": 24},
    {"ad": "Derslik 201", "kapasite": 40},
    {"ad": "Derslik 104", "kapasite": 24},
    {"ad": "Derslik 202", "kapasite": 40},
    {"ad": "Derslik 203", "kapasite": 20},
    {"ad": "Derslik 102", "kapasite": 40},
    {"ad": "Derslik 204 LAB 2", "kapasite": 25},
]

DERSLIK_SECENEKLERI = [
    f"{d['ad']} - Kapasite: {d['kapasite']}" for d in DERSLIKLER
]

STANDART_SAATLER = [
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
]

DOSYA_ADI = "kayitlar.json"
GECMIS_DOSYA = "gecmis.json"

if "dersler" not in st.session_state:
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            st.session_state.dersler = json.load(f)
    else:
        st.session_state.dersler = []

if "tarihler" not in st.session_state:
    st.session_state.tarihler = []

if "duzenlenen_ders_index" not in st.session_state:
    st.session_state.duzenlenen_ders_index = None
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "bekleyen_dersler" not in st.session_state:
    st.session_state.bekleyen_dersler = []
def excel_bytes_olustur(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sınav Programı")
    return output.getvalue()
def kaydet_json():
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(st.session_state.dersler, f, ensure_ascii=False, indent=2)

def gecmis_yukle():
    if os.path.exists(GECMIS_DOSYA):
        with open(GECMIS_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def degisiklik_ekle(eylem, ders):
    gecmis = gecmis_yukle()
    gecmis.append({
        "zaman": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "kullanici": st.session_state.get("aktif_kullanici", KULLANICI_ADI),
        "eylem": eylem,
        "ders": ders.get("ders", ""),
        "bolum": ders.get("bolum", ""),
        "sinif": ders.get("sinif", ""),
        "tarih": ders.get("tarih", ""),
        "saat": ders.get("saat", ""),
    })
    with open(GECMIS_DOSYA, "w", encoding="utf-8") as f:
        json.dump(gecmis, f, ensure_ascii=False, indent=2)

def _tr(text):
    """Türkçe karakterleri ASCII'ye dönüştür (PDF için)."""
    rep = {"ı": "i", "İ": "I", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G",
           "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    return "".join(rep.get(c, c) for c in str(text))

def pdf_bytes_olustur(df):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, _tr("SBMYO Sinav Programi"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    cols = list(df.columns)
    widths = {"Ders Kodu": 22, "Ders": 54, "Bölüm": 18, "Sınıf": 14,
              "Tarih": 22, "Saat": 14, "Derslik": 38, "Kapasite": 18, "Gözetmenler": 77}
    w = [widths.get(c, 28) for c in cols]

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(200, 200, 200)
    for col, cw in zip(cols, w):
        pdf.cell(cw, 8, _tr(col), border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for _, row in df.iterrows():
        for val, cw in zip(row, w):
            pdf.cell(cw, 6, _tr(str(val))[:45], border=1)
        pdf.ln()

    return bytes(pdf.output())

def otomatik_ata(bekleyen, mevcut):
    n = len(bekleyen)
    if n == 0:
        return [], None

    R = len(DERSLIKLER)
    G = len(GOZETMENLER)
    model = cp_model.CpModel()

    room = [model.new_int_var(0, R - 1, f"r{i}") for i in range(n)]
    proctor = [model.new_int_var(0, G - 1, f"p{i}") for i in range(n)]

    for i, ders in enumerate(bekleyen):
        ogrenci = ders.get("ogrenci_sayisi", 1)
        gecerli = [r for r, d in enumerate(DERSLIKLER) if d["kapasite"] >= ogrenci]
        if not gecerli:
            return None, f"'{ders['ders']}' için yeterli kapasiteli derslik yok (gereken: {ogrenci})."
        model.add_allowed_assignments([room[i]], [(r,) for r in gecerli])

    for i in range(n):
        for j in range(i + 1, n):
            di, dj = bekleyen[i], bekleyen[j]
            if di["tarih"] == dj["tarih"] and di["saat"] == dj["saat"]:
                model.add(room[i] != room[j])
                model.add(proctor[i] != proctor[j])

    for i, ders in enumerate(bekleyen):
        for mev in mevcut:
            if ders["tarih"] == mev["tarih"] and ders["saat"] == mev["saat"]:
                r_idx = next((r for r, d in enumerate(DERSLIKLER) if d["ad"] == mev["derslik_ad"]), None)
                if r_idx is not None:
                    model.add(room[i] != r_idx)
                for g in mev.get("gozetmenler", []):
                    if g in GOZETMENLER:
                        model.add(proctor[i] != GOZETMENLER.index(g))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.solve(model)

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        sonuclar = []
        for i, ders in enumerate(bekleyen):
            r = solver.value(room[i])
            g = solver.value(proctor[i])
            sonuc = {k: v for k, v in ders.items() if k != "ogrenci_sayisi"}
            sonuc["derslik_ad"] = DERSLIKLER[r]["ad"]
            sonuc["derslik_kapasite"] = DERSLIKLER[r]["kapasite"]
            sonuc["gozetmenler"] = [GOZETMENLER[g]]
            sonuclar.append(sonuc)
        return sonuclar, None
    else:
        return None, "Uygun atama bulunamadı. Kaynak yetersizliği veya çözülemeyen çakışma."

def cakismalari_kontrol_et(dersler):
    hatalar = []

    for i in range(len(dersler)):
        for j in range(i + 1, len(dersler)):
            d1 = dersler[i]
            d2 = dersler[j]

            ayni_zaman = (d1["tarih"] == d2["tarih"] and d1["saat"] == d2["saat"])

            if not ayni_zaman:
                continue

            ayni_sinav_mi = (
                d1["ders"] == d2["ders"]
                and d1["bolum"] == d2["bolum"]
                and d1["sinif"] == d2["sinif"]
            )

            # Aynı program/sınıf çakışması:
            # Eğer aynı ders değilse hata ver.
            if d1["program"] == d2["program"] and not ayni_sinav_mi:
                hatalar.append(
                    f"{d1['ders']} ile {d2['ders']} aynı tarih-saatte ve aynı program/sınıfta."
                )

            # Aynı derslik aynı anda kullanılamaz
            if d1["derslik_ad"] == d2["derslik_ad"]:
                hatalar.append(
                    f"{d1['ders']} ile {d2['ders']} aynı tarih-saatte aynı derslikte ({d1['derslik_ad']})."
                )

            # Aynı gözetmen aynı anda iki yerde olamaz
            ortak_gozetmenler = set(d1["gozetmenler"]).intersection(set(d2["gozetmenler"]))
            if ortak_gozetmenler:
                hatalar.append(
                    f"{d1['ders']} ile {d2['ders']} aynı tarih-saatte ortak gözetmen kullanıyor: {', '.join(sorted(ortak_gozetmenler))}."
                )

    return hatalar

st.subheader("Sınav Tarihi Ekle")

col_t1, col_t2 = st.columns([2, 1])

with col_t1:
    secilen_tarih = st.date_input("Tarih Seçin", value=date.today())

with col_t2:
    if st.button("Tarih Ekle"):
        tarih_str = secilen_tarih.strftime("%d.%m.%Y")
        if tarih_str not in st.session_state.tarihler:
            st.session_state.tarihler.append(tarih_str)
            st.session_state.tarihler.sort(key=lambda x: pd.to_datetime(x, format="%d.%m.%Y"))
            st.success(f"{tarih_str} eklendi.")
        else:
            st.warning("Bu tarih zaten eklenmiş.")

if st.session_state.tarihler:
    st.write("### Girilen Tarihler")
    st.dataframe(pd.DataFrame({"Tarih": st.session_state.tarihler}), use_container_width=True, hide_index=True)

    silinecek_tarih = st.selectbox("Silinecek Tarih", st.session_state.tarihler, key="sil_tarih")
    col_sil_t1, col_sil_t2 = st.columns(2)

    with col_sil_t1:
        if st.button("Seçili Tarihi Sil"):
            st.session_state.tarihler.remove(silinecek_tarih)
            st.success(f"{silinecek_tarih} silindi.")
            st.rerun()

    with col_sil_t2:
        if st.button("Tüm Tarihleri Temizle"):
            st.session_state.tarihler = []
            st.success("Tüm tarihler temizlendi.")
            st.rerun()
else:
    st.info("Henüz tarih eklenmedi.")


st.subheader("Ders Ekle")

duzenlenen = st.session_state.duzenlenen_ders_index

def get_value(key, default):
    if duzenlenen is not None:
        return st.session_state.dersler[duzenlenen][key]
    return default

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Önce bölüm seçimi yapılsın
    bolum_secenekleri = ["Tüm Bölümler"] + BOLUMLER + ["ORTAK"]
    bolum_secimi = st.selectbox(
        "Bölüm Seçin",
        bolum_secenekleri,
        index=0
    )
    # Bölüme göre filtrele
    secilen_bolum = None if bolum_secimi == "Tüm Bölümler" else bolum_secimi

with col2:
    # Ders seçimi - hem listeden hem manuel
    ders_secenekleri = ["-- Manuel Giriş --"] + get_ders_options(secilen_bolum)
    secili_ders = st.selectbox(
        "Ders Seçin",
        ders_secenekleri,
        index=0,
        key="ders_secimi"
    )

with col3:
    sinif_options = ["1. Sınıf", "2. Sınıf"]
    sinif_default = get_value("sinif", sinif_options[0])
    sinif = st.selectbox(
        "Sınıf",
        sinif_options,
        index=sinif_options.index(sinif_default)
    )

with col4:
    derslik_default_ad = get_value("derslik_ad", DERSLIKLER[0]["ad"])
    derslik_default_index = next(
        i for i, d in enumerate(DERSLIKLER) if d["ad"] == derslik_default_ad
    )
    secili_derslik = st.selectbox(
        "Derslik",
        DERSLIK_SECENEKLERI,
        index=derslik_default_index
    )

# Ders adını belirle
if secili_ders == "-- Manuel Giriş --":
    ders_adi = st.text_input("Ders Adı", value=get_value("ders", ""), key="ders_adi_input")
    ders_kodu = ""
else:
    # Seçili dersin kodunu ve adını al
    parts = secili_ders.split(" - ", 1)
    ders_kodu = parts[0]
    ders_adi = parts[1] if len(parts) > 1 else ""
    st.text_input("Ders Adı", value=ders_adi, disabled=True, key="ders_adi_input")

col5, col6 = st.columns(2)

with col5:
    if st.session_state.tarihler:
        tarih_default = get_value("tarih", st.session_state.tarihler[0])
        if tarih_default not in st.session_state.tarihler:
            tarih_default = st.session_state.tarihler[0]

        ders_tarihi = st.selectbox(
            "Sınav Tarihi",
            st.session_state.tarihler,
            index=st.session_state.tarihler.index(tarih_default)
        )
    else:
        ders_tarihi = None
        st.info("Önce tarih ekleyin.")

with col6:
    saat_default = get_value("saat", STANDART_SAATLER[0])
    ders_saati = st.selectbox(
        "Sınav Saati",
        STANDART_SAATLER,
        index=STANDART_SAATLER.index(saat_default)
    )

secili_gozetmenler = st.multiselect(
    "Gözetmenleri Seçin",
    GOZETMENLER,
    default=get_value("gozetmenler", [])
)

secili_derslik_ad = secili_derslik.split(" - Kapasite: ")[0]

ayni_derslik_kayitlari = []
for d in st.session_state.dersler:
    if d["derslik_ad"] == secili_derslik_ad:
        ayni_derslik_kayitlari.append({
            "Ders": d["ders"],
            "Bölüm": d["bolum"],
            "Sınıf": d["sinif"],
            "Tarih": d["tarih"],
            "Saat": d["saat"],
        })

if ayni_derslik_kayitlari:
    st.write("### Bu derslik şu derslerde kullanılıyor")
    st.dataframe(
        pd.DataFrame(ayni_derslik_kayitlari),
        use_container_width=True,
        hide_index=True
    )
buton_text = "Dersi Listeye Ekle" if st.session_state.duzenlenen_ders_index is None else "Dersi Güncelle"

if st.button(buton_text):
    if not st.session_state.tarihler:
        st.warning("Önce en az bir tarih ekleyin.")
    elif secili_ders == "-- Manuel Giriş --" and not ders_adi.strip():
        st.warning("Lütfen ders adını girin.")
    elif not ders_tarihi:
        st.warning("Lütfen sınav tarihi seçin.")
    elif len(secili_gozetmenler) == 0:
        st.warning("Lütfen en az bir gözetmen seçin.")
    else:
        secili_derslik_veri = next(
            d for d in DERSLIKLER
            if f"{d['ad']} - Kapasite: {d['kapasite']}" == secili_derslik
        )

        yeni_veri = {
            "ders": ders_adi.strip(),
            "ders_kodu": ders_kodu,
            "bolum": bolum_secimi if bolum_secimi else "ORTAK",
            "sinif": sinif,
            "program": f"{bolum_secimi if bolum_secimi else 'ORTAK'} {sinif}",
            "tarih": ders_tarihi,
            "saat": ders_saati,
            "derslik_ad": secili_derslik_veri["ad"],
            "derslik_kapasite": secili_derslik_veri["kapasite"],
            "gozetmenler": secili_gozetmenler,
        }

        if st.session_state.duzenlenen_ders_index is None:
            st.session_state.dersler.append(yeni_veri)
            degisiklik_ekle("Ekleme", yeni_veri)
            st.success(f"{ders_adi} eklendi.")
        else:
            st.session_state.dersler[st.session_state.duzenlenen_ders_index] = yeni_veri
            degisiklik_ekle("Güncelleme", yeni_veri)
            st.success(f"{ders_adi} güncellendi.")
            st.session_state.duzenlenen_ders_index = None

        st.rerun()

st.subheader("Girilen Dersler")

if st.session_state.dersler:

    gosterim_dersler = []
    for d in st.session_state.dersler:
        gosterim_dersler.append({
            "Ders Kodu": d.get("ders_kodu", ""),
            "Ders": d["ders"],
            "Bölüm": d["bolum"],
            "Sınıf": d["sinif"],
            "Tarih": d["tarih"],
            "Saat": d["saat"],
            "Derslik": d["derslik_ad"],
            "Kapasite": d["derslik_kapasite"],
            "Gözetmenler": ", ".join(d["gozetmenler"]),
        })

    st.dataframe(pd.DataFrame(gosterim_dersler), use_container_width=True, hide_index=True)

    ders_opsiyonlari = [
        f"{i+1} - {d['ders']} / {d['bolum']} / {d['sinif']} / {d['tarih']} {d['saat']}"
        for i, d in enumerate(st.session_state.dersler)
    ]

    secili_ders = st.selectbox("Silinecek Ders", ders_opsiyonlari, key="sil_ders")

    col_d1, col_d2, col_d3 = st.columns(3)

    with col_d1:
        if st.button("Seçili Dersi Sil"):
            idx = ders_opsiyonlari.index(secili_ders)
            silinen = st.session_state.dersler.pop(idx)
            if st.session_state.duzenlenen_ders_index == idx:
                st.session_state.duzenlenen_ders_index = None
            degisiklik_ekle("Silme", silinen)
            kaydet_json()
            st.success(f"{silinen['ders']} silindi.")
            st.rerun()

    with col_d2:
        if st.button("Seçili Dersi Düzenle"):
            idx = ders_opsiyonlari.index(secili_ders)
            st.session_state.duzenlenen_ders_index = idx
            st.rerun()

    with col_d3:
        if st.button("Tüm Dersleri Temizle"):
            degisiklik_ekle("Tümünü Silme", {"ders": f"({len(st.session_state.dersler)} ders)", "bolum": "", "sinif": "", "tarih": "", "saat": ""})
            st.session_state.dersler = []
            st.session_state.duzenlenen_ders_index = None
            kaydet_json()
            st.success("Tüm dersler temizlendi.")
            st.rerun()

else:
    st.info("Henüz ders eklenmedi.")
st.subheader("Veri Kaydet")

if st.button("Kaydet"):
    kaydet_json()
    st.success("Veriler kaydedildi.")

st.subheader("Program Oluştur")

if st.button("Programı Kontrol Et ve Excel Oluştur"):
    if not st.session_state.dersler:
        st.warning("Önce en az bir ders ekleyin.")
    else:
        hatalar = cakismalari_kontrol_et(st.session_state.dersler)

        if hatalar:
            st.error("Çakışmalar bulundu. Lütfen aşağıdaki sorunları düzeltin:")
            hata_df = pd.DataFrame({"Çakışma Açıklaması": hatalar})
            st.dataframe(hata_df, use_container_width=True, hide_index=True)
        else:
            program_df = pd.DataFrame([
                {
                    "Ders Kodu": d.get("ders_kodu", ""),
                    "Ders": d["ders"],
                    "Bölüm": d["bolum"],
                    "Sınıf": d["sinif"],
                    "Tarih": d["tarih"],
                    "Saat": d["saat"],
                    "Derslik": d["derslik_ad"],
                    "Kapasite": d["derslik_kapasite"],
                    "Gözetmenler": ", ".join(d["gozetmenler"]),
                }
                for d in st.session_state.dersler
            ]).sort_values(by=["Tarih", "Saat", "Derslik"]).reset_index(drop=True)

            st.success("Çakışma bulunmadı. Program hazır.")
            st.subheader("Oluşturulan Sınav Programı")
            st.dataframe(program_df, use_container_width=True, hide_index=True)

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                excel_data = excel_bytes_olustur(program_df)
                st.download_button(
                    "Excel Olarak İndir",
                    data=excel_data,
                    file_name="sinav_programi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with dl_col2:
                pdf_data = pdf_bytes_olustur(program_df)
                st.download_button(
                    "PDF Olarak İndir",
                    data=pdf_data,
                    file_name="sinav_programi.pdf",
                    mime="application/pdf",
                )

st.subheader("Otomatik Atama (OR-Tools)")
st.write("Derslik ve gözetmen atanmamış sınavlar için OR-Tools ile otomatik atama yapın.")

with st.expander("Bekleyen Sınav Ekle"):
    ba_col1, ba_col2, ba_col3 = st.columns(3)
    with ba_col1:
        ba_bolum = st.selectbox("Bölüm", BOLUMLER + ["ORTAK"], key="ba_bolum")
        ba_ders_opts = ["-- Manuel --"] + get_ders_options(ba_bolum if ba_bolum != "ORTAK" else None)
        ba_ders_sec = st.selectbox("Ders", ba_ders_opts, key="ba_ders_sec")
    with ba_col2:
        ba_sinif = st.selectbox("Sınıf", ["1. Sınıf", "2. Sınıf"], key="ba_sinif")
        ba_ogrenci = st.number_input("Öğrenci Sayısı", min_value=1, max_value=300, value=20, key="ba_ogrenci")
    with ba_col3:
        if st.session_state.tarihler:
            ba_tarih = st.selectbox("Tarih", st.session_state.tarihler, key="ba_tarih")
        else:
            ba_tarih = None
            st.info("Önce tarih ekleyin.")
        ba_saat = st.selectbox("Saat", STANDART_SAATLER, key="ba_saat")

    if ba_ders_sec == "-- Manuel --":
        ba_ders_kodu = ""
        ba_ders_adi = st.text_input("Ders Adı", key="ba_ders_adi")
    else:
        parts = ba_ders_sec.split(" - ", 1)
        ba_ders_kodu = parts[0]
        ba_ders_adi = parts[1] if len(parts) > 1 else ""
        st.text_input("Ders Adı", value=ba_ders_adi, disabled=True, key="ba_ders_adi")

    if st.button("Bekleyen Listeye Ekle") and ba_tarih and ba_ders_adi:
        st.session_state.bekleyen_dersler.append({
            "ders": ba_ders_adi,
            "ders_kodu": ba_ders_kodu,
            "bolum": ba_bolum,
            "sinif": ba_sinif,
            "program": f"{ba_bolum} {ba_sinif}",
            "tarih": ba_tarih,
            "saat": ba_saat,
            "ogrenci_sayisi": ba_ogrenci,
        })
        st.success(f"{ba_ders_adi} bekleyen listeye eklendi.")
        st.rerun()

if st.session_state.bekleyen_dersler:
    bekleyen_df = pd.DataFrame([{
        "Ders": d["ders"], "Bölüm": d["bolum"], "Sınıf": d["sinif"],
        "Tarih": d["tarih"], "Saat": d["saat"], "Öğrenci Sayısı": d["ogrenci_sayisi"],
    } for d in st.session_state.bekleyen_dersler])
    st.dataframe(bekleyen_df, use_container_width=True, hide_index=True)

    ba_btn1, ba_btn2 = st.columns(2)
    with ba_btn1:
        if st.button("Otomatik Ata"):
            with st.spinner("OR-Tools çözümü hesaplanıyor..."):
                sonuclar, hata = otomatik_ata(st.session_state.bekleyen_dersler, st.session_state.dersler)
            if hata:
                st.error(hata)
            else:
                st.session_state.atama_sonuclari = sonuclar
                st.success("Atama tamamlandı. Aşağıda onaylayın.")
                st.rerun()
    with ba_btn2:
        if st.button("Bekleyen Listeyi Temizle"):
            st.session_state.bekleyen_dersler = []
            st.session_state.pop("atama_sonuclari", None)
            st.rerun()

if st.session_state.get("atama_sonuclari"):
    st.write("### Atama Sonuçları")
    sonuc_df = pd.DataFrame([{
        "Ders": d["ders"], "Bölüm": d["bolum"], "Sınıf": d["sinif"],
        "Tarih": d["tarih"], "Saat": d["saat"],
        "Derslik": d["derslik_ad"], "Kapasite": d["derslik_kapasite"],
        "Gözetmen": ", ".join(d["gozetmenler"]),
    } for d in st.session_state.atama_sonuclari])
    st.dataframe(sonuc_df, use_container_width=True, hide_index=True)

    if st.button("Atamaları Programa Ekle"):
        for d in st.session_state.atama_sonuclari:
            st.session_state.dersler.append(d)
            degisiklik_ekle("Otomatik Ekleme", d)
        kaydet_json()
        st.session_state.bekleyen_dersler = []
        st.session_state.pop("atama_sonuclari", None)
        st.success("Tüm atamalar programa eklendi.")
        st.rerun()

st.subheader("Değişiklik Geçmişi")
gecmis = gecmis_yukle()
if gecmis:
    gecmis_df = pd.DataFrame(gecmis[::-1])
    gecmis_df.columns = ["Zaman", "Kullanıcı", "Eylem", "Ders", "Bölüm", "Sınıf", "Tarih", "Saat"]
    st.dataframe(gecmis_df, use_container_width=True, hide_index=True)
    if st.button("Geçmişi Temizle"):
        with open(GECMIS_DOSYA, "w", encoding="utf-8") as f:
            json.dump([], f)
        st.success("Geçmiş temizlendi.")
        st.rerun()
else:
    st.info("Henüz değişiklik kaydı yok.")

st.markdown("---")
st.caption("Bu yazılım Hacettepe Üniversitesi Sosyal Bilimler MYO tarafından yazılmıştır.")
