import streamlit as st

# ==============================
# CẤU HÌNH TRANG
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

st.subheader("📌 CÁC CHỨC NĂNG CHÍNH")

# ==============================
# HÀNG 1
# ==============================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄 Chứng từ")
    st.write("Tải lên và kiểm tra chứng từ kế toán.")

    st.page_link(
        "pages/1_Chung_tu.py",
        label="📄 Mở Chứng từ",
        use_container_width=True
    )

with col2:
    st.markdown("### 🧾 Hóa đơn")
    st.write("Quản lý và kiểm tra hóa đơn.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )

with col3:
    st.markdown("### 🏦 Ngân hàng")
    st.write("Đối chiếu dữ liệu ngân hàng.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )

# ==============================
# HÀNG 2
# ==============================

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("### 📒 Công nợ")
    st.write("Theo dõi công nợ phải thu và phải trả.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )

with col5:
    st.markdown("### 📚 Hệ thống tài khoản")
    st.write("Quản lý hệ thống tài khoản kế toán.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )

with col6:
    st.markdown("### 📊 Báo cáo")
    st.write("Tổng hợp và xuất báo cáo kế toán.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )

# ==============================
# CUỐI TRANG
# ==============================

st.markdown("---")

st.info(
    "💡 Hệ thống đang được xây dựng từng chức năng."
)
