import pycuber
from utils import *
import json
import os
import itertools
import traceback
import math

# ==========================================
# 1. Twist 邏輯定義
# ==========================================
C_TWIST_DIRECTION_MAP = {
    'UBL': {0: 'Normal', 1: '逆時針', 2: '順時針'}, 
    'UBR': {0: 'Normal', 1: '逆時針', 2: '順時針'}, 
    'UFL': {0: 'Normal', 1: '逆時針', 2: '順時針'}, 
    'DFL': {0: 'Normal', 1: '順時針', 2: '逆時針'}, 
    'DFR': {0: 'Normal', 1: '逆時針', 2: '順時針'}, 
    'DBR': {0: 'Normal', 1: '順時針', 2: '逆時針'}, 
    'DBL': {0: 'Normal', 1: '逆時針', 2: '順時針'}, 
    'BUFFER': {0: 'Normal', 1: '逆時針', 2: '順時針'},
    'UFR': {0: 'Normal', 1: '逆時針', 2: '順時針'}
}

TWIST_TARGET_NAMES = {
    ('UBL', '順時針'): 'BUL', ('UBL', '逆時針'): 'LUB',
    ('UBR', '順時針'): 'RBU', ('UBR', '逆時針'): 'BUR',
    ('UFL', '順時針'): 'LFU', ('UFL', '逆時針'): 'FUL',
    ('DFL', '順時針'): 'FDL', ('DFL', '逆時針'): 'LDF',
    ('DFR', '順時針'): 'RDF', ('DFR', '逆時針'): 'FDR',
    ('DBR', '順時針'): 'BDR', ('DBR', '逆時針'): 'RDB',
    ('DBL', '順時針'): 'LBD', ('DBL', '逆時針'): 'BDL',
    ('BUFFER', '順時針'): 'RUF', ('BUFFER', '逆時針'): 'FUR',
    ('UFR', '順時針'): 'RUF', ('UFR', '逆時針'): 'FUR'
}

BUFFER_TARGET_DEFS = {
    ('UFR', '白色'): 'UFR', 
    ('UFR', '綠色'): 'FUR',
    ('UFR', '紅色'): 'RUF'
}

def get_colors(cube, code, type='edge'):
    try:
        if type == 'edge': pos = E_COORDS[code]
        else:
            if code in C_COORDS: pos = C_COORDS[code]
            else: pos = C_TARGET_COORDS[code]
        return [WCA_MAP.get(str(cube.get_face(p[0])[p[1]][p[2]])) for p in pos]
    except: return ['ERR', 'ERR', 'ERR']

def identify_piece(colors, type='edge'):
    defs = E_PIECE_DEFS if type == 'edge' else C_PIECE_DEFS
    pset = frozenset(colors)
    return defs.get(pset, 'ERR')

def get_target_code(base_name, main_color, type='edge'):
    targets = E_TARGETS if type == 'edge' else C_TARGETS
    res = targets.get((base_name, main_color), 'ERR')
    if res == 'ERR' and (base_name == 'UFR' or base_name == 'BUFFER'):
        res = BUFFER_TARGET_DEFS.get(('UFR', main_color), 'ERR')
    return res

class BlindSolver:
    def __init__(self):
        self.cube = None
        self.logs = []
        self.edge_result = {}
        self.corner_result = {}
        self.has_parity = False
        self.analysis = {} 
        
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

    def pair_up_path(self, path, db, p_type="edge"):
        pairs_info = []; full_solution = []; total_moves = 0
        for i in range(0, len(path) - 1, 2):
            t1 = path[i]; t2 = path[i+1]
            info = self.get_alg_info(t1, t2, db)
            p_data = {"pair": f"{t1} {t2}", "alg": "未收錄", "seq": "", "moves": 0}
            if info: p_data.update(info); full_solution.append(info.get("seq", "")); total_moves += info.get("moves", 0)
            pairs_info.append(p_data)
        if len(path) % 2 != 0:
            last_target = path[-1]
            if p_type == "edge":
                info = db.get(last_target)
                p_data = {"pair": last_target, "alg": info.get("alg", "Pseudo Swap") if info else "Pseudo Swap", "seq": info.get("seq", "") if info else "", "moves": info.get("moves", 0) if info else 0, "is_pseudo": True}
                pairs_info.append(p_data)
            elif p_type == "corner":
                parity_info = self.db_parity.get(last_target)
                if not parity_info: parity_info = self.db_parity.get("Parity")
                alg_display = parity_info.get("alg", "未收錄 Parity") if parity_info else "未收錄 Parity"
                p_data = {"pair": f"{last_target} (Parity)", "alg": alg_display, "seq": parity_info.get("seq", "") if parity_info else "", "moves": parity_info.get("moves", 0) if parity_info else 0, "is_parity": True}
                if parity_info: full_solution.append(parity_info.get("seq", "")); total_moves += parity_info.get("moves", 0)
                pairs_info.append(p_data)
        return pairs_info, full_solution, total_moves

    def pair_up_flips(self, flips_list, db):
        results = []; remaining = set(flips_list); total_moves = 0; full_seq = []
        possible_pairs = list(itertools.combinations(remaining, 2))
        for p1, p2 in possible_pairs:
            if p1 not in remaining or p2 not in remaining: continue
            key1 = f"{p1} {p2}"; key2 = f"{p2} {p1}"
            match = None
            if key1 in db: match = (key1, db[key1])
            elif key2 in db: match = (key2, db[key2])
            if match:
                key, info = match
                results.append({"pair": key, "alg": info.get("alg", ""), "seq": info.get("seq", ""), "moves": info.get("moves", 0)})
                full_seq.append(info.get("seq", ""))
                total_moves += info.get("moves", 0)
                remaining.remove(p1); remaining.remove(p2)
        for p in list(remaining):
            info = db.get(p)
            if info:
                results.append({"pair": p, "alg": info.get("alg", ""), "seq": info.get("seq", ""), "moves": info.get("moves", 0)})
                full_seq.append(info.get("seq", ""))
                total_moves += info.get("moves", 0)
            else:
                results.append({"pair": p, "alg": "未收錄", "seq": "", "moves": 0})
        return results, full_seq, total_moves

    def pair_up_twists(self, twists_dict, db):
        results = []; full_seq = []; total_moves = 0
        for base, info in twists_dict.items():
            try:
                target_code = info['target']
                direction = info['direction']
                db_info = self.smart_search_twist(target_code, db)
                display_pair = db_info.get("pair") if db_info else f"{target_code} ({direction})"
                
                if db_info:
                    results.append({"pair": display_pair, "alg": db_info.get("alg", ""), "seq": db_info.get("seq", ""), "moves": db_info.get("moves", 0)})
                    full_seq.append(db_info.get("seq", ""))
                    total_moves += db_info.get("moves", 0)
                else:
                    results.append({"pair": display_pair, "alg": "未收錄 Twist", "seq": "", "moves": 0})
            except Exception as e:
                self.log(f"Twist Pair Error {base}: {e}")
        return results, full_seq, total_moves

    def calculate_difficulty(self, stats):
        """
        計算難易度分數 (1.000 - 10.000)
        基於加權成本模型 (Weighted Cost Model)
        """
        # 1. 定義權重 (可根據個人手感調整)
        W_EDGE = 1.0      # 每個邊塊目標的成本
        W_CORNER = 1.3    # 每個角塊目標的成本 (角塊通常稍慢)
        W_PARITY = 2.5    # Parity 的懲罰
        W_CYCLE = 0.6     # 每個循環的成本 (破圈成本)
        W_FLIP = 1.5      # 翻轉邊塊
        W_TWIST = 1.8     # 扭轉角塊
        
        # 2. 提取特徵
        n_edges = stats['Edges']['targets']
        n_corners = stats['Corners']['targets']
        has_parity = 1 if stats['Parity'] else 0
        n_cycles = (stats['Edges']['cycles'] - 1) + (stats['Corners']['cycles'] - 1) # 減1是因為基礎狀態算1個cycle
        if n_cycles < 0: n_cycles = 0
        n_flips = stats['Edges']['flips']
        n_twists = stats['Corners']['twists']
        
        # 3. 計算原始成本 (Raw Cost)
        raw_cost = (n_edges * W_EDGE) + \
                   (n_corners * W_CORNER) + \
                   (has_parity * W_PARITY) + \
                   (n_cycles * W_CYCLE) + \
                   (n_flips * W_FLIP) + \
                   (n_twists * W_TWIST)
                   
        # 4. 正規化 (Normalization)
        # 根據大量隨機模擬：
        # 極好運 (Skip多): Cost 約 16
        # 極差運 (無Skip+Parity+Twist): Cost 約 32
        # 平均: Cost 約 24
        
        min_cost = 14.0
        max_cost = 34.0
        
        # 線性映射到 1 - 10
        score = 1 + (raw_cost - min_cost) * (9) / (max_cost - min_cost)
        
        # 邊界限制
        if score < 1: score = 1.0
        if score > 10: score = 10.0
        
        return round(score, 3)

    def solve(self, scramble_text):
        try:
            my_cube = pycuber.Cube()
            clean_formula = " ".join([m for m in scramble_text.split() if 'w' not in m])
            my_cube(pycuber.Formula(clean_formula))
            self.cube = my_cube
            self.logs = []
            
            # 1. 角塊
            self.log(f"🧩 **[角塊階段]** (Buffer: UFR)")
            c_path, has_parity, c_twists_dict, c_stats = self.trace_corners()
            self.has_parity = has_parity
            c_pairs, c_sol, c_moves = self.pair_up_path(c_path, self.db_corners, "corner")
            c_twist_details, c_twist_seq, c_twist_moves = self.pair_up_twists(c_twists_dict, self.db_twists)
            
            self.log("-" * 30)
            
            # 2. 邊塊
            self.log("🧩 **[邊塊階段]**")
            e_path, e_flips_list, e_stats = self.trace_edges(has_parity)
            e_pairs, e_sol, e_moves = self.pair_up_path(e_path, self.db_edges, "edge")
            e_flip_details, e_flip_seq, e_flip_moves = self.pair_up_flips(e_flips_list, self.db_flips)
            
            # 3. 匯總統計
            total_algs = len(e_pairs) + len(e_flip_details) + len(c_pairs) + len(c_twist_details)
            total_moves = e_moves + e_flip_moves + c_moves + c_twist_moves

            self.analysis = {
                "Edges": {
                    "targets": len(e_path),
                    "cycles": e_stats['cycles'],
                    "solved": e_stats['solved'],
                    "flips": len(e_flips_list)
                },
                "Corners": {
                    "targets": len(c_path),
                    "cycles": c_stats['cycles'],
                    "solved": c_stats['solved'],
                    "twists": len(c_twists_dict)
                },
                "Parity": has_parity,
                "total_algs": total_algs,
                "total_moves": total_moves
            }
            
            # 4. 計算難易度分數
            difficulty_score = self.calculate_difficulty(self.analysis)
            self.analysis['difficulty_score'] = difficulty_score

            self.edge_result = {
                "path": e_path, "flips": e_flips_list, "flips_detailed": e_flip_details, 
                "details": e_pairs, "full_seq": " ".join(e_sol + e_flip_seq), "total_moves": e_moves + e_flip_moves
            }
            self.corner_result = {
                "path": c_path, "twists": c_twists_dict, "twists_detailed": c_twist_details, 
                "parity_target": c_path[-1] if has_parity and c_path else None, 
                "details": c_pairs, "full_seq": " ".join(c_sol + c_twist_seq), "total_moves": c_moves + c_twist_moves
            }
            return True
        except Exception as e: 
            self.log(f"Global Error: {e}"); 
            import traceback; traceback.print_exc(); 
            return False

    def trace_corners(self):
        solved_bases = set(); twists = {}; 
        stats = {'solved': 0, 'cycles': 0}
        
        self.log("   *預檢角塊...*")
        buffer_name = 'UFR'

        for base in C_PRIORITY:
            try:
                colors = get_colors(self.cube, base, 'corner')
                real_base = identify_piece(colors, 'corner')
                if real_base == 'ERR': continue
                if real_base == 'BUFFER': real_base = 'UFR'

                if real_base == base: # 原地
                    main_color_idx = -1
                    for i, c in enumerate(colors):
                        if c in ['白色', '黃色']: main_color_idx = i; break
                    
                    if main_color_idx != 0: 
                        direction = C_TWIST_DIRECTION_MAP.get(base, {}).get(main_color_idx, '未知')
                        target_code = TWIST_TARGET_NAMES.get((base, direction), 'ERR')
                        twists[base] = {'direction': direction, 'target': target_code}
                        self.log(f"   ⚠️ `{base}` 原地翻轉 -> 目標 `{target_code}` ({direction})")
                    else: 
                        self.log(f"   ✅ `{base}` 歸位")
                        stats['solved'] += 1
                    
                    if base != buffer_name:
                        solved_bases.add(base)
            except Exception as e: self.log(f"Check Error {base}: {e}")

        path = []; curr = buffer_name; start_base = buffer_name
        cycle_count = 0
        
        self.log(f"   *開始追蹤 (Buffer: {buffer_name})...*")
        
        for _ in range(30):
            try:
                colors = get_colors(self.cube, curr, 'corner')
                base = identify_piece(colors, 'corner')
                if base == 'BUFFER': base = 'UFR'
                target = get_target_code(base, colors[0], 'corner')
                if base == 'ERR' or target == 'ERR': break

                if base == start_base: 
                    if cycle_count == 0 and len(path) > 0: cycle_count = 1
                    
                    if base != buffer_name: 
                        path.append(target); solved_bases.add(base); 
                        self.log(f"   -> 指向 `{target}` (閉合)")
                    else: 
                        self.log(f"   -> Buffer 歸位")
                    
                    next_b = next((b for b in C_PRIORITY if b not in solved_bases and b != buffer_name), None)
                    if not next_b: break
                    
                    self.log(f"   ⚠️ **[破圈]** -> 去 【`{next_b}`】")
                    cycle_count += 1
                    path.append(next_b); curr = next_b; start_base = next_b
                elif base in solved_bases: break
                else: 
                    if target == 'ERR' and base == buffer_name:
                        target = BUFFER_TARGET_DEFS.get((base, colors[0]), 'ERR')
                    self.log(f"   -> 指向 `{target}`"); path.append(target); solved_bases.add(base); curr = target
            except Exception as e: break
        
        if len(path) > 0 and cycle_count == 0: cycle_count = 1
        stats['cycles'] = cycle_count
        has_parity = (len(path) % 2 != 0)
        return path, has_parity, twists, stats

    def trace_edges(self, has_parity):
        solved_bases = set(); flips = []
        stats = {'solved': 0, 'cycles': 0}
        
        self.log("   *預檢邊塊...*")
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
                    flips.append(base); self.log(f"   ⚠️ `{base}` 翻轉")
                else: 
                    self.log(f"   ✅ `{base}` 歸位")
                    stats['solved'] += 1
                solved_bases.add(base)

        path = []; curr = 'UF'; start_base = 'BUFFER'
        cycle_count = 0
        
        self.log("   *開始追蹤...*")
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
                if cycle_count == 0 and len(path) > 0: cycle_count = 1

                if effective_base != 'BUFFER':
                    path.append(target); solved_bases.add(effective_base); 
                    self.log(f"   -> 指向 `{target}` (閉合)")
                else: 
                    self.log(f"   -> Buffer 歸位")
                
                next_b = next((b for b in E_PRIORITY if b not in solved_bases), None)
                if not next_b: break
                
                self.log(f"   ⚠️ **[破圈]** -> 去 【`{next_b}`】")
                cycle_count += 1
                path.append(next_b); curr = next_b; start_base = next_b
            elif effective_base in solved_bases: break
            else: 
                self.log(f"   -> 指向 `{target}`"); path.append(target); solved_bases.add(effective_base); curr = target
        
        if len(path) > 0 and cycle_count == 0: cycle_count = 1
        stats['cycles'] = cycle_count
        return path, flips, stats