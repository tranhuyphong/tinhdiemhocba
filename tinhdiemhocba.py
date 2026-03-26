import streamlit as st
import cv2
import pytesseract
import pandas as pd
import numpy as np
import re
import io

st.set_page_config(page_title="Tính điểm học bạ TBD", layout="wide")
st.title("🎓 Công cụ Tính điểm Xét tuyển TBD")

# --- HÀM XỬ LÝ TỰ ĐỘNG QUÉT ĐIỂM ---
def auto_scan_scores(image):
    # Tiền xử lý ảnh để máy đọc số tốt hơn
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Tăng tương phản và khử nhiễu
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15)
    
    # Quét số với bộ lọc chỉ lấy chữ số và dấu ngăn cách
    custom_config = r'--psm 11 -c tessedit_char_whitelist=0123456789.,'
    raw_text = pytesseract.image_to_string(thresh, config=custom_config)
    
    # Tìm các số có định dạng điểm (ví dụ: 7.5, 8.0, 10)
    found_nums = re.findall(r'\d[.,]\d|\d{1,2}', raw_text)
    
    scores = []
    for n in found_nums:
        clean_n = n.replace(',', '.')
        try:
            val = float(clean_n)
            # Lọc lấy các giá trị thực tế của điểm môn học
            if 4.0 <= val <= 10.0:
                scores.append(val)
        except:
            continue
    return scores

# --- GIAO DIỆN CHÍNH ---
tab1, tab2 = st.tabs(["📸 Tự động từ Ảnh học bạ", "⌨️ Nhập điểm từ Tin nhắn"])

# --- TAB 1: TỰ ĐỘNG ---
with tab1:
    st.header("Quét ảnh tự động")
    file_up = st.file_uploader("Tải ảnh học bạ (Chụp rõ phần bảng điểm)", type=["jpg", "png", "jpeg"], key="auto")
    
    if file_up:
        file_bytes = np.asarray(bytearray(file_up.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(img, width=400, caption="Ảnh đã tải lên")
        
        if st.button("🚀 Bắt đầu tính điểm tự động"):
            with st.spinner("Đang phân tích bảng điểm..."):
                all_found = auto_scan_scores(img)
                if len(all_found) >= 3:
                    # Lấy 3 con số đầu tiên máy tìm thấy (thường là Toán - Lý - Hóa hoặc các môn chính)
                    d1, d2, d3 = all_found[0], all_found[1], all_found[2]
                    tong = d1 + d2 + d3
                    
                    st.success(f"Kết quả dự kiến: {d1} + {d2} + {d3} = {round(tong, 2)}")
                    st.metric("TỔNG ĐIỂM", round(tong, 2))
                    st.write("Các điểm khác máy tìm thấy:", all_found[3:8])
                else:
                    st.error("Máy không tìm đủ 3 đầu điểm. Hãy chụp ảnh gần hơn vào bảng điểm!")

# --- TAB 2: NHẬP TAY ---
with tab2:
    st.header("Nhập điểm thủ công")
    st.info("Nhìn tin nhắn Zalo và gõ nhanh vào đây")
    
    with st.form("manual_form"):
        ten = st.text_input("Tên thí sinh (không bắt buộc)")
        c1, c2, c3 = st.columns(3)
        with c1: m1 = st.number_input("Điểm Môn 1", 0.0, 10.0, 0.0, step=0.1)
        with c2: m2 = st.number_input("Điểm Môn 2", 0.0, 10.0, 0.0, step=0.1)
        with c3: m3 = st.number_input("Điểm Môn 3", 0.0, 10.0, 0.0, step=0.1)
        
        bonus = st.number_input("Điểm ưu tiên", 0.0, 2.0, 0.0, 0.25)
        
        submit = st.form_submit_button("Tính tổng ngay")
        
        if submit:
            tong_nhap = m1 + m2 + m3 + bonus
            st.write(f"### Thí sinh: {ten}")
            st.header(f"Tổng điểm: {round(tong_nhap, 2)}")
            if tong_nhap >= 18.0:
                st.balloons()
                st.success("Đạt ngưỡng xét tuyển!")
            else:
                st.warning("Dưới ngưỡng xét tuyển 18.0")
