import streamlit as st
from database import run_query
from auth import hash_password

def show_crud_user():
    st.header("👤 Manajemen User")
    
    if st.session_state.user["role"] != "admin":
        st.warning("Hanya Admin yang dapat mengakses halaman ini.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["Daftar User", "Tambah User", "Edit User", "Hapus / Nonaktifkan"])

    # ---------- DAFTAR ----------
    with tab1:
        users = run_query("""
            SELECT id, username, full_name, role, is_active, created_at 
            FROM users ORDER BY id
        """)
        if users:
            st.dataframe(users, use_container_width=True)
        else:
            st.info("Belum ada data user.")

    # ---------- TAMBAH ----------
    with tab2:
        with st.form("add_user", clear_on_submit=True):
            username = st.text_input("Username*")
            full_name = st.text_input("Nama Lengkap")
            password = st.text_input("Password*", type="password")
            role = st.selectbox("Peran", ["admin", "petugas", "dinas"])
            
            if st.form_submit_button("Simpan User", type="primary"):
                if not username or not password:
                    st.error("Username dan Password wajib diisi.")
                else:
                    existing = run_query("SELECT id FROM users WHERE username = %s", (username,))
                    if existing:
                        st.error("Username sudah digunakan.")
                    else:
                        hashed = hash_password(password)
                        run_query(
                            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s,%s,%s,%s)",
                            (username, hashed, full_name, role),
                            fetch=False
                        )
                        st.success("User berhasil ditambahkan.")
                        st.rerun()

    # ---------- EDIT ----------
    with tab3:
        users = run_query("SELECT id, username, full_name, role, is_active FROM users ORDER BY username")
        if not users:
            st.info("Belum ada data user.")
        else:
            options = {f"{u['username']} (ID: {u['id']})": u for u in users}
            selected_label = st.selectbox("Pilih User yang akan diedit", list(options.keys()))
            user = options[selected_label]

            with st.form("edit_user"):
                st.write(f"**Editing:** `{user['username']}`")
                new_fullname = st.text_input("Nama Lengkap", value=user["full_name"] or "")
                new_role = st.selectbox(
                    "Peran",
                    ["admin", "petugas", "dinas"],
                    index=["admin", "petugas", "dinas"].index(user["role"])
                )
                new_active = st.checkbox("Aktif", value=user["is_active"])
                new_password = st.text_input("Password Baru (kosongkan jika tidak ingin diubah)", type="password")

                if st.form_submit_button("Update User", type="primary"):
                    if new_password:
                        hashed = hash_password(new_password)
                        run_query(
                            """UPDATE users 
                               SET full_name = %s, role = %s, is_active = %s, password_hash = %s 
                               WHERE id = %s""",
                            (new_fullname, new_role, new_active, hashed, user["id"]),
                            fetch=False
                        )
                    else:
                        run_query(
                            """UPDATE users 
                               SET full_name = %s, role = %s, is_active = %s 
                               WHERE id = %s""",
                            (new_fullname, new_role, new_active, user["id"]),
                            fetch=False
                        )
                    st.success("User berhasil diupdate.")
                    st.rerun()

    # ---------- HAPUS / NONAKTIFKAN ----------
    with tab4:
        users = run_query("SELECT id, username, role, is_active FROM users ORDER BY username")
        if users:
            options = {f"{u['username']} ({u['role']})": u for u in users}
            selected = st.selectbox("Pilih User", list(options.keys()), key="delete_user")
            user = options[selected]

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Nonaktifkan User", use_container_width=True):
                    run_query("UPDATE users SET is_active = FALSE WHERE id = %s", (user["id"],), fetch=False)
                    st.success("User dinonaktifkan.")
                    st.rerun()
            with c2:
                if st.button("Hapus Permanen", type="primary", use_container_width=True):
                    run_query("DELETE FROM users WHERE id = %s", (user["id"],), fetch=False)
                    st.success("User dihapus permanen.")
                    st.rerun()