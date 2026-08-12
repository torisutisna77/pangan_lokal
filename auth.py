import streamlit as st
import bcrypt
from database import run_query

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login_user(username: str, password: str):
    result = run_query(
        "SELECT * FROM users WHERE username = %s AND is_active = TRUE",
        (username,)
    )
    if result and check_password(password, result[0]["password_hash"]):
        return result[0]
    return None

def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

def show_login_page():
    st.title("🔐 Sistem Analisis Pangan Lokal")
    st.markdown("**XGBoost • Kearifan Lokal • Cuaca Realtime**")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", type="primary"):
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Selamat datang, {user['full_name']}")
                    st.rerun()
                else:
                    st.error("Username / password salah atau akun nonaktif")

    with tab_register:
        st.info("Role default setelah register: **dinas**")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_fullname = st.text_input("Nama Lengkap")
            new_password = st.text_input("Password", type="password")
            confirm = st.text_input("Konfirmasi Password", type="password")

            if st.form_submit_button("Daftar"):
                if not new_username or not new_password:
                    st.error("Username dan Password wajib diisi")
                elif new_password != confirm:
                    st.error("Password tidak cocok")
                else:
                    existing = run_query("SELECT id FROM users WHERE username = %s", (new_username,))
                    if existing:
                        st.error("Username sudah digunakan")
                    else:
                        hashed = hash_password(new_password)
                        run_query(
                            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s,%s,%s,%s)",
                            (new_username, hashed, new_fullname, "dinas"),
                            fetch=False
                        )
                        st.success("Registrasi berhasil! Silakan login.")