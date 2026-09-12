import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Hệ Thống Kế Toán Tự Động",
    page_icon="📊",
    layout="wide"
)

# Khởi tạo session_state toàn hệ thống
if "chung_tu_db" not in st.session_state:
    st.session_state.chung_tu_db = pd.DataFrame(columns=["Số CT", "Ngày", "Loại", "Diễn Giải", "Tổng Tiền", "Trạng Thái"])

st.title("🚀 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA (ERP NỘI BỘ)")
st.markdown("---")

st.success("👋 Chào mừng bạn đến với hệ thống kế toán nội bộ.")
st.info("👈 **Hướng dẫn:** Vui lòng nhìn sang **thanh menu bên trái (Sidebar)** và bấm chọn mục **1_Chung_tu** để bắt đầu quản lý chứng từ.")

st.markdown("""
### 📌 Các phân hệ trong hệ thống:
1. **Chứng từ:** Ghi nhận và quản lý chứng từ kế toán.
2. **Hóa đơn:** Tiếp nhận và bóc tách hóa đơn tự động.
3. **Ngân hàng:** Quản lý sao kê và đối soát dòng tiền.
4. **Công nợ:** Theo dõi phải thu và phải trả.
5. **Hệ thống tài khoản:** Quản lý danh mục COA.
6. **Báo cáo:** Sổ cái và Nhật ký kiểm toán.
""")
