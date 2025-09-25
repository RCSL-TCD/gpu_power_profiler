import os
import sys
import pandas as pd

# === CONFIG ===
cwd = os.getcwd()

# If a CSV path is provided as argument, use that. Otherwise fallback to extracted_data.csv
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = os.path.join(cwd, "extracted_data.csv")

output_file = os.path.join(cwd, "extracted_features.csv")


def process_file(path):
    """Read one CSV and return: dict {metric_name: mean_value}"""
    df = pd.read_csv(path)

    # Keep only required columns
    cols = ["Section Name", "Metric Name", "Metric Unit", "Metric Value"]
    df = df[cols]

    # Filter invalid rows
    df = df[
        df["Metric Name"].notna()
        & (df["Metric Name"].astype(str).str.strip() != "")
        & (df["Metric Name"] != "Function Cache Configuration")
    ]

    # Clean Metric Value (remove commas, convert to float)
    df["Metric Value"] = (
        df["Metric Value"].astype(str).str.replace(",", "", regex=False).str.strip()
    )
    df["Metric Value"] = pd.to_numeric(df["Metric Value"], errors="coerce")
    df = df.dropna(subset=["Metric Value"])

    # Average by Metric Name
    averaged = df.groupby("Metric Name", as_index=False).agg({
        "Metric Value": "mean"
    })

    return dict(zip(averaged["Metric Name"], averaged["Metric Value"]))


def main():
    # Process extracted data
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    averaged_map = process_file(input_file)

    # Ordered by metric name for consistency
    metric_names_ordered = sorted(averaged_map.keys())

    # Build output dataset
    filename = os.path.splitext(os.path.basename(input_file))[0]
    columns = ["index", "filename"] + metric_names_ordered
    rows = []

    data_row = [1, filename]
    for m in metric_names_ordered:
        data_row.append(averaged_map.get(m, 0.0))
    rows.append(data_row)

    # Save CSV
    df_out = pd.DataFrame(rows, columns=columns)
    df_out.to_csv(output_file, index=False)

    print(f"✅ Extracted all features with metric names saved to: {output_file}")


if __name__ == "__main__":
    main()
