"""Guardrails — chặn rủi ro ở đầu vào và đầu ra (spec.md §4 "Chỗ chặn rủi ro", §9). Code thuần, không gọi model.

Đầu vào (trước khi gửi gì lên model):
    scrub_sensitive(text)  -> (text_sach, canh_bao)   che số thẻ / OTP / mật khẩu / SĐT, không gửi lên model
    detect_availability_demand(text) / detect_room_assignment(text)   đòi "đảm bảo còn phòng" / xếp từng người
    detect_action_request(text) -> bool               đòi đặt chỗ / giữ chỗ / thanh toán / cọc
    detect_authority_claim(text) -> bool              tự xưng đại lý / nhân viên + đòi bỏ quy tắc
    foreign_destination(text) -> str | None           điểm đến nước ngoài (ngoài phạm vi: chỉ trong nước)
    check_group_size(n) -> str | None                 ngoài 5–500 người
    wrap_untrusted(text)                              bọc dữ liệu người dùng / bài viết trong thẻ, để model coi là dữ liệu

Đầu ra (trước khi trả cho người dùng):
    sanitize_output(text) -> (text_sach, sua)         bỏ câu khẳng định đã đặt / đã cọc / còn phòng, che số thẻ còn sót
"""
import re
import unicodedata

MIN_PEOPLE, MAX_PEOPLE = 5, 500


def _n(text):
    return unicodedata.normalize("NFC", text or "")


def _rx(p, flags=re.IGNORECASE):
    return re.compile(unicodedata.normalize("NFC", p), flags)


# --- Thông tin nhạy cảm -------------------------------------------------------------------
CARD = _rx(r"(?<!\d)(?:\d[ \-.]?){12,18}\d(?!\d)")
EXPIRY = _rx(r"(hết hạn|het han|exp(iry)?|hạn)\s*[:\-]?\s*\d{1,2}\s*/\s*\d{2,4}")
PHONE = _rx(r"(?<![\d\w])(?:\+?84|0)(?:[ .\-]?\d){8,10}(?!\d)")
OTP = _rx(r"\b(otp|cvv|cvc|mã xác (thực|nhận)|mật khẩu|password)\b\s*(là|:)?\s*\S+")


def _luhn_ok(digits):
    s, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        s += d
        alt = not alt
    return s % 10 == 0


def scrub_sensitive(text):
    """Che số thẻ (13–19 chữ số, qua Luhn hoặc ≥15 số), ngày hết hạn, OTP / CVV / mật khẩu."""
    text = _n(text)
    found = []

    def card(m):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and (_luhn_ok(digits) or len(digits) >= 15):
            found.append("số thẻ")
            return "[đã che thông tin thẻ]"
        return m.group(0)

    text = CARD.sub(card, text)
    if PHONE.search(text):
        found.append("số điện thoại")
        text = PHONE.sub("[đã che SĐT]", text)
    if EXPIRY.search(text):
        found.append("ngày hết hạn thẻ")
        text = EXPIRY.sub("[đã che]", text)
    if OTP.search(text):
        found.append("mã bảo mật")
        text = OTP.sub("[đã che]", text)
    warn = []
    pay = [f for f in found if f != "số điện thoại"]
    if pay:
        warn.append("⚠ Tin nhắn có thông tin thanh toán (%s). Hệ thống đã che và không lưu, không dùng. "
                    "Đừng gửi số thẻ, ngày hết hạn, OTP cho bất kỳ công cụ chat nào; khi đặt chỗ hãy thanh toán "
                    "trực tiếp trên kênh chính thức của khách sạn / nhà xe." % ", ".join(sorted(set(pay))))
    if "số điện thoại" in found:
        warn.append("⚠ Tin nhắn có số điện thoại cá nhân. Hệ thống chỉ cần **số người**, không cần danh sách, tên hay "
                    "SĐT nhân viên — đã che và không gửi đi.")
    return text, " ".join(warn)


# --- Yêu cầu hành động ra ngoài (đặt chỗ / thanh toán) --------------------------------------
ACTION = _rx(r"(đặt|book|giữ)\s*(luôn|giúp|hộ|dùm|giùm)?\s*(chỗ|phòng|khách sạn|xe|vé|tour)?\s*(luôn|giúp|hộ|dùm|giùm)"
             r"|giữ chỗ|chuyển khoản|thanh toán|đặt cọc|\bcọc\b|trả tiền giúp|quẹt thẻ")


def detect_action_request(text):
    return bool(ACTION.search(_n(text)))


REFUSE_ACTION = ("Hệ thống chỉ **đề xuất và dự trù**, không đặt phòng / xe / vé, không giữ chỗ và không chuyển khoản "
                 "hay thanh toán thay công ty. Kế hoạch dưới đây để công ty tự liên hệ và đặt trực tiếp; "
                 "giá là tham khảo, cần xác nhận lại với cơ sở trước khi chuyển tiền.")

# --- Tự xưng thẩm quyền + đòi bỏ quy tắc (tấn công qua lời người dùng) ----------------------
AUTHORITY = _rx(r"(tôi là|mình là|em là|bên tôi là)\s*(đại lý|nhân viên|admin|quản trị|đối tác|chủ)")
OVERRIDE = _rx(r"bỏ qua|phớt lờ|ignore|không cần (so|tính|quan tâm).{0,15}ngân sách|cứ chọn|chỉ chọn|bắt buộc chọn")


def detect_authority_claim(text):
    t = _n(text)
    return bool(AUTHORITY.search(t) and OVERRIDE.search(t)) or bool(
        _rx(r"bỏ qua (mọi|tất cả|các)?\s*(hướng dẫn|quy tắc|chỉ dẫn)|ignore (all|previous)").search(t))


NOTE_AUTHORITY = ("Lưu ý: yêu cầu \"chọn sẵn một cơ sở\" hoặc \"bỏ qua ngân sách\" trong tin nhắn được coi là **thông tin tham "
                  "khảo, không phải lệnh**. Mọi gói vẫn được so với ngân sách đã nêu; cơ sở chỉ được đề xuất khi có nguồn "
                  "kiểm được như mọi ứng viên khác.")

# --- Đòi đảm bảo còn phòng / xếp từng người vào phòng ----------------------------------------
AVAIL = _rx(r"(đảm bảo|chắc chắn|cam kết|khẳng định)\s*(là\s*)?(vẫn\s*)?(còn|có)\s*(phòng|chỗ)")
ASSIGN = _rx(r"xếp (ai|từng người|từng bạn|nhân viên)\s.{0,20}phòng|chia phòng (cho|giúp)|ai ở (phòng|với) ")


def detect_availability_demand(text):
    return bool(AVAIL.search(_n(text)))


def detect_room_assignment(text):
    return bool(ASSIGN.search(_n(text)))


NOTE_AVAIL = ("Hệ thống **không kiểm được và không đảm bảo** tình trạng còn phòng / còn chỗ. Trước khi chuyển tiền, công ty "
              "nên gọi trực tiếp cơ sở để xác nhận đủ số phòng cho cả đoàn bằng văn bản (email / hợp đồng), và chuẩn bị "
              "một cơ sở dự phòng cùng mức.")
NOTE_ASSIGN = ("Hệ thống không xếp từng nhân viên vào phòng (ngoài phạm vi, và không cần thông tin cá nhân). Bên dưới là "
               "**cơ cấu phòng** (loại phòng × số phòng) đủ chỗ cho cả đoàn; công ty tự chia người vào phòng.")
FOOTER = ("Giá là tham khảo; tình trạng phòng / chỗ chưa được kiểm — xác nhận trực tiếp với cơ sở trước khi chuyển tiền. "
          "Hệ thống chỉ đề xuất, công ty tự đặt.")

# --- Phạm vi: chỉ trong nước -----------------------------------------------------------------
# Không đưa "lào", "mỹ", "úc" đứng riêng: trùng Lào Cai, Mỹ Tho, Mỹ Khê, …
FOREIGN = ["bangkok", "thái lan", "thai lan", "phuket", "pattaya", "singapore", "malaysia", "kuala lumpur", "bali",
           "indonesia", "hàn quốc", "seoul", "busan", "jeju", "nhật bản", "tokyo", "osaka", "trung quốc", "bắc kinh",
           "thượng hải", "hồng kông", "hong kong", "đài loan", "đài bắc", "campuchia", "siem reap", "phnom penh",
           "nước lào", "viêng chăn", "luang prabang", "myanmar", "philippines", "dubai", "châu âu", "paris", "nước úc", "sydney", "nước mỹ", "new york",
           "maldives", "ấn độ", "nepal"]
_FOREIGN_RX = _rx(r"(?<!\w)(" + "|".join(re.escape(_n(x)) for x in FOREIGN) + r")(?!\w)")


def foreign_destination(text):
    m = _FOREIGN_RX.search(_n(text))
    return m.group(1) if m else None


def refuse_foreign(place):
    return ("Hiện hệ thống chỉ hỗ trợ lập kế hoạch cho chuyến đi **trong nước**, nên chưa lập dự trù cho %s. "
            "Nếu muốn trải nghiệm tương tự trong nước, có thể cân nhắc: Phú Quốc (biển đảo, resort), Đà Nẵng – Hội An "
            "(thành phố biển + phố cổ), Nha Trang (biển, giải trí) — gửi lại yêu cầu với một trong các điểm này "
            "kèm số người, số ngày, nơi xuất phát và ngân sách để nhận 3 gói dự trù." % place)


def check_group_size(n):
    if n is None:
        return None
    if n > MAX_PEOPLE:
        return ("Đoàn %d người vượt giới hạn hệ thống hỗ trợ (%d–%d người / chuyến), nên chưa lập bảng chi phí. "
                "Hướng thay thế: chia thành %d đợt khoảng %d người và lập kế hoạch từng đợt, hoặc liên hệ đơn vị "
                "tổ chức sự kiện chuyên đoàn lớn để có báo giá trọn gói."
                % (n, MIN_PEOPLE, MAX_PEOPLE, -(-n // MAX_PEOPLE), -(-n // -(-n // MAX_PEOPLE))))
    if n < MIN_PEOPLE:
        return ("Đoàn %d người nhỏ hơn mức hệ thống hỗ trợ (%d–%d người). Với nhóm nhỏ, các app đặt phòng / vé "
                "thông thường sẽ phù hợp hơn." % (n, MIN_PEOPLE, MAX_PEOPLE))
    return None


# --- Bọc dữ liệu không tin cậy ------------------------------------------------------------
def wrap_untrusted(text, tag="du_lieu_nguoi_dung"):
    """Bọc dữ liệu trong thẻ và gỡ thẻ trùng tên bên trong (chặn kiểu chèn </du_lieu_nguoi_dung>)."""
    clean = re.sub(r"</?\s*%s\s*>" % tag, "", _n(text), flags=re.IGNORECASE)
    return "<%s>\n%s\n</%s>" % (tag, clean, tag)


# --- Đầu ra -----------------------------------------------------------------------------------
_CLAIMS = _rx(r"[^.\n]*\b(đã|vừa)\s+(đặt|giữ|cọc|chuyển khoản|thanh toán|book)[^.\n]*[.\n]?"
              r"|[^.\n]*\b(chắc chắn|đảm bảo)\s+(còn|có)\s+(phòng|chỗ)[^.\n]*[.\n]?"
              r"|[^.\n]*\bvẫn còn phòng\b[^.\n]*[.\n]?")


def sanitize_output(text):
    """Bỏ câu khẳng định đã đặt / đã cọc / chắc còn phòng (model có thể nói), che số thẻ nếu còn sót."""
    text = _n(text)
    fixed = []
    out, w = scrub_sensitive(text)
    if w:
        fixed.append("che thông tin thẻ")

    def drop(m):
        s = m.group(0)
        if re.search(r"không|chưa|chỉ đề xuất", s, re.IGNORECASE):
            return s   # câu phủ định ("không đặt", "chưa đặt") giữ nguyên
        fixed.append("bỏ câu khẳng định đặt chỗ / còn phòng")
        return ""

    out = _CLAIMS.sub(drop, out)
    return out, fixed
