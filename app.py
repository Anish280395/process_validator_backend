from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import io, os
import base64

app = Flask(__name__)
CORS(app, origins=["https://anish280395.github.io"])

# CORS(app, resources={r"/*": {"origins": "*"}}) # Uncomment for local testing

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

        breach_counts = {}
        for breach in breaches:
            btype = breach["Breach Type"]
            breach_counts[btype] = breach_counts.get(btype, 0) + 1

        chart_base64 = None
        if breach_counts:
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(breach_counts.keys(), breach_counts.values(), color='orange')
            ax.set_title('Breach Type Counts')
            ax.set_xlabel('Breach Type')
            ax.set_ylabel('Number of Cases')
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            buf.seek(0)
            chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        
        return jsonify({
            "breaches": breaches,
            "chart": f"data:image/png;base64,{chart_base64}" if chart_base64 else None
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)