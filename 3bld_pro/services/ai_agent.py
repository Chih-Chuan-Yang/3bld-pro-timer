import google.generativeai as genai
import json
import time

# 🔥 API Key 設定
HARDCODED_API_KEY = "AIzaSyD9PbOer9aENGPzBeDMMmhq7cP7UNn-Ccw"

AI_READY = False
try:
    genai.configure(api_key=HARDCODED_API_KEY)
    AI_READY = True
except Exception as e:
    print(f"AI Config Error: {e}")

def call_ai_with_fallback(prompt):
    if not AI_READY: return None
    
    # 優先順序：2.0 Flash -> 2.0 Flash Lite -> 1.5 Flash
    models_to_try = ['gemini-2.0-flash', 'gemini-2.0-flash-lite-001', 'gemini-flash-latest']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text
            # 清理 Markdown 標籤，確保是純 JSON
            if "```json" in text: text = text.replace("```json", "").replace("```", "")
            elif "```" in text: text = text.replace("```", "")
            return json.loads(text)
        except Exception as e:
            error_msg = str(e)
            # 如果是額度滿了 (429) 或找不到模型 (404)，就換下一個
            if "429" in error_msg or "404" in error_msg or "quota" in error_msg.lower():
                time.sleep(1)
                continue
            else: return None
    return None

def generate_single_pair_mnemonic(pair_text):
    prompt = f"""
    請針對盲解代碼「{pair_text}」提供 3 個生動的中文記憶圖像。
    請嚴格使用 JSON 格式輸出，不要有其他廢話。
    格式範例：
    [
        {{"word": "聯想詞1", "desc": "為什麼這樣聯想"}},
        {{"word": "聯想詞2", "desc": "為什麼這樣聯想"}},
        {{"word": "聯想詞3", "desc": "為什麼這樣聯想"}}
    ]
    """
    return call_ai_with_fallback(prompt)