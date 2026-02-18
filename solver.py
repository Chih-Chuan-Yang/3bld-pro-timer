import pycuber
import json
import os
import itertools
import traceback
import math
import sys

# ==========================================
# 1. 基礎設定 & 常數
# ==========================================
WCA_MAP = {
    '[y]': '白色', 
    '[w]': '黃色', 
    '[g]': '綠色',
    '[b]': '藍色', 
    '[r]': '橘色', 
    '[o]': '紅色'
}

# --- 角塊資料庫 ---
C_COORDS = {
    'UFR': [('U', 2, 2), ('F', 0, 2), ('R', 0, 0)], # Buffer
    'UBL': [('U', 0, 0), ('L', 0, 0), ('B', 0, 2)],
    'UBR': [('U', 0, 2), ('B', 0, 0), ('R', 0, 2)],
    'UFL': [('U', 2, 0), ('F', 0, 0), ('L', 0, 2)],
    'DFL': [('D', 0, 0), ('F', 2, 0), ('L', 2, 2)],
    'DFR': [('D', 0, 2), ('F', 2, 2), ('R', 2, 0)],
    'DBR': [('D', 2, 2), ('B', 2, 0), ('R', 2, 2)],
    'DBL': [('D', 2, 0), ('B', 2, 2), ('L', 2, 0)]
}

C_TARGET_COORDS = C_COORDS.copy()
C_TARGET_COORDS.update({
    'FUL': [('F', 0, 0), ('L', 0, 2), ('U', 2, 0)], 'LUF': [('L', 0, 2), ('U', 2, 0), ('F', 0, 0)],
    'FDR': [('F', 2, 2), ('D', 0, 2), ('R', 2, 0)], 'FDL': [('F', 2, 0), ('L', 2, 2), ('D', 0, 0)],
    'RUB': [('R', 0, 2), ('U', 0, 2), ('B', 0, 0)], 'RDB': [('R', 2, 2), ('D', 2, 2), ('B', 2, 0)],
    'RDF': [('R', 2, 0), ('F', 2, 2), ('D', 0, 2)], 'BUR': [('B', 0, 0), ('R', 0, 2), ('U', 0, 2)],
    'BUL': [('B', 0, 2), ('U', 0, 0), ('L', 0, 0)], 'BDL': [('B', 2, 2), ('D', 2, 0), ('L', 2, 0)],
    'BDR': [('B', 2, 0), ('R', 2, 2), ('D', 2, 2)], 'LUB': [('L', 0, 0), ('B', 0, 2), ('U', 0, 0)],
    'LDF': [('L', 2, 2), ('D', 0, 0), ('F', 2, 0)], 'LDB': [('L', 2, 0), ('B', 2, 2), ('D', 2, 0)]
})

C_PIECE_DEFS = {
    frozenset(['白色', '藍色', '橘色']): 'UBL', 
    frozenset(['白色', '紅色', '藍色']): 'UBR',
    frozenset(['白色', '綠色', '橘色']): 'UFL', 
    frozenset(['白色', '綠色', '紅色']): 'BUFFER',
    frozenset(['黃色', '綠色', '橘色']): 'DFL', 
    frozenset(['黃色', '紅色', '綠色']): 'DFR',
    frozenset(['黃色', '藍色', '紅色']): 'DBR', 
    frozenset(['黃色', '橘色', '藍色']): 'DBL'
}

C_TARGETS = {
    ('UBL', '白色'): 'UBL', ('UBL', '藍色'): 'BUL', ('UBL', '橘色'): 'LUB',
    ('UBR', '白色'): 'UBR', ('UBR', '紅色'): 'RUB', ('UBR', '藍色'): 'BUR',
    ('UFL', '白色'): 'UFL', ('UFL', '綠色'): 'FUL', ('UFL', '橘色'): 'LUF',
    ('DFL', '黃色'): 'DFL', ('DFL', '綠色'): 'FDL', ('DFL', '橘色'): 'LDF',
    ('DFR', '黃色'): 'DFR', ('DFR', '綠色'): 'FDR', ('DFR', '紅色'): 'RDF',
    ('DBR', '黃色'): 'DBR', ('DBR', '藍色'): 'BDR', ('DBR', '紅色'): 'RDB',
    ('DBL', '黃色'): 'DBL', ('DBL', '藍色'): 'BDL', ('DBL', '橘色'): 'LDB'
}

C_PRIORITY = ['UBL', 'UBR', 'UFL', 'DFL', 'DFR', 'DBR', 'DBL']

C_TWIST_DIRECTION_MAP = {
    'UBL': {0: 0, 1: 1, 2: 2}, 
    'UBR': {0: 0, 1: 1, 2: 2},
    'UFL': {0: 0, 1: 1, 2: 2},
    'DFL': {0: 0, 1: 2, 2: 1}, 
    'DFR': {0: 0, 1: 1, 2: 2},
    'DBR': {0: 0, 1: 2, 2: 1},
    'DBL': {0: 0, 1: 1, 2: 2}
}

TWIST_TARGET_NAMES = {
    ('UBL', 2): 'BUL', ('UBL', 1): 'LUB',
    ('UBR', 2): 'RBU', ('UBR', 1): 'BUR', 
    ('UFL', 2): 'LFU', ('UFL', 1): 'FUL',
    ('DFL', 2): 'FDL', ('DFL', 1): 'LDF',
    ('DFR', 2): 'RDF', ('DFR', 1): 'FDR',
    ('DBR', 2): 'BDR', ('DBR', 1): 'RDB',
    ('DBL', 2): 'LBD', ('DBL', 1): 'BDL'
}

BUFFER_TARGET_DEFS = {
    ('UFR', '白色'): 'UFR', 
    ('UFR', '綠色'): 'FUR', 
    ('UFR', '紅色'): 'RUF'
}

# --- 邊塊資料庫 ---
E_COORDS = {
    'UF': [('U', 2, 1), ('F', 0, 1)], 'FU': [('F', 0, 1), ('U', 2, 1)],
    'UB': [('U', 0, 1), ('B', 0, 1)], 'BU': [('B', 0, 1), ('U', 0, 1)],
    'UL': [('U', 1, 0), ('L', 0, 1)], 'LU': [('L', 0, 1), ('U', 1, 0)],
    'UR': [('U', 1, 2), ('R', 0, 1)], 'RU': [('R', 0, 1), ('U', 1, 2)],
    'DF': [('D', 0, 1), ('F', 2, 1)], 'FD': [('F', 2, 1), ('D', 0, 1)],
    'DR': [('D', 1, 2), ('R', 2, 1)], 'RD': [('R', 2, 1), ('D', 1, 2)],
    'DB': [('D', 2, 1), ('B', 2, 1)], 'BD': [('B', 2, 1), ('D', 2, 1)],
    'DL': [('D', 1, 0), ('L', 2, 1)], 'LD': [('L', 2, 1), ('D', 1, 0)],
    'FR': [('F', 1, 2), ('R', 1, 0)], 'RF': [('R', 1, 0), ('F', 1, 2)],
    'FL': [('F', 1, 0), ('L', 1, 2)], 'LF': [('L', 1, 2), ('F', 1, 0)],
    'BR': [('B', 1, 0), ('R', 1, 2)], 'RB': [('R', 1, 2), ('B', 1, 0)],
    'BL': [('B', 1, 2), ('L', 1, 0)], 'LB': [('L', 1, 0), ('B', 1, 2)]
}

E_PIECE_DEFS = {
    frozenset(['白色', '藍色']): 'UB', frozenset(['白色', '橘色']): 'UL',
    frozenset(['白色', '紅色']): 'UR', frozenset(['白色', '綠色']): 'BUFFER',
    frozenset(['黃色', '綠色']): 'DF', frozenset(['黃色', '紅色']): 'DR',
    frozenset(['黃色', '藍色']): 'DB', frozenset(['黃色', '橘色']): 'DL',
    frozenset(['綠色', '紅色']): 'FR', frozenset(['綠色', '橘色']): 'FL',
    frozenset(['藍色', '紅色']): 'BR', frozenset(['藍色', '橘色']): 'BL'
}

E_TARGETS = {
    ('UB', '白色'): 'UB', ('UB', '藍色'): 'BU',
    ('UL', '白色'): 'UL', ('UL', '橘色'): 'LU',
    ('UR', '白色'): 'UR', ('UR', '紅色'): 'RU',
    ('UF', '白色'): 'UF', ('UF', '綠色'): 'FU',
    ('DF', '黃色'): 'DF', ('DF', '綠色'): 'FD',
    ('DR', '黃色'): 'DR', ('DR', '紅色'): 'RD',
    ('DB', '黃色'): 'DB', ('DB', '藍色'): 'BD',
    ('DL', '黃色'): 'DL', ('DL', '橘色'): 'LD',
    ('FR', '綠色'): 'FR', ('FR', '紅色'): 'RF',
    ('FL', '綠色'): 'FL', ('FL', '橘色'): 'LF',
    ('BR', '藍色'): 'BR', ('BR', '紅色'): 'RB',
    ('BL', '藍色'): 'BL', ('BL', '橘色'): 'LB'
}

E_PRIORITY = ['UL', 'UB', 'UR', 'FR', 'FL', 'DF', 'BL', 'BR', 'DR', 'DL', 'DB']

# ==========================================
# 2. 核心工具函式
# ==========================================
def get_colors(cube, code, type='edge'):
    try:
        if type == 'edge': 
            pos = E_COORDS[code]
        else:
            if code in C_COORDS: 
                pos = C_COORDS[code]
            else: 
                pos = C_TARGET_COORDS[code]
        
        raw_colors = [str(cube.get_face(p[0])[p[1]][p[2]]) for p in pos]
        colors = []
        for r in raw_colors:
            if r in WCA_MAP: 
                colors.append(WCA_MAP[r])
            else:
                print(f"❌ [色彩錯誤] 在 {code} 讀到未知代碼: '{r}' (請檢查 WCA_MAP)")
                return ['ERR']
        return colors
    except Exception as e:
        print(f"❌ [讀取錯誤] {code}: {e}")
        return ['ERR']

def identify_piece(colors, type='edge'):
    if 'ERR' in colors: return 'ERR'
    defs = E_PIECE_DEFS if type == 'edge' else C_PIECE_DEFS
    pset = frozenset(colors)
    return defs.get(pset, 'ERR')

def get_target_code(base_name, main_color, type='edge'):
    targets = E_TARGETS if type == 'edge' else C_TARGETS
    res = targets.get((base_name, main_color), 'ERR')
    if res == 'ERR' and (base_name == 'UFR' or base_name == 'BUFFER'):
        res = BUFFER_TARGET_DEFS.get(('UFR', main_color), 'ERR')
    return res

# ==========================================
# 3. Solver 類別
# ==========================================
class BlindSolver:
    def __init__(self):
        print("🔥 Loaded Solver V6 (Full Original Style)")
        self.cube = None
        self.logs = []
        self.db_edges = self.load_db("db_edges.json")
        self.db_corners = self.load_db("db_corners.json")
        self.db_parity = self.load_db("db_parity.json")
        self.db_flips = self.load_db("db_flips.json")
        self.db_twists = self.load_db("db_twists.json")

    def log(self, message): 
        print(f"[Solver] {message}")
        self.logs.append(message)

    def load_db(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
            except: return {}
        return {}

    def get_alg_info(self, t1, t2, db):
        if not t1 or not t2: return None
        key = f"{t1} {t2}"
        if key in db: return db[key]
        return None

    def smart_search_twist(self, target_code, db):
        if not target_code or target_code == 'ERR': return None
        if target_code in db: return db[target_code]
        try:
            perms = [''.join(p) for p in itertools.permutations(target_code)]
            for p in perms:
                if p in db: return db[p]
        except: pass
        return None

    # --- 配對路徑 (Pair Up Path) ---
    def pair_up_path(self, path_objs, db, p_type="edge"):
        """
        將路徑物件轉換為字母對 (Letter Pairs) 並查詢公式。
        input path_objs: [{'pair': 'UB', 'is_new_cycle': False}, ...]
        """
        pairs_info = []
        full_solution = []
        total_moves = 0
        
        # 1. 兩兩配對
        for i in range(0, len(path_objs) - 1, 2):
            item1 = path_objs[i]
            item2 = path_objs[i+1]
            t1 = item1['pair']
            t2 = item2['pair']
            
            # 斷圈偵測：只要這組 Pair 中有任何一個是新循環起點
            is_break = item1['is_new_cycle'] or item2['is_new_cycle']
            
            info = self.get_alg_info(t1, t2, db)
            p_data = {
                "pair": f"{t1} {t2}", 
                "alg": "未收錄", 
                "seq": "", 
                "moves": 0, 
                "is_new_cycle": is_break
            }
            
            if info: 
                p_data.update(info)
                full_solution.append(info.get("seq", ""))
                total_moves += info.get("moves", 0)
            
            pairs_info.append(p_data)

        # 2. 處理剩單 (Parity)
        if len(path_objs) % 2 != 0:
            last_item = path_objs[-1]
            last_target = last_item['pair']
            is_break = last_item['is_new_cycle']
            
            if p_type == "edge":
                # 邊塊 Parity (Pseudo Swap)
                info = db.get(last_target)
                p_data = {
                    "pair": last_target, 
                    "alg": "Pseudo Swap", 
                    "seq": "", 
                    "moves": 0, 
                    "is_pseudo": True, 
                    "is_new_cycle": is_break
                }
                if info: p_data.update(info)
                pairs_info.append(p_data)
            
            elif p_type == "corner":
                # 角塊 Parity
                parity_info = self.db_parity.get(last_target) or self.db_parity.get("Parity")
                alg_display = parity_info.get("alg", "Parity") if parity_info else "Parity"
                
                p_data = {
                    "pair": f"{last_target} (Parity)", 
                    "alg": alg_display, 
                    "seq": "", 
                    "moves": 0, 
                    "is_parity": True, 
                    "is_new_cycle": is_break
                }
                if parity_info: 
                    full_solution.append(parity_info.get("seq", ""))
                    total_moves += parity_info.get("moves", 0)
                pairs_info.append(p_data)
                
        return pairs_info, full_solution, total_moves

    def pair_up_flips(self, flips_list, db):
        results = []
        full_seq = []
        total_moves = 0
        for p in flips_list:
            info = db.get(p)
            res = {
                "pair": p, 
                "part": p, 
                "alg": "未收錄", 
                "seq": "", 
                "moves": 0
            }
            if info: 
                res.update(info)
                full_seq.append(info.get("seq", ""))
                total_moves += info.get("moves", 0)
            results.append(res)
        return results, full_seq, total_moves

    def pair_up_twists(self, twists_dict, db):
        results = []
        full_seq = []
        total_moves = 0
        for base, info in twists_dict.items():
            target = info['target']
            direction = info['direction']
            db_info = self.smart_search_twist(target, db)
            
            res = {
                "pair": target, 
                "part": base, 
                "dir": direction, 
                "target": target, 
                "alg": "未收錄", 
                "seq": "", 
                "moves": 0
            }
            
            if db_info: 
                res.update(db_info)
                full_seq.append(db_info.get("seq", ""))
                total_moves += db_info.get("moves", 0)
            
            results.append(res)
        return results, full_seq, total_moves

    def calculate_difficulty(self, stats):
        return 5.0 # Placeholder

    # ==========================================
    # 核心解算流程
    # ==========================================
    def solve(self, scramble_text):
        try:
            my_cube = pycuber.Cube()
            # 簡單過濾寬層，避免程式崩潰 (pycuber 不支援 'w')
            clean_formula = " ".join([m for m in scramble_text.split() if 'w' not in m])
            my_cube(pycuber.Formula(clean_formula))
            self.cube = my_cube
            self.logs = []
            
            # 1. 解角塊
            self.log(f"🧩 **[角塊階段]**")
            c_path_objs, has_parity, c_twists_dict, c_stats = self.trace_corners()
            
            # 設定全域 Parity (邊塊會用到)
            self.has_parity = has_parity
            
            # 2. 解邊塊
            self.log(f"🧩 **[邊塊階段]** (Parity: {has_parity})")
            e_path_objs, e_flips_list, e_stats = self.trace_edges(has_parity)
            
            # 3. 配對與數據整合
            c_pairs, c_sol, c_moves = self.pair_up_path(c_path_objs, self.db_corners, "corner")
            c_twist_details, c_twist_seq, c_twist_moves = self.pair_up_twists(c_twists_dict, self.db_twists)
            e_pairs, e_sol, e_moves = self.pair_up_path(e_path_objs, self.db_edges, "edge")
            e_flip_details, e_flip_seq, e_flip_moves = self.pair_up_flips(e_flips_list, self.db_flips)

            total_algs = len(e_pairs) + len(e_flip_details) + len(c_pairs) + len(c_twist_details)
            total_moves = e_moves + e_flip_moves + c_moves + c_twist_moves

            self.analysis = {
                "Edges": {
                    "targets": len(e_path_objs),
                    "cycles": e_stats['cycles'],
                    "solved": e_stats['solved'],
                    "flips": len(e_flips_list)
                },
                "Corners": {
                    "targets": len(c_path_objs),
                    "cycles": c_stats['cycles'],
                    "solved": c_stats['solved'],
                    "twists": len(c_twists_dict)
                },
                "Parity": has_parity,
                "difficulty_score": 5.0
            }
            
            # 4. 回傳詳細結果 (Frontend 需要 path_detailed 來顯示斷圈)
            self.edge_result = {
                "path": [p['pair'] for p in e_path_objs], 
                "path_detailed": e_path_objs, 
                "flips": e_flips_list, 
                "flips_detailed": e_flip_details, 
                "details": e_pairs
            }
            self.corner_result = {
                "path": [p['pair'] for p in c_path_objs], 
                "path_detailed": c_path_objs,
                "twists": c_twists_dict, 
                "twists_detailed": c_twist_details, 
                "parity_target": c_path_objs[-1]['pair'] if has_parity and c_path_objs else None,
                "details": c_pairs
            }
            return True
        except Exception as e: 
            self.log(f"Global Error: {e}")
            import traceback; traceback.print_exc(); 
            return False

    # ==========================================
    # 追蹤邏輯 (核心修復)
    # ==========================================
    def trace_corners(self):
        solved_bases = set()
        twists = {}
        stats = {'solved': 0, 'cycles': 0}
        buffer_name = 'UFR'

        # 1. 預檢 (Twist)
        for base in C_PRIORITY:
            colors = get_colors(self.cube, base, 'corner')
            real_base = identify_piece(colors, 'corner')
            
            if real_base == 'ERR' or real_base == 'BUFFER': 
                if real_base == 'BUFFER': real_base = 'UFR'
            
            if real_base == base:
                main_color_idx = -1
                for i, c in enumerate(colors):
                    if c in ['白色', '黃色']: main_color_idx = i; break
                
                if main_color_idx != 0:
                    direction = C_TWIST_DIRECTION_MAP.get(base, {}).get(main_color_idx, 0)
                    target = TWIST_TARGET_NAMES.get((base, direction), 'ERR')
                    twists[base] = {'direction': direction, 'target': target}
                    self.log(f"   ⚠️ 原地翻轉: {base} -> {target}")
                else: 
                    stats['solved'] += 1
                    self.log(f"   ✅ {base} 歸位")
                
                if base != buffer_name: solved_bases.add(base)

        # 2. 追蹤
        path_objs = [] # 儲存字典 [{'pair': 'UB', 'is_new_cycle': False}]
        curr = buffer_name
        start_base = buffer_name
        cycle_count = 0
        
        for _ in range(30):
            colors = get_colors(self.cube, curr, 'corner')
            base = identify_piece(colors, 'corner')
            if base == 'BUFFER': base = 'UFR'
            target = get_target_code(base, colors[0], 'corner')
            
            if base == 'ERR' or target == 'ERR': break

            if base == start_base:
                if cycle_count == 0 and len(path_objs) > 0: cycle_count = 1
                
                # 閉合
                if base != buffer_name:
                    # 這是一個正常的閉合目標
                    path_objs.append({'pair': target, 'is_new_cycle': False})
                    solved_bases.add(base)
                    self.log(f"   -> 閉合: {target}")
                else:
                    self.log(f"   -> Buffer 歸位")
                
                # 尋找新循環
                next_b = next((b for b in C_PRIORITY if b not in solved_bases and b != buffer_name), None)
                if not next_b: break
                
                self.log(f"   ⚠️ [破圈] -> {next_b}")
                cycle_count += 1
                
                # 🔥 關鍵修復：破圈時，必須將「新起點」加入路徑，並標記 is_new_cycle=True
                path_objs.append({'pair': next_b, 'is_new_cycle': True})
                
                # 轉移焦點到新循環
                curr = next_b
                start_base = next_b
            
            elif base in solved_bases: break
            else:
                self.log(f"   -> 指向: {target}")
                path_objs.append({'pair': target, 'is_new_cycle': False})
                solved_bases.add(base)
                curr = target
        
        if len(path_objs) > 0 and cycle_count == 0: cycle_count = 1
        stats['cycles'] = cycle_count
        
        # Parity 判定：路徑長度為奇數
        has_parity = (len(path_objs) % 2 != 0)
        return path_objs, has_parity, twists, stats

    def trace_edges(self, has_parity):
        solved_bases = set()
        flips = []
        stats = {'solved': 0, 'cycles': 0}
        
        # 1. 預檢 (Flip)
        for base in E_PRIORITY:
            colors = get_colors(self.cube, base, 'edge')
            real_base = identify_piece(colors, 'edge')
            
            if real_base == base:
                is_flip = False
                if base in ['UB','UL','UR','DF','DR','DB','DL']: 
                    if colors[0] not in ['白色','黃色']: is_flip = True
                else: 
                    if colors[0] not in ['綠色','藍色']: is_flip = True
                
                if is_flip: 
                    flips.append(base)
                    self.log(f"   ⚠️ 翻轉: {base}")
                else: 
                    stats['solved'] += 1
                    self.log(f"   ✅ 歸位: {base}")
                
                solved_bases.add(base)

        # 2. 追蹤
        path_objs = []
        curr = 'UF'
        start_base = 'BUFFER'
        cycle_count = 0

        for _ in range(40):
            colors = get_colors(self.cube, curr, 'edge')
            base = identify_piece(colors, 'edge')
            
            effective_base = base
            if has_parity:
                if base == 'UR': effective_base = 'BUFFER'
                elif base == 'BUFFER': effective_base = 'UR'
            
            target = 'ERR'
            if effective_base == 'BUFFER': pass 
            elif effective_base == 'UR' and has_parity and base == 'BUFFER':
                if colors[0] == '白色': target = 'UR';
                else: target = 'RU'
            else: target = get_target_code(base, colors[0], 'edge')

            if effective_base == start_base:
                if cycle_count == 0 and len(path_objs) > 0: cycle_count = 1

                if effective_base != 'BUFFER':
                    path_objs.append({'pair': target, 'is_new_cycle': False})
                    solved_bases.add(effective_base)
                    self.log(f"   -> 閉合: {target}")
                else:
                    self.log(f"   -> Buffer 歸位")
                
                next_b = next((b for b in E_PRIORITY if b not in solved_bases), None)
                if not next_b: break
                
                self.log(f"   ⚠️ [破圈] -> {next_b}")
                cycle_count += 1
                
                # 🔥 關鍵修復：破圈時，必須將「新起點」加入路徑，並標記 is_new_cycle=True
                path_objs.append({'pair': next_b, 'is_new_cycle': True})
                
                curr = next_b
                start_base = next_b
            
            elif effective_base in solved_bases: break
            else:
                self.log(f"   -> 指向: {target}")
                path_objs.append({'pair': target, 'is_new_cycle': False})
                solved_bases.add(effective_base)
                curr = target
        
        if len(path_objs) > 0 and cycle_count == 0: cycle_count = 1
        stats['cycles'] = cycle_count
        return path_objs, flips, stats