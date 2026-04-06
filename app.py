import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import json
import os
KULLANICI_ADI = "Sbmy"
SIFRE = "sbmy2026.0"
st.set_page_config(
    page_title="SBMYO Sınav Sistemi",
    page_icon=":material/calendar_month:",
    layout="wide"
)
if not st.session_state.giris_yapildi:

    st.title("Giriş Yap")

    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")

    if st.button("Giriş"):
        if kullanici == KULLANICI_ADI and sifre == SIFRE:
            st.session_state.giris_yapildi = True
            st.success("Giriş başarılı")
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı")

    st.stop()
st.image("logo.png", width=400)
col_l1, col_l2 = st.columns([6, 1])

with col_l2:
   if st.button("🔒 Çıkış Yap"):
    st.session_state.giris_yapildi = False
    st.rerun()
st.title("SBMYO Sınav Programı Sistemi")
st.caption("Hacettepe Üniversitesi Sosyal Bilimler Meslek Yüksekokulu")

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
]

BOLUMLER = ["BYA", "MVU", "TOT", "SGP"]

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
def excel_bytes_olustur(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sınav Programı")
    return output.getvalue()
def kaydet_json():
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(st.session_state.dersler, f, ensure_ascii=False, indent=2)

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
    ders_adi = st.text_input("Ders Adı", value=get_value("ders", ""))

with col2:
    bolum_default = get_value("bolum", BOLUMLER[0])
    bolum = st.selectbox(
        "Bölüm",
        BOLUMLER,
        index=BOLUMLER.index(bolum_default)
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
    elif not ders_adi.strip():
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
            "bolum": bolum,
            "sinif": sinif,
            "program": f"{bolum} {sinif}",
            "tarih": ders_tarihi,
            "saat": ders_saati,
            "derslik_ad": secili_derslik_veri["ad"],
            "derslik_kapasite": secili_derslik_veri["kapasite"],
            "gozetmenler": secili_gozetmenler,
        }

        if st.session_state.duzenlenen_ders_index is None:
            st.session_state.dersler.append(yeni_veri)
            st.success(f"{ders_adi} eklendi.")
        else:
            st.session_state.dersler[st.session_state.duzenlenen_ders_index] = yeni_veri
            st.success(f"{ders_adi} güncellendi.")
            st.session_state.duzenlenen_ders_index = None

        st.rerun()

st.subheader("Girilen Dersler")

if st.session_state.dersler:

    gosterim_dersler = []
    for d in st.session_state.dersler:
        gosterim_dersler.append({
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

            excel_data = excel_bytes_olustur(program_df)
            st.download_button(
                "Excel Olarak İndir",
                data=excel_data,
                file_name="sinav_programi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

st.markdown("---")
st.caption("Bu yazılım Hacettepe Üniversitesi Sosyal Bilimler MYO tarafından yazılmıştır.")
