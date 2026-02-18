from solver import BlindSolver
import json

def run_test(name, scramble):
    print(f"\n{'='*30} {name} {'='*30}")
    print(f"🔥 打亂: {scramble}")
    
    solver = BlindSolver()
    success = solver.solve(scramble)
    
    if success:
        print("\n🔎 [資料結構檢查]")
        
        # 1. 邊塊
        print(f"\n🧠 【邊塊路徑 (Edges)】:")
        e_data = solver.edge_result.get('path_detailed', [])
        print(json.dumps([{"pair": p['pair'], "is_new_cycle": p.get('is_new_cycle', False)} for p in e_data], indent=2, ensure_ascii=False))
        
        # 2. 角塊
        print(f"\n🧠 【角塊路徑 (Corners)】:")
        c_data = solver.corner_result.get('path_detailed', [])
        print(json.dumps([{"pair": p['pair'], "is_new_cycle": p.get('is_new_cycle', False)} for p in c_data], indent=2, ensure_ascii=False))
        
        # 3. Parity
        print(f"\n⚠️ Parity 狀態: {solver.has_parity}")
        if solver.has_parity:
            print(f"🎯 Parity Target: {solver.corner_result.get('parity_target')}")
    else:
        print("❌ 解算失敗")

scramble_3 = "B' L' F2 L2 F' D L' B' D F2 U2 B2 L2 U F2 D F2 L2 B2 D F' R"
run_test("測試 3", scramble_3)