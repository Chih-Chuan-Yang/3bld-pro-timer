import streamlit as st

def render_scheme_settings():
    st.markdown("## ⚙️ 記憶編碼自定義")
    with st.form("scheme_form"):
        current = st.session_state.scheme_manager.scheme
        
        def face_grid(face_name, keys, css_class):
            st.markdown(f"<div class='cube-face-container {css_class}'><div class='face-label'>{face_name}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i in range(3): cols[i].text_input("", value=current[face_name].get(keys[i], ""), key=f"{face_name}_{keys[i]}", label_visibility="collapsed")
            cols = st.columns(3)
            cols[0].text_input("", value=current[face_name].get(keys[3], ""), key=f"{face_name}_{keys[3]}", label_visibility="collapsed")
            cols[1].markdown(f"<div style='height:42px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:24px; color:#fff;'>{face_name}</div>", unsafe_allow_html=True)
            cols[2].text_input("", value=current[face_name].get(keys[5], ""), key=f"{face_name}_{keys[5]}", label_visibility="collapsed")
            cols = st.columns(3)
            for i in range(3): cols[i].text_input("", value=current[face_name].get(keys[6+i], ""), key=f"{face_name}_{keys[6+i]}", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            for k in keys:
                widget_key = f"{face_name}_{k}"
                if widget_key in st.session_state: current[face_name][k] = st.session_state[widget_key]

        cl, cu, cr = st.columns([1, 1, 1])
        with cu: face_grid("U", ["UBL", "UB", "UBR", "UL", "XX", "UR", "UFL", "UF", "UFR"], "face-u")
        c_l, c_f, c_r, c_b = st.columns(4)
        with c_l: face_grid("L", ["LUB", "LU", "LUF", "LB", "XX", "LF", "LDB", "LD", "LDF"], "face-l")
        with c_f: face_grid("F", ["FUL", "FU", "FUR", "FL", "XX", "FR", "FDL", "FD", "FDR"], "face-f")
        with c_r: face_grid("R", ["RUF", "RU", "RUB", "RF", "XX", "RB", "RDF", "RD", "RDB"], "face-r")
        with c_b: face_grid("B", ["BUR", "BU", "BUL", "BR", "XX", "BL", "BDR", "BD", "BDL"], "face-b")
        cl, cd, cr = st.columns([1, 1, 1])
        with cd: face_grid("D", ["DFL", "DF", "DFR", "DL", "XX", "DR", "DBL", "DB", "DBR"], "face-d")
        
        if st.form_submit_button("💾 儲存並套用"):
            st.session_state.scheme_manager.save_scheme(current)
            st.success("編碼已更新！")
            st.rerun()