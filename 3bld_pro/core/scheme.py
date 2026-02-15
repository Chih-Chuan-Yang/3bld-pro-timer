import os
import json

SCHEME_FILE = "scheme.json"

class SchemeManager:
    def __init__(self):
        self.default_scheme = {
            "U": {"UBL":"A", "UB":"A", "UBR":"B", "UR":"B", "UFR":"C", "UF":"C", "UFL":"D", "UL":"D"},
            "L": {"LUB":"E", "LU":"E", "LUF":"F", "LF":"F", "LDF":"G", "LD":"G", "LDB":"H", "LB":"H"},
            "F": {"FUL":"I", "FU":"I", "FUR":"J", "FR":"J", "FDR":"K", "FD":"K", "FDL":"L", "FL":"L"},
            "R": {"RUF":"M", "RU":"M", "RUB":"N", "RB":"N", "RDB":"O", "RD":"O", "RDF":"P", "RF":"P"},
            "B": {"BUR":"Q", "BU":"Q", "BUL":"R", "BL":"R", "BDL":"S", "BD":"S", "BDR":"T", "BR":"T"},
            "D": {"DFL":"U", "DF":"U", "DFR":"V", "DR":"V", "DBR":"W", "DB":"W", "DBL":"X", "DL":"X"}
        }
        self.scheme = self.load_and_repair_scheme()

    def load_and_repair_scheme(self):
        data = self.default_scheme.copy()
        if os.path.exists(SCHEME_FILE):
            try:
                with open(SCHEME_FILE, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                for face, keys in self.default_scheme.items():
                    if face not in file_data: file_data[face] = keys
                    else:
                        for k, v in keys.items():
                            if k not in file_data[face]: file_data[face][k] = v
                return file_data
            except: pass
        return data

    def save_scheme(self, new_scheme):
        if "L" in new_scheme and "LBD" in new_scheme["L"]:
             if new_scheme["L"]["LBD"] and not new_scheme["L"].get("LDB"):
                 new_scheme["L"]["LDB"] = new_scheme["L"]["LBD"]
             del new_scheme["L"]["LBD"]
        with open(SCHEME_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_scheme, f, ensure_ascii=False, indent=2)
        self.scheme = new_scheme
        
    def reset_scheme(self):
        self.save_scheme(self.default_scheme)

    def get_letter(self, target):
        for face_code, mappings in self.scheme.items():
            if target in mappings:
                val = mappings[target]
                return val if val and val.strip() != "" else target
        return target