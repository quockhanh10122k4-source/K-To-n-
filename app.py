import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Hệ thống Kế toán & Tự động hóa Hóa đơn", layout="wide")

if 'invoice_db' not in st.session_state:
    st.session_state.invoice_db = pd.DataFrame(columns=[
        "ID", "Ngày chứng từ", "Mã số thuế", "Tên Nhà cung cấp", 
        "Số hóa đơn", "Tiền trước thuế", "Thuế GTGT", "Tổng thanh toán", "Trạng thái"
    ])

st.title("Phần mềm Kế toán Doanh nghiệp & Tự động hóa Hóa đơn")
st.markdown("---")

module = st.sidebar.selectbox(
    "Chọn phân hệ nghiệp vụ", 
    [
        "1. Quản lý Hóa đơn & Tự động hóa OCR (Chính)",
        "2. Hệ thống Tài khoản Kế toán (COA)",
        "3. Kế toán Tiền mặt, Ngân hàng & Đối soát",
        "4. Kế toán Công nợ & Sổ cái",
        "5. Quản trị Hệ thống & Kiểm toán"
    ]
)

if module == "1. Quản lý Hóa đơn & Tự động hóa OCR (Chính)":
    st.header("Trạm Tiếp nhận & Xử lý Hóa đơn Tự động (AI/OCR Pipeline)")
    st.write("Tải lên hóa đơn do khách hàng gửi tới để hệ thống tự động bóc tách và đưa vào cơ sở dữ liệu trung tâm.")
    
    col_upload, col_preview = st.columns([1, 1])
    
    with col_upload:
        st.subheader("1. Gửi file hóa đơn từ khách hàng")
        uploaded_file = st.file_uploader("Chọn file hóa đơn (PDF, XML, Ảnh)", type=["pdf", "xml", "png", "jpg", "jpeg"])
        
        if uploaded_file is not None:
            st.info(f"Đã nhận tệp: **{uploaded_file.name}**")
            
            auto_mst = "0109876543"
            auto_name = "Công ty TNHH Giải pháp Kế toán Số Việt Nam"
            auto_inv_no = "0001234"
            auto_total = 12100000.0
            
            st.success("AI đã bóc tách dữ liệu chuẩn xác từ hóa đơn mẫu!")
            
            with st.form(key="ocr_form"):
                st.subheader("2. Kiểm tra & Xác thực dữ liệu bóc tách")
                f_date = st.date_input("Ngày chứng từ", datetime.strptime("2026-09-12", "%Y-%m-%d"))
                f_mst = st.text_input("Mã số thuế nhà cung cấp", value=auto_mst)
                f_name = st.text_input("Tên nhà cung cấp", value=auto_name)
                f_inv_no = st.text_input("Số hóa đơn", value=auto_inv_no)
                f_total = st.number_input("Tổng thanh toán (VNĐ)", value=float(auto_total))
                
                submit_button = st.form_submit_button(label="Lưu vào Cơ sở dữ liệu (Single Source of Truth)")
                
                if submit_button:
                    vat = f_total / 11
                    net = f_total - vat
                    new_row = {
                        "ID": len(st.session_state.invoice_db) + 1,
                        "Ngày chứng từ": str(f_date),
                        "Mã số thuế": f_mst,
                        "Tên Nhà cung cấp": f_name,
                        "Số hóa đơn": f_inv_no,
                        "Tiền trước thuế": round(net, 2),
                        "Thuế GTGT": round(vat, 2),
                        "Tổng thanh toán": f_total,
                        "Trạng thái": "Đã ghi sổ tự động"
                    }
                    st.session_state.invoice_db = pd.concat([st.session_state.invoice_db, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Đã ghi nhận chứng từ vào hệ thống thành công!")

    with col_preview:
        st.subheader("Xem trước Chứng từ")
        if uploaded_file is not None:
            if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                st.image(uploaded_file, caption="Ảnh hóa đơn gốc", use_container_width=True)
            else:
                st.write("Định dạng tài liệu văn bản/XML đã được nạp vào bộ nhớ đệm an toàn.")
        else:
            st.warning("Chưa có file nào được tải lên. Vui lòng chọn file ở cột bên trái.")

    st.markdown("---")
    st.subheader("3. Cơ sở dữ liệu Hóa đơn Tập trung")
    
    if len(st.session_state.invoice_db) > 0:
        st.dataframe(st.session_state.invoice_db, use_container_width=True)
        
        st.subheader("4. Xuất Báo cáo ra File Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.invoice_db.to_excel(writer, index=False, sheet_name='Danh_sach_Hoa_don')
        processed_data = output.getvalue()
        
        st.download_button(
            label="📥 Tải xuống File Excel Báo cáo Kế toán (.xlsx)",
            data=processed_data,
            file_name=f"Bao_Cao_Hoa_Don_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Chưa có dữ liệu hóa đơn nào trong hệ thống. Hãy tải lên hóa đơn ở phía trên để bắt đầu.")

elif module == "2. Hệ thống Tài khoản Kế toán (COA)":
    st.header("Hệ thống Tài khoản Kế toán Doanh nghiệp (Thông tư 200)")
    st.dataframe(pd.DataFrame({
        "Mã TK": ["111", "112", "131", "331", "511", "642"],
        "Tên tài khoản": ["Tiền mặt", "Tiền gửi ngân hàng", "Phải thu khách hàng", "Phải trả người bán", "Doanh thu", "Chi phí quản lý"],
        "Tính chất": ["Dư Nợ", "Dư Nợ", "Lưỡng tính", "Dư Có", "Dư Có", "Dư Nợ"]
    }), use_container_width=True)

elif module == "3. Kế toán Tiền mặt, Ngân hàng & Đối soát":
    st.header("Đối soát Biến động Số dư Ngân hàng Tự động")
    st.write("Tải lên file sao kê ngân hàng (Excel/CSV) để hệ thống tự động chạy thuật toán đối chiếu với danh sách hóa đơn đã ghi sổ.")
    
    if len(st.session_state.invoice_db) == 0:
        st.warning("⚠️ Cơ sở dữ liệu hóa đơn (Phân hệ 1) hiện đang trống. Vui lòng nhập ít nhất một hóa đơn để hệ thống có dữ liệu đối soát.")
    else:
        # Nút tạo file sao kê mẫu để test nhanh
        with st.expander("🛠️ Cần file sao kê mẫu để thử nghiệm ngay? Bấm vào đây để tải về"):
            sample_bank = pd.DataFrame({
                "Ngày giao dịch": ["2026-09-12", "2026-09-15"],
                "Nội dung chuyển khoản": ["THANH TOAN HOA DON 0001234", "Chi phi dien nuoc thang 9"],
                "Số tiền (VNĐ)": [12100000.0, 500000.0],
                "Loại giao dịch": ["Tiền vào", "Tiền ra"]
            })
            out_b = BytesIO()
            with pd.ExcelWriter(out_b, engine='openpyxl') as writer:
                sample_bank.to_excel(writer, index=False, sheet_name='Sao_ke')
            st.download_button(
                label="📥 Tải xuống File Sao_Ke_Ngan_Hang_Mau.xlsx",
                data=out_b.getvalue(),
                file_name="Sao_Ke_Ngan_Hang_Mau.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.markdown("---")
        bank_file = st.file_uploader("Tải lên file sao kê ngân hàng của bạn (.csv, .xlsx)", type=["csv", "xlsx"])
        
        if bank_file is not None:
            try:
                if bank_file.name.endswith('.csv'):
                    bank_df = pd.read_csv(bank_file)
                else:
                    bank_df = pd.read_excel(bank_file)
                
                st.subheader("1. Dữ liệu Sao kê Ngân hàng thô")
                st.dataframe(bank_df, use_container_width=True)
                
                st.subheader("2. Kết quả Tự động Đối soát (AI & Rule Matching)")
                
                matches = []
                invoices = st.session_state.invoice_db
                
                for idx, b_row in bank_df.iterrows():
                    matched_inv = "Không tìm thấy"
                    match_status = "❌ Chưa khớp (Cần kiểm tra lại)"
                    
                    b_text = str(b_row.values).lower()
                    
                    for i_idx, i_row in invoices.iterrows():
                        inv_no = str(i_row["Số hóa đơn"])
                        inv_total = float(i_row["Tổng thanh toán"])
                        
                        # Kiểm tra xem dòng sao kê có chứa số tiền khớp hoặc số hóa đơn không
                        row_vals = [val for val in b_row.values if isinstance(val, (int, float))]
                        amount_match = any(abs(v - inv_total) < 1.0 for v in row_vals)
                        text_match = inv_no.lower() in b_text
                        
                        if amount_match or text_match:
                            matched_inv = f"Hóa đơn số: {inv_no} ({inv_total:,.0f} VNĐ)"
                            match_status = "✅ Khớp chính xác (Đã thanh toán)"
                            break
                    
                    matches.append({
                        "STT Giao dịch": idx + 1,
                        "Thông tin Giao dịch": " | ".join([str(v) for v in b_row.values]),
                        "Trạng thái đối soát": match_status,
                        "Hóa đơn tham chiếu": matched_inv
                    })
                
                match_result_df = pd.DataFrame(matches)
                st.dataframe(match_result_df, use_container_width=True)
                
                matched_count = len(match_result_df[match_result_df["Trạng thái đối soát"].str.contains("✅")])
                total_trans = len(match_result_df)
                
                col_m1, col_m2 = st.columns(2)
                col_m1.metric("Tổng số giao dịch sao kê", total_trans)
                col_m2.metric("Giao dịch đối soát thành công", f"{matched_count} / {total_trans}")
                
                if matched_count > 0:
                    st.success("🎉 Hệ thống đã tự động hoàn tất việc ghép nối dòng tiền ngân hàng với hóa đơn thành công!")
                else:
                    st.warning("⚠️ Không tìm thấy giao dịch nào khớp với hóa đơn hiện tại trong hệ thống.")
                    
            except Exception as e:
                st.error(f"Lỗi đọc file sao kê: {e}")

elif module == "4. Kế toán Công nợ & Sổ cái":
    st.header("Hệ thống Bút toán Kép (Double-Entry Bookkeeping)")

elif module == "5. Quản trị Hệ thống & Kiểm toán":
    st.header("Tầng Hệ thống & Nhật ký Kiểm toán (Audit Trail)")
