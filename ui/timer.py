import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import urllib.parse
import google.generativeai as genai
from datetime import datetime

from solver import BlindSolver
from scramble_translator import ScrambleTranslator
from services.helpers import generate_scramble, save_to_db
from ui.analysis import render_analysis_results

def render_timer_page():
    # === 1. 詳細頁面 (當點擊編碼/Parity/Flip/Twist 按鈕後) ===
    if st.session_state.selected_pair_detail:
        render_detail_view()
        return

    # === 2. 計算解法 (如果需要) ===
    ai_val_num = 0.0
    ai_text = "--"
    score_val = 0.0
    solver_result = None

    if st.session_state.timer_state == 'IDLE' or st.session_state.timer_state == 'STOPPED':
            try:
                tmp_solver = BlindSolver()
                tmp_trans = ScrambleTranslator()
                real_s = tmp_trans.translate(st.session_state.current_scramble)
                if tmp_solver.solve(real_s):
                    solver_result = tmp_solver
                    s = tmp_solver.analysis
                    score_val = s.get('difficulty_score', 0)
                    if st.session_state.predictor:
                        feat = pd.DataFrame([{
                            "Total_Targets": s['Edges']['targets'] + s['Corners']['targets'],
                            "Total_Cycles": s['Edges']['cycles'] + s['Corners']['cycles'],
                            "Parity": 1 if s['Parity'] else 0,
                            "Flips": s['Edges']['flips'],
                            "Twists": s['Corners']['twists'],
                            "Difficulty_Score": score_val
                        }])
                        pred = st.session_state.predictor.predict(feat.fillna(0))[0]
                        ai_val_num = pred
                        ai_text = f"{pred:.2f}s"
            except Exception as e: st.error(f"解算器錯誤: {e}")

    # === 3. 分析結果頁面 ===
    if st.session_state.show_analysis:
        st.markdown(f'<div class="scramble-box">{st.session_state.current_scramble}</div>', unsafe_allow_html=True)
        
        if st.button("⬅️ 返回計時器", use_container_width=True, type="secondary"):
            st.session_state.show_analysis = False
            st.session_state.ai_word_suggestion = ""
            st.rerun()

        if solver_result:
            render_analysis_results(solver_result, ai_val_num, ai_text)
        return

    # === 4. 正常計時介面 ===
    col_scr, col_btn = st.columns([5, 1])
    with col_scr:
        new_scramble = st.text_area("打亂 (Scramble)", value=st.session_state.current_scramble, height=70, label_visibility="collapsed")
    with col_btn:
        if st.button("🎲", use_container_width=True, help="隨機生成"):
            st.session_state.current_scramble = generate_scramble()
            st.rerun()
    if new_scramble != st.session_state.current_scramble:
        st.session_state.current_scramble = new_scramble

    c1, c2 = st.columns([4, 1])
    with c1: st.info(f"AI 預測: {ai_text}")
    with c2: 
        if st.button("📋 分析", use_container_width=True): 
            st.session_state.show_analysis = True
            st.rerun()

    # Timer HTML
    timer_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { margin: 0; padding: 0; background-color: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; }
        #timer { font-size: 160px; font-weight: 700; color: #fff; text-shadow: 0 0 20px rgba(255,255,255,0.2); line-height: 1.1; cursor: pointer; user-select: none; }
        .idle { color: #fff; } .holding { color: #ff0055; text-shadow: 0 0 20px #ff0055; } .ready { color: #00ff99; text-shadow: 0 0 20px #00ff99; } .running { color: #fff; }
        #info { font-size: 16px; color: #888; margin-top: 5px; font-family: sans-serif; }
    </style>
    </head>
    <body>
    <div id="timer" class="idle">0.00</div>
    <div id="info">長按空白鍵 (Space) 變綠後放開</div>
    <script>
        let state = 'IDLE'; let startTime = 0; let timerInterval;
        let timeDisplay = document.getElementById('timer');
        let infoDisplay = document.getElementById('info');
        function formatTime(ms) { return (ms / 1000).toFixed(2); }
        function updateTimer() { timeDisplay.innerText = formatTime(Date.now() - startTime); }
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                if (state === 'IDLE' || state === 'STOPPED') {
                    state = 'HOLDING'; timeDisplay.className = 'holding'; timeDisplay.innerText = '0.00';
                    setTimeout(() => { if (state === 'HOLDING') { state = 'READY'; timeDisplay.className = 'ready'; } }, 300);
                } else if (state === 'RUNNING') {
                    clearInterval(timerInterval); state = 'STOPPED';
                    let final = (Date.now() - startTime) / 1000;
                    timeDisplay.innerText = final.toFixed(2); timeDisplay.className = 'idle';
                    infoDisplay.innerText = "請在下方輸入成績";
                }
            }
        });
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                if (state === 'READY') {
                    state = 'RUNNING'; startTime = Date.now(); timeDisplay.className = 'running';
                    timerInterval = setInterval(updateTimer, 10);
                } else if (state === 'HOLDING') { state = 'IDLE'; timeDisplay.className = 'idle'; }
            }
        });
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
            st.write(""); st.write("")
            if st.button("✅ 提交成績 (Next)", type="primary", use_container_width=True):
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
                    st.session_state.ai_word_suggestion = ""
                    st.session_state.selected_pair_detail = None
                    st.rerun()

def render_detail_view():
    pair_data = st.session_state.selected_pair_detail
    u_code = pair_data['user_code']
    if st.button("⬅️ 返回"): 
        st.session_state.selected_pair_detail = None
        st.session_state.ai_word_suggestion = None 
        st.rerun()
        
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown(f"<h2 style='color:#00FFA3;'>{u_code}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div>原始位置: {pair_data['pair_code']}</div>", unsafe_allow_html=True)
        st.markdown("#### 📝 公式")
        st.markdown(f"<div class='scramble-box' style='font-size:18px;'>{pair_data['alg']}</div>", unsafe_allow_html=True)
        safe_alg = urllib.parse.quote(pair_data['alg'])
        url = f"https://alg.cubing.net/?alg={safe_alg}&type=alg&view=playback"
        components.iframe(url, height=300)
        
    with col_right:
        st.markdown("#### 🧠 記憶輔助")
        c1, c2 = st.columns([3, 1])
        with c1: new_word_input = st.text_input("手動新增", label_visibility="collapsed", placeholder="輸入新詞彙...")
        with c2:
            if st.button("➕ 新增"):
                if st.session_state.pro_db_manager.add_word(u_code, new_word_input):
                    st.toast(f"已加入：{new_word_input}", icon="✅"); st.rerun()
        
        st.caption("我的 Letter Pairs")
        pro_words = st.session_state.pro_db_manager.get_words(u_code)
        if pro_words:
            for w in pro_words: st.markdown(f"<span style='background:#333; padding:5px 10px; border-radius:5px; margin:5px; display:inline-block;'>{w}</span>", unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 🤖 AI 靈感助手")
        if st.button("✨ 幫我想像 (Ask Gemini)", type="primary"):
            if not st.session_state.gemini_key:
                st.error("請先在側邊欄輸入 API Key")
            else:
                with st.spinner("AI 正在腦力激盪..."):
                    try:
                        genai.configure(api_key=st.session_state.gemini_key)
                        model = genai.GenerativeModel('gemini-pro')
                        prompt = f"我正在練習魔術方塊盲解，需要記憶一組編碼：【{u_code}】。請給我 3 個具體的、強烈的中文詞彙聯想。"
                        response = model.generate_content(prompt)
                        st.session_state.ai_word_suggestion = response.text
                    except Exception as e: st.error(f"AI 連線失敗: {e}")

        if st.session_state.get('ai_word_suggestion'):
            st.markdown(f"<div class='ai-suggestion-box'>{st.session_state.ai_word_suggestion}</div>", unsafe_allow_html=True)