import streamlit as st

# Import modul-modul
from auth import init_session, show_login_page
from modules.dashboard import show_dashboard
from modules.crud_user import show_crud_user
from modules.crud_daerah import show_crud_daerah
from modules.crud_komoditas import show_crud_komoditas
from modules.crud_produksi import show_crud_produksi


def main():
    # Konfigurasi halaman
    st.set_page_config(
        page_title="Sistem Analisis Pangan Lokal",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inisialisasi session
    init_session()

    # ==================== ROUTING UTAMA ====================
    # Jika belum login → tampilkan halaman login/register
    if not st.session_state.logged_in:
        show_login_page()
        return

    # ==================== SIDEBAR & MENU ====================
    with st.sidebar:
        st.title("🌾 Pangan Lokal")
        st.markdown(f"**👤 {st.session_state.user['full_name']}**")
        st.caption(f"Role: `{st.session_state.user['role'].upper()}`")
        st.markdown("---")

        # Definisikan menu berdasarkan role
        menu_items = {
            "Dashboard + XGBoost": show_dashboard,
        }

        # Menu untuk petugas & admin
        if st.session_state.user["role"] in ["admin", "petugas"]:
            menu_items["Data Produksi"] = show_crud_produksi
            menu_items["Manajemen Daerah"] = show_crud_daerah
            menu_items["Manajemen Komoditas"] = show_crud_komoditas

        # Menu khusus admin
        if st.session_state.user["role"] == "admin":
            menu_items["Manajemen User"] = show_crud_user

        # Pilihan menu
        selected_menu = st.radio(
            "Menu Navigasi",
            options=list(menu_items.keys()),
            key="main_menu"
        )

        st.markdown("---")

        # Tombol Logout
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    # ==================== ROUTING HALAMAN ====================
    # Panggil fungsi sesuai menu yang dipilih
    page_function = menu_items.get(selected_menu)

    if page_function:
        page_function()
    else:
        st.error("Halaman tidak ditemukan.")


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    main()