import streamlit as st

st.set_page_config(
    page_title="Hacettepe Universitesi SBMYO Sınav Sistemi",
    layout="wide"
)

st.logo("logo.png")   # sol üst uygulama logosu
st.image("logo.png", width=500)  # sayfa içinde büyük logo
st.title("Hacettepe Üniversitesi Sosyal Bilimler Meslek Yüksekokulu")
import streamlit as st
import pandas as pd
from ortools.sat.python import cp_model
from datetime import date

st.set_page_config(
    page_title="Hacettepe Üniversitesi Sosyal Bilimler MYO Sınav Programı",
    layout="wide"
)

st.title("Hacettepe Üniversitesi Sosyal Bilimler MYO Sınav Programı")
st.write("Ders, tarih, salon ve gözetmen bilgilerini kullanarak otomatik sınav programı oluşturun.")

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

STANDART_SAATLER = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
]

if "dersler" not in st.session_state:
    st.session_state.dersler = []

if "salonlar" not in st.session_state:
    st.session_state.salonlar = []

if "tarihler" not in st.session_state:
    st.session_state.tarihler = []


def timeslot_olustur(tarihler, saatler):
    slots = []
    for tarih in tarihler:
        for saat in saatler:
            slots.append(f"{tarih} {saat}")
    return slots


def sinav_programi_olustur(dersler, salonlar, timeslots):
    model = cp_model.CpModel()

    num_courses = len(dersler)
    num_rooms = len(salonlar)
    num_slots = len(timeslots)

    # x[c, r, t] = ders c, salon r, zaman t
    x = {}

    for c in range(num_courses):
        for r in range(num_rooms):
            if salonlar[r]["kapasite"] < dersler[c]["ogrenci"]:
                continue
            for t in range(num_slots):
                x[(c, r, t)] = model.NewBoolVar(f"x_{c}_{r}_{t}")

    # Her ders tam bir kez atanmalı
    for c in range(num_courses):
        uygun_atamalar = [x[key] for key in x if key[0] == c]
        if not uygun_atamalar:
            return None
        model.Add(sum(uygun_atamalar) == 1)

    # Aynı programdaki dersler aynı saatte olmasın
    for t in range(num_slots):
        for c1 in range(num_courses):
            for c2 in range(c1 + 1, num_courses):
                if dersler[c1]["program"] == dersler[c2]["program"]:
                    atamalar_c1 = [x[key] for key in x if key[0] == c1 and key[2] == t]
                    atamalar_c2 = [x[key] for key in x if key[0] == c2 and key[2] == t]
                    if atamalar_c1 and atamalar_c2:
                        model.Add(sum(atamalar_c1) + sum(atamalar_c2) <= 1)

    # Aynı salon aynı saatte iki sınavda kullanılmasın
    for r in range(num_rooms):
        for t in range(num_slots):
            ayni_salon = [x[key] for key in x if key[1] == r and key[2] == t]
            if ayni_salon:
                model.Add(sum(ayni_salon) <= 1)

    # Aynı gözetmen aynı saatte iki sınavda olmasın
    # Burada artık gözetmenler derse önceden elle atanmış kabul ediliyor.
    for t in range(num_slots):
        for g in GOZETMENLER:
            ilgili_dersler = []
            for c in range(num_courses):
                if g in dersler[c]["gozetmenler"]:
                    ilgili_dersler.extend([x[key] for key in x if key[0] == c and key[2] == t])
            if ilgili_dersler:
                model.Add(sum(ilgili_dersler) <= 1)

    # Amaç: erken slotlar ve düşük indeksli salonları tercih et
    model.Minimize(
        sum((key[2] * 100 + key[1]) * x[key] for key in x)
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 20

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    sonuc = []
    for (c, r, t), var in x.items():
        if solver.Value(var) == 1:
            sonuc.append(
                {
                    "Ders": dersler[c]["ders"],
                    "Bölüm": dersler[c]["bolum"],
                    "Sınıf": dersler[c]["sinif"],
                    "Öğrenci Sayısı": dersler[c]["ogrenci"],
                    "Tarih-Saat": timeslots[t],
                    "Salon": salonlar[r]["salon"],
                    "Salon Kapasitesi": salonlar[r]["kapasite"],
                    "Gözetmenler": ", ".join(dersler[c]["gozetmenler"]),
                }
            )

    sonuc_df = pd.DataFrame(sonuc)
    sonuc_df = sonuc_df.sort_values(by=["Tarih-Saat", "Salon"]).reset_index(drop=True)
    return sonuc_df


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
    st.dataframe(pd.DataFrame({"Tarih": st.session_state.tarihler}), use_container_width=True)

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

col1, col2, col3, col4 = st.columns(4)

with col1:
    ders_adi = st.text_input("Ders Adı")
with col2:
    ogrenci_sayisi = st.number_input("Öğrenci Sayısı", min_value=1, step=1)
with col3:
    bolum = st.selectbox("Bölüm", BOLUMLER)
with col4:
    sinif = st.selectbox("Sınıf", ["1. Sınıf", "2. Sınıf"])

secili_gozetmenler = st.multiselect(
    "Gözetmenleri Seçin",
    GOZETMENLER
)

if st.button("Dersi Listeye Ekle"):
    if not ders_adi.strip():
        st.warning("Lütfen ders adını girin.")
    elif len(secili_gozetmenler) == 0:
        st.warning("Lütfen en az bir gözetmen seçin.")
    else:
        st.session_state.dersler.append(
            {
                "ders": ders_adi.strip(),
                "ogrenci": int(ogrenci_sayisi),
                "bolum": bolum,
                "sinif": sinif,
                "program": f"{bolum} {sinif}",
                "gozetmenler": secili_gozetmenler,
            }
        )
        st.success(f"{ders_adi} eklendi.")


st.subheader("Salon Ekle")

col5, col6 = st.columns(2)
with col5:
    salon_adi = st.text_input("Salon Adı")
with col6:
    salon_kapasite = st.number_input("Salon Kapasitesi", min_value=1, step=1, key="salon_kapasite")

if st.button("Salonu Listeye Ekle"):
    if salon_adi.strip():
        st.session_state.salonlar.append(
            {
                "salon": salon_adi.strip(),
                "kapasite": int(salon_kapasite),
            }
        )
        st.success(f"{salon_adi} eklendi.")
    else:
        st.warning("Lütfen salon adını girin.")


left, right = st.columns(2)

with left:
    st.subheader("Girilen Dersler")
    if st.session_state.dersler:
        gosterim_dersler = []
        for d in st.session_state.dersler:
            gosterim_dersler.append({
                "Ders": d["ders"],
                "Öğrenci Sayısı": d["ogrenci"],
                "Bölüm": d["bolum"],
                "Sınıf": d["sinif"],
                "Gözetmenler": ", ".join(d["gozetmenler"])
            })
        st.dataframe(pd.DataFrame(gosterim_dersler), use_container_width=True)

        ders_opsiyonlari = [
            f"{i+1} - {d['ders']} / {d['bolum']} / {d['sinif']} / {d['ogrenci']} öğrenci"
            for i, d in enumerate(st.session_state.dersler)
        ]
        secili_ders = st.selectbox("Silinecek Ders", ders_opsiyonlari, key="sil_ders")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("Seçili Dersi Sil"):
                idx = ders_opsiyonlari.index(secili_ders)
                silinen = st.session_state.dersler.pop(idx)
                st.success(f"{silinen['ders']} silindi.")
                st.rerun()

        with col_d2:
            if st.button("Tüm Dersleri Temizle"):
                st.session_state.dersler = []
                st.success("Tüm dersler temizlendi.")
                st.rerun()
    else:
        st.info("Henüz ders eklenmedi.")

with right:
    st.subheader("Girilen Salonlar")
    if st.session_state.salonlar:
        df_salonlar = pd.DataFrame(st.session_state.salonlar)
        st.dataframe(df_salonlar, use_container_width=True)

        salon_opsiyonlari = [
            f"{i+1} - {s['salon']} / {s['kapasite']} kişilik"
            for i, s in enumerate(st.session_state.salonlar)
        ]
        secili_salon = st.selectbox("Silinecek Salon", salon_opsiyonlari, key="sil_salon")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Seçili Salonu Sil"):
                idx = salon_opsiyonlari.index(secili_salon)
                silinen = st.session_state.salonlar.pop(idx)
                st.success(f"{silinen['salon']} silindi.")
                st.rerun()

        with col_s2:
            if st.button("Tüm Salonları Temizle"):
                st.session_state.salonlar = []
                st.success("Tüm salonlar temizlendi.")
                st.rerun()
    else:
        st.info("Henüz salon eklenmedi.")


st.subheader("Gözetmen Listesi")
st.dataframe(pd.DataFrame({"Gözetmen": GOZETMENLER}), use_container_width=True, height=300)

st.subheader("Program Oluştur")

if st.button("Otomatik Sınav Programı Oluştur"):
    if not st.session_state.tarihler:
        st.warning("Önce en az bir tarih ekleyin.")
    elif not st.session_state.dersler:
        st.warning("Önce en az bir ders ekleyin.")
    elif not st.session_state.salonlar:
        st.warning("Önce en az bir salon ekleyin.")
    else:
        TIMESLOTS = timeslot_olustur(st.session_state.tarihler, STANDART_SAATLER)

        program_df = sinav_programi_olustur(
            st.session_state.dersler,
            st.session_state.salonlar,
            TIMESLOTS
        )

        if program_df is None:
            st.error("Uygun bir program oluşturulamadı. Tarih/saat, salon kapasitesi veya gözetmen çakışmaları yetersiz olabilir.")
        else:
            st.success("Sınav programı oluşturuldu.")
            st.subheader("Oluşturulan Sınav Programı")
            st.dataframe(program_df, use_container_width=True)

            csv = program_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "CSV Olarak İndir",
                data=csv,
                file_name="sinav_programi.csv",
                mime="text/csv",
            )

st.markdown("---")
st.caption("Bu yazılım Hacettepe Üniversitesi Sosyal Bilimler MYO tarafından yazılmıştır.")
