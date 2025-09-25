import argparse
import subprocess
import os
import sys
from loguru import logger
import importlib.util
import gpu_profiler


def run_profiler(app_path, script_path):
    logger.info("Running Nsight Compute profiler via gpu_profiler3.py")
    env = os.environ.copy()
    # Pass the application path into the profiler script via APP_EXE (backwards-compatible with TARGET_APP)
    if app_path:
        env["APP_EXE"] = app_path
        env["TARGET_APP"] = app_path  # keep TARGET_APP for older versions that might expect it
    if script_path:
        env["SCRIPT_FILE"] = script_path

    # Locate gpu_profiler3.py inside the installed package
    profiler_script = os.path.join(os.path.dirname(gpu_profiler.__file__), "gpu_profiler3.py")
    subprocess.run([sys.executable, profiler_script], check=True, env=env)


def run_feature_extraction(input_csv):
    logger.info("Running feature extraction")
    subprocess.run([sys.executable, "-m", "gpu_profiler.feature_extract", input_csv], check=True)


def run_prediction(mode):
    """
    Run predictions depending on mode:
      - min  -> only model_min.joblib
      - avg  -> only model_avg.joblib
      - peak -> only model_max.joblib
      - all  -> run all three
    """
    logger.info(f"Running prediction for mode: {mode}")

    if mode == "min":
        subprocess.run([sys.executable, "-m", "gpu_profiler.predict_power", "-m", "min"], check=True)
    elif mode == "avg":
        subprocess.run([sys.executable, "-m", "gpu_profiler.predict_power", "-m", "avg"], check=True)
    elif mode == "peak":
        subprocess.run([sys.executable, "-m", "gpu_profiler.predict_power", "-m", "peak"], check=True)
    elif mode == "all":
        subprocess.run([sys.executable, "-m", "gpu_profiler.predict_power", "-m", "all"], check=True)
    else:
        raise ValueError(f"Unknown mode: {mode}")


def main():
    parser = argparse.ArgumentParser(description="GPU Power Prediction CLI")
    parser.add_argument("-m", "--mode", choices=["min", "avg", "peak", "all"], required=True,
                        help="Prediction mode")
    parser.add_argument("-a", "--app", help="Application executable to profile")
    parser.add_argument("-s", "--script", help="Optional input script for app (e.g., .nk for Nuke)")
    parser.add_argument("-c", "--csv", help="Use an existing pre-collected CSV file instead of profiling")

    args = parser.parse_args()

    # Case 1: CSV explicitly provided
    if args.csv:
        input_csv = args.csv
        logger.info(f"Using existing CSV: {input_csv}")
        run_feature_extraction(input_csv)
        run_prediction(args.mode)

    # Case 2: Application profiling requested
    elif args.app:
        run_profiler(args.app, args.script)
        input_csv = "extracted_data.csv"
        run_feature_extraction(input_csv)
        run_prediction(args.mode)

    # Case 3: No -a and no -c provided → Use already generated extracted_features.csv
    else:
        default_features = "extracted_features.csv"
        if not os.path.exists(default_features):
            parser.error("No -a or -c provided and extracted_features.csv not found in current directory.")
        logger.info(f"Using default extracted features: {default_features}")
        run_prediction(args.mode)


if __name__ == "__main__":
    main()
