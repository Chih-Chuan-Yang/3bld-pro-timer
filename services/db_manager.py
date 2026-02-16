import os
import json
import pandas as pd
import re

class ProDBManager:
    def __init__(self):
        self.db_file = "pro_pairs.json"
        self.db = self.load_db()

    def _normalize_key(self, key):
        """解決數字一與注音ㄧ的問題"""
        if not isinstance(key, str): return str(key)
        return key.replace("一", "ㄧ")

    def load_db(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {self._normalize_key(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Read DB Error: {e}")
        return {}

    def save_db(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)

    def get_words(self, pair_code):
        normalized_code = self._normalize_key(pair_code)
        return self.db.get(normalized_code, [])

    def add_word(self, pair_code, new_word):
        new_word = new_word.strip()
        if not new_word: return False
        key = self._normalize_key(pair_code)
        
        if key not in self.db: self.db[key] = []
        if new_word not in self.db[key]:
            self.db[key].append(new_word)
            self.save_db()
            return True
        return False

    def import_from_csv(self, uploaded_file):
        """讀取 2D 矩陣 CSV (上標題=字首, 左索引=字尾)"""
        try:
            try:
                df_import = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df_import = pd.read_csv(uploaded_file, encoding='cp950')
            
            count = 0
            # 第一列的標題是「字首」(Prefix)
            col_headers = [str(c).strip() for c in df_import.columns[1:]]
            
            # 逐列讀取，第一欄是「字尾」(Suffix)
            for index, row in df_import.iterrows():
                suffix_raw = str(row.iloc[0]).strip()
                if not suffix_raw or suffix_raw == 'nan': continue
                suffix_val = self._normalize_key(suffix_raw)
                
                for i, prefix_raw in enumerate(col_headers):
                    if not prefix_raw or 'Unnamed' in prefix_raw: continue 
                    p_clean = self._normalize_key(prefix_raw)
                    
                    # 組合：字首 + 字尾
                    pair_code = p_clean + suffix_val 
                    
                    cell_val = str(row.iloc[i+1])
                    if cell_val.strip() and cell_val.strip() != 'nan':
                        words = [w.strip() for w in re.split(r'[,，、\s\n]+', cell_val) if w.strip()]
                        if words:
                            if pair_code in self.db:
                                current_set = set(self.db[pair_code])
                                for w in words:
                                    if w not in current_set: self.db[pair_code].append(w)
                            else:
                                self.db[pair_code] = words
                            count += 1
            self.save_db()
            return True, count
        except Exception as e:
            return False, str(e)