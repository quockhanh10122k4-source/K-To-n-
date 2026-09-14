import streamlit as st
import pandas as pd
import easyocr
import io
import re
import numpy as np
import fitz

from PIL import Image


# =========================================================
# CẤU HÌNH
# =========================================================

st.set_page_config(
    page_title="Chứng từ - Kế Toán Tự Động Hóa",
    page_icon="📄",
    layout="wide"
)

st.title("📄 QUẢN LÝ CHỨNG TỪ")

st.write(
    "Tải chứng từ gốc → đọc OCR → kiểm tra dữ liệu → xuất Excel"
)


# =========================================================
# SESSION STATE
# =========================================================

if "documents" not in st.session_state:
    st.session_state.documents = []

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None


# =========================================================
# KHỞI TẠO OCR
# =========================================================

@st.cache_resource
def load_ocr():

    reader = easyocr.Reader(
        ["vi", "en"],
        gpu=False,
        verbose=False
    )

    return reader


# =========================================================
# PDF -> ẢNH
# =========================================================

def pdf_to_images(file_bytes):

    images = []

    pdf = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    for page in pdf:

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        images.append(image)

    pdf.close()

    return images


# =========================================================
# OCR ẢNH
# =========================================================

def read_image(reader, image):

    # PIL Image -> NumPy
    image_array = np.array(image)

    result = reader.readtext(
        image_array,
        detail=1,
        paragraph=False
    )

    lines = []

    for item in result:

        if len(item) >= 2:

            text = str(item[1]).strip()

            if text:
                lines.append(text)

    return "\n".join(lines)


# =========================================================
# TÌM NGÀY
# =========================================================

def extract_date(text):

    patterns = [

        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",

        r"Ngày\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",

        r"Date\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            if match.lastindex:
                return match.group(1)

            return match.group(0)

    return ""


# =========================================================
# TÌM MST
# =========================================================

def extract_tax_code(text):

    patterns = [

        r"MST\s*[:\-]?\s*(\d{10,14})",

        r"Mã số thuế\s*[:\-]?\s*(\d{10,14})",

        r"Tax Code\s*[:\-]?\s*(\d{10,14})"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


# =========================================================
# TÌM SỐ CHỨNG TỪ / SỐ HÓA ĐƠN
# =========================================================

def extract_document_number(text):

    patterns = [

        r"Số\s*[:\-]?\s*([A-Z0-9\/\-]+)",

        r"No\.\s*[:\-]?\s*([A-Z0-9\/\-]+)",

        r"Số hóa đơn\s*[:\-]?\s*([A-Z0-9\/\-]+)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


# =========================================================
# TÌM TỔNG TIỀN
# =========================================================

def extract_total(text):

    patterns = [

        r"Tổng tiền thanh toán\s*[:\-]?\s*([\d\.,]+)",

        r"Tổng cộng tiền thanh toán\s*[:\-]?\s*([\d\.,]+)",

        r"Tổng cộng\s*[:\-]?\s*([\d\.,]+)",

        r"Total\s*[:\-]?\s*([\d\.,]+)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


# =========================================================
# TÌM VAT
# =========================================================

def extract_vat(text):

    patterns = [

        r"Tiền thuế GTGT\s*[:\-]?\s*([\d\.,]+)",

        r"Tiền thuế\s*[:\-]?\s*([\d\.,]+)",

        r"VAT\s*[:\-]?\s*([\d\.,]+)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


# =========================================================
# TÌM NGƯỜI BÁN
# =========================================================

def extract_seller(text):

    lines = text.splitlines()

    for i, line in enumerate(lines):

        clean = line.strip()

        if (
            "Người bán" in clean
            or "NGƯỜI BÁN" in clean
        ):

            # Lấy dòng tiếp theo
            if i + 1 < len(lines):

                next_line = lines[i + 1].strip()

                if next_line:
                    return next_line

    return ""


# =========================================================
# TẠO DỮ LIỆU CHỨNG TỪ
# =========================================================

def create_record(
    file_name,
    file_type,
    raw_text,
    file_bytes,
    preview_image
):

    return {

        "STT": 0,

        "Tên file": file_name,

        "Loại file": file_type,

        "Ngày chứng từ":
            extract_date(raw_text),

        "Số chứng từ":
            extract_document_number(raw_text),

        "Mã số thuế":
            extract_tax_code(raw_text),

        "Người bán":
            extract_seller(raw_text),

        "Tiền hàng": "",

        "Thuế suất VAT": "",

        "Tiền VAT":
            extract_vat(raw_text),

        "Tổng tiền":
            extract_total(raw_text),

        "Nội dung": "",

        "Trạng thái":
            "⚠️ Chưa kiểm tra",

        "_raw_text":
            raw_text,

        "_file_bytes":
            file_bytes,

        "_preview_image":
            preview_image
    }


# =========================================================
# 1. TẢI CHỨNG TỪ
# =========================================================

st.markdown("---")

st.subheader("1️⃣ TẢI CHỨNG TỪ GỐC")

uploaded_files = st.file_uploader(

    "📤 Chọn một hoặc nhiều chứng từ",

    type=[
        "jpg",
        "jpeg",
        "png",
        "pdf"
    ],

    accept_multiple_files=True
)


# =========================================================
# HIỂN THỊ FILE ĐÃ CHỌN
# =========================================================

if uploaded_files:

    st.success(
        f"📁 Đã chọn {len(uploaded_files)} chứng từ."
    )

    for file in uploaded_files:

        st.write(
            f"📄 **{file.name}** "
            f"— {round(file.size / 1024, 1)} KB"
        )


# =========================================================
# 2. ĐỌC CHỨNG TỪ
# =========================================================

if uploaded_files:

    st.markdown("---")

    if st.button(
        "🔍 ĐỌC & GHI DỮ LIỆU CHỨNG TỪ",
        type="primary",
        use_container_width=True
    ):

        # Xóa kết quả cũ
        st.session_state.documents = []

        # ---------------------------------------------
        # KHỞI ĐỘNG OCR
        # ---------------------------------------------

        try:

            with st.spinner(
                "⏳ Đang khởi động hệ thống OCR..."
            ):

                reader = load_ocr()

        except Exception as e:

            st.error(
                "❌ Không thể khởi động OCR."
            )

            st.exception(e)

            st.stop()


        # ---------------------------------------------
        # TIẾN TRÌNH
        # ---------------------------------------------

        progress = st.progress(0)

        status_box = st.empty()

        total = len(uploaded_files)


        # ---------------------------------------------
        # ĐỌC TỪNG FILE
        # ---------------------------------------------

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            file_name = uploaded_file.name

            status_box.info(
                f"🔍 Đang đọc "
                f"{index + 1}/{total}: {file_name}"
            )

            try:

                file_bytes = uploaded_file.getvalue()

                file_type = uploaded_file.type


                # =====================================
                # ẢNH
                # =====================================

                if file_type.startswith("image/"):

                    image = Image.open(
                        io.BytesIO(file_bytes)
                    ).convert("RGB")

                    raw_text = read_image(
                        reader,
                        image
                    )

                    preview_image = image


                # =====================================
                # PDF
                # =====================================

                elif file_type == "application/pdf":

                    images = pdf_to_images(
                        file_bytes
                    )

                    all_text = []

                    for page_number, image in enumerate(
                        images
                    ):

                        page_text = read_image(
                            reader,
                            image
                        )

                        if page_text:

                            all_text.append(
                                f"--- Trang {page_number + 1} ---\n"
                                f"{page_text}"
                            )

                    raw_text = "\n\n".join(
                        all_text
                    )

                    if images:

                        preview_image = images[0]

                    else:

                        preview_image = None


                else:

                    raw_text = ""

                    preview_image = None


                # =====================================
                # TẠO RECORD
                # =====================================

                record = create_record(

                    file_name,

                    file_type,

                    raw_text,

                    file_bytes,

                    preview_image
                )

                record["STT"] = index + 1


                # =====================================
                # LƯU
                # =====================================

                st.session_state.documents.append(
                    record
                )


            except Exception as e:

                st.error(
                    f"❌ Lỗi khi đọc {file_name}"
                )

                st.exception(e)


            progress.progress(
                (index + 1) / total
            )


        status_box.success(
            f"✅ Đã xử lý xong {len(st.session_state.documents)} "
            f"/ {total} chứng từ."
        )


# =========================================================
# 3. KẾT QUẢ
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    st.subheader(
        "2️⃣ DỮ LIỆU CHỨNG TỪ"
    )

    st.info(
        "Mỗi chứng từ = 1 dòng dữ liệu. "
        "Hãy kiểm tra dữ liệu và ảnh gốc trước khi xuất Excel."
    )


    # =====================================================
    # BẢNG TỔNG QUAN
    # =====================================================

    table_data = []

    for document in st.session_state.documents:

        table_data.append({

            "STT":
                document["STT"],

            "Tên file":
                document["Tên file"],

            "Ngày":
                document["Ngày chứng từ"],

            "Số CT":
                document["Số chứng từ"],

            "MST":
                document["Mã số thuế"],

            "Người bán":
                document["Người bán"],

            "Tiền VAT":
                document["Tiền VAT"],

            "Tổng tiền":
                document["Tổng tiền"],

            "Trạng thái":
                document["Trạng thái"]

        })


    df = pd.DataFrame(table_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # TỪNG CHỨNG TỪ
    # =====================================================

    st.markdown("---")

    st.subheader(
        "3️⃣ KIỂM TRA TỪNG CHỨNG TỪ"
    )


    for index, document in enumerate(
        st.session_state.documents
    ):

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [0.6, 5, 2]
            )

            with col1:

                st.markdown(
                    f"### {document['STT']}"
                )

            with col2:

                st.markdown(
                    f"**📄 {document['Tên file']}**"
                )

                st.write(
                    f"Ngày: "
                    f"{document['Ngày chứng từ'] or '❓ Chưa đọc được'}"
                )

                st.write(
                    f"MST: "
                    f"{document['Mã số thuế'] or '❓ Chưa đọc được'}"
                )

                st.write(
                    f"Tổng tiền: "
                    f"{document['Tổng tiền'] or '❓ Chưa đọc được'}"
                )

            with col3:

                if st.button(
                    "👁️ XEM CHỨNG TỪ GỐC",
                    key=f"view_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_document = index

            # =========================================
            # CHỈNH SỬA
            # =========================================

            with st.expander(
                "✏️ Kiểm tra / chỉnh sửa dữ liệu"
            ):

                col_a, col_b = st.columns(2)

                with col_a:

                    document["Ngày chứng từ"] = st.text_input(
                        "Ngày chứng từ",
                        document["Ngày chứng từ"],
                        key=f"date_{index}"
                    )

                    document["Số chứng từ"] = st.text_input(
                        "Số chứng từ",
                        document["Số chứng từ"],
                        key=f"number_{index}"
                    )

                    document["Mã số thuế"] = st.text_input(
                        "Mã số thuế",
                        document["Mã số thuế"],
                        key=f"tax_{index}"
                    )

                    document["Người bán"] = st.text_input(
                        "Người bán",
                        document["Người bán"],
                        key=f"seller_{index}"
                    )

                with col_b:

                    document["Tiền hàng"] = st.text_input(
                        "Tiền hàng",
                        document["Tiền hàng"],
                        key=f"amount_{index}"
                    )

                    document["Thuế suất VAT"] = st.text_input(
                        "Thuế suất VAT",
                        document["Thuế suất VAT"],
                        key=f"rate_{index}"
                    )

                    document["Tiền VAT"] = st.text_input(
                        "Tiền VAT",
                        document["Tiền VAT"],
                        key=f"vat_{index}"
                    )

                    document["Tổng tiền"] = st.text_input(
                        "Tổng tiền",
                        document["Tổng tiền"],
                        key=f"total_{index}"
                    )

                document["Nội dung"] = st.text_input(
                    "Nội dung chứng từ",
                    document["Nội dung"],
                    key=f"content_{index}"
                )

                document["Trạng thái"] = st.selectbox(
                    "Trạng thái kiểm tra",
                    [
                        "⚠️ Chưa kiểm tra",
                        "✅ Đã kiểm tra",
                        "❌ Có sai lệch"
                    ],
                    key=f"status_{index}"
                )


# =========================================================
# 4. XEM ẢNH GỐC + OCR
# =========================================================

if st.session_state.selected_document is not None:

    selected = st.session_state.selected_document

    if selected < len(
        st.session_state.documents
    ):

        document = st.session_state.documents[selected]

        st.markdown("---")

        st.subheader(
            f"👁️ KIỂM TRA: {document['Tên file']}"
        )

        col_image, col_data = st.columns(
            [1.2, 1]
        )


        # =============================================
        # ẢNH GỐC
        # =============================================

        with col_image:

            st.markdown(
                "### 📷 CHỨNG TỪ GỐC"
            )

            if document["_preview_image"] is not None:

                st.image(
                    document["_preview_image"],
                    use_container_width=True
                )

            else:

                st.warning(
                    "Không có ảnh xem trước."
                )


        # =============================================
        # DỮ LIỆU
        # =============================================

        with col_data:

            st.markdown(
                "### 📝 DỮ LIỆU ĐÃ ĐỌC"
            )

            st.write(
                f"**Ngày:** "
                f"{document['Ngày chứng từ']}"
            )

            st.write(
                f"**Số chứng từ:** "
                f"{document['Số chứng từ']}"
            )

            st.write(
                f"**MST:** "
                f"{document['Mã số thuế']}"
            )

            st.write(
                f"**Người bán:** "
                f"{document['Người bán']}"
            )

            st.write(
                f"**Tiền hàng:** "
                f"{document['Tiền hàng']}"
            )

            st.write(
                f"**VAT:** "
                f"{document['Tiền VAT']}"
            )

            st.write(
                f"**Tổng tiền:** "
                f"{document['Tổng tiền']}"
            )

            st.write(
                f"**Trạng thái:** "
                f"{document['Trạng thái']}"
            )


        # =============================================
        # OCR THÔ
        # =============================================

        st.markdown("---")

        st.markdown(
            "### 🔍 TOÀN BỘ NỘI DUNG OCR"
        )

        if document["_raw_text"]:

            st.text_area(
                "Kết quả OCR",
                document["_raw_text"],
                height=350,
                key=f"ocr_text_{selected}"
            )

        else:

            st.error(
                "❌ OCR không đọc được chữ từ chứng từ này."
            )


        if st.button(
            "❌ Đóng chứng từ",
            key="close_document",
            use_container_width=True
        ):

            st.session_state.selected_document = None

            st.rerun()


# =========================================================
# 5. KIỂM TRA TRƯỚC KHI XUẤT
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    st.subheader(
        "4️⃣ KIỂM TRA TRƯỚC KHI XUẤT EXCEL"
    )

    unchecked = [

        document

        for document
        in st.session_state.documents

        if document["Trạng thái"]
        != "✅ Đã kiểm tra"

    ]


    if unchecked:

        st.warning(
            f"⚠️ Còn {len(unchecked)} chứng từ "
            "chưa được xác nhận."
        )

    else:

        st.success(
            "✅ Tất cả chứng từ đã được kiểm tra."
        )


    # =====================================================
    # DỮ LIỆU EXCEL
    # =====================================================

    export_data = []

    for document in st.session_state.documents:

        export_data.append({

            "STT":
                document["STT"],

            "Tên file":
                document["Tên file"],

            "Ngày chứng từ":
                document["Ngày chứng từ"],

            "Số chứng từ":
                document["Số chứng từ"],

            "Mã số thuế":
                document["Mã số thuế"],

            "Người bán":
                document["Người bán"],

            "Tiền hàng":
                document["Tiền hàng"],

            "Thuế suất VAT":
                document["Thuế suất VAT"],

            "Tiền VAT":
                document["Tiền VAT"],

            "Tổng tiền":
                document["Tổng tiền"],

            "Nội dung":
                document["Nội dung"],

            "Trạng thái":
                document["Trạng thái"]

        })


    df_export = pd.DataFrame(
        export_data
    )


    st.dataframe(
        df_export,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 6. XUẤT EXCEL
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    st.subheader(
        "5️⃣ XUẤT EXCEL"
    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_export.to_excel(
            writer,
            index=False,
            sheet_name="Chung_tu"
        )


    excel_data = output.getvalue()


    st.download_button(

        label="📥 XUẤT EXCEL",

        data=excel_data,

        file_name="Du_lieu_chung_tu.xlsx",

        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),

        use_container_width=True
    )


# =========================================================
# 7. XÓA DỮ LIỆU
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    if st.button(
        "🗑️ XÓA TOÀN BỘ CHỨNG TỪ",
        use_container_width=True
    ):

        st.session_state.documents = []

        st.session_state.selected_document = None

        st.rerun()
