import streamlit as st
from database import run_query
from weather import get_weather

def show_crud_daerah():
    st.header("🗺️ Manajemen Daerah + Cuaca Realtime")

    tab1, tab2, tab3, tab4 = st.tabs(["Daftar + Cuaca", "Tambah Daerah", "Edit Daerah", "Hapus Daerah"])

    # ---------- DAFTAR + CUACA ----------
    with tab1:
        data = run_query("SELECT * FROM daerah ORDER BY pulau, nama_daerah")
        if not data:
            st.info("Belum ada data daerah.")
        else:
            st.dataframe(data, use_container_width=True)

            st.subheader("Cuaca Realtime")
            options = [f"{d['nama_daerah']} ({d['pulau']})" for d in data]
            selected = st.selectbox("Pilih Daerah untuk melihat cuaca", options)
            daerah = next(d for d in data if f"{d['nama_daerah']} ({d['pulau']})" == selected)

            if daerah.get("latitude") and daerah.get("longitude"):
                weather = get_weather(float(daerah["latitude"]), float(daerah["longitude"]))
                if weather:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Suhu", f"{weather['suhu']:.1f} °C")
                    c2.metric("Terasa", f"{weather['terasa_seperti']:.1f} °C")
                    c3.metric("Kelembaban", f"{weather['kelembaban']}%")
                    c4.metric("Angin", f"{weather['angin']} m/s")
                    st.success(f"**Kondisi Cuaca:** {weather['cuaca']}")
                else:
                    st.warning("Gagal mengambil data cuaca. Periksa API Key OpenWeather.")
            else:
                st.warning("Koordinat daerah belum diisi.")

    # ---------- TAMBAH ----------
    with tab2:
        with st.form("add_daerah", clear_on_submit=True):
            nama = st.text_input("Nama Daerah / Kota*")
            pulau = st.selectbox("Pulau*", ["Sumatra", "Jawa", "NTT", "Kalimantan", "Sulawesi", "Papua", "Bali", "Maluku", "Lainnya"])
            lat = st.number_input("Latitude*", value=0.0, format="%.6f")
            lon = st.number_input("Longitude*", value=0.0, format="%.6f")
            ket = st.text_area("Keterangan")
            
            if st.form_submit_button("Simpan Daerah", type="primary"):
                if not nama:
                    st.error("Nama daerah wajib diisi.")
                else:
                    run_query(
                        "INSERT INTO daerah (nama_daerah, pulau, latitude, longitude, keterangan) VALUES (%s,%s,%s,%s,%s)",
                        (nama, pulau, lat, lon, ket),
                        fetch=False
                    )
                    st.success("Daerah berhasil ditambahkan.")
                    st.rerun()

    # ---------- EDIT ----------
    with tab3:
        data = run_query("SELECT * FROM daerah ORDER BY nama_daerah")
        if not data:
            st.info("Belum ada data daerah.")
        else:
            options = {f"{d['nama_daerah']} ({d['pulau']}) - ID:{d['id']}": d for d in data}
            selected_label = st.selectbox("Pilih Daerah yang akan diedit", list(options.keys()))
            daerah = options[selected_label]

            with st.form("edit_daerah"):
                st.write(f"**Editing ID:** {daerah['id']}")
                new_nama = st.text_input("Nama Daerah*", value=daerah["nama_daerah"])
                pulau_list = ["Sumatra", "Jawa", "NTT", "Kalimantan", "Sulawesi", "Papua", "Bali", "Maluku", "Lainnya"]
                new_pulau = st.selectbox("Pulau*", pulau_list, index=pulau_list.index(daerah["pulau"]) if daerah["pulau"] in pulau_list else 0)
                new_lat = st.number_input("Latitude*", value=float(daerah["latitude"] or 0), format="%.6f")
                new_lon = st.number_input("Longitude*", value=float(daerah["longitude"] or 0), format="%.6f")
                new_ket = st.text_area("Keterangan", value=daerah["keterangan"] or "")

                if st.form_submit_button("Update Daerah", type="primary"):
                    run_query(
                        """UPDATE daerah 
                           SET nama_daerah = %s, pulau = %s, latitude = %s, longitude = %s, keterangan = %s 
                           WHERE id = %s""",
                        (new_nama, new_pulau, new_lat, new_lon, new_ket, daerah["id"]),
                        fetch=False
                    )
                    st.success("Daerah berhasil diupdate.")
                    st.rerun()

    # ---------- HAPUS ----------
    with tab4:
        data = run_query("SELECT id, nama_daerah, pulau FROM daerah ORDER BY nama_daerah")
        if data:
            options = {f"{d['nama_daerah']} ({d['pulau']})": d["id"] for d in data}
            selected = st.selectbox("Pilih Daerah yang akan dihapus", list(options.keys()))
            if st.button("Hapus Daerah", type="primary"):
                run_query("DELETE FROM daerah WHERE id = %s", (options[selected],), fetch=False)
                st.success("Daerah berhasil dihapus.")
                st.rerun()