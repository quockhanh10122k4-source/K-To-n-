import streamlit as st

# ==============================
# CẤU HÌNH WEBSITE
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

st.markdown("---")

st.write(
    "Hệ thống hỗ trợ quản lý chứng từ, hóa đơn, "
    "ngân hàng, công nợ và dữ liệu kế toán."
)


# ==============================
# MENU CHỨC NĂNG
# ==============================

st.subheader("Các chức năng chính")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📄\n\n**Chứng từ**\n\nQuản lý chứng từ kế toán.")

with col2:
    st.info("🧾\n\n**Hóa đơn**\n\nTiếp nhận và kiểm tra hóa đơn.")

with col3:
    st.info("🏦\n\n**Ngân hàng**\n\nNhập và đối soát giao dịch.")


col4, col5, col6 = st.columns(3)

with col4:
    st.info("📒\n\n**Công nợ**\n\nTheo dõi phải thu và phải trả.")

with col5:
    st.info("📚\n\n**Hệ thống tài khoản**\n\nQuản lý hệ thống tài khoản kế toán.")

with col6:
    st.info("📊\n\n**Báo cáo**\n\nTổng hợp và xuất báo cáo.")


st.markdown("---")

st.success("Hệ thống đã sẵn sàng.")
