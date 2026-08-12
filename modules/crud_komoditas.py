import streamlit as st
from database import run_query

def show_crud_komoditas():
    st.header("🌾 Manajemen Komoditas Pangan")

    tab1, tab2, tab3, tab4 = st.tabs(["Daftar", "Tambah", "Edit", "Hapus"])

    # ---------- DAFTAR ----------
    with tab1:
        data = run_query("SELECT * FROM komoditas ORDER BY nama_komoditas")
        if data:
            st.dataframe(data, use_container_width=True)
        else:
            st.info("Belum ada data komoditas.")

    # ---------- TAMBAH ----------
    with tab2:
        with st.form("add_komoditas", clear_on_submit=True):
            nama = st.text_input("Nama Komoditas*")
            kategori = st.selectbox("Kategori", ["Padi-padian", "Umbi-umbian", "Sagu", "Jagung", "Kacang-kacangan", "Lainnya"])
            deskripsi = st.text_area("Deskripsi")
            is_lokal = st.checkbox("Tanaman Lokal", value=True)
            
            if st.form_submit_button("Simpan Komoditas", type="primary"):
                if not nama:
                    st.error("Nama komoditas wajib diisi.")
                else:
                    run_query(
                        "INSERT INTO komoditas (nama_komoditas, kategori, deskripsi, is_lokal) VALUES (%s,%s,%s,%s)",
                        (nama, kategori, deskripsi, is_lokal),
                        fetch=False
                    )
                    st.success("Komoditas berhasil ditambahkan.")
                    st.rerun()

    # ---------- EDIT ----------
    with tab3:
        data = run_query("SELECT * FROM komoditas ORDER BY nama_komoditas")
        if not data:
            st.info("Belum ada data komoditas.")
        else:
            options = {f"{d['nama_komoditas']} (ID: {d['id']})": d for d in data}
            selected_label = st.selectbox("Pilih Komoditas yang akan diedit", list(options.keys()))
            kom = options[selected_label]

            with st.form("edit_komoditas"):
                st.write(f"**Editing ID:** {kom['id']}")
                new_nama = st.text_input("Nama Komoditas*", value=kom["nama_komoditas"])
                
                kategori_list = ["Padi-padian", "Umbi-umbian", "Sagu", "Jagung", "Kacang-kacangan", "Lainnya"]
                current_kat = kom["kategori"] if kom["kategori"] in kategori_list else "Lainnya"
                new_kategori = st.selectbox("Kategori", kategori_list, index=kategori_list.index(current_kat))
                
                new_deskripsi = st.text_area("Deskripsi", value=kom["deskripsi"] or "")
                new_is_lokal = st.checkbox("Tanaman Lokal", value=bool(kom["is_lokal"]))

                if st.form_submit_button("Update Komoditas", type="primary"):
                    run_query(
                        """UPDATE komoditas 
                           SET nama_komoditas = %s, kategori = %s, deskripsi = %s, is_lokal = %s 
                           WHERE id = %s""",
                        (new_nama, new_kategori, new_deskripsi, new_is_lokal, kom["id"]),
                        fetch=False
                    )
                    st.success("Komoditas berhasil diupdate.")
                    st.rerun()

    # ---------- HAPUS ----------
    with tab4:
        data = run_query("SELECT id, nama_komoditas FROM komoditas ORDER BY nama_komoditas")
        if data:
            options = {d["nama_komoditas"]: d["id"] for d in data}
            selected = st.selectbox("Pilih Komoditas yang akan dihapus", list(options.keys()))
            if st.button("Hapus Komoditas", type="primary"):
                run_query("DELETE FROM komoditas WHERE id = %s", (options[selected],), fetch=False)
                st.success("Komoditas berhasil dihapus.")
                st.rerun()