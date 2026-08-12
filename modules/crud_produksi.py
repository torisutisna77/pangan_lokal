import streamlit as st
from database import run_query

def show_crud_produksi():
    st.header("📥 Manajemen Data Produksi")

    daerah_list = run_query("SELECT id, nama_daerah, pulau FROM daerah ORDER BY nama_daerah")
    komoditas_list = run_query("SELECT id, nama_komoditas FROM komoditas ORDER BY nama_komoditas")

    if not daerah_list or not komoditas_list:
        st.warning("Harap isi data **Daerah** dan **Komoditas** terlebih dahulu.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["Daftar Data", "Tambah Data", "Edit Data", "Hapus Data"])

    # ---------- DAFTAR ----------
    with tab1:
        data = run_query("""
            SELECT p.id, d.nama_daerah, d.pulau, k.nama_komoditas, p.tahun,
                   p.produksi_ton, p.luas_ha, p.produktivitas,
                   p.curah_hujan_mm, p.suhu_c, p.indeks_kearifan, p.status_gagal_panen
            FROM data_produksi p
            JOIN daerah d ON p.daerah_id = d.id
            JOIN komoditas k ON p.komoditas_id = k.id
            ORDER BY p.tahun DESC, p.id DESC
        """)
        if data:
            st.dataframe(data, use_container_width=True)
        else:
            st.info("Belum ada data produksi.")

    # ---------- TAMBAH ----------
    with tab2:
        with st.form("add_produksi", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                daerah_opt = {f"{d['nama_daerah']} ({d['pulau']})": d["id"] for d in daerah_list}
                sel_daerah = st.selectbox("Daerah*", list(daerah_opt.keys()))
                
                kom_opt = {k["nama_komoditas"]: k["id"] for k in komoditas_list}
                sel_kom = st.selectbox("Komoditas*", list(kom_opt.keys()))
                
                tahun = st.number_input("Tahun*", min_value=2000, max_value=2030, value=2025)
                produksi = st.number_input("Produksi (Ton)*", min_value=0.0, value=1000.0)
                luas = st.number_input("Luas (Ha)*", min_value=0.0, value=400.0)
            with c2:
                produktivitas = st.number_input("Produktivitas (ton/ha)", min_value=0.0, value=2.5)
                curah = st.number_input("Curah Hujan (mm)", min_value=0.0, value=1500.0)
                suhu = st.number_input("Suhu (°C)", min_value=15.0, max_value=40.0, value=27.0)
                kearifan = st.slider("Indeks Kearifan Lokal (1-5)", 1, 5, 3)
                status = st.selectbox("Status Gagal Panen", [0, 1], format_func=lambda x: "Aman (0)" if x == 0 else "Gagal Panen (1)")

            if st.form_submit_button("Simpan Data Produksi", type="primary"):
                run_query("""
                    INSERT INTO data_produksi 
                    (daerah_id, komoditas_id, tahun, produksi_ton, luas_ha, produktivitas,
                     curah_hujan_mm, suhu_c, indeks_kearifan, status_gagal_panen)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (daerah_opt[sel_daerah], kom_opt[sel_kom], tahun, produksi, luas,
                      produktivitas, curah, suhu, kearifan, status), fetch=False)
                st.success("Data produksi berhasil disimpan.")
                st.rerun()

    # ---------- EDIT ----------
    with tab3:
        data = run_query("""
            SELECT p.*, d.nama_daerah, d.pulau, k.nama_komoditas
            FROM data_produksi p
            JOIN daerah d ON p.daerah_id = d.id
            JOIN komoditas k ON p.komoditas_id = k.id
            ORDER BY p.id DESC
        """)
        
        if not data:
            st.info("Belum ada data produksi.")
        else:
            options = {
                f"ID:{d['id']} | {d['nama_daerah']} - {d['nama_komoditas']} ({d['tahun']})": d 
                for d in data
            }
            selected_label = st.selectbox("Pilih Data yang akan diedit", list(options.keys()))
            row = options[selected_label]

            with st.form("edit_produksi"):
                st.write(f"**Editing Data ID:** {row['id']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    # Daerah
                    daerah_opt = {f"{d['nama_daerah']} ({d['pulau']})": d["id"] for d in daerah_list}
                    current_daerah_label = next(
                        (label for label, id_ in daerah_opt.items() if id_ == row["daerah_id"]), 
                        list(daerah_opt.keys())[0]
                    )
                    sel_daerah = st.selectbox("Daerah*", list(daerah_opt.keys()), 
                                              index=list(daerah_opt.keys()).index(current_daerah_label))
                    
                    # Komoditas
                    kom_opt = {k["nama_komoditas"]: k["id"] for k in komoditas_list}
                    current_kom_label = next(
                        (label for label, id_ in kom_opt.items() if id_ == row["komoditas_id"]),
                        list(kom_opt.keys())[0]
                    )
                    sel_kom = st.selectbox("Komoditas*", list(kom_opt.keys()),
                                           index=list(kom_opt.keys()).index(current_kom_label))
                    
                    tahun = st.number_input("Tahun*", 2000, 2030, value=int(row["tahun"]))
                    produksi = st.number_input("Produksi (Ton)*", 0.0, value=float(row["produksi_ton"] or 0))
                    luas = st.number_input("Luas (Ha)*", 0.0, value=float(row["luas_ha"] or 0))
                
                with c2:
                    produktivitas = st.number_input("Produktivitas (ton/ha)", 0.0, value=float(row["produktivitas"] or 0))
                    curah = st.number_input("Curah Hujan (mm)", 0.0, value=float(row["curah_hujan_mm"] or 0))
                    suhu = st.number_input("Suhu (°C)", 15.0, 40.0, value=float(row["suhu_c"] or 27))
                    kearifan = st.slider("Indeks Kearifan Lokal", 1, 5, value=int(row["indeks_kearifan"] or 3))
                    status = st.selectbox(
                        "Status Gagal Panen", 
                        [0, 1], 
                        index=int(row["status_gagal_panen"] or 0),
                        format_func=lambda x: "Aman (0)" if x == 0 else "Gagal Panen (1)"
                    )

                if st.form_submit_button("Update Data Produksi", type="primary"):
                    run_query("""
                        UPDATE data_produksi SET
                            daerah_id = %s,
                            komoditas_id = %s,
                            tahun = %s,
                            produksi_ton = %s,
                            luas_ha = %s,
                            produktivitas = %s,
                            curah_hujan_mm = %s,
                            suhu_c = %s,
                            indeks_kearifan = %s,
                            status_gagal_panen = %s
                        WHERE id = %s
                    """, (
                        daerah_opt[sel_daerah], kom_opt[sel_kom], tahun, produksi, luas,
                        produktivitas, curah, suhu, kearifan, status, row["id"]
                    ), fetch=False)
                    st.success("Data produksi berhasil diupdate.")
                    st.rerun()

    # ---------- HAPUS ----------
    with tab4:
        data = run_query("""
            SELECT p.id, d.nama_daerah, k.nama_komoditas, p.tahun
            FROM data_produksi p
            JOIN daerah d ON p.daerah_id = d.id
            JOIN komoditas k ON p.komoditas_id = k.id
            ORDER BY p.id DESC LIMIT 100
        """)
        if data:
            options = {
                f"ID:{d['id']} | {d['nama_daerah']} - {d['nama_komoditas']} ({d['tahun']})": d["id"] 
                for d in data
            }
            selected = st.selectbox("Pilih data yang akan dihapus", list(options.keys()))
            if st.button("Hapus Data", type="primary"):
                run_query("DELETE FROM data_produksi WHERE id = %s", (options[selected],), fetch=False)
                st.success("Data berhasil dihapus.")
                st.rerun()