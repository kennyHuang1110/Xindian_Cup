import openpyxl
import json
from pathlib import Path

# 讀取 Excel
wb = openpyxl.load_workbook('app/data/新店盃_8隊賽程.xlsx')
ws = wb['新店盃賽程']

# 解析資料
matches = []
for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=50, values_only=True), 1):
    if not any(cell is not None for cell in row):
        break
    
    time = row[0]
    court1 = row[1]
    ref1 = row[2]
    court2 = row[3]
    ref2 = row[4]
    
    # 場地1的比賽
    if court1:
        matches.append({
            "time": time,
            "court": "場地 1",
            "match": court1,
            "referee": str(ref1) if ref1 else "-"
        })
    
    # 場地2的比賽
    if court2:
        matches.append({
            "time": time,
            "court": "場地 2",
            "match": court2,
            "referee": str(ref2) if ref2 else "-"
        })

# 輸出為 JSON
print(json.dumps(matches, indent=2, ensure_ascii=False))
