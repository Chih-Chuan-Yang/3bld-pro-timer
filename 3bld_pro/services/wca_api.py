import requests
import pandas as pd
import numpy as np

class WCAService:
    def __init__(self):
        self.base_url = "https://www.worldcubeassociation.org/api/v0"
        
        # WCA 事件代碼對照表 (中文)
        self.EVENT_NAMES = {
            "333": "3x3", "222": "2x2", "444": "4x4", "555": "5x5", "666": "6x6", "777": "7x7",
            "333bf": "3x3 盲解", "333fm": "最少步數", "333oh": "3x3 單手",
            "clock": "魔表", "minx": "五魔方", "pyram": "金字塔", "skewb": "斜轉",
            "sq1": "Square-1", "444bf": "4x4 盲解", "555bf": "5x5 盲解", "333mbf": "多顆盲解"
        }

    def format_wca_time(self, result, event_id=None):
        """
        將 WCA 的成績數值轉為人類可讀格式
        - 一般項目: 厘秒 -> 分:秒.厘
        - 333mbf (多盲): 特殊編碼 -> 解/試 時間
        - 333fm (最少步): 直接回傳步數
        """
        if result is None: return "--"
        if result == -1: return "DNF"
        if result == -2: return "DNS"
        if result == 0: return ""

        # --- 1. 處理多顆盲解 (333mbf) ---
        # 格式: 0DDTTTTTMM (DD=99-差值, TTTTT=秒數, MM=漏掉)
        if event_id == "333mbf":
            s_val = str(result)
            # 新制格式通常是 9 位數 (因為開頭 0 會被 int 省略)
            if len(s_val) != 9: return str(result) 
            
            diff = 99 - int(s_val[:2])   # 第一部分算出 (解-漏) 的分數
            missed = int(s_val[-2:])     # 最後兩位是漏掉的顆數
            time_sec = int(s_val[2:7])   # 中間五位是秒數
            
            solved = diff + missed       # 反推解掉幾顆
            attempted = solved + missed  # 反推總共幾顆
            
            # 格式化時間 mm:ss
            m = time_sec // 60
            s = time_sec % 60
            return f"{solved}/{attempted} {m}:{s:02d}"

        # --- 2. 處理最少步數 (333fm) ---
        if event_id == "333fm":
            return str(result)

        # --- 3. 處理一般計時項目 (轉為 分:秒.厘) ---
        # WCA 時間存的是「厘秒 (Centiseconds)」
        seconds = result / 100
        
        if seconds >= 60:
            m = int(seconds // 60)
            s = seconds % 60
            # {:05.2f} 會讓 5.23 變成 05.23，顯示為 1:05.23
            return f"{m}:{s:05.2f}"
        else:
            return f"{seconds:.2f}"

    def get_user_data(self, wca_id):
        """輸入 WCA ID，回傳原始 JSON"""
        wca_id = wca_id.upper().strip()
        url = f"{self.base_url}/persons/{wca_id}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "找不到此 WCA ID，請確認輸入正確。"}
            else:
                return {"error": f"連線錯誤: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def parse_stats_for_card(self, user_data):
        """解析數據：找出最佳 NR 項目，並整理所有成績"""
        if "error" in user_data: return None

        person = user_data.get('person', {})
        if not person: return None

        # 1. 基本資料
        competition_count = user_data.get('competition_count', 0)
        medals = user_data.get('medals', {'gold': 0, 'silver': 0, 'bronze': 0})
        
        avatar_url = "https://www.worldcubeassociation.org/assets/missing_avatar_thumb-12654dd6f1aa6d458e80d02d6eed8b1fbea050954bc474521249b71ec9c6cd0a.png"
        if person.get('avatar'):
            avatar_url = person['avatar']['url']

        profile = {
            "name": person.get('name', 'Unknown'),
            "wca_id": person.get('wca_id', 'Unknown'),
            "country": person.get('country_iso2', 'TW'),
            "avatar_url": avatar_url,
            "competition_count": competition_count,
            "medals": medals
        }

        # 2. 處理成績 (找出最佳 NR)
        raw_records = user_data.get('personal_records', {})
        
        processed_records = {} 
        best_event_id = "333"  # 預設
        best_nr_value = 999999 

        for event_id, records in raw_records.items():
            event_name = self.EVENT_NAMES.get(event_id, event_id)
            
            single = records.get('single', {})
            average = records.get('average', {})
            
            nr_single = single.get('country_rank') if single.get('country_rank') else 999999
            nr_avg = average.get('country_rank') if average.get('country_rank') else 999999
            
            # 多盲通常只看單次排名
            if event_id == '333mbf':
                current_best_nr = nr_single
            else:
                current_best_nr = min(nr_single, nr_avg)
            
            if current_best_nr < best_nr_value:
                best_nr_value = current_best_nr
                best_event_id = event_id

            # 🔥 這裡呼叫 format_wca_time 時，傳入 event_id 以便特殊處理
            processed_records[event_id] = {
                "name": event_name,
                "single_time": self.format_wca_time(single.get('best'), event_id),
                "single_nr": single.get('country_rank', '-'),
                "single_wr": single.get('world_rank', '-'),
                "avg_time": self.format_wca_time(average.get('best'), event_id),
                "avg_nr": average.get('country_rank', '-'),
                "avg_wr": average.get('world_rank', '-')
            }

        if not processed_records:
            best_event_id = None

        return {
            "profile": profile,
            "best_event_id": best_event_id, 
            "all_records": processed_records 
        }