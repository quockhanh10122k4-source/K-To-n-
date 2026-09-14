import streamlit as st
import pandas as pd
import easyocr
import io
import re
import fitz

from PIL import Image


# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Chứng từ - Kế Toán Tự Động Hóa",
    page_icon="📄",
    layout="wide"
)

st.title("📄 QUẢN LÝ CHỨNG TỪ")

st.write(
    "Tải lên nhiều chứng từ gốc → đọc dữ liệu → kiểm tra → xuất Excel."
)


# =========================================================
# KHỞI TẠO SESSION STATE
# =========================================================

if "documents" not in st.session_state:
    st.session_state.documents = []

if "ocr_reader" not in st.session_state:
    st.session_state.ocr_reader = None

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None


# =========================================================
# HÀM KHỞI TẠO OCR
# =========================================================

@st.cache_resource
def load_ocr():

    reader = easyocr.Reader(
        ["vi", "en"],
        gpu=False
    )

    return reader


# =========================================================
# HÀM CHUYỂN FILE PDF THÀNH ẢNH
# =========================================================

def pdf_to_images(file_bytes):

    images = []

    pdf = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    for page in pdf:

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        img = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        images.append(img)

    pdf.close()

    return images


# =========================================================
# HÀM ĐỌC ẢNH
# =========================================================

def read_image_ocr(reader, image):

    result = reader.readtext(
        image,
        detail=0,
        paragraph=True
    )

    return "\n".join(result)


# =========================================================
# HÀM LẤY NGÀY
# =========================================================

def extract_date(text):

    patterns = [

        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",

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
# HÀM LẤY MÃ SỐ THUẾ
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
# HÀM LẤY SỐ CHỨNG TỪ / SỐ HÓA ĐƠN
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
# HÀM LẤY TỔNG TIỀN
# =========================================================

def extract_total(text):

    patterns = [

        r"Tổng tiền thanh toán\s*[:\-]?\s*([\d\.,]+)",

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
# HÀM LẤY TIỀN THUẾ VAT
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
# HÀM LẤY TÊN NGƯỜI BÁN
# =========================================================

def extract_seller(text):

    lines = text.splitlines()

    for i, line in enumerate(lines):

        clean = line.strip()

        if (
            "Người bán" in clean
            or "NGƯỜI BÁN" in clean
        ):

            if i + 1 < len(lines):

                next_line = lines[i + 1].strip()

                if next_line:
                    return next_line

    return ""


# =========================================================
# HÀM TẠO DÒNG DỮ LIỆU
# =========================================================

def create_document_record(
    file_name,
    file_type,
    raw_text,
    file_bytes,
    preview_image
):

    record = {

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

        "Tiền hàng":
            "",

        "VAT":
            extract_vat(raw_text),

        "Tổng tiền":
            extract_total(raw_text),

        "Nội dung":
            "",

        "Trạng thái":
            "⚠️ Cần kiểm tra",

        "_file_bytes":
            file_bytes,

        "_preview_image":
            preview_image,

        "_raw_text":
            raw_text

    }

    return record


# =========================================================
# PHẦN 1 - TẢI CHỨNG TỪ
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
        f"Đã nhận {len(uploaded_files)} chứng từ."
    )

    for file in uploaded_files:

        st.write(
            f"📄 {file.name} — "
            f"{round(file.size / 1024, 1)} KB"
        )


# =========================================================
# NÚT ĐỌC TẤT CẢ CHỨNG TỪ
# =========================================================

if uploaded_files:

    st.markdown("---")

    if st.button(
        "🔍 ĐỌC & GHI DỮ LIỆU TẤT CẢ CHỨNG TỪ",
        use_container_width=True
    ):

        with st.spinner(
            "Đang khởi động hệ thống OCR..."
        ):

            reader = load_ocr()

        st.session_state.documents = []

        progress = st.progress(0)

        total_files = len(uploaded_files)

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            try:

                file_bytes = uploaded_file.getvalue()

                file_name = uploaded_file.name

                file_type = uploaded_file.type


                # -----------------------------------------
                # XỬ LÝ ẢNH
                # -----------------------------------------

                if file_type.startswith("image/"):

                    image = Image.open(
                        io.BytesIO(file_bytes)
                    ).convert("RGB")

                    raw_text = read_image_ocr(
                        reader,
                        image
                    )

                    preview_image = image


                # -----------------------------------------
                # XỬ LÝ PDF
                # -----------------------------------------

                elif file_type == "application/pdf":

                    images = pdf_to_images(
                        file_bytes
                    )

                    all_text = []

                    for image in images:

                        page_text = read_image_ocr(
                            reader,
                            image
                        )

                        all_text.append(
                            page_text
                        )

                    raw_text = "\n\n".join(
                        all_text
                    )

                    preview_image = images[0]


                else:

                    raw_text = ""

                    preview_image = None


                # -----------------------------------------
                # TẠO DÒNG DỮ LIỆU
                # -----------------------------------------

                record = create_document_record(

                    file_name,

                    file_type,

                    raw_text,

                    file_bytes,

                    preview_image

                )

                st.session_state.documents.append(
                    record
                )


            except Exception as e:

                st.error(
                    f"Lỗi khi đọc {uploaded_file.name}: {e}"
                )


            progress.progress(
                (index + 1) / total_files
            )


        st.success(
            f"✅ Đã đọc xong {len(st.session_state.documents)} chứng từ."
        )

        st.rerun()


# =========================================================
# PHẦN 2 - DỮ LIỆU ĐÃ ĐỌC
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    st.subheader(
        "2️⃣ DỮ LIỆU CHỨNG TỪ ĐÃ ĐỌC"
    )

    st.info(
        "Mỗi chứng từ tương ứng với một dòng. "
        "Bạn có thể xem ảnh gốc trước khi xuất Excel."
    )


    # =====================================================
    # HIỂN THỊ TỪNG DÒNG
    # =====================================================

    for index, document in enumerate(
        st.session_state.documents
    ):

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [0.5, 3, 2, 1.5]
            )

            with col1:

                st.write(
                    f"**{index + 1}**"
                )

            with col2:

                st.write(
                    f"📄 **{document['Tên file']}**"
                )

            with col3:

                st.write(
                    f"Ngày: {document['Ngày chứng từ'] or 'Chưa đọc được'}"
                )

                st.write(
                    f"MST: {document['Mã số thuế'] or 'Chưa đọc được'}"
                )

            with col4:

                if st.button(
                    "👁️ Xem ảnh",
                    key=f"view_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_document = index


            # =================================================
            # KHU VỰC SỬA DỮ LIỆU
            # =================================================

            with st.expander(
                "✏️ Kiểm tra / chỉnh sửa dữ liệu"
            ):

                c1, c2 = st.columns(2)

                with c1:

                    document["Ngày chứng từ"] = st.text_input(
                        "Ngày chứng từ",
                        value=document["Ngày chứng từ"],
                        key=f"date_{index}"
                    )

                    document["Số chứng từ"] = st.text_input(
                        "Số chứng từ",
                        value=document["Số chứng từ"],
                        key=f"number_{index}"
                    )

                    document["Mã số thuế"] = st.text_input(
                        "Mã số thuế",
                        value=document["Mã số thuế"],
                        key=f"tax_{index}"
                    )

                    document["Người bán"] = st.text_input(
                        "Người bán",
                        value=document["Người bán"],
                        key=f"seller_{index}"
                    )

                with c2:

                    document["Tiền hàng"] = st.text_input(
                        "Tiền hàng",
                        value=document["Tiền hàng"],
                        key=f"amount_{index}"
                    )

                    document["VAT"] = st.text_input(
                        "VAT",
                        value=document["VAT"],
                        key=f"vat_{index}"
                    )

                    document["Tổng tiền"] = st.text_input(
                        "Tổng tiền",
                        value=document["Tổng tiền"],
                        key=f"total_{index}"
                    )

                    document["Nội dung"] = st.text_input(
                        "Nội dung",
                        value=document["Nội dung"],
                        key=f"content_{index}"
                    )


                document["Trạng thái"] = st.selectbox(
                    "Trạng thái kiểm tra",
                    [
                        "⚠️ Cần kiểm tra",
                        "✅ Đã kiểm tra",
                        "❌ Có sai lệch"
                    ],
                    index=[
                        "⚠️ Cần kiểm tra",
                        "✅ Đã kiểm tra",
                        "❌ Có sai lệch"
                    ].index(
                        document["Trạng thái"]
                    ),
                    key=f"status_{index}"
                )


# =========================================================
# PHẦN 3 - XEM ẢNH CHỨNG TỪ GỐC
# =========================================================

if (
    st.session_state.selected_document is not None
    and
    st.session_state.selected_document
    <
    len(st.session_state.documents)
):

    index = st.session_state.selected_document

    document = st.session_state.documents[index]

    st.markdown("---")

    st.subheader(
        f"👁️ KIỂM TRA CHỨNG TỪ: {document['Tên file']}"
    )

    col_image, col_text = st.columns(
        [1.2, 1]
    )

    with col_image:

        st.markdown("### 📷 Chứng từ gốc")

        if document["_preview_image"] is not None:

            st.image(
                document["_preview_image"],
                use_container_width=True
            )


    with col_text:

        st.markdown("### 📝 Dữ liệu hệ thống đọc được")

        st.write(
            f"**Ngày:** {document['Ngày chứng từ']}"
        )

        st.write(
            f"**Số chứng từ:** {document['Số chứng từ']}"
        )

        st.write(
            f"**Mã số thuế:** {document['Mã số thuế']}"
        )

        st.write(
            f"**Người bán:** {document['Người bán']}"
        )

        st.write(
            f"**Tiền hàng:** {document['Tiền hàng']}"
        )

        st.write(
            f"**VAT:** {document['VAT']}"
        )

        st.write(
            f"**Tổng tiền:** {document['Tổng tiền']}"
        )

        st.write(
            f"**Nội dung:** {document['Nội dung']}"
        )

        st.markdown("---")

        st.markdown("### 🔍 OCR thô")

        st.text_area(
            "Nội dung OCR",
            document["_raw_text"],
            height=250,
            key=f"raw_{index}"
        )


    if st.button(
        "❌ Đóng xem chứng từ",
        key="close_document"
    ):

        st.session_state.selected_document = None

        st.rerun()


# =========================================================
# PHẦN 4 - KIỂM TRA TRƯỚC KHI XUẤT
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    st.subheader(
        "3️⃣ KIỂM TRA TRƯỚC KHI XUẤT EXCEL"
    )

    export_data = []

    for index, document in enumerate(
        st.session_state.documents
    ):

        export_data.append({

            "STT":
                index + 1,

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

            "VAT":
                document["VAT"],

            "Tổng tiền":
                document["Tổng tiền"],

            "Nội dung":
                document["Nội dung"],

            "Trạng thái":
                document["Trạng thái"]

        })


    df = pd.DataFrame(export_data)


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # KIỂM TRA ĐÃ DUYỆT HẾT CHƯA
    # =====================================================

    not_checked = [

        d for d in st.session_state.documents

        if d["Trạng thái"] != "✅ Đã kiểm tra"

    ]


    if not_checked:

        st.warning(
            f"⚠️ Còn {len(not_checked)} chứng từ "
            "chưa được đánh dấu 'Đã kiểm tra'."
        )

    else:

        st.success(
            "✅ Tất cả chứng từ đã được kiểm tra."
        )


# =========================================================
# PHẦN 5 - XUẤT EXCEL
# =========================================================

if st.session_state.documents:

    st.markdown("---")

    st.subheader(
        "4️⃣ XUẤT DỮ LIỆU RA EXCEL"
    )


    # -----------------------------------------------------
    # TẠO FILE EXCEL
    # -----------------------------------------------------

    output = io.BytesIO()

    export_data = []

    for index, document in enumerate(
        st.session_state.documents
    ):

        export_data.append({

            "STT":
                index + 1,

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

            "VAT":
                document["VAT"],

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


    # -----------------------------------------------------
    # NÚT DOWNLOAD
    # -----------------------------------------------------

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
# XÓA TOÀN BỘ DỮ LIỆU
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
