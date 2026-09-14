import streamlit as st
import pandas as pd
import easyocr
import io
import re
import numpy as np
import fitz

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


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
    "Tải chứng từ gốc → xử lý ảnh → OCR nhiều bước → "
    "phân tích dữ liệu → kiểm tra → xuất Excel"
)


# =========================================================
# SESSION STATE
# =========================================================

if "documents" not in st.session_state:
    st.session_state.documents = []

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None


# =========================================================
# OCR
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
# TIỀN XỬ LÝ ẢNH
# =========================================================

def preprocess_image(image):
    """
    Tăng chất lượng ảnh trước khi OCR.
    """

    image = image.convert("RGB")

    # Tăng kích thước
    width, height = image.size

    scale = 2

    image = image.resize(
        (width * scale, height * scale),
        Image.Resampling.LANCZOS
    )

    # Tăng tương phản
    image = ImageEnhance.Contrast(image).enhance(1.5)

    # Tăng độ nét
    image = ImageEnhance.Sharpness(image).enhance(1.5)

    # Khử nhiễu nhẹ
    image = image.filter(
        ImageFilter.MedianFilter(size=3)
    )

    return image


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
            matrix=fitz.Matrix(3, 3),
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
# OCR CHI TIẾT
# =========================================================

def read_image_detail(reader, image):

    image_array = np.array(image)

    result = reader.readtext(
        image_array,
        detail=1,
        paragraph=False,
        text_threshold=0.4,
        low_text=0.2,
        link_threshold=0.2,
        mag_ratio=1.5
    )

    data = []

    for item in result:

        if len(item) < 3:
            continue

        box = item[0]
        text = str(item[1]).strip()
        confidence = float(item[2])

        if not text:
            continue

        xs = [point[0] for point in box]
        ys = [point[1] for point in box]

        x1 = min(xs)
        y1 = min(ys)
        x2 = max(xs)
        y2 = max(ys)

        data.append({
            "text": text,
            "confidence": confidence,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "center_x": (x1 + x2) / 2,
            "center_y": (y1 + y2) / 2
        })

    return data


# =========================================================
# SẮP XẾP OCR THEO DÒNG
# =========================================================

def sort_ocr_data(data):

    if not data:
        return []

    data = sorted(
        data,
        key=lambda x: (
            round(x["center_y"] / 15),
            x["x1"]
        )
    )

    return data


# =========================================================
# GHÉP OCR THÀNH TEXT
# =========================================================

def ocr_data_to_text(data):

    if not data:
        return ""

    data = sort_ocr_data(data)

    lines = []

    current_line = []

    current_y = None

    for item in data:

        y = item["center_y"]

        if current_y is None:

            current_line = [item]
            current_y = y

        elif abs(y - current_y) <= 25:

            current_line.append(item)

        else:

            current_line = sorted(
                current_line,
                key=lambda x: x["x1"]
            )

            lines.append(
                " ".join(
                    x["text"]
                    for x in current_line
                )
            )

            current_line = [item]
            current_y = y

    if current_line:

        current_line = sorted(
            current_line,
            key=lambda x: x["x1"]
        )

        lines.append(
            " ".join(
                x["text"]
                for x in current_line
            )
        )

    return "\n".join(lines)


# =========================================================
# OCR NHIỀU LẦN
# =========================================================

def multi_ocr(reader, image):

    processed = preprocess_image(image)

    data_1 = read_image_detail(
        reader,
        processed
    )

    # OCR ảnh gốc + ảnh xử lý
    data_2 = read_image_detail(
        reader,
        image
    )

    combined = data_1 + data_2

    # Loại text trùng
    unique = {}

    for item in combined:

        key = (
            item["text"].lower().strip(),
            round(item["center_x"] / 20),
            round(item["center_y"] / 20)
        )

        if key not in unique:

            unique[key] = item

        else:

            # Giữ confidence cao hơn
            if item["confidence"] > unique[key]["confidence"]:

                unique[key] = item

    data = list(unique.values())

    data = sort_ocr_data(data)

    text = ocr_data_to_text(data)

    return {
        "data": data,
        "text": text,
        "processed_image": processed
    }


# =========================================================
# CHUẨN HÓA TEXT
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.replace(
        "\xa0",
        " "
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# TÌM NGÀY
# =========================================================

def extract_date(text):

    patterns = [

        r"\b([0-3]?\d)[/\-.]([0-1]?\d)[/\-.](20\d{2})\b",

        r"Ngày\s*[:\-]?\s*([0-3]?\d[/\-.][0-1]?\d[/\-.]20\d{2})",

        r"Date\s*[:\-]?\s*([0-3]?\d[/\-.][0-1]?\d[/\-.]20\d{2})"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            if match.lastindex == 3:

                return (
                    f"{match.group(1)}/"
                    f"{match.group(2)}/"
                    f"{match.group(3)}"
                )

            return match.group(1)

    return ""


# =========================================================
# TÌM MST
# =========================================================

def extract_tax_code(text):

    patterns = [

        r"(?:MST|Mã số thuế|Tax Code)"
        r"\s*[:\-]?\s*"
        r"(\d{10}(?:-\d{3})?)",

        r"\b(\d{10}-\d{3})\b",

        r"\b(\d{10})\b"

    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        if matches:

            for value in matches:

                value = value.replace(
                    " ",
                    ""
                )

                if len(
                    re.sub(r"\D", "", value)
                ) in [10, 13]:

                    return value

    return ""


# =========================================================
# TÌM SỐ HÓA ĐƠN
# =========================================================

def extract_document_number(text):

    patterns = [

        r"Số hóa đơn\s*[:\-]?\s*([A-Z0-9\/\-.]+)",

        r"Số\s*[:\-]\s*([A-Z0-9\/\-.]+)",

        r"No\.\s*[:\-]?\s*([A-Z0-9\/\-.]+)",

        r"Invoice\s*(?:No|Number)"
        r"\s*[:\-]?\s*([A-Z0-9\/\-.]+)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            if value:

                return value

    return ""


# =========================================================
# CHUYỂN TIỀN VỀ SỐ
# =========================================================

def parse_money(value):

    if not value:
        return None

    value = str(value)

    value = value.replace(
        " ",
        ""
    )

    value = re.sub(
        r"[^\d.,]",
        "",
        value
    )

    if not value:
        return None

    # Việt Nam:
    # 110.000.000
    # 10,000,000
    if "." in value and "," in value:

        if value.rfind(".") > value.rfind(","):

            value = value.replace(
                ",",
                ""
            )

        else:

            value = value.replace(
                ".",
                ""
            )

            value = value.replace(
                ",",
                "."
            )

    elif "." in value:

        parts = value.split(".")

        if all(
            len(part) == 3
            for part in parts[1:]
        ):

            value = "".join(parts)

    elif "," in value:

        parts = value.split(",")

        if all(
            len(part) == 3
            for part in parts[1:]
        ):

            value = "".join(parts)

    try:

        return float(value)

    except:

        return None


# =========================================================
# FORMAT TIỀN
# =========================================================

def format_money(value):

    if value is None:
        return ""

    try:

        return f"{value:,.0f}".replace(
            ",",
            "."
        )

    except:

        return str(value)


# =========================================================
# TÌM TIỀN HÀNG
# =========================================================

def extract_subtotal(text):

    patterns = [

        r"Cộng tiền hàng\s*[:\-]?\s*([\d\.,]+)",

        r"Tiền hàng\s*[:\-]?\s*([\d\.,]+)",

        r"Tiền trước thuế\s*[:\-]?\s*([\d\.,]+)",

        r"Giá trị hàng hóa\s*[:\-]?\s*([\d\.,]+)",

        r"Subtotal\s*[:\-]?\s*([\d\.,]+)",

        r"Amount before tax\s*[:\-]?\s*([\d\.,]+)"

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

        r"Tiền thuế GTGT\s*[\s\S]{0,100}?"
        r"([\d\.,]+)",

        r"Tiền thuế\s*[:\-]?\s*([\d\.,]+)",

        r"VAT\s*[:\-]?\s*([\d\.,]+)",

        r"Tax amount\s*[:\-]?\s*([\d\.,]+)"

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
# TÌM THUẾ SUẤT
# =========================================================

def extract_vat_rate(text):

    patterns = [

        r"Thuế suất\s*[:\-]?\s*(\d{1,2}(?:[.,]\d+)?)\s*%",

        r"GTGT\s*[:\-]?\s*(\d{1,2}(?:[.,]\d+)?)\s*%",

        r"VAT\s*[:\-]?\s*(\d{1,2}(?:[.,]\d+)?)\s*%",

        r"\b(0|5|8|10)\s*%"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1) + "%"

    return ""


# =========================================================
# TÌM TỔNG TIỀN
# =========================================================

def extract_total(text):

    patterns = [

        r"Tổng tiền thanh toán"
        r"\s*[:\-]?\s*([\d\.,]+)",

        r"Tổng cộng tiền thanh toán"
        r"\s*[:\-]?\s*([\d\.,]+)",

        r"Tổng cộng"
        r"\s*[:\-]?\s*([\d\.,]+)",

        r"Thành tiền"
        r"\s*[:\-]?\s*([\d\.,]+)",

        r"Total"
        r"\s*[:\-]?\s*([\d\.,]+)",

        r"Grand Total"
        r"\s*[:\-]?\s*([\d\.,]+)"

    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        if matches:

            # Lấy số cuối cùng có ý nghĩa
            for value in reversed(matches):

                if parse_money(value) is not None:

                    return value

    return ""


# =========================================================
# TÌM NGƯỜI BÁN
# =========================================================

def extract_seller(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    keywords = [
        "người bán",
        "đơn vị bán",
        "tên đơn vị",
        "tên người bán",
        "seller",
        "company"
    ]

    for i, line in enumerate(lines):

        lower = line.lower()

        for keyword in keywords:

            if keyword in lower:

                # Trường hợp:
                # Người bán: CÔNG TY ABC
                parts = re.split(
                    r"[:\-]",
                    line,
                    maxsplit=1
                )

                if len(parts) == 2:

                    value = parts[1].strip()

                    if len(value) > 3:

                        return value

                # Trường hợp dòng sau
                if i + 1 < len(lines):

                    value = lines[i + 1]

                    if len(value) > 3:

                        return value

    # Phương án dự phòng:
    # tìm dòng có CÔNG TY
    for line in lines:

        upper = line.upper()

        if (
            "CÔNG TY" in upper
            or "CTY" in upper
            or "COMPANY" in upper
        ):

            return line

    return ""


# =========================================================
# TÌM NỘI DUNG HÀNG HÓA
# =========================================================

def extract_content(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    keywords = [
        "tên hàng",
        "tên hàng hóa",
        "hàng hóa",
        "dịch vụ",
        "description"
    ]

    for i, line in enumerate(lines):

        lower = line.lower()

        for keyword in keywords:

            if keyword in lower:

                if i + 1 < len(lines):

                    next_line = lines[i + 1]

                    # Không lấy dòng tổng tiền
                    if not re.search(
                        r"tổng|vat|thuế",
                        next_line,
                        re.IGNORECASE
                    ):

                        return next_line

    return ""


# =========================================================
# KIỂM TRA LOGIC
# =========================================================

def validate_record(record):

    warnings = []

    subtotal = parse_money(
        record["Tiền hàng"]
    )

    vat = parse_money(
        record["Tiền VAT"]
    )

    total = parse_money(
        record["Tổng tiền"]
    )

    rate_text = record[
        "Thuế suất VAT"
    ]

    rate = None

    if rate_text:

        try:

            rate = float(
                rate_text.replace(
                    "%",
                    ""
                ).replace(
                    ",",
                    "."
                )
            )

        except:

            pass

    # =========================================
    # KIỂM TRA THIẾU
    # =========================================

    required = {

        "Ngày chứng từ":
            record["Ngày chứng từ"],

        "Số chứng từ":
            record["Số chứng từ"],

        "Mã số thuế":
            record["Mã số thuế"],

        "Người bán":
            record["Người bán"],

        "Tổng tiền":
            record["Tổng tiền"]

    }

    missing = []

    for field, value in required.items():

        if not value:

            missing.append(field)

    if missing:

        warnings.append(
            "Thiếu: " +
            ", ".join(missing)
        )

    # =========================================
    # KIỂM TRA VAT
    # =========================================

    if (
        subtotal is not None
        and vat is not None
        and rate is not None
    ):

        expected_vat = subtotal * rate / 100

        tolerance = max(
            1,
            abs(expected_vat) * 0.01
        )

        if abs(
            expected_vat - vat
        ) > tolerance:

            warnings.append(
                "VAT không khớp tiền hàng × thuế suất"
            )

    # =========================================
    # KIỂM TRA TỔNG
    # =========================================

    if (
        subtotal is not None
        and vat is not None
        and total is not None
    ):

        expected_total = (
            subtotal + vat
        )

        tolerance = max(
            1,
            abs(expected_total) * 0.01
        )

        if abs(
            expected_total - total
        ) > tolerance:

            warnings.append(
                "Tổng tiền không khớp tiền hàng + VAT"
            )

    # =========================================
    # TRẠNG THÁI
    # =========================================

    if not warnings:

        status = "🟢 Có vẻ hợp lệ"

    else:

        status = "🟡 Cần kiểm tra"

    return status, warnings


# =========================================================
# TẠO RECORD
# =========================================================

def create_record(
    file_name,
    file_type,
    raw_text,
    file_bytes,
    preview_image
):

    record = {

        "STT": 0,

        "Tên file":
            file_name,

        "Loại file":
            file_type,

        "Ngày chứng từ":
            extract_date(raw_text),

        "Số chứng từ":
            extract_document_number(raw_text),

        "Mã số thuế":
            extract_tax_code(raw_text),

        "Người bán":
            extract_seller(raw_text),

        "Tiền hàng":
            extract_subtotal(raw_text),

        "Thuế suất VAT":
            extract_vat_rate(raw_text),

        "Tiền VAT":
            extract_vat(raw_text),

        "Tổng tiền":
            extract_total(raw_text),

        "Nội dung":
            extract_content(raw_text),

        "Trạng thái":
            "⚠️ Chưa kiểm tra",

        "Cảnh báo":
            [],

        "_raw_text":
            raw_text,

        "_file_bytes":
            file_bytes,

        "_preview_image":
            preview_image

    }

    status, warnings = validate_record(
        record
    )

    record["Cảnh báo"] = warnings

    if warnings:

        record["Trạng thái"] = status

    else:

        record["Trạng thái"] = status

    return record


# =========================================================
# 1. TẢI CHỨNG TỪ
# =========================================================

st.markdown("---")

st.subheader(
    "1️⃣ TẢI CHỨNG TỪ GỐC"
)

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
        "🔍 ĐỌC & PHÂN TÍCH CHỨNG TỪ",
        type="primary",
        use_container_width=True
    ):

        st.session_state.documents = []

        try:

            with st.spinner(
                "⏳ Đang khởi động OCR..."
            ):

                reader = load_ocr()

        except Exception as e:

            st.error(
                "❌ Không thể khởi động OCR."
            )

            st.exception(e)

            st.stop()

        progress = st.progress(0)

        status_box = st.empty()

        total_files = len(
            uploaded_files
        )

        for file_index, uploaded_file in enumerate(
            uploaded_files
        ):

            file_name = uploaded_file.name

            status_box.info(
                f"🔍 Đang xử lý "
                f"{file_index + 1}/{total_files}: "
                f"{file_name}"
            )

            try:

                file_bytes = uploaded_file.getvalue()

                file_type = uploaded_file.type

                pages = []

                # =====================================
                # ẢNH
                # =====================================

                if file_type.startswith(
                    "image/"
                ):

                    image = Image.open(
                        io.BytesIO(file_bytes)
                    ).convert("RGB")

                    pages.append(image)

                # =====================================
                # PDF
                # =====================================

                elif file_type == "application/pdf":

                    pages = pdf_to_images(
                        file_bytes
                    )

                else:

                    raise ValueError(
                        "Định dạng file không được hỗ trợ."
                    )

                all_page_text = []

                preview_image = (
                    pages[0]
                    if pages
                    else None
                )

                # =====================================
                # OCR TỪNG TRANG
                # =====================================

                for page_number, image in enumerate(
                    pages
                ):

                    status_box.info(
                        f"🔍 {file_name} "
                        f"→ đang đọc trang "
                        f"{page_number + 1}/{len(pages)}"
                    )

                    ocr_result = multi_ocr(
                        reader,
                        image
                    )

                    page_text = ocr_result[
                        "text"
                    ]

                    if page_text:

                        all_page_text.append(

                            f"========== TRANG "
                            f"{page_number + 1} ==========\n"
                            f"{page_text}"

                        )

                raw_text = "\n\n".join(
                    all_page_text
                )

                raw_text = normalize_text(
                    raw_text
                )

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

                record["STT"] = (
                    file_index + 1
                )

                st.session_state.documents.append(
                    record
                )

            except Exception as e:

                st.error(
                    f"❌ Lỗi khi đọc {file_name}"
                )

                st.exception(e)

            progress.progress(
                (file_index + 1)
                / total_files
            )

        status_box.success(
            f"✅ Đã xử lý xong "
            f"{len(st.session_state.documents)}"
            f"/{total_files} chứng từ."
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
        "⚠️ Dữ liệu OCR chỉ là dữ liệu trích xuất ban đầu. "
        "Chứng từ cần được kiểm tra trước khi xác nhận."
    )

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

            "Tiền hàng":
                document["Tiền hàng"],

            "VAT":
                document["Tiền VAT"],

            "Tổng tiền":
                document["Tổng tiền"],

            "Trạng thái":
                document["Trạng thái"]

        })

    df = pd.DataFrame(
        table_data
    )

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

        with st.container(
            border=True
        ):

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
                    "Ngày: "
                    + (
                        document["Ngày chứng từ"]
                        or "❓ Chưa đọc được"
                    )
                )

                st.write(
                    "MST: "
                    + (
                        document["Mã số thuế"]
                        or "❓ Chưa đọc được"
                    )
                )

                st.write(
                    "Tổng tiền: "
                    + (
                        document["Tổng tiền"]
                        or "❓ Chưa đọc được"
                    )
                )

            with col3:

                if st.button(
                    "👁️ XEM CHỨNG TỪ",
                    key=f"view_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_document = index

            # =========================================
            # CẢNH BÁO
            # =========================================

            if document["Cảnh báo"]:

                st.warning(
                    "⚠️ "
                    + " | ".join(
                        document["Cảnh báo"]
                    )
                )

            else:

                st.success(
                    "🟢 Chưa phát hiện lỗi logic cơ bản."
                )

            # =========================================
            # CHỈNH SỬA
            # =========================================

            with st.expander(
                "✏️ Kiểm tra / chỉnh sửa dữ liệu"
            ):

                col_a, col_b = st.columns(
                    2
                )

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

                if st.button(
                    "🔎 KIỂM TRA LẠI SỐ LIỆU",
                    key=f"validate_{index}",
                    use_container_width=True
                ):

                    status, warnings = validate_record(
                        document
                    )

                    document["Cảnh báo"] = warnings

                    if warnings:

                        document["Trạng thái"] = status

                        st.warning(
                            " | ".join(
                                warnings
                            )
                        )

                    else:

                        document["Trạng thái"] = (
                            "🟢 Có vẻ hợp lệ"
                        )

                        st.success(
                            "✅ Dữ liệu vượt qua kiểm tra logic cơ bản."
                        )

                document["Trạng thái"] = st.selectbox(
                    "Trạng thái kiểm tra",
                    [
                        "⚠️ Chưa kiểm tra",
                        "🟢 Có vẻ hợp lệ",
                        "✅ Đã kiểm tra",
                        "❌ Có sai lệch"
                    ],
                    key=f"status_{index}",
                    index=[
                        "⚠️ Chưa kiểm tra",
                        "🟢 Có vẻ hợp lệ",
                        "✅ Đã kiểm tra",
                        "❌ Có sai lệch"
                    ].index(
                        document["Trạng thái"]
                    )
                    if document["Trạng thái"]
                    in [
                        "⚠️ Chưa kiểm tra",
                        "🟢 Có vẻ hợp lệ",
                        "✅ Đã kiểm tra",
                        "❌ Có sai lệch"
                    ]
                    else 0
                )


# =========================================================
# 4. XEM CHỨNG TỪ
# =========================================================

if st.session_state.selected_document is not None:

    selected = (
        st.session_state.selected_document
    )

    if selected < len(
        st.session_state.documents
    ):

        document = (
            st.session_state.documents[selected]
        )

        st.markdown("---")

        st.subheader(
            f"👁️ KIỂM TRA: "
            f"{document['Tên file']}"
        )

        col_image, col_data = st.columns(
            [1.2, 1]
        )

        # =============================================
        # ẢNH
        # =============================================

        with col_image:

            st.markdown(
                "### 📷 CHỨNG TỪ GỐC"
            )

            if document["_preview_image"]:

                st.image(
                    document["_preview_image"],
                    use_container_width=True
                )

            else:

                st.warning(
                    "Không có ảnh xem trước."
                )

        # =============================================
        # DATA
        # =============================================

        with col_data:

            st.markdown(
                "### 📝 DỮ LIỆU ĐÃ ĐỌC"
            )

            fields = [

                ("Ngày",
                 "Ngày chứng từ"),

                ("Số chứng từ",
                 "Số chứng từ"),

                ("MST",
                 "Mã số thuế"),

                ("Người bán",
                 "Người bán"),

                ("Tiền hàng",
                 "Tiền hàng"),

                ("Thuế suất",
                 "Thuế suất VAT"),

                ("Tiền VAT",
                 "Tiền VAT"),

                ("Tổng tiền",
                 "Tổng tiền"),

                ("Nội dung",
                 "Nội dung")

            ]

            for label, key in fields:

                value = document[key]

                if value:

                    st.write(
                        f"**{label}:** {value}"
                    )

                else:

                    st.warning(
                        f"⚠️ {label}: chưa đọc được"
                    )

            st.write(
                f"**Trạng thái:** "
                f"{document['Trạng thái']}"
            )

        # =============================================
        # CẢNH BÁO
        # =============================================

        if document["Cảnh báo"]:

            st.markdown("---")

            st.warning(
                "⚠️ CÁC VẤN ĐỀ PHÁT HIỆN"
            )

            for warning in document["Cảnh báo"]:

                st.write(
                    f"• {warning}"
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
                "OCR",
                document["_raw_text"],
                height=450,
                key=f"ocr_text_{selected}"
            )

        else:

            st.error(
                "❌ Không đọc được nội dung."
            )

        if st.button(
            "❌ ĐÓNG CHỨNG TỪ",
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
        not in [
            "✅ Đã kiểm tra"
        ]

    ]

    if unchecked:

        st.warning(
            f"⚠️ Còn {len(unchecked)} chứng từ "
            "chưa được xác nhận chính thức."
        )

    else:

        st.success(
            "✅ Tất cả chứng từ đã được xác nhận."
        )

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
                document["Trạng thái"],

            "Cảnh báo":
                " | ".join(
                    document["Cảnh báo"]
                )

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
# 7. XÓA
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
