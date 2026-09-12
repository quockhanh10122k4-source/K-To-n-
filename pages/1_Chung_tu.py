import streamlit as st

st.set_page_config(
    page_title="Chứng từ",
    page_icon="📄",
    layout="wide"
)

st.title("📄 QUẢN LÝ CHỨNG TỪ")

st.success("🎉 Bạn đã chuyển sang trang Chứng từ thành công!")

st.write(
    "Đây là trang riêng dành cho chức năng quản lý chứng từ."
)

st.markdown("---")

st.subheader("📤 Tải chứng từ")

uploaded_file = st.file_uploader(
    "Chọn chứng từ",
    type=["pdf", "jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    st.success(
        f"Đã tải lên: {uploaded_file.name}"
    )

    st.write(
        f"Loại file: {uploaded_file.type}"
    )

    st.write(
        f"Dung lượng: {uploaded_file.size / 1024:.2f} KB"
    )

    if uploaded_file.type.startswith("image/"):

        st.image(
            uploaded_file,
            caption="Chứng từ",
            use_container_width=True
        )
