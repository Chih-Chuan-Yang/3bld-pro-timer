import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import urllib.parse
import joblib
import os
import textwrap
import plotly.graph_objects as go
from datetime import datetime

# --- 引入自定義服務模組 ---
from core.scheme import SchemeManager
from services.ai_agent import AI_READY, generate_single_pair_mnemonic
from services.db_manager import ProDBManager
from services.helpers import generate_scramble, calc_ao, save_to_db, get_display_text
from services.trainer import train_model
from services.wca_api import WCAService

# --- 外部解算模組載入檢查 ---
try:
    from solver import BlindSolver
    from visualizer import get_3d_html
    from scramble_translator import ScrambleTranslator
except ImportError as e:
    st.error(f"❌ 核心解算模組缺失：{e}")
    st.stop()

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="3BLD Pro Timer", page_icon="⏱️", layout="wide", initial_sidebar_state="expanded")

# --- 2. 初始化 Session State ---
if 'timer_state' not in st.session_state: st.session_state.timer_state = 'IDLE' 
if 'current_scramble' not in st.session_state: st.session_state.current_scramble = generate_scramble()
if 'sessions' not in st.session_state: st.session_state.sessions = {'預設': []} 
if 'current_session' not in st.session_state: st.session_state.current_session = '預設'
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'last_solve_result' not in st.session_state: st.session_state.last_solve_result = None
if 'selected_pair_detail' not in st.session_state: st.session_state.selected_pair_detail = None

# 實例化管理器
if 'pro_db_manager' not in st.session_state: st.session_state.pro_db_manager = ProDBManager()
if 'scheme_manager' not in st.session_state: st.session_state.scheme_manager = SchemeManager()
if 'wca_service' not in st.session_state: st.session_state.wca_service = WCAService()

# --- 3. 全域介面 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #fafafa; }
    div.stButton > button { width: 100%; border-radius: 12px; font-family: 'JetBrains Mono'; font-weight: bold; font-size: 20px; border: 2px solid #e0e0e0; background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.05); height: auto; min-height: 60px; transition: 0.3s; }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(108, 92, 231, 0.2); border-color: #6c5ce7; color: #6c5ce7; z-index: 100; }
    .scramble-box { background-color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-family: 'JetBrains Mono', font-size: 24px; color: #333; margin-bottom: 15px; border: 1px solid #eee; }
    .cube-face-container { padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center; background-color: white; border: 1px solid #eee; }
    div[data-testid="stTextInput"] input { text-align: center !important; font-weight: 800 !important; font-size: 18px !important; }
</style>
""", unsafe_allow_html=True)

# --- 參數與模型載入 ---
MODEL_FILE = "3bld_predictor.pkl"
HISTORY_FILE = "3bld_history.csv"

@st.cache_resource
def load_prediction_model():
    if os.path.exists(MODEL_FILE):
        try: return joblib.load(MODEL_FILE)
        except: return None
    return None

if 'predictor' not in st.session_state: st.session_state.predictor = load_prediction_model()

# ==========================================
# 側邊欄
# ==========================================
with st.sidebar:
    st.title("🧩 3BLD Pro")
    st.caption("Professional Training Suite")
    st.divider()
    mode = st.radio("功能模式", ["📊 練習數據", "🏆 戰力卡", "⚙️ 編碼設定"], horizontal=True, label_visibility="collapsed")
    
    if mode == "📊 練習數據":
        with st.expander("進階工具"):
            if st.button("🧠 重新訓練 AI"):
                ok, msg = train_model()
                if ok: 
                    st.success(msg)
                    load_prediction_model.clear()
                    st.session_state.predictor = load_prediction_model()
                else: st.error(msg)

# ==========================================
# 主畫面邏輯
# ==========================================

# --- 模式 1：戰力卡 (含雷達圖 + 旗艦卡片 + MBLD 優化) ---
if mode == "🏆 戰力卡":
    st.markdown("## 🆔 選手戰力分析")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        wca_input = st.text_input("輸入 WCA ID", value="", placeholder="例如: 2015WANG09").upper()
    with col2:
        st.write("") # Spacer
        st.write("")
        search_btn = st.button("🔍 查詢", use_container_width=True)

    # 查詢與顯示邏輯
    if search_btn and wca_input:
        with st.spinner(f"正在連線 WCA 資料庫查詢 {wca_input}..."):
            data = st.session_state.wca_service.get_user_data(wca_input)
            parsed = st.session_state.wca_service.parse_stats_for_card(data)
            if parsed:
                st.session_state.wca_data = parsed
            else:
                st.error("找不到此 ID 或發生錯誤，請確認 ID 是否正確。")
                st.session_state.wca_data = None

    if st.session_state.get('wca_data'):
        parsed = st.session_state.wca_data
        p = parsed['profile']
        records = parsed['all_records']
        
        # 下拉選單切換項目
        event_options = list(records.keys())
        if event_options:
            def format_func(evt_id):
                return f"{records[evt_id]['name']} ({evt_id})"
            
            default_idx = 0
            if parsed['best_event_id'] in event_options:
                default_idx = event_options.index(parsed['best_event_id'])

            st.write("---")
            selected_event = st.selectbox(
                "⭐ 選擇您的主打項目 (預設為國家排名最高項)", 
                options=event_options, 
                format_func=format_func,
                index=default_idx
            )
            
            stats = records[selected_event]
            m = p['medals']
            medals_html = "".join([f'<span class="badge gold">🥇 {m["gold"]}</span>' if m['gold']>0 else "",
                                  f'<span class="badge silver">🥈 {m["silver"]}</span>' if m['silver']>0 else "",
                                  f'<span class="badge bronze">🥉 {m["bronze"]}</span>' if m['bronze']>0 else ""])
            if not medals_html: medals_html = '<span class="badge normal">參賽選手</span>'

            # --- 🔥 MBLD 特殊處理邏輯 ---
            is_mbld = (selected_event == '333mbf')
            
            if is_mbld:
                # 多盲模式：單欄置中，不顯示平均
                grid_style = "grid-template-columns: 1fr; max-width: 600px; margin: 20px auto;"
                avg_box_html = "" # 空字串，隱藏平均
            else:
                # 一般模式：雙欄並排
                grid_style = "grid-template-columns: 1fr 1fr;"
                
                # 🔥 關鍵修正：這裡也要用 textwrap.dedent 來消除縮排，否則會變成程式碼區塊
                avg_box_html = textwrap.dedent(f"""
                <div class="stat-box">
                    <div class="stat-label">Best Average</div>
                    <div class="stat-val">{stats['avg_time']}</div>
                    <div class="rank-row">
                        <span class="rank-tag" title="National Rank">NR #{stats.get('avg_nr', '-')}</span>
                        <span class="rank-world" title="World Rank">WR #{stats.get('avg_wr', '-')}</span>
                    </div>
                </div>
                """)

            # --- 旗艦版 HTML ---
            card_html = textwrap.dedent(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Roboto:wght@400;700&display=swap');
.player-card {{ background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); border-radius: 24px; padding: 30px; color: white; box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); font-family: 'Roboto', sans-serif; position: relative; overflow: hidden; }}
.header-flex {{ display: flex; align-items: center; margin-bottom: 25px; }}
.avatar {{ width: 110px; height: 110px; border-radius: 50%; border: 4px solid #fff; box-shadow: 0 0 20px rgba(79,172,254,0.6); object-fit: cover; margin-right: 25px; }}
.info h2 {{ margin: 0; font-size: 32px; font-weight: 700; color: #fff; font-family: 'Russo One', sans-serif; }}
.badge {{ padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; margin-right: 5px; background: rgba(255,255,255,0.1); }}
.gold {{ background: linear-gradient(45deg, #FFD700, #FDB931); color: #333; }}
.silver {{ background: linear-gradient(45deg, #E0E0E0, #BDBDBD); color: #333; }}
.bronze {{ background: linear-gradient(45deg, #CD7F32, #A0522D); color: #fff; }}
.normal {{ background: rgba(255,255,255,0.15); color: #ddd; }}
.stats-grid {{ display: grid; {grid_style} gap: 20px; margin-top: 20px; }}
.stat-box {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 16px; text-align: center; border: 1px solid rgba(255,255,255,0.05); transition: 0.3s; }}
.stat-box:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-5px); border-color: #4facfe; }}
.stat-val {{ font-size: 36px; font-weight: 700; font-family: 'Russo One', sans-serif; color: #fff; }}
.stat-label {{ font-size: 13px; opacity: 0.7; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }}
.rank-row {{ display: flex; justify-content: center; gap: 10px; margin-top: 8px; font-size: 13px; }}
.rank-tag {{ background: #ff416c; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
.rank-world {{ background: #3a3f55; color: #ccc; padding: 2px 8px; border-radius: 4px; }}
</style>
<div class="player-card">
<div class="header-flex">
<img class="avatar" src="{p['avatar_url']}">
<div class="info">
<h2>{p['name']}</h2>
<p>{p['country']} | {p['wca_id']}</p>
<div class="badge-row">
<span class="badge">📅 {p['competition_count']} 場比賽</span>
{medals_html}
</div>
</div>
</div>
<div style="color: #4facfe; font-weight: bold; margin-bottom: 10px; letter-spacing: 1px;">🔥 專長項目：{stats['name']}</div>
<div class="stats-grid">
<div class="stat-box">
<div class="stat-label">Best Single</div>
<div class="stat-val">{stats['single_time']}</div>
<div class="rank-row">
<span class="rank-tag" title="National Rank">NR #{stats['single_nr']}</span>
<span class="rank-world" title="World Rank">WR #{stats['single_wr']}</span>
</div>
</div>
{avg_box_html}
</div>
</div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)
            
            # --- 🔥 五力雷達圖 ---
            st.markdown("### 📊 綜合能力分析 (Radar Analysis)")
            
            def get_time_score(evt_id, wr_seconds):
                if evt_id not in records: return 0
                try:
                    t_str = records[evt_id]['single_time']
                    if t_str in ['--', 'DNF', '特殊格式']: return 0
                    
                    # 處理 MBLD 的字串 (例如 "8/10 53:34")
                    if evt_id == '333mbf' and ' ' in t_str:
                        parts = t_str.split(' ')[0].split('/') # ["8", "10"]
                        solved = int(parts[0])
                        score = (solved / 30) * 100 
                        return min(int(score), 100)

                    # 處理 分:秒.厘 格式
                    if ':' in t_str:
                        parts = t_str.split(':') # ["1", "05.23"]
                        m = int(parts[0])
                        s = float(parts[1])
                        t_val = m * 60 + s
                    else:
                        t_val = float(t_str)

                    if t_val == 0: return 0
                    score = (wr_seconds / t_val) * 100
                    return min(int(score), 100)
                except: return 0

            score_speed = get_time_score('333', 3.13)
            score_blind = get_time_score('333bf', 12.00)
            score_oh = get_time_score('333oh', 6.20)
            score_big = get_time_score('555', 32.88)
            score_exp = min(int((p['competition_count'] / 50) * 100), 100)
            
            categories = ['速解力 (Speed)', '盲解力 (Blind)', '單手力 (OH)', '高階力 (Big Cube)', '經驗值 (Exp)']
            values = [score_speed, score_blind, score_oh, score_big, score_exp]
            values.append(values[0]) # 閉合
            categories.append(categories[0]) # 閉合

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=p['name'],
                line=dict(color='#00d2ff'),
                fillcolor='rgba(0, 210, 255, 0.2)', 
                marker=dict(size=8, color='#00d2ff')
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color='gray'), gridcolor='rgba(0,0,0,0.1)'),
                    angularaxis=dict(tickfont=dict(size=14, color='#333'), gridcolor='rgba(0,0,0,0.1)'),
                    bgcolor='rgba(0,0,0,0)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=20, b=20),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("這位選手尚未參加過任何比賽，沒有成績資料。")

# --- 模式 2：編碼設定 ---
elif mode == "⚙️ 編碼設定":
    st.markdown("## ⚙️ 記憶編碼自定義")
    with st.form("scheme_form"):
        current = st.session_state.scheme_manager.scheme
        def face_grid(face_name, keys, css_class):
            st.markdown(f"<div class='cube-face-container {css_class}'><div class='face-label'>{face_name}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i in range(3): cols[i].text_input("", value=current[face_name].get(keys[i], ""), key=f"{face_name}_{keys[i]}", label_visibility="collapsed")
            cols = st.columns(3)
            cols[0].text_input("", value=current[face_name].get(keys[3], ""), key=f"{face_name}_{keys[3]}", label_visibility="collapsed")
            cols[1].markdown(f"<div style='height:42px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:24px;'>{face_name}</div>", unsafe_allow_html=True)
            cols[2].text_input("", value=current[face_name].get(keys[5], ""), key=f"{face_name}_{keys[5]}", label_visibility="collapsed")
            cols = st.columns(3)
            for i in range(3): cols[i].text_input("", value=current[face_name].get(keys[6+i], ""), key=f"{face_name}_{keys[6+i]}", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 手動綁定 Session State
            for i, k in enumerate(keys):
                widget_key = f"{face_name}_{k}"
                if widget_key in st.session_state:
                    current[face_name][k] = st.session_state[widget_key]

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
            st.success("編碼方案已更新！")
            st.rerun()

# --- 模式 3：練習數據 (預設) ---
else:
    # 詳情頁面
    if st.session_state.selected_pair_detail:
        pair_data = st.session_state.selected_pair_detail
        u_code = pair_data['user_code']
        if st.button("⬅️ 返回列表", type="secondary"):
            st.session_state.selected_pair_detail = None
            st.rerun()
        st.markdown("---")
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown(f"<div class='detail-code'>{u_code}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-sub'>原始位置: {pair_data['pair_code']}</div>", unsafe_allow_html=True)
            st.markdown("#### 📝 公式")
            st.markdown(f"<div class='alg-box'>{pair_data['alg']}</div>", unsafe_allow_html=True)
            safe_alg = urllib.parse.quote(pair_data['alg'])
            url = f"https://alg.cubing.net/?alg={safe_alg}&type=alg&view=playback"
            components.iframe(url, height=300)
        with col_right:
            st.markdown("#### 🧠 記憶輔助")
            new_word_input = st.text_input("手動新增", label_visibility="collapsed", placeholder="輸入新詞彙...")
            if st.button("➕ 新增"):
                if st.session_state.pro_db_manager.add_word(u_code, new_word_input):
                    st.toast(f"已加入：{new_word_input}", icon="✅")
                    st.rerun()
            st.caption("我的 Letter Pairs")
            pro_words = st.session_state.pro_db_manager.get_words(u_code)
            if pro_words:
                for w in pro_words:
                    st.markdown(f"<span class='word-tag'>{w}</span>", unsafe_allow_html=True)
    else:
        # 計時器主畫面
        if st.session_state.timer_state != 'RUNNING':
            st.markdown(f'<div class="scramble-box">{st.session_state.current_scramble}</div>', unsafe_allow_html=True)
            
            ai_text = "🤖 AI 未訓練"
            score_val = 0.0
            
            if st.session_state.predictor:
                try:
                    tmp_solver = BlindSolver()
                    tmp_trans = ScrambleTranslator()
                    real_s = tmp_trans.translate(st.session_state.current_scramble)
                    if tmp_solver.solve(real_s):
                        s = tmp_solver.analysis
                        score_val = s.get('difficulty_score', 0)
                        feat = pd.DataFrame([{
                            "Total_Targets": s['Edges']['targets'] + s['Corners']['targets'],
                            "Total_Cycles": s['Edges']['cycles'] + s['Corners']['cycles'],
                            "Parity": 1 if s['Parity'] else 0,
                            "Flips": s['Edges']['flips'],
                            "Twists": s['Corners']['twists'],
                            "Difficulty_Score": score_val
                        }])
                        pred = st.session_state.predictor.predict(feat.fillna(0))[0]
                        ai_text = f"🤖 AI 預測: **{pred:.2f}s**"
                except: pass

            c1, c2 = st.columns([4, 1])
            with c1: st.info(f"{ai_text} | 難度: {score_val:.2f}")
            with c2: 
                if st.button("📋 分析"): 
                    st.session_state.show_analysis = not st.session_state.show_analysis

            if st.session_state.show_analysis or st.session_state.last_solve_result:
                if st.session_state.show_analysis:
                    try:
                        t_trans = ScrambleTranslator()
                        t_real = t_trans.translate(st.session_state.current_scramble)
                        t_solver = BlindSolver()
                        t_solver.solve(t_real)
                        data_source = {"edge": t_solver.edge_result, "corner": t_solver.corner_result, "parity": t_solver.has_parity, "logs": t_solver.logs}
                    except: data_source = None
                else: data_source = st.session_state.last_solve_result

                if data_source:
                    e_res = data_source['edge']
                    c_res = data_source['corner']
                    def render_btn_group(title, color, items, prefix=""):
                        if not items: return
                        st.markdown(f'<div style="color:{color}; font-weight:bold; margin:10px 0;">{title}</div>', unsafe_allow_html=True)
                        cols = st.columns(4)
                        for idx, item in enumerate(items):
                            if item.get('is_parity') or item.get('is_pseudo'): continue
                            pair_code = item['pair']
                            user_code = get_display_text(pair_code, st.session_state.scheme_manager)
                            with cols[idx % 4]:
                                if st.button(f"{prefix}{user_code}", key=f"{title}_{idx}"):
                                    st.session_state.selected_pair_detail = {"user_code": user_code, "pair_code": pair_code, "alg": item['alg']}
                                    st.rerun()
                    render_btn_group("Edges", "#1565C0", e_res.get('details', []))
                    st.markdown("---")
                    render_btn_group("Corners", "#E65100", c_res.get('details', []))

        # 計時器 HTML/JS
        timer_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; }}
            #timer {{ font-size: 160px; font-weight: 700; color: #2d3436; text-shadow: 4px 4px 0px #eee; line-height: 1.1; cursor: pointer; user-select: none; }}
            .idle {{ color: #2d3436; }} .holding {{ color: #d63031; }} .ready {{ color: #00b894; }} .running {{ color: #2d3436; }}
            #info {{ font-size: 16px; color: #aaa; margin-top: 5px; font-family: sans-serif; }}
        </style>
        </head>
        <body>
        <div id="timer" class="idle">0.00</div>
        <div id="info">長按空白鍵 (Space) 變綠後放開</div>
        <script>
            let state = 'IDLE'; let startTime = 0; let timerInterval;
            let timeDisplay = document.getElementById('timer');
            let infoDisplay = document.getElementById('info');
            function formatTime(ms) {{ return (ms / 1000).toFixed(2); }}
            function updateTimer() {{ timeDisplay.innerText = formatTime(Date.now() - startTime); }}
            document.addEventListener('keydown', (e) => {{
                if (e.code === 'Space') {{
                    e.preventDefault();
                    if (state === 'IDLE' || state === 'STOPPED') {{
                        state = 'HOLDING'; timeDisplay.className = 'holding'; timeDisplay.innerText = '0.00';
                        setTimeout(() => {{ if (state === 'HOLDING') {{ state = 'READY'; timeDisplay.className = 'ready'; }} }}, 300);
                    }} else if (state === 'RUNNING') {{
                        clearInterval(timerInterval); state = 'STOPPED';
                        let final = (Date.now() - startTime) / 1000;
                        timeDisplay.innerText = final.toFixed(2); timeDisplay.className = 'idle';
                        infoDisplay.innerText = "請在下方輸入成績";
                    }}
                }}
            }});
            document.addEventListener('keyup', (e) => {{
                if (e.code === 'Space') {{
                    if (state === 'READY') {{
                        state = 'RUNNING'; startTime = Date.now(); timeDisplay.className = 'running';
                        timerInterval = setInterval(updateTimer, 10);
                    }} else if (state === 'HOLDING') {{ state = 'IDLE'; timeDisplay.className = 'idle'; }}
                }}
            }});
        </script>
        </body>
        </html>
        """
        st.markdown("<div class='timer-box'>", unsafe_allow_html=True)
        components.html(timer_html, height=280)

        if st.session_state.timer_state == 'RUNNING':
            st.button("停止計時", key="stop_btn_main", disabled=True)
        elif st.session_state.timer_state == 'STOPPED':
            c1, c2 = st.columns([1, 2])
            with c1: input_time = st.number_input("⏱️ 輸入剛剛的秒數", min_value=0.0, step=0.01, format="%.2f", key="js_res_input")
            with c2:
                st.write("")
                st.write("")
                if st.button("✅ 提交成績 & 自動分析 (Next)", type="primary", use_container_width=True):
                    if input_time > 0:
                        final_time = input_time
                        this_scramble = st.session_state.current_scramble
                        st.session_state.session_times = st.session_state.sessions[st.session_state.current_session]
                        st.session_state.session_times.append({"time": final_time, "scramble": this_scramble, "raw_time": final_time, "penalty": "", "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        try:
                            trans = ScrambleTranslator()
                            real_s = trans.translate(this_scramble)
                            solver = BlindSolver()
                            if solver.solve(real_s):
                                save_to_db({"raw_time": final_time, "penalty": "", "scramble": this_scramble, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, solver.analysis)
                                st.session_state.last_solve_result = {"time": final_time, "scramble": this_scramble, "edge": solver.edge_result, "corner": solver.corner_result, "stats": solver.analysis, "parity": solver.has_parity, "logs": solver.logs}
                        except: pass
                        st.session_state.current_scramble = generate_scramble()
                        st.session_state.show_analysis = False
                        st.session_state.temp_result = None
                        st.session_state.selected_pair_detail = None
                        st.rerun()