#!/usr/bin/env python3
import os
import shlex
import subprocess
import sys


def check(name, cmd):
    """Run a simple command (no shell pipes) and return (ok, output)."""
    try:
        args = shlex.split(cmd)
        output = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, timeout=10).strip()
        return True, output
    except subprocess.CalledProcessError as e:
        return False, e.output.strip()
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

def main():
    bot_name = os.environ.get("BOT_NAME", "Gotchi")
    print(f"=== 🏥 {bot_name} Doctor ===")
    all_ok = True

    # 1. Internet
    ok, out = check("Internet", "ping -c 1 google.com")
    if ok:
        print("[✅] Internet: OK")
    else:
        print(f"[❌] Internet: FAIL\n{out}")
        all_ok = False

    # 2. Disk Space
    try:
        df_out = subprocess.check_output(["df", "-h", "/"], text=True, timeout=10)
        lines = df_out.strip().splitlines()
        out = lines[-1] if lines else ""
        ok = True
    except Exception as e:
        out = str(e)
        ok = False
    if ok:
        try:
            used_pct = int(out.split()[-2].replace("%", ""))
            if used_pct < 90:
                print(f"[✅] Disk: {used_pct}% used")
            else:
                print(f"[⚠️] Disk: {used_pct}% used (CRITICAL)")
                all_ok = False
        except Exception:
            print(f"[❌] Disk: Failed to parse df output\n{out}")
            all_ok = False
    else:
        print(f"[❌] Disk: FAIL\n{out}")
        all_ok = False

    # 3. Temperature
    try:
        temp_raw = subprocess.check_output(["vcgencmd", "measure_temp"], text=True, timeout=5).strip()
        ok, out = True, temp_raw
    except Exception:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp_val = float(f.read().strip()) / 1000
            ok, out = True, f"{temp_val}°C"
        except Exception:
            ok = False
            out = ""
    if ok:
        try:
            temp = float(out.replace("temp=", "").replace("'C", "").replace("°C", "").strip())
            if temp < 70:
                print(f"[✅] Temp: {temp}°C")
            else:
                print(f"[⚠️] Temp: {temp}°C (HOT)")
                all_ok = False
        except Exception:
            print(f"[❌] Temp: Failed to parse temperature\n{out}")
            all_ok = False
    else:
        print("[⚠️] Temp: Unavailable")
        all_ok = False

    # 4. Service Status
    ok, out = check('Service', 'systemctl is-active gotchi')
    if out == 'active':
        print("[✅] Service: Active")
    else:
        print(f"[❌] Service: {out}")
        all_ok = False

    # 5. Recent Errors
    try:
        journal_out = subprocess.check_output(
            ["journalctl", "-u", "gotchi", "-n", "50", "--no-pager"],
            text=True, timeout=10
        )
        lines = [line for line in journal_out.splitlines() if "error" in line.lower()]
        out = "\n".join(lines[-3:]) if lines else ""
        ok = True
    except Exception:
        out = ""
        ok = False
    if not out:
        print("[✅] Logs: No recent errors")
    else:
        print(f"[⚠️] Logs (Recent Errors):\n{out}")
        # Not marking as fail, just warning

    print("==========================")
    if all_ok:
        print("Result: SYSTEM HEALTHY")
        sys.exit(0)
    else:
        print("Result: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
