import pandas as pd
import random
from datetime import datetime, timedelta

# Defining 12 Standard Steps
STANDARD_STEPS = [
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

# Parameters
NUM_CASES = 20000
BREACH_PERCENTAGE = 0.2   # 20% of cases will have breaches
start_date = datetime(2025, 1, 1, 8, 0, 0)

# Store all generated rows
rows = []
for i in range(1, NUM_CASES + 1):
    case_id = f"ORDER-{i:05d}"
    steps = STANDARD_STEPS.copy()

    # Decide if this case is normal or has breaches
    is_breach = random.random() < BREACH_PERCENTAGE

    if is_breach:
        breach_type = random.choice(['missing', 'out_of_order'])

        if breach_type == 'missing':
            # Random removal of 1-3 steps
            steps_to_remove = random.sample(steps, k=random.randint(1, 3))
            steps = [s for s in steps if s not in steps_to_remove]

        elif breach_type == 'out_of_order':
            # Shuffle the steps slightly
            random.shuffle(steps)

    # Generate timestamps for this case
    timestamp = start_date + timedelta(days=i % 365)
    for step_name, sequence in steps:
        timestamp += timedelta(minutes=random.randint(10, 120))
        rows.append({
            "Case ID": case_id,
            "Activity": step_name,
            "Sequence": sequence,
            "Timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

# Create DataFrame
df = pd.DataFrame(rows)

df.columns = [col.strip().title() for col in df.columns]

# Shuffle the entire log for realism
df = df.sample(frac=1).reset_index(drop=True)

# Save to CSV
df.to_csv("synthetic_process_log.csv", index=False)

print("synthetic_process_log.csv generated successfully!")