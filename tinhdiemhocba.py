import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Tính điểm học bạ TBD", layout="wide")

# Giao diện Header của trường
st.image("https://tbd.edu.vn/wp-content/uploads/2023/04/Logo-TBD-Final-No-Slogan.png", width=200)
st.title("🎓 Hệ thống Tính điểm & Quản lý Xét tuyển TBD")

# --- PHẦN 1: CÀI ĐẶT ---
st.sidebar.header("⚙️ Cấu hình Xét tuyển")
diem_san = st.sidebar.number_input("Điểm sàn trúng tuyển", value=18.0, step=0.5)

# Khởi tạo danh sách lưu trữ trong phiên làm việc
if 'ds_xet_tuyen' not in st.session_state:
    st.session_state.ds_xet_tuyen = []

# --- PHẦN 2: NHẬP LIỆU ---
tab1, tab2 = st.tabs(["⌨️ Nhập tay nhanh", "📸 Soi ảnh học bạ"])

with tab1:
    st.info("Dành cho trường hợp thí sinh nhắn tin điểm qua Zalo/Messenger.")
    with st.form("form_nhap_tay"):
        ten_ts = st.text_input("Họ và tên thí sinh")
        sdt_ts = st.text_input("Số điện thoại")
        
        c1, c2, c3 = st.columns(3)
        with c1: m1 = st.number_input("Điểm Môn 1", 0.0, 10.0, 0.0)
        with c2: m2 = st.number_input("Điểm Môn 2", 0.0, 10.0, 0.0)
        with c3: m3 = st.number_input("Điểm Môn 3", 0.0, 10.0, 0.0)
        
        diem_ut = st.number_input("Điểm ưu tiên (khu vực/đối tượng)", 0.0, 2.0, 0.0, 0.25)
        btn_tinh = st.form_submit_button("➕ Tính điểm & Thêm vào danh sách")
        
        if btn_tinh:
            tong = m1 + m2 + m3 + diem_ut
            status = "✅ Đạt" if tong >= diem_san else "❌ Chưa đạt"
            new_entry = {
                "Họ Tên": ten_ts, "SĐT": sdt_ts, 
                "Môn 1": m1, "Môn 2": m2, "Môn 3": m3, 
                "Ưu tiên": diem_ut, "Tổng điểm": round(tong, 2), "Trạng thái": status
            }
            st.session_state.ds_xet_tuyen.append(new_entry)
            st.success(f"Đã thêm thí sinh {ten_ts} với tổng điểm {tong}")

with tab2:
    st.info("Tải ảnh học bạ lên để vừa nhìn vừa nhập cho chuẩn.")
    up_file = st.file_uploader("Tải ảnh học bạ...", type=["jpg", "png", "jpeg"])
    if up_file:
        col_img, col_input = st.columns([1, 1])
        with col_img:
            st.image(up_file, caption="Ảnh học bạ đối chiếu", use_container_width=True)
        with col_input:
            st.warning("Nhìn ảnh bên trái và nhập số vào đây:")
            # Tái sử dụng logic nhập liệu ở đây để lưu vào cùng danh sách
            t_img = st.text_input("Họ tên (từ ảnh)")
            s_img = st.text_input("SĐT (từ ảnh)")
            d1 = st.number_input("Môn 1 ", 0.0, 10.0, 0.0, key="d1")
            d2 = st.number_input("Môn 2 ", 0.0, 10.0, 0.0, key="d2")
            d3 = st.number_input("Môn 3 ", 0.0, 10.0, 0.0, key="d3")
            if st.button("Lưu từ ảnh"):
                t_tong = d1 + d2 + d3
                st.session_state.ds_xet_tuyen.append({
                    "Họ Tên": t_img, "SĐT": s_img, "Môn 1": d1, "Môn 2": d2, "Môn 3": d3, 
                    "Ưu tiên": 0, "Tổng điểm": round(t_tong, 2), 
                    "Trạng thái": "✅ Đạt" if t_tong >= diem_san else "❌ Chưa đạt"
                })

# --- PHẦN 3: HIỂN THỊ & XUẤT FILE ---
if st.session_state.ds_xet_tuyen:
    st.markdown("---")
    st.subheader("📊 Danh sách thí sinh đã tính điểm")
    df = pd.DataFrame(st.session_state.ds_xet_tuyen)
    
    # Hiển thị bảng có màu sắc phân biệt
    st.dataframe(df.style.applymap(lambda x: 'color: green' if x == '✅ Đạt' else ('color: red' if x == '❌ Chưa đạt' else ''), subset=['Trạng thái']))

    # Xuất Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Tải File Excel Tổng Hợp Thí Sinh",
        data=buffer.getvalue(),
        file_name="xet_tuyen_TBD.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    if st.button("🗑️ Xóa danh sách"):
        st.session_state.ds_xet_tuyen = []
        st.rerun()
