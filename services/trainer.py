import pandas as pd
import joblib
import os
import sys
import re
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# 為了引用上一層的 solver，需要加入路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from solver import BlindSolver
    from scramble_translator import ScrambleTranslator
except ImportError:
    print("❌ Trainer 無法引用 Solver，請確認檔案結構")

def parse_time(time_str):
    """解析 csTimer 的時間格式 (DNF, +2, etc)"""
    time_str = str(time_str).strip()
    
    # 處理 DNF (例如: "DNF(23.51)") -> 回傳 None 代表不訓練這筆
    if "DNF" in time_str:
        return None
    
    # 處理 +2 (例如: "21.68+")
    if "+" in time_str:
        try:
            raw_t = float(time_str.replace('+', ''))
            return raw_t + 2.0
        except: return None
        
    # 一般時間
    try:
        return float(time_str)
    except: return None

def train_model(history_file='3bld_history.csv', model_file='3bld_predictor.pkl', progress_callback=None):
    """
    讀取歷史紀錄 -> 解析每一筆打亂 -> 算出特徵 -> 訓練 AI
    """
    if not os.path.exists(history_file):
        return False, "❌ 找不到 CSV 檔案"

    try:
        # 1. 嘗試讀取 (支援 csTimer 的分號格式)
        # 預設無標題，我們手動給欄位：ID, Time, Penalty, Scramble, Date, ...
        df = pd.read_csv(history_file, sep=';', header=None, on_bad_lines='skip')
        
        # 簡單判斷：如果欄位少於 4，可能是逗號分隔的舊格式，重讀一次
        if len(df.columns) < 4:
            df = pd.read_csv(history_file, sep=',')
            # 確保有 Scramble 和 Time 欄位 (簡單映射)
            if 'Scramble' not in df.columns: # 假設是簡單格式
                return False, "❌ CSV 格式無法識別，請確認分隔符號"
        else:
            # csTimer 格式映射: Col 1=Time, Col 3=Scramble
            df = df.rename(columns={1: 'TimeRaw', 3: 'Scramble'})

        # 2. 開始資料前處理 (比較花時間)
        clean_data = []
        solver = BlindSolver()
        translator = ScrambleTranslator()
        
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            # 更新進度條
            if progress_callback:
                progress_callback(int((idx / total_rows) * 100), f"正在分析第 {idx+1}/{total_rows} 筆打亂...")

            t_val = parse_time(row['TimeRaw']) if 'TimeRaw' in row else parse_time(row['Time'])
            scr = str(row['Scramble'])
            
            if t_val is None: continue # 跳過 DNF
            if not scr or len(scr) < 5: continue # 跳過無效打亂

            try:
                # 🔥 核心：解算打亂，取得難度特徵 🔥
                real_scr = translator.translate(scr)
                if solver.solve(real_scr):
                    stats = solver.analysis
                    
                    clean_data.append({
                        'Time': t_val,
                        'Total_Targets': stats['Edges']['targets'] + stats['Corners']['targets'],
                        'Total_Cycles': stats['Edges']['cycles'] + stats['Corners']['cycles'],
                        'Parity': 1 if stats['Parity'] else 0,
                        'Flips': stats['Edges']['flips'],
                        'Twists': stats['Corners']['twists'],
                        'Difficulty_Score': stats.get('difficulty_score', 0)
                    })
            except:
                continue # 解算失敗就跳過

        if len(clean_data) < 5:
            return False, f"⚠️ 有效資料過少 (僅 {len(clean_data)} 筆)，無法訓練。"

        # 3. 轉成 DataFrame 準備訓練
        train_df = pd.DataFrame(clean_data)
        
        features = ['Total_Targets', 'Total_Cycles', 'Parity', 'Flips', 'Twists', 'Difficulty_Score']
        X = train_df[features]
        y = train_df['Time']

        # 4. 訓練隨機森林
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # 5. 存檔
        joblib.dump(model, model_file)
        
        avg_time = y.mean()
        mae = mean_absolute_error(y, model.predict(X))

        return True, f"✅ 訓練成功！\n學習了 {len(train_df)} 筆有效成績。\n您的平均約 {avg_time:.2f} 秒，模型誤差 ±{mae:.2f} 秒。"

    except Exception as e:
        return False, f"❌ 訓練發生錯誤: {str(e)}"