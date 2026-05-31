#!/usr/bin/env python3
import subprocess
import os
import sys

def check(name, cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
        return True, output
    except subprocess.CalledProcessError as e:
        return False, e.output.strip()

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
    ok, out = check("Disk", "df -h / | tail -1")
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
    ok, out = check("Temp", "vcgencmd measure_temp")
    if not ok:
        # Fallback for non-vcgencmd environments
        ok, out = check("Temp", "cat /sys/class/thermal/thermal_zone0/temp")
        if ok:
            try:
                temp = float(out.strip()) / 1000
                out = f"{temp}°C"
            except Exception:
                ok = False
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
    ok, out = check("Service", "systemctl is-active gotchi-bot")
    if out == "active":
        print("[✅] Service: Active")
    else:
        print(f"[❌] Service: {out}")
        all_ok = False

    # 5. Recent Errors
    ok, out = check("Logs", "journalctl -u gotchi-bot -n 50 | grep -i 'error' | tail -3")
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
