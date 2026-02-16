import re

class ScrambleTranslator:
    def __init__(self):
        # 初始面位對應 (Key=物理位置, Value=邏輯面)
        # 物理位置: 'U'(頂), 'D'(底), 'L'(左), 'R'(右), 'F'(前), 'B'(後)
        self.map = {
            'U': 'U', 'D': 'D', 
            'L': 'L', 'R': 'R', 
            'F': 'F', 'B': 'B'
        }

    def _rotate(self, axis, times):
        """更新面位映射 (模擬整顆方塊旋轉)"""
        for _ in range(times % 4):
            new_map = self.map.copy()
            if axis == 'x': # 向上翻 (R面不動)
                new_map['F'] = self.map['D']
                new_map['U'] = self.map['F']
                new_map['B'] = self.map['U']
                new_map['D'] = self.map['B']
            elif axis == 'y': # 向左轉 (U面不動)
                new_map['F'] = self.map['R']
                new_map['L'] = self.map['F']
                new_map['B'] = self.map['L']
                new_map['R'] = self.map['B']
            elif axis == 'z': # 順時針倒 (F面不動)
                new_map['U'] = self.map['L']
                new_map['R'] = self.map['U']
                new_map['D'] = self.map['R']
                new_map['L'] = self.map['D']
            self.map = new_map

    def translate(self, scramble_str):
        """將含 Wide Moves 的打亂轉換為標準外層打亂"""
        # 正規化: 處理 Rw, r, 2', '2 等格式
        moves = scramble_str.strip().split()
        clean_moves = []
        
        for m in moves:
            # 解析 轉動面 / 寬轉標記 /後綴
            match = re.match(r"([UDLRFBudlrfb])([w]?)(['2]?)", m)
            if not match: continue
            
            base, is_wide, suffix = match.groups()
            
            # 判斷旋轉次數 (1, 2, 3代表逆時針)
            count = 1
            if suffix == '2': count = 2
            elif suffix == "'": count = 3
            
            # 處理小寫 (r = Rw)
            if base.islower():
                base = base.upper()
                is_wide = 'w' # 強制視為寬轉
            
            output_move_base = None
            rotation_axis = None
            
            # === 定義寬轉邏輯 (Decomposition) ===
            # 邏輯: Wide = 對面外層轉動 + 整顆旋轉
            if is_wide == 'w':
                if base == 'R': # Rw -> L + x
                    output_move_base = 'L'
                    rotation_axis = 'x'
                elif base == 'L': # Lw -> R + x'
                    output_move_base = 'R'
                    rotation_axis = 'x'
                    count = (4 - count) % 4 # 方向相反 (Lw 是 x', 所以要反轉旋轉方向)
                    # 注意: Lw 的外層 R 轉動方向跟 Lw 是相反的嗎？
                    # Lw (左下壓) = R (右下壓) + x'. 方向一致.
                    # 但 Rw (右上推) = L (左上推) + x. 
                    # 實際上 Rw = x L (L是順時針). 
                    # 讓我們統一用標準定義: Rw(順) = L(順) + x(順)
                    pass 
                elif base == 'U': # Uw -> D + y
                    output_move_base = 'D'
                    rotation_axis = 'y'
                elif base == 'D': # Dw -> U + y'
                    output_move_base = 'U'
                    rotation_axis = 'y'
                    count = (4 - count) % 4
                elif base == 'F': # Fw -> B + z
                    output_move_base = 'B'
                    rotation_axis = 'z'
                elif base == 'B': # Bw -> F + z'
                    output_move_base = 'F'
                    rotation_axis = 'z'
                    count = (4 - count) % 4
            else:
                # 一般轉動
                output_move_base = base
            
            # 1. 輸出轉換後的步驟
            # 根據當前的 map，找出物理位置 (output_move_base) 對應的邏輯面
            logical_face = self.map[output_move_base]
            
            # 組合後綴
            out_suffix = ""
            if suffix == '2': out_suffix = "2"
            elif suffix == "'": out_suffix = "'"
            
            clean_moves.append(f"{logical_face}{out_suffix}")
            
            # 2. 如果是寬轉，更新方塊方向 (狀態機)
            if is_wide == 'w' and rotation_axis:
                self._rotate(rotation_axis, count)
                
        return " ".join(clean_moves)

# 測試用
if __name__ == "__main__":
    translator = ScrambleTranslator()
    scramble = "Rw' Fw'"
    result = translator.translate(scramble)
    print(f"原本: {scramble}")
    print(f"翻譯: {result}") 
    # 預期輸出: L2 U