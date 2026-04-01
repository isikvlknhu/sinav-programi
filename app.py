import streamlit as st
import pandas as pd
from ortools.sat.python import cp_model
from datetime import date
from io import BytesIO

st.set_page_config(
    page_title="SBMYO Sınav Sistemi",
    page_icon=":material/calendar_month:",
    layout="wide"
)

st.image("logo.png", width=200)
st.title("SBMYO Sınav Programı Sistemi")
st.caption("Hacettepe Üniversitesi Sosyal Bilimler Meslek Yüksekokulu")

st.write("Ders, tarih, derslik ve gözetmen bilgilerini kullanarak otomatik sınav programı oluşturun.")

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

if "tarihler" not in st.session_state:
    st.session_state.tarihler = []


def timeslot_olustur(tarihler, saatler):
    slots = []
    for tarih in tarihler:
        for saat in saatler:
            slots.append(f"{tarih} {saat}")
    return slots


def sinav_programi_olustur(dersler, timeslots):
    model = cp_model.CpModel()

    num_courses = len(dersler)
    num_slots = len(timeslots)

    x = {}
    for c in range(num_courses):
        for t in range(num_slots):
            x[(c, t)] = model.NewBoolVar(f"x_{c}_{t}")

    for c in range(num_courses):
        model.Add(sum(x[(c, t)] for t in range(num_slots)) == 1)

    # Aynı bölüm+sınıf aynı saatte olmasın
    for t in range(num_slots):
        for c1 in range(num_courses):
            for c2 in range(c1 + 1, num_courses):
                if dersler[c1]["program"] == dersler[c2]["program"]:
                    model.Add(x[(c1, t)] + x[(c2, t)] <= 1)

    # Aynı derslik aynı saatte iki sınavda olmasın
    for t in range(num_slots):
        for i in range(num_courses):
            for j in range(i + 1, num_courses):
                if dersler[i]["derslik_ad"] == dersler[j]["derslik_ad"]:
                    model.Add(x[(i, t)] + x[(j, t)] <= 1)

    # Aynı gözetmen aynı saatte iki sınavda olmasın
    for t in range(num_slots):
        for g in GOZETMENLER:
            ilgili_dersler = []
            for c in range(num_courses):
                if g in dersler[c]["gozetmenler"]:
                    ilgili_dersler.append(x[(c, t)])
            if ilgili_dersler:
                model.Add(sum(ilgili_dersler) <= 1)

    model.Minimize(
        sum(t * x[(c, t)] for c in range(num_courses) for t in range(num_slots))
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 20

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    sonuc = []
    for c in range(num_courses):
        for t in range(num_slots):
            if solver.Value(x[(c, t)]) == 1:
                sonuc.append(
                    {
                        "Ders": dersler[c]["ders"],
                        "Bölüm": dersler[c]["bolum"],
                        "Sınıf": dersler[c]["sinif"],
                        "Tarih-Saat": timeslots[t],
                        "Derslik": dersler[c]["derslik_ad"],
                        "Kapasite": dersler[c]["derslik_kapasite"],
                        "Gözetmenler": ", ".join(dersler[c]["gozetmenler"]),
                    }
                )
                break

    sonuc_df = pd.DataFrame(sonuc)
    sonuc_df = sonuc_df.sort_values(by=["Tarih-Saat", "Derslik"]).reset_index(drop=True)
    return sonuc_df


def excel_bytes_olustur(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sınav Programı")
    return output.getvalue()


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
    bolum = st.selectbox("Bölüm", BOLUMLER)
with col3:
    sinif = st.selectbox("Sınıf", ["1. Sınıf", "2. Sınıf"])
with col4:
    secili_derslik = st.selectbox("Derslik", DERSLIK_SECENEKLERI)

secili_gozetmenler = st.multiselect("Gözetmenleri Seçin", GOZETMENLER)

# Aynı derslik daha önce seçildiyse uyarı
secili_derslik_ad = secili_derslik.split(" - Kapasite: ")[0]
ayni_derslikli_dersler = [
    d["ders"] for d in st.session_state.dersler if d["derslik_ad"] == secili_derslik_ad
]

if ayni_derslikli_dersler:
    st.warning(
        f"Uyarı: {secili_derslik_ad} daha önce şu ders(ler) için seçildi: "
        + ", ".join(ayni_derslikli_dersler)
    )

if st.button("Dersi Listeye Ekle"):
    if not ders_adi.strip():
        st.warning("Lütfen ders adını girin.")
    elif len(secili_gozetmenler) == 0:
        st.warning("Lütfen en az bir gözetmen seçin.")
    else:
        secili_derslik_veri = next(
            d for d in DERSLIKLER
            if f"{d['ad']} - Kapasite: {d['kapasite']}" == secili_derslik
        )

        st.session_state.dersler.append(
            {
                "ders": ders_adi.strip(),
                "bolum": bolum,
                "sinif": sinif,
                "program": f"{bolum} {sinif}",
                "derslik_ad": secili_derslik_veri["ad"],
                "derslik_kapasite": secili_derslik_veri["kapasite"],
                "gozetmenler": secili_gozetmenler,
            }
        )
        st.success(f"{ders_adi} eklendi.")

st.subheader("Girilen Dersler")
if st.session_state.dersler:
    gosterim_dersler = []
    for d in st.session_state.dersler:
        gosterim_dersler.append({
            "Ders": d["ders"],
            "Bölüm": d["bolum"],
            "Sınıf": d["sinif"],
            "Derslik": d["derslik_ad"],
            "Kapasite": d["derslik_kapasite"],
            "Gözetmenler": ", ".join(d["gozetmenler"]),
        })

    st.dataframe(pd.DataFrame(gosterim_dersler), use_container_width=True)

    ders_opsiyonlari = [
        f"{i+1} - {d['ders']} / {d['bolum']} / {d['sinif']} / {d['derslik_ad']}"
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

st.subheader("Program Oluştur")

if st.button("Otomatik Sınav Programı Oluştur"):
    if not st.session_state.tarihler:
        st.warning("Önce en az bir tarih ekleyin.")
    elif not st.session_state.dersler:
        st.warning("Önce en az bir ders ekleyin.")
    else:
        TIMESLOTS = timeslot_olustur(st.session_state.tarihler, STANDART_SAATLER)

        program_df = sinav_programi_olustur(st.session_state.dersler, TIMESLOTS)

        if program_df is None:
            st.error("Uygun bir program oluşturulamadı. Tarih/saat veya gözetmen/derslik çakışmaları yetersiz olabilir.")
        else:
            st.success("Sınav programı oluşturuldu.")
            st.subheader("Oluşturulan Sınav Programı")
            st.dataframe(program_df, use_container_width=True)

            excel_data = excel_bytes_olustur(program_df)
            st.download_button(
                "Excel Olarak İndir",
                data=excel_data,
                file_name="sinav_programi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

st.markdown("---")
st.caption("Bu yazılım Hacettepe Üniversitesi Sosyal Bilimler MYO tarafından yazılmıştır.")
