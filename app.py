import streamlit as st

# ==============================
# CẤU HÌNH
# ==============================

st.set_page_config(
    page_title="Kế Toán Tự Động Hóa",
    page_icon="📊",
    layout="wide"
)

# ==============================
# TIÊU ĐỀ
# ==============================

st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

st.write(
    "Hệ thống hỗ trợ quản lý chứng từ, hóa đơn, "
    "ngân hàng, công nợ và dữ liệu kế toán."
)

st.markdown("---")

st.subheader("📌 Các chức năng chính")

# ==============================
# HÀNG 1
# ==============================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄 Chứng từ")
    st.write("Quản lý và tải chứng từ.")

    if st.button(
        "Mở Chứng từ",
        key="chung_tu",
        use_container_width=True
    ):
        st.switch_page("pages/1_Chung_tu.py")


with col2:
    st.markdown("### 🧾 Hóa đơn")
    st.write("Đang xây dựng.")

    st.button(
        "Chưa mở",
        key="hoa_don",
        disabled=True,
        use_container_width=True
    )


with col3:
    st.markdown("### 🏦 Ngân hàng")
    st.write("Đang xây dựng.")

    st.button(
        "Chưa mở",
        key="ngan_hang",
        disabled=True,
        use_container_width=True
    )


# ==============================
# HÀNG 2
# ==============================

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("### 📒 Công nợ")
    st.write("Đang xây dựng.")

    st.button(
        "Chưa mở",
        key="cong_no",
        disabled=True,
        use_container_width=True
    )


with col5:
    st.markdown("### 📚 Hệ thống tài khoản")
    st.write("Đang xây dựng.")

    st.button(
        "Chưa mở",
        key="tai_khoan",
        disabled=True,
        use_container_width=True
    )


with col6:
    st.markdown("### 📊 Báo cáo")
    st.write("Đang xây dựng.")

    st.button(
        "Chưa mở",
        key="bao_cao",
        disabled=True,
        use_container_width=True
    )


st.markdown("---")

st.info("💡 Chức năng sẽ được mở dần trong quá trình xây dựng.")
