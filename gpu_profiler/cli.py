import argparse
import subprocess
import os
import sys
from loguru import logger
import pandas as pd
import joblib

def run_nsight_compute(app_path, capture_time):
    logger.info("Running Nsight Compute profiling...")

    # Output file name (overwrite if exists)
    ncu_output = "ncu_report.ncu-rep"

    # Run Nsight Compute with minimal required metrics
    cmd = [
        "ncu", "--target-processes", "all",
        "--set", "base", "--export", "profile",
        "--output", ncu_output,
        "--launch-timeout", str(capture_time),
        app_path
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.success("Nsight Compute profiling complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Nsight Compute failed: {e}")
        sys.exit(1)

def run_feature_extraction():
    logger.info("Extracting features from Nsight CSV...")
    cmd = [sys.executable, "gpu_profiler/feature_extract.py"]
    try:
        subprocess.run(cmd, check=True)
        logger.success("Feature extraction complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Feature extraction failed: {e}")
        sys.exit(1)

def run_prediction(mode):
    logger.info("Running power prediction...")
    cmd = [sys.executable, "gpu_profiler/predict_power.py", "--mode", mode]
    try:
        subprocess.run(cmd, check=True)
        logger.success("Power prediction complete. See predictions.csv.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Prediction failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="GPU Power Profiler CLI")
    parser.add_argument("-a", "--app", required=True, help="Path to the application to profile")
    parser.add_argument("-m", "--mode", required=True, choices=["min", "avg", "max", "all"], help="Power prediction mode")
    parser.add_argument("-c", "--capture_time", type=int, default=60, help="Capture time in seconds (default: 60)")
    parser.add_argument("-s", "--skip_profiling", action="store_true", help="Skip Nsight profiling if data already exists")
    args = parser.parse_args()

    logger.info(f"App to profile: {args.app}")
    logger.info(f"Prediction mode: {args.mode}")
    logger.info(f"Capture time: {args.capture_time}")
    logger.info(f"Skip profiling: {args.skip_profiling}")

    os.chdir(os.getcwd())  # Ensure cwd

    if not args.skip_profiling:
        run_nsight_compute(args.app, args.capture_time)

    run_feature_extraction()
    run_prediction(args.mode)

if __name__ == "__main__":
    main()