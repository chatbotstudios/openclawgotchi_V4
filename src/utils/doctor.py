#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime


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


def run_checks() -> dict:
    """Run all health checks and return structured results."""
    checks = {}

    # 1. Internet
    ok, out = check("Internet", "ping -c 1 google.com")
    checks["internet"] = {"ok": ok, "output": out}

    # 2. Disk Space
    disk_result = {"ok": False, "output": "", "used_pct": None}
    try:
        df_out = subprocess.check_output(["df", "-h", "/"], text=True, timeout=10)
        lines = df_out.strip().splitlines()
        out = lines[-1] if lines else ""
        used_pct = int(out.split()[-2].replace("%", ""))
        disk_result = {"ok": True, "output": f"{used_pct}% used", "used_pct": used_pct}
    except Exception as e:
        disk_result = {"ok": False, "output": str(e), "used_pct": None}
    checks["disk"] = disk_result

    # 3. Temperature
    temp_result = {"ok": False, "output": "", "celsius": None}
    try:
        temp_raw = subprocess.check_output(["vcgencmd", "measure_temp"], text=True, timeout=5).strip()
        temp = float(temp_raw.replace("temp=", "").replace("'C", "").replace("°C", "").strip())
        temp_result = {"ok": True, "output": f"{temp}°C", "celsius": temp}
    except Exception:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp_val = float(f.read().strip()) / 1000
            temp_result = {"ok": True, "output": f"{temp_val}°C", "celsius": temp_val}
        except Exception:
            temp_result = {"ok": False, "output": "", "celsius": None}
    checks["temperature"] = temp_result

    # 4. Service Status
    ok, out = check('Service', 'systemctl is-active gotchi')
    checks["service"] = {"ok": ok, "output": out}

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
    checks["logs"] = {"ok": ok, "output": out}

    return checks


def main():
    bot_name = os.environ.get("BOT_NAME", "Gotchi")

    if "--json" in sys.argv:
        checks = run_checks()
        all_ok = all(c["ok"] for c in checks.values())
        print(json.dumps({
            "status": "healthy" if all_ok else "issues",
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }))
        sys.exit(0 if all_ok else 1)
        return

    print(f"=== 🏥 {bot_name} Doctor ===")
    all_ok = True

    checks = run_checks()

    # 1. Internet
    c = checks["internet"]
    if c["ok"]:
        print("[✅] Internet: OK")
    else:
        print(f"[❌] Internet: FAIL\n{c['output']}")
        all_ok = False

    # 2. Disk Space
    c = checks["disk"]
    if c["ok"]:
        if c["used_pct"] < 90:
            print(f"[✅] Disk: {c['used_pct']}% used")
        else:
            print(f"[⚠️] Disk: {c['used_pct']}% used (CRITICAL)")
            all_ok = False
    else:
        print(f"[❌] Disk: FAIL\n{c['output']}")
        all_ok = False

    # 3. Temperature
    c = checks["temperature"]
    if c["ok"]:
        if c["celsius"] < 70:
            print(f"[✅] Temp: {c['celsius']}°C")
        else:
            print(f"[⚠️] Temp: {c['celsius']}°C (HOT)")
            all_ok = False
    else:
        print("[⚠️] Temp: Unavailable")
        all_ok = False

    # 4. Service Status
    c = checks["service"]
    if c["output"] == "active":
        print("[✅] Service: Active")
    else:
        print(f"[❌] Service: {c['output']}")
        all_ok = False

    # 5. Recent Errors
    c = checks["logs"]
    if not c["output"]:
        print("[✅] Logs: No recent errors")
    else:
        print(f"[⚠️] Logs (Recent Errors):\n{c['output']}")

    print("==========================")
    if all_ok:
        print("Result: SYSTEM HEALTHY")
        sys.exit(0)
    else:
        print("Result: ISSUES DETECTED")
        sys.exit(1)


if __name__ == "__main__":
    main()
