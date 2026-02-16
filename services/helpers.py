import random
import pandas as pd
import os
import re

HISTORY_FILE = "3bld_history.csv"

def generate_scramble(length=20):
    moves = ["U", "D", "L", "R", "F", "B"]
    suffixes = ["", "'", "2"]
    scramble = []; last = ""
    for _ in range(length):
        m = random.choice(moves)
        while m == last: m = random.choice(moves)
        scramble.append(m + random.choice(suffixes))
        last = m
    return " ".join(scramble)

def calc_ao(times, n):
    if len(times) < n: return None
    subset = times[-n:]
    valid_vals = []
    dnf_count = 0
    for r in subset:
        if r['penalty'] == 'DNF': valid_vals.append(999999); dnf_count += 1
        elif r['penalty'] == '+2': valid_vals.append(r['raw_time'] + 2)
        else: valid_vals.append(r['raw_time'])
    if dnf_count >= 2 and n == 5: return "DNF"
    if dnf_count >= 2 and n == 12: return "DNF"
    valid_vals.sort()
    middle = valid_vals[1:-1]
    avg = sum(middle) / len(middle)
    return f"{avg:.2f}"

def save_to_db(record, stats):
    final_time = record['raw_time']
    if record['penalty'] == '+2': final_time += 2
    if record['penalty'] == 'DNF': return 
    new_data = {
        "Timestamp": record['date'], "Scramble": record['scramble'], "Time": final_time,
        "Total_Moves": stats['total_moves'], "Total_Algs": stats['total_algs'],
        "Total_Targets": stats['Edges']['targets'] + stats['Corners']['targets'],
        "Parity": 1 if stats['Parity'] else 0,
        "Total_Cycles": stats['Edges']['cycles'] + stats['Corners']['cycles'],
        "Edge_Cycles": stats['Edges']['cycles'], "Corner_Cycles": stats['Corners']['cycles'],
        "Solved_Pieces": stats['Edges']['solved'] + stats['Corners']['solved'],
        "Flips": stats['Edges']['flips'], "Twists": stats['Corners']['twists'],
        "Difficulty_Score": stats.get('difficulty_score', 0)
    }
    df = pd.DataFrame([new_data])
    if not os.path.exists(HISTORY_FILE): df.to_csv(HISTORY_FILE, index=False)
    else:
        try:
            old = pd.read_csv(HISTORY_FILE)
            pd.concat([old, df], ignore_index=True).to_csv(HISTORY_FILE, index=False)
        except: df.to_csv(HISTORY_FILE, index=False)

def get_display_text(target_code, scheme_manager):
    target_code = target_code.strip()
    if " " in target_code and not "(" in target_code:
        parts = target_code.split()
        return f"{scheme_manager.get_letter(parts[0])}{scheme_manager.get_letter(parts[1])}"
    match = re.match(r"([A-Za-z]+)(.*)", target_code)
    if match:
        core_code = match.group(1).strip()
        suffix = match.group(2).strip()
        user_char = scheme_manager.get_letter(core_code)
        if user_char != core_code: return f"{user_char}{suffix}"
    return scheme_manager.get_letter(target_code)