import streamlit as st

def render_battle_card():
    # --- 🎨 專屬戰力卡 CSS ---
    st.markdown("""
    <style>
        /* --- 🔥 破解 Streamlit 的輸入框外層限制 --- */
        div[data-testid="stTextInput"] {
            height: 85px !important;
        }
        
        div[data-testid="stTextInput"] div[data-baseweb="input"] {
            height: 85px !important;
            border-radius: 16px !important;
            background-color: #12141A !important;
            border: 2px solid #3A3F58 !important;
            box-shadow: inset 0 4px 10px rgba(0,0,0,0.6) !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #00FFA3 !important;
            box-shadow: 0 0 20px rgba(0, 255, 163, 0.4), inset 0 2px 5px rgba(0,0,0,0.5) !important;
        }
        
        div[data-testid="stTextInput"] input {
            height: 100% !important;
            font-size: 32px !important;
            font-weight: 900 !important;
            text-align: center !important;
            color: #00FFA3 !important;
            -webkit-text-fill-color: #00FFA3 !important; 
            padding: 0 !important;
        }
        
        div[data-testid="stTextInput"] input::placeholder {
            color: #7887A5 !important;
            -webkit-text-fill-color: #7887A5 !important;
            font-size: 22px !important;
            font-weight: 600 !important;
            letter-spacing: 1.5px !important;
        }
        
        /* 🔥 放大鏡按鈕 (全透明 + 發光互動) */
        .search-btn-container button {
            height: 85px !important; 
            min-height: 85px !important;
            font-size: 40px !important; 
            border-radius: 16px !important;
            background: transparent !important; 
            border: none !important;
            outline: none !important;
            box-shadow: none !important; 
            color: #7887A5 !important; 
            transition: all 0.3s ease !important;
            padding: 0 !important;
        }
        .search-btn-container button:hover {
            background: transparent !important; 
            color: #00FFA3 !important; 
            text-shadow: 0 0 20px rgba(0, 255, 163, 1) !important; 
            transform: scale(1.15) !important; 
        }

        /* --- 戰力卡主體 --- */
        .battle-card {
            background: linear-gradient(180deg, #161821 0%, #0d0f14 100%);
            border: 1px solid #333;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
            margin-top: 20px;
            margin-bottom: 40px;
        }
        .avatar-img {
            border-radius: 16px;
            border: 2px solid #444;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
            width: 100%;
            max-width: 250px;
            object-fit: cover;
            display: block;
            margin: 0 auto;
        }
        
        /* 基本資料 */
        .profile-name { 
            font-size: 42px; font-weight: 900; color: #fff; 
            line-height: 1.1; margin-bottom: 5px; font-family: 'Russo One', sans-serif;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .profile-id { 
            font-size: 22px; color: #00FFA3; 
            font-family: 'JetBrains Mono', monospace; font-weight: bold;
            margin-bottom: 10px;
        }
        
        /* --- 獎牌區 --- */
        .medal-container { 
            display: flex; gap: 15px; margin-top: 20px; flex-wrap: wrap;
        }
        .medal-item { 
            flex: 1; min-width: 80px; text-align: center; padding: 15px 5px; 
            border-radius: 16px; background: rgba(0,0,0,0.4); 
            border: 1px solid rgba(255,255,255,0.05); 
            transition: transform 0.2s;
        }
        .medal-item:hover { transform: translateY(-5px); }
        .gold { border-bottom: 3px solid #FFD700; box-shadow: inset 0 -20px 30px -20px rgba(255, 215, 0, 0.2); }
        .silver { border-bottom: 3px solid #C0C0C0; box-shadow: inset 0 -20px 30px -20px rgba(192, 192, 192, 0.2); }
        .bronze { border-bottom: 3px solid #CD7F32; box-shadow: inset 0 -20px 30px -20px rgba(205, 127, 50, 0.2); }
        .m-icon { font-size: 36px; margin-bottom: -5px; }
        .m-count { font-size: 32px; font-weight: 900; font-family: 'JetBrains Mono'; color: #FFF;}
        .m-label { font-size: 14px; font-weight: bold; color: #AAA; display:block; margin-top:5px; letter-spacing:1px;}

        /* --- 炫泡 Signature Event --- */
        .signature-container { display: flex; flex-direction: column; justify-content: center; height: 100%;}
        .signature-event {
            background: linear-gradient(135deg, rgba(255, 0, 153, 0.15) 0%, rgba(0, 255, 163, 0.05) 100%);
            border: 2px solid #FF0099;
            padding: 25px 20px;
            border-radius: 16px;
            position: relative;
            box-shadow: 0 0 20px rgba(255, 0, 153, 0.3), inset 0 0 15px rgba(255, 0, 153, 0.1);
            text-align: center;
            animation: pulse-neon 2s infinite alternate;
        }
        @keyframes pulse-neon {
            0% { box-shadow: 0 0 15px rgba(255, 0, 153, 0.3), inset 0 0 10px rgba(255, 0, 153, 0.1); border-color: #FF0099; }
            100% { box-shadow: 0 0 35px rgba(255, 0, 153, 0.7), inset 0 0 25px rgba(255, 0, 153, 0.3); border-color: #FF55BB; }
        }
        .signature-title {
            color: #00FFA3; font-weight: 900; font-size: 14px; 
            letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;
            text-shadow: 0 0 8px rgba(0, 255, 163, 0.8);
        }
        .signature-name {
            font-size: 42px; font-weight: 900; color: #FFF; 
            font-family: "Russo One", sans-serif; 
            text-shadow: 3px 3px 0px #FF0099, -2px -2px 0px rgba(0, 255, 163, 0.5);
            margin-bottom: 20px; line-height: 1.2;
        }
        .signature-stats { display: flex; justify-content: center; gap: 15px; width: 100%; }
        
        .stat-box {
            background: rgba(0,0,0,0.6); padding: 12px 15px; border-radius: 10px; 
            border: 1px solid #FF0099; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        .stat-label { font-size:12px; color:#AAA; font-weight:bold; letter-spacing:1px; text-transform:uppercase;}
        .stat-val { font-size: 26px; color: #00FFA3; font-weight: 900; font-family: 'JetBrains Mono'; margin: 5px 0;}
        .stat-nr { font-size: 14px; color: #FFF; background: #FF0099; padding: 2px 8px; border-radius: 12px; font-weight: bold; display:inline-block;}

        /* --- 官方成績紀錄 Table --- */
        .record-table-container {
            background: #161821; border: 1px solid #333; border-radius: 16px; padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            overflow-x: auto;
        }
        .record-table { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono'; text-align: left; }
        .record-table th { 
            background: #1A1C24; color: #00FFA3; padding: 15px; 
            border-bottom: 2px solid #00FFA3; font-size: 16px; font-family: 'Russo One', sans-serif;
            letter-spacing: 1px;
        }
        .record-table td { padding: 15px; border-bottom: 1px solid #2A2D3A; color: #EEE; font-size: 18px; vertical-align: middle;}
        .record-table tr:hover { background: rgba(0, 255, 163, 0.05); }
        
        .rank-nr { color: #FFF; background: rgba(255,0,153,0.8); padding: 3px 8px; border-radius: 6px; font-size: 14px; font-weight:bold; font-family: sans-serif; margin-right:5px;}
        .rank-wr { color: #000; background: #FFD700; padding: 3px 8px; border-radius: 6px; font-size: 14px; font-weight:bold; font-family: sans-serif;}
        .rank-gray { color: #888; border: 1px solid #444; padding: 2px 8px; border-radius: 6px; font-size: 14px; font-family: sans-serif; margin-right:5px;}
        .event-name { font-weight: bold; color: #FFF; font-family: 'Inter', sans-serif; font-size: 20px;}
        .time-val { font-weight: bold; font-size: 24px; margin-bottom:5px; display:inline-block; margin-right: 10px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; margin-bottom:30px;'>🏆 選手戰力分析 (Battle Card)</h2>", unsafe_allow_html=True)
    
    # 搜尋列比例
    c_empty1, c_input, c_btn, c_empty2 = st.columns([0.5, 5.5, 0.8, 0.5])
    
    with c_input: 
        wca_input = st.text_input("輸入 WCA ID", value="", placeholder="輸入 WCA ID (例: 2015WANG09)", label_visibility="collapsed").upper()
    with c_btn: 
        st.markdown('<div class="search-btn-container">', unsafe_allow_html=True)
        search_btn = st.button("🔍", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if search_btn and wca_input:
        with st.spinner("🌐 連線 WCA 資料庫..."):
            data = st.session_state.wca_service.get_user_data(wca_input)
            if "error" in data:
                st.error(f"❌ {data['error']}")
                st.session_state.wca_data = None
            else:
                parsed = st.session_state.wca_service.parse_stats_for_card(data)
                st.session_state.wca_data = parsed if parsed else None

    if st.session_state.get('wca_data'):
        data = st.session_state.wca_data
        profile = data['profile']
        best_event = data['best_event_id']
        records = data['all_records']
        
        st.markdown("<div class='battle-card'>", unsafe_allow_html=True)
        
        col_img, col_info, col_sig = st.columns([1, 1.8, 2])
        
        with col_img:
            st.markdown(f'<img src="{profile["avatar_url"]}" class="avatar-img">', unsafe_allow_html=True)
            
        with col_info:
            st.markdown(f"<div class='profile-name'>{profile['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='profile-id'>🆔 {profile['wca_id']} 🇹🇼 {profile['country']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#AAA; font-size:16px;'>🏅 總參賽次數: <span style='color:#FFF; font-weight:bold; font-size:20px;'>{profile['competition_count']}</span> 場</div>", unsafe_allow_html=True)
            
            m = profile['medals']
            # 🔥 移除多餘縮排，寫成單行避免被當作 Markdown 程式碼區塊
            medal_html = f"<div class='medal-container'><div class='medal-item gold'><div class='m-icon'>🥇</div><span class='m-count'>{m.get('gold', 0)}</span><span class='m-label'>金牌</span></div><div class='medal-item silver'><div class='m-icon'>🥈</div><span class='m-count'>{m.get('silver', 0)}</span><span class='m-label'>銀牌</span></div><div class='medal-item bronze'><div class='m-icon'>🥉</div><span class='m-count'>{m.get('bronze', 0)}</span><span class='m-label'>銅牌</span></div></div>"
            st.markdown(medal_html, unsafe_allow_html=True)

        with col_sig:
            if best_event and best_event in records:
                be_data = records[best_event]
                has_avg = be_data['avg_time'] != "--"
                
                # 🔥 同樣改為單行 HTML，並處理好單次與平均的顯示比例
                if has_avg:
                    stats_html = f"<div class='signature-stats'><div class='stat-box' style='flex: 1;'><div class='stat-label'>Single</div><div class='stat-val'>{be_data['single_time']}</div><div class='stat-nr'>NR {be_data['single_nr']}</div></div><div class='stat-box' style='flex: 1;'><div class='stat-label'>Average</div><div class='stat-val'>{be_data['avg_time']}</div><div class='stat-nr'>NR {be_data['avg_nr']}</div></div></div>"
                else:
                    # 如果只有單次 (例如多顆盲解)，框框自動置中且放大到最大寬度的 70%
                    stats_html = f"<div class='signature-stats'><div class='stat-box' style='flex: 1; max-width: 70%;'><div class='stat-label'>Single (單次最佳)</div><div class='stat-val'>{be_data['single_time']}</div><div class='stat-nr'>NR {be_data['single_nr']}</div></div></div>"
                
                sig_html = f"<div class='signature-container'><div class='signature-event'><div class='signature-title'>★ Signature Event ★</div><div class='signature-name'>{be_data['name']}</div>{stats_html}</div></div>"
                st.markdown(sig_html, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### 📈 官方成績紀錄 (Official Records)")
        table_html = "<div class='record-table-container'><table class='record-table'>"
        table_html += "<tr><th>EVENT (項目)</th><th>SINGLE (單次最佳)</th><th>AVERAGE (平均最佳)</th></tr>"
        
        for ev_id, r in records.items():
            s_nr_val = str(r['single_nr'])
            s_wr_val = str(r['single_wr'])
            s_nr_badge = f"<span class='rank-nr'>NR {s_nr_val}</span>" if s_nr_val.isdigit() and int(s_nr_val) <= 100 else f"<span class='rank-gray'>NR {s_nr_val}</span>"
            s_wr_badge = f"<span class='rank-wr'>WR {s_wr_val}</span>" if s_wr_val.isdigit() and int(s_wr_val) <= 100 else ""
            
            a_nr_val = str(r['avg_nr'])
            a_wr_val = str(r['avg_wr'])
            a_nr_badge = ""
            a_wr_badge = ""
            if r['avg_time'] != "--":
                a_nr_badge = f"<span class='rank-nr'>NR {a_nr_val}</span>" if a_nr_val.isdigit() and int(a_nr_val) <= 100 else f"<span class='rank-gray'>NR {a_nr_val}</span>"
                a_wr_badge = f"<span class='rank-wr'>WR {a_wr_val}</span>" if a_wr_val.isdigit() and int(a_wr_val) <= 100 else ""
            
            table_html += f"<tr><td class='event-name'>{r['name']}</td><td><span class='time-val'>{r['single_time']}</span>{s_nr_badge}{s_wr_badge}</td><td><span class='time-val'>{r['avg_time']}</span>{a_nr_badge}{a_wr_badge}</td></tr>"
            
        table_html += "</table></div>"
        st.markdown(table_html, unsafe_allow_html=True)