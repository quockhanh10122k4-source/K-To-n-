```python
import streamlit as st

st.set_page_config(
    page_title="Kế Toán Tự Động Hóa",
    page_icon="📊"
)

st.title("📊 HỆ THỐNG KẾ TOÁN TỰ ĐỘNG HÓA")

st.write("Hệ thống quản lý kế toán.")

st.markdown("---")

st.header("📌 Chức năng")

# Chứng từ
st.subheader("📄 Chứng từ")
st.write("Quản lý và tải chứng từ.")

if st.button("📄 Mở Chứng từ"):
    st.header("📄 QUẢN LÝ CHỨNG TỪ")

    st.success("🎉 Chứng từ đã mở thành công!")

    file = st.file_uploader(
        "📤 Chọn chứng từ",
        type=["pdf", "jpg", "jpeg", "png"]
    )

    if file is not None:

        st.success(
            "Đã tải lên: " + file.name
        )

        st.write(
            "Loại file:",
            file.type
        )

        st.write(
            "Dung lượng:",
            round(file.size / 1024, 2),
            "KB"
        )

        if file.type.startswith("image/"):
            st.image(
                file,
                caption="Chứng từ",
                use_container_width=True
            )

# Các chức năng khác
st.markdown("---")

st.subheader("🧾 Hóa đơn")
st.info("Đang xây dựng.")

st.subheader("🏦 Ngân hàng")
st.info("Đang xây dựng.")

st.subheader("📒 Công nợ")
st.info("Đang xây dựng.")

st.subheader("📚 Hệ thống tài khoản")
st.info("Đang xây dựng.")

st.subheader("📊 Báo cáo")
st.info("Đang xây dựng.")
```
