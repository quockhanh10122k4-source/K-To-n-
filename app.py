```python
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
# TIÊU ĐỀ
# ==============================

st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

st.write(
    "Hệ thống quản lý và tự động hóa nghiệp vụ kế toán."
)

st.markdown("---")

# ==============================
# CHỨC NĂNG
# ==============================

st.subheader("📌 CÁC CHỨC NĂNG")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄 Chứng từ")
    st.write("Tải và kiểm tra chứng từ.")

    if st.button(
        "📄 Mở Chứng từ",
        key="chung_tu",
        use_container_width=True
    ):
        st.session_state["trang"] = "chung_tu"


with col2:
    st.markdown("### 🧾 Hóa đơn")
    st.write("Đang xây dựng.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )


with col3:
    st.markdown("### 🏦 Ngân hàng")
    st.write("Đang xây dựng.")

    st.button(
        "🔒 Chưa mở",
        disabled=True,
        use_container_width=True
    )


# ==============================
# TRANG CHỨNG TỪ
# ==============================

if st.session_state.get("trang") == "chung_tu":

    st.markdown("---")

    st.title("📄 QUẢN LÝ CHỨNG TỪ")

    st.success(
        "🎉 Đã mở chức năng Chứng từ thành công!"
    )

    st.write(
        "Tại đây bạn có thể tải chứng từ kế toán."
    )

    st.markdown("---")

    st.subheader("📤 Tải chứng từ")

    uploaded_file = st.file_uploader(
        "Chọn file chứng từ",
        type=["pdf", "jpg", "jpeg", "png"]
    )

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

        # Hiển thị ảnh
        if uploaded_file.type.startswith("image/"):

            st.markdown("---")

            st.subheader("👁️ Xem chứng từ")

            st.image(
                uploaded_file,
                caption="Chứng từ",
                use_container_width=True
            )

        # PDF
        elif uploaded_file.type == "application/pdf":

            st.markdown("---")

            st.subheader("📑 Chứng từ PDF")

            st.info(
                "Đã nhận file PDF thành công."
            )

    st.markdown("---")

    if st.button("⬅️ Quay về trang chủ"):
        st.session_state["trang"] = "home"
        st.rerun()
```
