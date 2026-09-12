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
# TRANG CHỦ
# ==============================

st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

st.write(
    "Hệ thống hỗ trợ quản lý và tự động hóa nghiệp vụ kế toán."
)

st.markdown("---")

st.subheader("📌 CHỨC NĂNG CHÍNH")

# ==============================
# NÚT CHỨNG TỪ
# ==============================

if st.button(
    "📄 CHỨNG TỪ",
    use_container_width=True
):

    st.title("📄 QUẢN LÝ CHỨNG TỪ")

    st.success(
        "✅ Bạn đã mở chức năng Chứng từ!"
    )

    st.write(
        "Tải chứng từ gốc lên hệ thống để kiểm tra và xử lý."
    )

    st.markdown("---")

    # ==============================
    # UPLOAD FILE
    # ==============================

    st.subheader("📤 TẢI CHỨNG TỪ")

    uploaded_file = st.file_uploader(
        "Chọn file chứng từ",
        type=[
            "pdf",
            "jpg",
            "jpeg",
            "png"
        ]
    )

    # ==============================
    # XỬ LÝ FILE
    # ==============================

    if uploaded_file is not None:

        st.success(
            f"✅ Đã tải lên: {uploaded_file.name}"
        )

        st.markdown("---")

        st.subheader("📋 THÔNG TIN CHỨNG TỪ")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write("**Tên file**")

            st.write(
                uploaded_file.name
            )

        with col2:

            st.write("**Loại file**")

            st.write(
                uploaded_file.type
            )

        with col3:

            st.write("**Dung lượng**")

            st.write(
                f"{uploaded_file.size / 1024:.2f} KB"
            )

        # ==============================
        # NẾU LÀ ẢNH
        # ==============================

        if uploaded_file.type.startswith("image/"):

            st.markdown("---")

            st.subheader("👁️ XEM CHỨNG TỪ")

            st.image(
                uploaded_file,
                caption="Chứng từ gốc",
                use_container_width=True
            )

        # ==============================
        # NẾU LÀ PDF
        # ==============================

        elif uploaded_file.type == "application/pdf":

            st.markdown("---")

            st.subheader("📑 CHỨNG TỪ PDF")

            st.info(
                "✅ Hệ thống đã nhận file PDF thành công."
            )

            st.write(
                "Chức năng đọc nội dung PDF sẽ được "
                "xây dựng ở bước tiếp theo."
            )
