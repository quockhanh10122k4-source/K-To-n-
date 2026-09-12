import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hệ thống Kế toán Thông minh", layout="wide")

st.title("Phần mềm Kế toán Tự động & Hóa đơn Điện tử")
st.markdown("---")

# Sidebar điều hướng phân hệ
menu = st.sidebar.selectbox(
    "Chọn phân hệ nghiệp vụ", 
    ["1. Tiếp nhận & OCR Hóa đơn", "2. Đối soát & Duyệt lệch dòng", "3. Bút toán & Sổ cái"]
)

if menu == "1. Tiếp nhận & OCR Hóa đơn":
    st.header("Tải lên & Bóc tách Hóa đơn tự động (AI/OCR)")
    
    uploaded_file = st.file_uploader("Chọn file hóa đơn (PDF, XML, Ảnh)", type=["pdf", "xml", "png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Xem trước Chứng từ")
            if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                st.image(uploaded_file, caption="Hóa đơn gốc", use_column_width=True)
            else:
                st.write(f"Đã nhận tệp: {uploaded_file.name}")
        
        with col2:
            st.subheader("Dữ liệu AI bóc tách (Trạng thái: Nháp)")
            # Giả lập kết quả trích xuất từ OCR
            extracted_data = {
                "Trường dữ liệu": ["Mã số thuế", "Tên người bán", "Tổng thanh toán", "Thuế GTGT"],
                "Giá trị bóc tách": ["0101234567", "Công ty TNHH Giải pháp Số", "11.000.000 VNĐ", "1.000.000 VNĐ"],
                "Độ tin cậy (Confidence)": ["98%", "95%", "99%", "90%"]
            }
            st.table(pd.DataFrame(extracted_data))
            
            if st.button("Xác nhận & Lưu vào CSDL Staging"):
                st.success("Đã lưu chứng từ thành công! Chuyển sang phân hệ đối soát.")

elif menu == "2. Đối soát & Duyệt lệch dòng":
    st.header("Giao diện Human-in-the-Loop & Xử lý Lệch dòng")
    st.info("So khớp tự động biến động số dư ngân hàng (TK 112) với công nợ phải thu (TK 131).")
    
    # Bảng dữ liệu mẫu kiểm thử lệch dòng
    mock_match_data = {
        "Mã chứng từ": ["HD001", "HD002", "HD003"],
        "Khách hàng": ["Công ty X", "Công ty Y", "Công ty Z"],
        "Phải thu (131)": ["5.000.000", "12.000.000", "3.200.000"],
        "Sao kê thực tế (112)": ["5.000.000", "11.500.000", "3.200.000"],
        "Trạng thái": ["Khớp (Matched)", "Lệch số tiền (-500.000)", "Khớp (Matched)"]
    }
    st.dataframe(pd.DataFrame(mock_match_data), use_container_width=True)

elif menu == "3. Bút toán & Sổ cái":
    st.header("Hệ thống Bút toán Kép (Double-Entry Bookkeeping)")
    st.write("Sổ cái lưu vết toàn bộ giao dịch tài chính đã được ghi sổ chính thức.")
    
    ledger_data = {
        "Ngày": ["2026-06-06", "2026-06-06"],
        "Số chứng từ": ["PC001", "PT001"],
        "Diễn giải": ["Thanh toán mua văn phòng phẩm", "Thu tiền khách hàng X qua ngân hàng"],
        "Nợ": ["TK 642 / 1.000.000", "TK 112 / 5.000.000"],
        "Có": ["TK 111 / 1.000.000", "TK 131 / 5.000.000"],
        "Khóa sổ": ["Đã khóa", "Đã khóa"]
    }
    st.table(pd.DataFrame(ledger_data))
