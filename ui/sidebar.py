import streamlit as st
from services.trainer import train_model

def render_sidebar(history_file, mode):
    with st.sidebar:
        st.title("🧩 3BLD Pro")
        # 這裡不使用 radio，而是單純顯示標題，模式選擇由 app.py 控制，
        # 或者我們可以在這裡回傳 mode，但為了簡單，我們假設 mode 是外部傳入的
        st.divider()
        
        with st.expander("🤖 AI 助手設定 (Gemini)", expanded=True):
            api_key_input = st.text_input("Gemini API Key", type="password", 
                                          value=st.session_state.gemini_key,
                                          placeholder="貼上 Key 以啟用聯想...")
            if api_key_input: st.session_state.gemini_key = api_key_input
            
            if mode == "📊 練習數據":
                if st.button("🧠 重新訓練時間預測"):
                    ok, msg = train_model()
                    if ok: 
                        st.success(msg)
                        # 清除 cache 需在 app.py 處理，或使用 st.cache_resource.clear()
                    else: st.error(msg)

        with st.expander("📂 匯入檔案", expanded=False):
            uploaded_hist = st.file_uploader("匯入 csTimer CSV", type=["csv"], key="hist_upload")
            if uploaded_hist is not None:
                if st.button("📥 確認匯入紀錄"):
                    try:
                        with open(history_file, "wb") as f: f.write(uploaded_hist.getbuffer())
                        st.success("✅ 紀錄已更新！")
                    except: st.error("匯入失敗")

            uploaded_lp = st.file_uploader("匯入 Letter Pairs CSV", type=["csv"], key="lp_upload")
            if uploaded_lp is not None:
                if st.button("📥 確認匯入 Pairs"):
                    success, result = st.session_state.pro_db_manager.import_from_csv(uploaded_lp)
                    if success: st.success(f"✅ {result}")
                    else: st.error(result)