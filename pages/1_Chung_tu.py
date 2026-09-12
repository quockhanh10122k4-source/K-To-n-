import streamlit as st

# ==============================
# CẤU HÌNH TRANG
# ==============================

st.set_page_config(
    page_title="Chứng từ",
    page_icon="📄",
    layout="wide"
)

# ==============================
# TIÊU ĐỀ
# ==============================

st.title("📄 QUẢN LÝ CHỨNG TỪ")

st.success(
    "🎉 Bạn đã mở chức năng Chứng từ thành công!"
)

st.write(
    "Tại đây bạn có thể tải chứng từ kế toán "
    "để hệ thống kiểm tra và xử lý."
)

st.markdown("---")

# ==============================
# TẢI CHỨNG TỪ
# ==============================

st.subheader("📤 Tải chứng từ")

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

    st.markdown("### 📋 Thông tin file")

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
    # XEM ẢNH
    # ==============================

    if uploaded_file.type.startswith("image/"):

        st.markdown("---")

        st.subheader("👁️ Xem chứng từ")

        st.image(
            uploaded_file,
            caption="Chứng từ đã tải lên",
            use_container_width=True
        )

    # ==============================
    # PDF
    # ==============================

    elif uploaded_file.type == "application/pdf":

        st.markdown("---")

        st.subheader("📑 File PDF")

        st.info(
            "Đã nhận file PDF thành công. "
            "Chức năng đọc và phân tích nội dung PDF "
            "sẽ được xây dựng ở bước tiếp theo."
        )
