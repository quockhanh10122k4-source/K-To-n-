import streamlit as st

st.set_page_config(
    page_title="Kế Toán Tự Động Hóa",
    page_icon="📊",
    layout="wide"
)

st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

st.write("Hệ thống quản lý và tự động hóa nghiệp vụ kế toán.")

st.markdown("---")

st.subheader("📌 CHỨC NĂNG CHÍNH")

# =========================
# NÚT CHỨNG TỪ
# =========================

if st.button("📄 CHỨNG TỪ", use_container_width=True):

    st.title("📄 QUẢN LÝ CHỨNG TỪ")

    st.success("✅ Bạn đã mở chức năng Chứng từ!")

    st.write(
        "Đây là khu vực quản lý chứng từ kế toán."
    )

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📤 Chọn chứng từ",
        type=["pdf", "jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        st.success(
            f"Đã tải lên: {uploaded_file.name}"
        )
