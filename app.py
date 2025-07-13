from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import io, os

app = Flask(__name__)
CORS(app)

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

def analyze_breaches(df):
    breach_records = []
    expected_sequences = set(seq for _, seq in STANDARD_PROCESS)

    grouped = df.groupby("Case ID")

    for Case_ID, group in grouped:
        group_sorted = group.sort_values(by="Timestamp")
        actual_sequence = set(group_sorted["Sequence"])
        missing_steps = expected_sequences - actual_sequence
        if missing_steps:
            for step in missing_steps:
                breach_records.append({
                    "Case ID": Case_ID,
                    "Breach Type": "Missing Steps",
                    "Details": f"Missing Sequence Numbers: {sorted(list(missing_steps))}",                  
                })
# Check for out-of-order steps
        sequence_list = list(group_sorted["Sequence"])
        if sequence_list != sorted(sequence_list):
            breach_records.append({
                "Case ID": Case_ID,
                "Breach Type": "Out of Order Steps",
                "Details": "Steps are not in the expected order."
                })
    return breach_records

@app.route("/analyze", methods=["POST"])
def analyze(): 
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]

        df = pd.read_csv(file)
        required_cols = { "Case ID", "Activity", "Sequence", "Timestamp" }
        if not required_cols.issubset(df.columns):
            return jsonify({"error": f"CSV must contain columns: {required_cols}"}), 400
        
        breaches = analyze_breaches(df)
        return jsonify({"breaches": breaches})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)