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
# KHỞI TẠO TRẠNG THÁI
# ==============================

if "trang" not in st.session_state:
    st.session_state.trang = "home"


# ==============================
# TRANG CHỦ
# ==============================

if st.session_state.trang == "home":

    st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

    st.write(
        "Hệ thống hỗ trợ quản lý và tự động hóa nghiệp vụ kế toán."
    )

    st.markdown("---")

    st.subheader("📌 CHỨC NĂNG CHÍNH")

    if st.button(
        "📄 CHỨNG TỪ",
        use_container_width=True
    ):
        st.session_state.trang = "chung_tu"
        st.rerun()


# ==============================
# TRANG CHỨNG TỪ
# ==============================

elif st.session_state.trang == "chung_tu":

    st.title("📄 QUẢN LÝ CHỨNG TỪ")

    st.success(
        "✅ Bạn đang ở chức năng Chứng từ."
    )

    # ==============================
    # NÚT QUAY LẠI
    # ==============================

    if st.button("⬅️ Quay lại trang chủ"):
        st.session_state.trang = "home"
        st.rerun()

    st.markdown("---")

    # ==============================
    # TẢI CHỨNG TỪ
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
    # SAU KHI TẢI FILE
    # ==============================

    if uploaded_file is not None:

        st.success(
            f"✅ Đã tải lên: {uploaded_file.name}"
        )

        st.markdown("---")

        st.subheader("📋 THÔNG TIN FILE")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Tên file**")
            st.write(uploaded_file.name)

        with col2:
            st.write("**Loại file**")
            st.write(uploaded_file.type)

        with col3:
            st.write("**Dung lượng**")
            st.write(
                f"{uploaded_file.size / 1024:.2f} KB"
            )

        # ==============================
        # ẢNH
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
        # PDF
        # ==============================

        elif uploaded_file.type == "application/pdf":

            st.markdown("---")

            st.subheader("📑 CHỨNG TỪ PDF")

            st.info(
                "✅ Hệ thống đã nhận file PDF thành công."
            )
