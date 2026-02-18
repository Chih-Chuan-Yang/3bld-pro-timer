import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&family=Russo+One&display=swap');
        
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        h1, h2, h3, h4, h5 { color: #FFFFFF; font-family: 'Russo One', sans-serif !important; }

        /* 數據卡片 */
        .stats-card {
            background: #1e2130; padding: 20px; border-radius: 12px;
            border: 1px solid #333; text-align: center; margin-bottom: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .stats-val { font-size: 32px; font-weight: bold; color: #00FFA3; font-family: 'JetBrains Mono'; margin-bottom: 5px; }
        .stats-label { font-size: 14px; color: #aaa; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
        
        /* 按鈕樣式 */
        div.stButton > button { 
            width: 100%; border-radius: 12px; font-family: 'JetBrains Mono'; font-weight: bold; 
            font-size: 22px; border: none; background: #2b5876; color: white;
            height: auto; min-height: 70px; transition: 0.2s; 
        }
        div.stButton > button:hover { 
            transform: translateY(-3px); background: #3a4150; color: #00FFA3;
            box-shadow: 0 5px 15px rgba(0, 255, 163, 0.2);
        }
        div.stButton > button[kind="primary"] { background: linear-gradient(45deg, #FF0099, #493240); }

        /* 輸入框優化 */
        div[data-testid="stTextArea"] textarea {
            font-family: 'JetBrains Mono', monospace; font-size: 24px !important; line-height: 1.5;
            background-color: #1A1C24; color: #00FFA3; border: 1px dashed #444; text-align: center;
        }
        div[data-testid="stTextInput"] input { 
            text-align: center !important; font-weight: 800 !important; font-size: 18px !important; 
            background-color: #333; color: white; border: 1px solid #555;
        }

        /* 記憶序列 */
        .memo-sequence {
            display: flex; flex-wrap: wrap; gap: 10px; align-items: center; 
            background: #12141a; padding: 20px; border-radius: 12px; 
            border-left: 5px solid #00FFA3; margin-bottom: 20px;
        }
        .memo-char {
            background: #2d3436; color: #fff; padding: 8px 16px; border-radius: 8px; 
            font-family: 'JetBrains Mono'; font-weight: bold; font-size: 24px; border: 1px solid #444;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .memo-break {
            color: #FF0055; font-weight: 900; font-size: 28px; margin: 0 15px; font-family: 'JetBrains Mono';
            text-shadow: 0 0 10px rgba(255,0,85,0.5);
        }
        .memo-visual {
            background: rgba(255, 170, 0, 0.15); color: #FFAA00; border: 1px solid #FFAA00;
            padding: 8px 16px; border-radius: 8px; font-size: 18px; font-weight: bold;
        }
        .memo-parity {
            background: rgba(255, 0, 85, 0.15); color: #FF0055; border: 1px solid #FF0055;
            padding: 8px 16px; border-radius: 8px; font-size: 18px; font-weight: bold;
        }
        
        /* AI 建議 */
        .ai-suggestion-box {
            background-color: #1a1c24; border-left: 4px solid #9b59b6; padding: 15px;
            border-radius: 6px; margin-top: 10px; font-size: 16px; color: #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)