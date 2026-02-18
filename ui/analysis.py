import streamlit as st
from services.helpers import get_display_text

def render_analysis_results(solver_result, ai_val_num, ai_text):
    s = solver_result.analysis
    e_res = solver_result.edge_result
    c_res = solver_result.corner_result

    # --- Helper Functions ---
    def count_real_moves(alg_str):
        if not alg_str: return 0
        clean = alg_str.split('//')[0].replace('(', '').replace(')', '')
        moves = [m for m in clean.split(' ') if m.strip()]
        return len(moves)

    def get_twist_info(t):
        if isinstance(t, dict): return t.get('part', '?'), t.get('dir', 0)
        return str(t), 1

    def get_twist_dir_text(direction):
        if direction == 1: return "(逆)" 
        return "(順)" 

    # --- 1. 數據統計 ---
    st.markdown("### 📊 數據統計 (Stats)")
    total_moves = 0
    total_algs = 0
    
    for item in e_res.get('details', []):
        total_moves += count_real_moves(item.get('alg', ''))
        total_algs += 1
    for item in c_res.get('details', []):
        total_moves += count_real_moves(item.get('alg', ''))
        total_algs += 1
    for f in e_res.get('flips_detailed', []):
        total_moves += count_real_moves(f.get('alg', ''))
        total_algs += 1
    for t in c_res.get('twists_detailed', []):
        total_moves += count_real_moves(t.get('alg', ''))
        total_algs += 1

    tps_text = "--"
    if ai_val_num > 0 and total_moves > 0:
        tps = total_moves / ai_val_num
        tps_text = f"{tps:.1f}"

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.markdown(f"<div class='stats-card'><div class='stats-val'>{total_algs}</div><div class='stats-label'>Total Algs</div></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div class='stats-card'><div class='stats-val'>{total_moves}</div><div class='stats-label'>Real Moves</div></div>", unsafe_allow_html=True)
    sc3.markdown(f"<div class='stats-card'><div class='stats-val'>{ai_text}</div><div class='stats-label'>AI Predicted</div></div>", unsafe_allow_html=True)
    sc4.markdown(f"<div class='stats-card'><div class='stats-val'>{tps_text}</div><div class='stats-label'>Est. TPS</div></div>", unsafe_allow_html=True)

    st.divider()

    # --- 2. 記憶階段 ---
    st.markdown("### 🧠 記憶階段 (Memory)")
    
    def render_memo_sequence(items_detailed, visuals_html, scheme):
        html_content = "<div class='memo-sequence'>"
        for idx, item in enumerate(items_detailed):
            if item.get('is_parity') or item.get('is_pseudo'): continue
            
            # 🔴 斷圈顯示 (讀取 is_new_cycle)
            if item.get('is_new_cycle', False) and idx > 0:
                    html_content += "<span class='memo-break'>//</span>"
            
            pair_code = item.get('pair', '')
            uc = get_display_text(pair_code, scheme)
            for char in uc:
                    html_content += f"<span class='memo-char'>{char}</span>"
        
        if visuals_html:
            html_content += "<span class='memo-break'>+</span>" + visuals_html
        
        if items_detailed and items_detailed[-1].get('is_parity'):
            html_content += "<span class='memo-break'>+</span><span class='memo-parity'>Parity</span>"

        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)

    # Visuals
    twist_html = ""
    for t_key, t_info in c_res.get('twists', {}).items():
        direction = t_info.get('direction', 0)
        dir_text = get_twist_dir_text(direction)
        twist_html += f"<span class='memo-visual'>{t_key} {dir_text}</span>"

    flip_html = ""
    for f in e_res.get('flips', []):
        f_part = f['part'] if isinstance(f, dict) else f
        flip_html += f"<span class='memo-visual'>{f_part}</span>"

    st.markdown("#### 1. 角塊 (Corners)")
    render_memo_sequence(c_res.get('path_detailed', []), twist_html, st.session_state.scheme_manager)
    
    st.markdown("#### 2. 邊塊 (Edges)")
    render_memo_sequence(e_res.get('path_detailed', []), flip_html, st.session_state.scheme_manager)

    st.divider()

    # --- 3. 執行階段 ---
    st.markdown("### ⚔️ 執行階段 (Execution)")

    def render_btn_group(title, color, items):
        if not items: return
        st.markdown(f'<div style="color:{color}; font-weight:bold; margin:10px 0; font-size:18px;">{title} ({len(items)})</div>', unsafe_allow_html=True)
        cols = st.columns(4) 
        for idx, item in enumerate(items):
            if item.get('is_parity') or item.get('is_pseudo'): continue
            pair_raw = item.get('pair', '')
            uc = get_display_text(pair_raw, st.session_state.scheme_manager)
            with cols[idx % 4]:
                if st.button(f"{uc}", key=f"{title}_{idx}", use_container_width=True):
                    st.session_state.selected_pair_detail = {"user_code": uc, "pair_code": pair_raw, "alg": item.get('alg', 'No Alg')}
                    st.rerun()
    
    render_btn_group("1. 邊塊 (Edges)", "#42A5F5", e_res.get('details', []))

    flips_detailed = e_res.get('flips_detailed', [])
    if flips_detailed:
        st.markdown(f'<div style="color:#00D2FF; font-weight:bold; margin:10px 0; font-size:18px;">2. 邊塊翻轉 (Edge Flips)</div>', unsafe_allow_html=True)
        f_cols = st.columns(4)
        for idx, f in enumerate(flips_detailed):
            f_part = f.get('part', 'Unknown')
            f_alg = f.get('alg', 'No Alg')
            with f_cols[idx % 4]:
                if st.button(f"🔄 {f_part}", key=f"flip_{idx}", use_container_width=True):
                    st.session_state.selected_pair_detail = {"user_code": f"Flip {f_part}", "pair_code": "Flip", "alg": f_alg}
                    st.rerun()

    render_btn_group("3. 角塊 (Corners)", "#FFA726", c_res.get('details', []))

    if solver_result.has_parity:
        st.markdown(f'<div style="color:#FF0055; font-weight:bold; margin:10px 0; font-size:18px;">4. 奇偶校驗 (Parity)</div>', unsafe_allow_html=True)
        target_display = "?"
        parity_target = c_res.get('parity_target')
        if parity_target: target_display = get_display_text(parity_target, st.session_state.scheme_manager)
        p_cols = st.columns(4)
        with p_cols[0]:
            btn_label = f"⚠️ Parity (Target: {target_display})"
            p_alg = "需執行 Parity 公式"
            for d in c_res.get('details', []):
                if d.get('is_parity'): p_alg = d.get('alg', p_alg); break
            if st.button(btn_label, key="parity_btn", type="primary", use_container_width=True):
                    st.session_state.selected_pair_detail = {"user_code": "Parity", "pair_code": "Parity", "alg": p_alg}
                    st.rerun()

    twists_detailed = c_res.get('twists_detailed', [])
    if twists_detailed:
        st.markdown(f'<div style="color:#FFAA00; font-weight:bold; margin:10px 0; font-size:18px;">5. 角塊色向 (Corner Twists)</div>', unsafe_allow_html=True)
        t_cols = st.columns(4)
        for idx, t in enumerate(twists_detailed):
            part = t.get('part', '?')
            direction = t.get('dir', 0)
            dir_str = get_twist_dir_text(direction)
            t_alg = t.get('alg', 'No Alg')
            with t_cols[idx % 4]:
                if st.button(f"🌀 {part} {dir_str}", key=f"twist_{idx}", use_container_width=True):
                    st.session_state.selected_pair_detail = {"user_code": f"Twist {part}", "pair_code": "Twist", "alg": t_alg}
                    st.rerun()

    # 參考表
    with st.expander("🔍 角塊色向參考表 (Twist Reference)"):
        st.markdown("""
        **註：顯示的代號代表該位置在打亂時，白色/黃色面所朝向的貼紙名稱**
        | 位置 (Pos) | 順時針 (CW, 1) | 逆時針 (CCW, -1) |
        | :--- | :--- | :--- |
        | **UBL** | BUL | LUB |
        | **UBR** | RUB | BUR |
        | **UFR** | FUR | RUF |
        | **UFL** | LUF | FUL |
        | **DFL** | FDL | LDF |
        | **DFR** | RDF | FDR |
        | **DBR** | BDR | RDB |
        | **DBL** | LDB | BDL |
        """)