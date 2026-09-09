import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json

st.set_page_config(page_title="Dashboard Pembangunan Wilayah Jatim", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('dataset_dengan_klaster.csv')
    with open('Provinsi Jawa Timur-KAB_KOTA.geojson', encoding='utf-8') as f:
        geojson_data = json.load(f)
    return df, geojson_data

df, geojson_data = load_data()

st.sidebar.title("📊 Navigasi Dashboard")
menu = st.sidebar.radio("Pilih Halaman:", ["Overview", "Peta Klaster", "Perbandingan Klaster", "Hasil Regresi", "Eksplorasi Data"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Sumber Data:** Open Data Jatim & BPS Jatim, 2025")
st.sidebar.markdown("**Metode:** K-Means Clustering & Regresi Linier Berganda")

if menu == "Overview":
    st.title("🗺️ Dashboard Pembangunan Wilayah Jawa Timur")
    st.markdown("Analisis klasterisasi dan faktor determinan pembangunan 38 kabupaten/kota di Jawa Timur, tahun 2025.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jumlah Wilayah", f"{df.shape[0]}")
    col2.metric("Rata-rata IPM", f"{df['ipm'].mean():.2f}")
    col3.metric("Rata-rata Kemiskinan", f"{df['persentase_miskin'].mean():.2f}%")
    col4.metric("Jumlah Klaster", f"{df['label_klaster'].nunique()}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribusi Wilayah per Klaster")
        klaster_count = df['label_klaster'].value_counts().reset_index()
        klaster_count.columns = ['Klaster', 'Jumlah Wilayah']
        fig = px.pie(klaster_count, names='Klaster', values='Jumlah Wilayah',
                     color='Klaster',
                     color_discrete_map={'Maju': '#2ecc71', 'Berkembang': '#f39c12', 'Tertinggal': '#e74c3c'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ranking IPM Tertinggi & Terendah")
        top5 = df.nlargest(5, 'ipm')[['wilayah', 'ipm']]
        bottom5 = df.nsmallest(5, 'ipm')[['wilayah', 'ipm']]
        tab1, tab2 = st.tabs(["5 Tertinggi", "5 Terendah"])
        with tab1:
            st.dataframe(top5, use_container_width=True, hide_index=True)
        with tab2:
            st.dataframe(bottom5, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Ranking Seluruh Wilayah Berdasarkan IPM")
    df_sorted = df.sort_values('ipm', ascending=True)
    fig = px.bar(df_sorted, x='ipm', y='wilayah', orientation='h', color='label_klaster',
                 color_discrete_map={'Maju': '#2ecc71', 'Berkembang': '#f39c12', 'Tertinggal': '#e74c3c'},
                 height=800, labels={'ipm': 'IPM', 'wilayah': 'Wilayah', 'label_klaster': 'Klaster'})
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Peta Klaster":
    st.title("🗺️ Peta Sebaran Klaster Wilayah")

    variabel_peta = st.selectbox(
        "Tampilkan berdasarkan:",
        ['label_klaster', 'ipm', 'persentase_miskin', 'pdrb_per_kapita', 'total_faskes']
    )

    if variabel_peta == 'label_klaster':
        fig = px.choropleth(
            df,
            geojson=geojson_data,
            locations='wilayah',
            featureidkey='properties.kab_kota',
            color='label_klaster',
            color_discrete_map={'Maju': '#2ecc71', 'Berkembang': '#f39c12', 'Tertinggal': '#e74c3c'},
            hover_name='wilayah',
            hover_data={'ipm': True, 'persentase_miskin': True, 'wilayah': False},
            labels={'label_klaster': 'Klaster'}
        )
    else:
        fig = px.choropleth(
            df,
            geojson=geojson_data,
            locations='wilayah',
            featureidkey='properties.kab_kota',
            color=variabel_peta,
            color_continuous_scale='YlOrRd',
            hover_name='wilayah',
            hover_data={'label_klaster': True, 'wilayah': False}
        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=650, margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 Arahkan kursor ke tiap wilayah pada peta untuk melihat detail data.")

elif menu == "Perbandingan Klaster":
    st.title("🔍 Perbandingan Karakteristik Antar Klaster")

    variabel_pilihan = st.selectbox(
        "Pilih variabel untuk dibandingkan:",
        ['ipm', 'persentase_miskin', 'rls', 'tpt', 'pdrb_per_kapita', 'total_faskes', 'persentase_jalan_memenuhi']
    )

    label_variabel = {
        'ipm': 'Indeks Pembangunan Manusia',
        'persentase_miskin': 'Persentase Penduduk Miskin (%)',
        'rls': 'Rata-Rata Lama Sekolah (tahun)',
        'tpt': 'Tingkat Pengangguran Terbuka (%)',
        'pdrb_per_kapita': 'PDRB per Kapita (ribu rupiah)',
        'total_faskes': 'Total Fasilitas Kesehatan',
        'persentase_jalan_memenuhi': 'Persentase Jalan Memenuhi Syarat (%)'
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"Rata-rata {label_variabel[variabel_pilihan]} per Klaster")
        rata_rata = df.groupby('label_klaster')[variabel_pilihan].mean().reset_index()
        fig = px.bar(rata_rata, x='label_klaster', y=variabel_pilihan,
                     color='label_klaster',
                     color_discrete_map={'Maju': '#2ecc71', 'Berkembang': '#f39c12', 'Tertinggal': '#e74c3c'},
                     labels={'label_klaster': 'Klaster', variabel_pilihan: label_variabel[variabel_pilihan]})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader(f"Sebaran {label_variabel[variabel_pilihan]} per Klaster")
        fig = px.box(df, x='label_klaster', y=variabel_pilihan,
                     color='label_klaster',
                     color_discrete_map={'Maju': '#2ecc71', 'Berkembang': '#f39c12', 'Tertinggal': '#e74c3c'},
                     labels={'label_klaster': 'Klaster', variabel_pilihan: label_variabel[variabel_pilihan]})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Tabel Ringkasan Karakteristik Tiap Klaster")
    tabel_ringkasan = df.groupby('label_klaster')[
        ['ipm', 'persentase_miskin', 'rls', 'tpt', 'pdrb_per_kapita', 'total_faskes', 'persentase_jalan_memenuhi']
    ].mean().round(2)
    st.dataframe(tabel_ringkasan, use_container_width=True)

    st.markdown("---")
    st.subheader("Daftar Wilayah per Klaster")
    klaster_terpilih = st.selectbox("Pilih klaster:", df['label_klaster'].unique())
    wilayah_list = df[df['label_klaster'] == klaster_terpilih][['wilayah', 'ipm']].sort_values('ipm', ascending=False)
    st.dataframe(wilayah_list, use_container_width=True, hide_index=True)

elif menu == "Hasil Regresi":
    st.title("📈 Hasil Analisis Regresi Linier Berganda")
    st.markdown("Model regresi untuk mengetahui faktor yang paling berpengaruh terhadap IPM.")

    st.info("**Model:** IPM = 30.75 + 1.58(TPT) + 3.81(log PDRB per Kapita) − 0.0019(Total Faskes)")

    col1, col2, col3 = st.columns(3)
    col1.metric("R-squared", "0.672")
    col2.metric("Adj. R-squared", "0.643")
    col3.metric("F-statistic p-value", "1.41e-06")

    st.markdown("---")

    hasil_regresi = pd.DataFrame({
        'Variabel': ['Konstanta', 'TPT', 'log PDRB per Kapita', 'Total Faskes'],
        'Koefisien': [30.75, 1.58, 3.81, -0.0019],
        'p-value': [0.049, 0.021, 0.017, 0.008],
        'Signifikan (α=0.05)': ['Ya', 'Ya', 'Ya', 'Ya']
    })
    st.subheader("Tabel Koefisien Regresi")
    st.dataframe(hasil_regresi, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Visualisasi Kekuatan Pengaruh Tiap Variabel")
    fig = px.bar(hasil_regresi[hasil_regresi['Variabel'] != 'Konstanta'],
                 x='Variabel', y='Koefisien', color='Koefisien',
                 color_continuous_scale='RdYlGn',
                 labels={'Koefisien': 'Koefisien Regresi'})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Interpretasi Hasil")
    st.markdown("""
    - **PDRB per Kapita** berpengaruh paling besar dan positif terhadap IPM — semakin tinggi ekonomi wilayah, semakin tinggi IPM.
    - **TPT (Tingkat Pengangguran Terbuka)** berpengaruh positif — hal ini terjadi karena wilayah maju/perkotaan memiliki lebih banyak angkatan kerja formal yang aktif mencari kerja, dibanding wilayah tertinggal yang banyak bekerja informal/pertanian.
    - **Total Fasilitas Kesehatan** berpengaruh negatif kecil — mengindikasikan jumlah faskes lebih mencerminkan luas wilayah/populasi, bukan kualitas pembangunan.
    """)

elif menu == "Eksplorasi Data":
    st.title("🔎 Eksplorasi Data Wilayah")

    col1, col2 = st.columns([1, 3])
    with col1:
        filter_klaster = st.multiselect("Filter Klaster:", df['label_klaster'].unique(), default=df['label_klaster'].unique())

    df_filtered = df[df['label_klaster'].isin(filter_klaster)]

    st.subheader(f"Data Wilayah ({len(df_filtered)} wilayah)")
    kolom_tampil = ['wilayah', 'label_klaster', 'ipm', 'persentase_miskin', 'rls', 'tpt', 'pdrb_per_kapita', 'total_faskes', 'persentase_jalan_memenuhi']
    st.dataframe(df_filtered[kolom_tampil], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Cari Wilayah Spesifik")
    wilayah_cari = st.selectbox("Pilih wilayah:", sorted(df['wilayah'].unique()))
    data_wilayah = df[df['wilayah'] == wilayah_cari].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("IPM", f"{data_wilayah['ipm']:.2f}")
    col2.metric("Persentase Miskin", f"{data_wilayah['persentase_miskin']:.2f}%")
    col3.metric("RLS", f"{data_wilayah['rls']:.2f} tahun")
    col4.metric("Klaster", data_wilayah['label_klaster'])

    st.markdown("---")
    st.subheader("Download Data")
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "data_wilayah_jatim.csv", "text/csv")
