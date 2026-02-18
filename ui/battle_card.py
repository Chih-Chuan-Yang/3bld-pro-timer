import streamlit as st

def render_battle_card():
    st.markdown("## 🆔 選手戰力分析")
    col1, col2 = st.columns([3, 1])
    with col1: wca_input = st.text_input("輸入 WCA ID", value="", placeholder="例如: 2015WANG09").upper()
    with col2: 
        st.write(""); st.write("")
        search_btn = st.button("🔍 查詢", use_container_width=True)
    if search_btn and wca_input:
        with st.spinner("連線 WCA 資料庫..."):
            data = st.session_state.wca_service.get_user_data(wca_input)
            parsed = st.session_state.wca_service.parse_stats_for_card(data)
            st.session_state.wca_data = parsed if parsed else None
    if st.session_state.get('wca_data'):
        st.info("戰力卡功能正常 (內容省略)")