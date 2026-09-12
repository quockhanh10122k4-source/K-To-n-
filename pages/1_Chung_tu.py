# =========================
# NÚT CHỨNG TỪ
# =========================

if st.button("📄 CHỨNG TỪ", use_container_width=True):

    st.title("📄 QUẢN LÝ CHỨNG TỪ")

    st.success("✅ Bạn đã mở chức năng Chứng từ!")

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

        st.write("**Tên file:**", uploaded_file.name)
        st.write("**Loại file:**", uploaded_file.type)
        st.write(
            "**Dung lượng:**",
            round(uploaded_file.size / 1024, 2),
            "KB"
        )

        if uploaded_file.type.startswith("image/"):

            st.markdown("---")
            st.subheader("👁️ Xem chứng từ")

            st.image(
                uploaded_file,
                use_container_width=True
            )

        elif uploaded_file.type == "application/pdf":

            st.markdown("---")
            st.subheader("📑 Chứng từ PDF")

            st.info(
                "Đã nhận file PDF thành công."
            )
