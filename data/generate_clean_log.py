import pandas as pd
import random
from datetime import datetime, timedelta

STANDARD_PROCESS = [
    ("Issuance of RFQ", 1),
    ("Technical Evaluation", 2),
    ("Commercial Evaluation", 3),
    ("PO Creation", 4),
    ("Production Planning", 5),
    ("Parts Manufacturing", 6),
    ("Packaging & Dispatch", 7),
    ("Goods In Transit", 8),
    ("Goods Receipt at Warehouse", 9),
    ("Quality Inspection", 10),
    ("Invoice Generation", 11),
    ("Payment Clearance", 12)
]

NUM_CASES = 20000
start_date = datetime(2025, 1, 1, 8, 0, 0)

row = []
for i in range(1, NUM_CASES + 1):
    case_id = f"ORDER-{i:05d}"
    timestamp = start_date + timedelta(days=i % 365)

    for step_name, sequence in STANDARD_PROCESS:
        timestamp += timedelta(minutes=random.randint(10, 120))
        row.append({
            "Case ID": case_id,
            "Activity": step_name,
            "Sequence": sequence,
            "Timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

df = pd.DataFrame(row)

df.columns = [col.strip() for col in df.columns]
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv("clean_process_log.csv", index=False)

print("clean_process_log.csv generated successfully.")
