import os
import sys
import argparse
import pandas as pd
import joblib
from importlib.resources import files
import gpu_profiler

# ==============================
# Config
# ==============================
# Input file defaults to extracted_features.csv in cwd, unless provided
cwd = os.getcwd()
if len(sys.argv) > 1 and sys.argv[-1].endswith(".csv"):
    input_file = sys.argv[-1]
else:
    input_file = os.path.join(cwd, "extracted_features.csv")

output_file = os.path.join(cwd, "predictions.csv")

# Path to trained models inside gpu_profiler package
model_dir = files(gpu_profiler)
MODEL_MIN_FILE = model_dir / "model_min.joblib"
MODEL_MAX_FILE = model_dir / "model_max.joblib"
MODEL_AVG_FILE = model_dir / "model_avg.joblib"

# Manually choose features (must match training)
SELECTED_METRIC_NAMES = [
    "Avg. Executed Instructions Per Scheduler",
    "Avg. Issued Instructions Per Scheduler",
    "Branch Instructions",
    "Branch Instructions Ratio",
    "Compute (SM) Throughput",
 "Executed Instructions",
 "Executed Ipc Active",
 "Issued Instructions",
"Issued Ipc Active",
"Maximum Sampling Interval",
"Memory Throughput",
"SM Frequency" 
]

# ==============================
# Parse arguments
# ==============================
parser = argparse.ArgumentParser(description="Predict GPU power consumption")
parser.add_argument("-m", "--mode", choices=["min", "avg", "peak", "all"], required=True,
                    help="Prediction mode")
args = parser.parse_args()
mode = args.mode

# ==============================
# Load dataset
# ==============================
df_data = pd.read_csv(input_file)

# Check features
missing = [f for f in SELECTED_METRIC_NAMES if f not in df_data.columns]
if missing:
    raise ValueError(
        f"Missing features in {input_file}: {missing}\n"
        f"Available features: {list(df_data.columns)}"
    )

# Keep only selected features
for col in SELECTED_METRIC_NAMES:
    df_data[col] = pd.to_numeric(df_data[col], errors="coerce")
df_data = df_data.fillna(0.0)

# ==============================
# Load trained models
# ==============================
model_min = model_avg = model_max = None
if mode in ["min", "all"]:
    model_min = joblib.load(MODEL_MIN_FILE)
if mode in ["avg", "all"]:
    model_avg = joblib.load(MODEL_AVG_FILE)
if mode in ["peak", "all"]:
    model_max = joblib.load(MODEL_MAX_FILE)

# ==============================
# Run predictions
# ==============================
results = []
for _, row in df_data.iterrows():
    input_vector = pd.DataFrame([[row[f] for f in SELECTED_METRIC_NAMES]],
                                columns=SELECTED_METRIC_NAMES)
    result_row = {"filename": row.get("filename", "unknown")}

    if model_min:
        result_row["pred_min"] = model_min.predict(input_vector)[0]
    if model_avg:
        result_row["pred_avg"] = model_avg.predict(input_vector)[0]
    if model_max:
        result_row["pred_max"] = model_max.predict(input_vector)[0]

    results.append(result_row)

# ==============================
# Save predictions
# ==============================
result_df = pd.DataFrame(results)
result_df.to_csv(output_file, index=False)

print("✅ Prediction complete.")
print(f"Results saved to: {output_file}")
print(result_df)
