#!/usr/bin/env python3
"""
gpu_profiler3.py

Cross-platform wrapper to run Nsight Compute (ncu) against an application.
- Launches the application *through ncu*
- Profiles for a given duration (or until Ctrl-C)
- Stops ncu (entire process group) gracefully so it can flush .ncu-rep
- Exports results to CSV

Usage:
  python gpu_profiler3.py -a /path/to/app -s optional_script -d 60
Or, if called via gpu_profiler.py, APP_EXE and SCRIPT_FILE can be set in env.
"""

import argparse
import os
import subprocess
import sys
import signal

# === CONFIGURATION ===
working_dir = os.getcwd()
report_path = os.path.join(working_dir, "extracted_data")
csv_output = report_path + ".csv"

# Default Nsight Compute binary path (override with --ncu or env NCU_PATH)
if sys.platform.startswith("win"):
    default_ncu = r"C:\Program Files\NVIDIA Corporation\Nsight Compute 2024.2.0\target\windows-desktop-win7-x64\ncu.exe"
elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
    default_ncu = "/opt/nvidia/nsight-compute/2024.2.0/ncu"
else:
    default_ncu = "ncu"

default_duration_seconds = 120


def parse_args():
    p = argparse.ArgumentParser(description="Wrapper to run Nsight Compute against any app.")
    p.add_argument("-a", "--app", help="Path to application executable (or use APP_EXE/TARGET_APP env var).")
    p.add_argument("-s", "--script", help="Optional script file to pass to the application (or SCRIPT_FILE env var).")
    p.add_argument("-d", "--duration", type=int, default=default_duration_seconds,
                   help=f"Profiling duration in seconds (default: {default_duration_seconds})")
    p.add_argument("--ncu", help="Path to ncu executable (optional override).")
    return p.parse_args()


def stop_ncu(proc, platform_hint):
    """Stop ncu and its process group cleanly, fallback to kill if needed."""
    try:
        if platform_hint == "windows":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

        proc.wait(timeout=15)
        print("✅ Nsight Compute stopped cleanly.")
    except subprocess.TimeoutExpired:
        print("⚠️ Graceful stop failed, forcing kill...")
        try:
            if platform_hint == "windows":
                proc.kill()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception as e:
            print(f"❌ Failed to kill Nsight Compute: {e}")


def main():
    args = parse_args()

    ncu = args.ncu or os.environ.get("NCU_PATH") or default_ncu
    app_path = args.app or os.environ.get("APP_EXE") or os.environ.get("TARGET_APP")
    script_file = args.script or os.environ.get("SCRIPT_FILE")
    duration = args.duration

    if not app_path:
        print("❌ Error: application executable not provided (use -a or set APP_EXE/TARGET_APP).")
        sys.exit(2)

    # Decide platform
    platform_hint = "windows" if sys.platform.startswith("win") else "unix"

    # Build ncu command
    ncu_cmd = [
        ncu,
        "--set", "full",
        "--force-overwrite",
        "--export", report_path,
        "--target-processes", "all",
        "--replay-mode", "kernel",
        "--kernel-name", "regex:.*",
        app_path,
    ]
    if script_file:
        ncu_cmd.append(script_file)

    print(f"🚀 Starting Nsight Compute: {' '.join(ncu_cmd)}")
    print(f"⏱ Duration: {duration}s")

    popen_kwargs = {"cwd": working_dir}
    if platform_hint == "windows":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    try:
        proc = subprocess.Popen(ncu_cmd, **popen_kwargs)
    except Exception as e:
        print(f"❌ Failed to start ncu: {e}")
        sys.exit(3)

    print("⏳ Profiling in progress... Press Ctrl-C to stop early.")

    try:
        proc.wait(timeout=duration)
        print("✅ Nsight Compute finished within duration.")
    except subprocess.TimeoutExpired:
        print(f"⏲ Duration expired ({duration}s). Stopping Nsight Compute...")
        stop_ncu(proc, platform_hint)
    except KeyboardInterrupt:
        print("⛔ Interrupted by user. Stopping Nsight Compute...")
        stop_ncu(proc, platform_hint)

    # === Export results to CSV ===
    import_cmd = [
        ncu,
        "--import", report_path + ".ncu-rep",
        "--csv",
        "--page", "details",
    ]

    print("📤 Exporting metrics to CSV...")
    try:
        with open(csv_output, "w", encoding="utf-8") as f:
            subprocess.run(import_cmd, stdout=f, check=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("❌ ncu export timed out.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ncu export command failed: {e}")
    except FileNotFoundError as e:
        print(f"❌ Failed to run ncu at '{ncu}': {e}")

    if os.path.exists(csv_output):
        print(f"✅ Export complete: {csv_output}")
    else:
        print("❌ Export failed. CSV not generated.")


if __name__ == "__main__":
    main()

