import streamlit as st

# =========================
# CẤU HÌNH WEBSITE
# =========================

st.set_page_config(
    page_title="Kế Toán Tự Động Hóa",
    page_icon="📊",
    layout="wide"
)


# =========================
# TÀI KHOẢN TEST
# =========================

USERNAME = "admin"
PASSWORD = "123456"


# =========================
# KIỂM TRA ĐĂNG NHẬP
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================
# MÀN HÌNH ĐĂNG NHẬP
# =========================

if not st.session_state.logged_in:

    st.title("📊 KẾ TOÁN TỰ ĐỘNG HÓA")
    st.subheader("Đăng nhập hệ thống")

    username = st.text_input(
        "Tên đăng nhập",
        placeholder="Nhập tên đăng nhập"
    )

    password = st.text_input(
        "Mật khẩu",
        type="password",
        placeholder="Nhập mật khẩu"
    )

    if st.button("🔐 Đăng nhập", use_container_width=True):

        if username == USERNAME and password == PASSWORD:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.rerun()

        else:

            st.error("❌ Tên đăng nhập hoặc mật khẩu không đúng.")


# =========================
# TRANG CHÍNH
# =========================

else:

    st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

    st.success(
        f"Đăng nhập thành công! Xin chào {st.session_state.username}."
    )

    st.write("Chào mừng bạn đến với hệ thống.")

    if st.button("🚪 Đăng xuất"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()
