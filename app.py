import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hệ thống Kế toán & Quản trị Tự động", layout="wide")

st.title("Phần mềm Kế toán Doanh nghiệp & Tích hợp Tự động hóa")
st.markdown("---")

# Điều hướng phân hệ nghiệp vụ chi tiết
module = st.sidebar.selectbox(
    "Chọn phân hệ nghiệp vụ", 
    [
        "1. Kế toán Tổng hợp & Danh mục (COA)",
        "2. Kế toán Tiền mặt, Ngân hàng & Đối soát",
        "3. Kế toán Công nợ Mua/Bán (AR/AP)",
        "4. Quản lý Hóa đơn Điện tử & OCR AI",
        "5. Kế toán Kho, Tài sản & Giá thành",
        "6. Quản trị Hệ thống & Kiểm toán (Audit Trail)"
    ]
)

if module == "1. Kế toán Tổng hợp & Danh mục (COA)":
    st.header("Hệ thống Tài khoản Kế toán (Theo Thông tư 200/2014/TT-BTC)")
    st.write("Quản lý danh mục tài khoản cấp mẹ và tài khoản chi tiết (sub-accounts) đảm bảo nguyên tắc bút toán kép.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        coa_df = pd.DataFrame({
            "Mã TK": ["111", "1111", "112", "131", "331", "511", "3331", "642"],
            "Tên Tài khoản": [
                "Tiền mặt", "Tiền mặt tại quỹ VNĐ", "Tiền gửi ngân hàng", 
                "Phải thu của khách hàng", "Phải trả cho người bán", 
                "Doanh thu bán hàng và cung cấp dịch vụ", "Thuế GTGT phải nộp", "Chi phí quản lý doanh nghiệp"
            ],
            "Cấp TK": ["Cấp 1", "Cấp 2", "Cấp 1", "Cấp 1", "Cấp 1", "Cấp 1", "Cấp 2", "Cấp 1"],
            "Tính chất": ["Dư Nợ", "Dư Nợ", "Dư Nợ", "Lưỡng tính", "Dư Có", "Dư Có", "Dư Có", "Dư Nợ"]
        })
        st.dataframe(coa_df, use_container_width=True)
    with col2:
        st.subheader("Thêm/Sửa Tài khoản")
        st.text_input("Mã tài khoản mới")
        st.text_input("Tên tài khoản")
        st.selectbox("Tính chất", ["Dư Nợ", "Dư Có", "Lưỡng tính"])
        st.button("Cập nhật Danh mục")

elif module == "2. Kế toán Tiền mặt, Ngân hàng & Đối soát":
    st.header("Đối soát Biến động Số dư Ngân hàng (Bank Reconciliation Engine)")
    st.write("Tự động khớp nối giao dịch từ file sao kê ngân hàng với các khoản phải thu/phải trả.")
    
    uploaded_bank = st.file_uploader("Tải lên file sao kê ngân hàng (.xlsx, .csv)", type=["xlsx", "csv"])
    
    matching_data = pd.DataFrame({
        "Mã Giao dịch": ["TXN9921", "TXN9922", "TXN9923"],
        "Ngày giờ": ["2026-06-06 08:30", "2026-06-06 09:15", "2026-06-06 10:00"],
        "Nội dung chuyển khoản": ["Cty A thanh toán HD001", "Chuyen khoan mua hang khong ro noi dung", "Cty B thanh toan tien hang thang 5"],
        "Số tiền sao kê": ["10.000.000", "5.500.000", "22.300.000"],
        "Khớp nối Hệ thống": ["Khớp hoàn toàn (Auto-Matched)", "Lệch / Thiếu chứng từ", "Khớp hoàn toàn (Auto-Matched)"],
        "Trạng thái xử lý": ["Đã gạch nợ TK 131", "Cần duyệt thủ công", "Đã gạch nợ TK 131"]
    })
    st.dataframe(matching_data, use_container_width=True)

elif module == "3. Kế toán Công nợ Mua/Bán (AR/AP)":
    st.header("Quản lý Công nợ Khách hàng (TK 131) & Nhà cung cấp (TK 331)")
    
    tab1, tab2 = st.tabs(["Công nợ Phải Thu (AR)", "Công nợ Phải Trả (AP)"])
    
    with tab1:
        st.subheader("Theo dõi Tuổi nợ & Hạn thanh toán")
        ar_df = pd.DataFrame({
            "Mã KH": ["KH01", "KH02", "KH03"],
            "Tên Khách hàng": ["Công ty Cổ phần Thương mại Alpha", "Công ty TNHH Beta", "Doanh nghiệp Tư nhân Gamma"],
            "Tổng Phải Thu": ["45.000.000", "120.500.000", "8.200.000"],
            "Đã thanh toán": ["45.000.000", "60.000.000", "0"],
            "Còn phải thu": ["0", "60.500.000", "8.200.000"],
            "Quá hạn": ["Không", "15 ngày", "Quá hạn 45 ngày (Cảnh báo đỏ)"]
        })
        st.dataframe(ar_df, use_container_width=True)
        
    with tab2:
        st.subheader("Danh sách công nợ nhà cung cấp đến hạn")
        st.write("Chưa có khoản phải trả quá hạn nào trong kỳ.")

elif module == "4. Quản lý Hóa đơn Điện tử & OCR AI":
    st.header("Trích xuất Hóa đơn Tự động bằng AI/OCR & Hạch toán Định khoản")
    
    uploaded_inv = st.file_uploader("Tải lên hóa đơn điện tử (XML/PDF/Ảnh)", type=["xml", "pdf", "png", "jpg"])
    
    if uploaded_inv:
        col_a, col_b = st.columns(2)
        with col_a:
            st.info("Đã tiếp nhận file hóa đơn đầu vào.")
            st.code("File Hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nTrạng thái: Đã qua kiểm tra ClamAV (An toàn)")
        with col_b:
            st.success("Kết quả bóc tách AI (Độ tin cậy: 98.4%)")
            st.json({
                "seller_tax_code": "0102938475",
                "seller_name": "Công ty Giải pháp Công nghệ Việt",
                "invoice_number": "0001234",
                "total_amount": 16500000,
                "vat_amount": 1500000,
                "suggested_posting": "Nợ TK 642 / Có TK 331"
            })
            if st.button("Xác nhận Ghi sổ Định khoản"):
                st.balloons()
                st.success("Đã sinh bút toán kép vào Sổ cái thành công!")

elif module == "5. Kế toán Kho, Tài sản & Giá thành":
    st.header("Quản lý Kho, Khấu hao Tài sản Cố định & Phân bổ CCDC")
    
    sub_tab = st.selectbox("Chọn phân hệ phụ", ["Kế toán Kho & Giá xuất kho", "Khấu hao Tài sản Cố định (TSCĐ)"])
    if sub_tab == "Kế toán Kho & Giá xuất kho":
        st.write("Phương pháp tính giá: **Bình quân gia quyền cuối kỳ** hoặc **FIFO**.")
        inventory_df = pd.DataFrame({
            "Mã VT": ["VT01", "VT02"],
            "Tên Vật tư / Hàng hóa": ["Giấy A4 Double A", "Mực máy in Canon"],
            "Tồn đầu kỳ": ["100 thùng", "20 hộp"],
            "Nhập trong kỳ": ["50 thùng", "10 hộp"],
            "Xuất trong kỳ": ["120 thùng", "25 hộp"],
            "Tồn cuối kỳ": ["30 thùng", "5 hộp"]
        })
        st.dataframe(inventory_df, use_container_width=True)
    else:
        st.write("Bảng phân bổ khấu hao TSCĐ tự động hàng tháng vào chi phí.")
        fa_df = pd.DataFrame({
            "Mã TSCĐ": ["TS01", "TS02"],
            "Tên Tài sản": ["Máy photocopy văn phòng", "Hệ thống máy chủ Server Dell"],
            "Nguyên giá": ["50.000.000", "120.000.000"],
            "Khấu hao lũy kế": ["10.000.000", "24.000.000"],
            "Giá trị còn lại": ["40.000.000", "96.000.000"]
        })
        st.dataframe(fa_df, use_container_width=True)

elif module == "6. Quản trị Hệ thống & Kiểm toán (Audit Trail)":
    st.header("Tầng Hệ thống, Bảo mật & Nhật ký Kiểm toán (Audit Trail)")
    st.write("Theo dõi toàn bộ vết hoạt động của người dùng và trạng thái hạ tầng kỹ thuật.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("Trạng thái Hạ tầng Hệ thống")
        st.markdown("""
        * **Database PostgreSQL (ACID):** `Kết nối ổn định (Online)`
        * **Redis Queue (Celery Worker):** `Đang hoạt động (0 tác vụ nghẽn)`
        * **Trạng thái Kỳ kế toán Tháng 06/2026:** `Đang mở (Chưa khóa sổ)`
        * **Cơ chế Idempotency Key:** `Đã kích hoạt (Chống gọi trùng lặp API)`
        """)
    with col_s2:
        st.subheader("Nhật ký Thao tác (Audit Trail)")
        audit_df = pd.DataFrame({
            "Thời gian": ["2026-06-06 11:00:22", "2026-06-06 10:45:12", "2026-06-06 09:30:05"],
            "Người dùng": ["ketoan_truong", "nhanvien_kho", "admin_it"],
            "Hành động": ["PHEDUYET_CHUNGTU", "TAO_MOI_HOADON", "CAP_NHAT_COA"],
            "IP Address": ["192.168.1.50", "192.168.1.65", "10.0.0.15"]
        })
        st.dataframe(audit_df, use_container_width=True)
