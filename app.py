import streamlit as st

st.set_page_config(
    page_title="Kế Toán Tự Động Hóa",
    page_icon="📊",
    layout="wide"
)

st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

st.write(
    "Hệ thống hỗ trợ tiếp nhận, kiểm tra và xử lý chứng từ kế toán."
)

st.markdown("---")

st.subheader("📌 CÁC PHÂN HỆ")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        """
        📄 **Chứng từ**

        - Tải nhiều chứng từ
        - Đọc dữ liệu
        - Kiểm tra ảnh gốc
        - Xuất Excel
        """
    )

with col2:
    st.info(
        """
        🧾 **Hóa đơn**

        Đang phát triển
        """
    )

with col3:
    st.info(
        """
        🏦 **Ngân hàng**

        Đang phát triển
        """
    )

st.markdown("---")

st.success(
    "✅ Hãy chọn **Chứng từ** ở thanh bên trái để bắt đầu."
)
