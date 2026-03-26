import streamlit as st
import cv2
import pytesseract
import pandas as pd
import numpy as np
import re
import io

st.set_page_config(page_title="Tính điểm học bạ TBD", layout="wide")
st.title("🎓 Công cụ Tính điểm Xét tuyển TBD")
st.markdown("---")

# --- HÀM TỰ ĐỘNG QUÉT SỐ ---
def auto_extract_scores(image):
    # Chuyển ảnh xám và tăng nét
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    thresh = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15)
    
    # Quét lấy số
    custom_config = r'--psm 11 -c tessedit_char_whitelist=0123456789.,'
    raw_text = pytesseract.image_to_string(thresh, config=custom_config)
    
    # Tìm các số từ 4.0 đến 10.0
    found_nums = re.findall(r'\d[.,]\d|\d{1,2}', raw_text)
    scores = []
    for n in found_nums:
        clean_n = n.replace(',', '.')
        try:
            val = float(clean_n)
            if 4.0 <= val <= 10.0: scores.append(val)
        except: continue
    return scores

# --- GIAO DIỆN CHÍNH ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📸 Tự động từ Ảnh")
    up_file = st.file_uploader("Tải ảnh bảng điểm học bạ", type=["jpg", "png", "jpeg"])
    
    if up_file:
        file_bytes = np.asarray(bytearray(up_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(img, use_container_width=True)
        
        if st.button("🚀 Máy tự tính điểm ngay"):
            scores = auto_extract_scores(img)
            if len(scores) >= 3:
                # Lấy 3 số đầu tiên máy quét được
                s1, s2, s3 = scores[0], scores[1], scores[2]
                tong = s1 + s2 + s3
                st.success(f"Kết quả máy đọc: {s1} + {s2} + {s3} = **{round(tong, 2)}**")
                if tong >= 18.0: st.balloons()
            else:
                st.error("Không tìm đủ số. Bạn hãy dùng bảng Nhập tay bên phải nhé!")

with col_right:
    st.subheader("⌨️ Nhập tay (Zalo/Tin nhắn)")
    with st.form("manual_entry"):
        name = st.text_input("Tên thí sinh")
        c1, c2, c3 = st.columns(3)
        m1 = c1.number_input("Môn 1", 0.0, 10.0, 0.0)
        m2 = c2.number_input("Môn 2", 0.0, 10.0, 0.0)
        m3 = c3.number_input("Môn 3", 0.0, 10.0, 0.0)
        bonus = st.number_input("Điểm ưu tiên", 0.0, 2.0, 0.0, 0.25)
        
        submit = st.form_submit_button("Tính tổng & Lưu")
        if submit:
            tong_m = m1 + m2 + m3 + bonus
            st.metric("TỔNG ĐIỂM", round(tong_m, 2))
            if tong_m >= 18.0:
                st.success("ĐỦ ĐIỂM XÉT TUYỂN!")
            else:
                st.warning("Dưới ngưỡng 18.0")
