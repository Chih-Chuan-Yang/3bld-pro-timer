import streamlit as st
import joblib
import os
from services.db_manager import ProDBManager
from services.helpers import generate_scramble
from core.scheme import SchemeManager
from services.wca_api import WCAService

# 導入 UI 模組
from ui.styles import apply_custom_styles
from ui.sidebar import render_sidebar
from ui.timer import render_timer_page
from ui.battle_card import render_battle_card
from ui.scheme_settings import render_scheme_settings

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="3BLD Pro", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")

# --- 2. 初始化 Session State (全域) ---
if 'timer_state' not in st.session_state: st.session_state.timer_state = 'IDLE' 
if 'current_scramble' not in st.session_state: st.session_state.current_scramble = generate_scramble()
if 'sessions' not in st.session_state: st.session_state.sessions = {'預設': []} 
if 'current_session' not in st.session_state: st.session_state.current_session = '預設'
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'last_solve_result' not in st.session_state: st.session_state.last_solve_result = None
if 'selected_pair_detail' not in st.session_state: st.session_state.selected_pair_detail = None
if 'ai_word_suggestion' not in st.session_state: st.session_state.ai_word_suggestion = "" 
if 'gemini_key' not in st.session_state: st.session_state.gemini_key = ""

# 實例化管理器
if 'pro_db_manager' not in st.session_state: st.session_state.pro_db_manager = ProDBManager()
if 'scheme_manager' not in st.session_state: st.session_state.scheme_manager = SchemeManager()
if 'wca_service' not in st.session_state: st.session_state.wca_service = WCAService()

# 載入模型 (Cache)
MODEL_FILE = "3bld_predictor.pkl"
@st.cache_resource
def load_prediction_model():
    if os.path.exists(MODEL_FILE):
        try: return joblib.load(MODEL_FILE)
        except: return None
    return None
if 'predictor' not in st.session_state: st.session_state.predictor = load_prediction_model()

# --- 3. 應用樣式 ---
apply_custom_styles()

# --- 4. 側邊欄與導航 ---
# 在這裡定義模式，並傳給 sidebar
HISTORY_FILE = "3bld_history.csv"
with st.sidebar:
    mode = st.radio("功能模式", ["📊 練習數據", "🏆 戰力卡", "⚙️ 編碼設定"], horizontal=True, label_visibility="collapsed")

render_sidebar(HISTORY_FILE, mode)

# --- 5. 主畫面路由 ---
if mode == "🏆 戰力卡":
    render_battle_card()
elif mode == "⚙️ 編碼設定":
    render_scheme_settings()
else:
    render_timer_page()