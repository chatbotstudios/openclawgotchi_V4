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

    # 4. Uptime
    uptime_result = {"ok": True, "output": "", "days": 0, "hours": 0}
    try:
        with open("/proc/uptime") as f:
            uptime_sec = float(f.read().split()[0])
        days = int(uptime_sec // 86400)
        hours = int((uptime_sec % 86400) // 3600)
        mins = int((uptime_sec % 3600) // 60)
        uptime_result = {"ok": True, "output": f"{days}d {hours}h {mins}m", "days": days, "hours": hours}
    except Exception as e:
        uptime_result = {"ok": False, "output": str(e), "days": 0, "hours": 0}
    checks["uptime"] = uptime_result

    # 5. Memory
    mem_result = {"ok": False, "output": "", "available_mb": 0, "total_mb": 0, "pct": 0}
    try:
        import psutil
        mem = psutil.virtual_memory()
        avail_mb = int(mem.available / (1024 * 1024))
        total_mb = int(mem.total / (1024 * 1024))
        pct = int(mem.percent)
        ok = pct < 90
        mem_result = {"ok": ok, "output": f"{avail_mb}/{total_mb} MB free ({pct}% used)", "available_mb": avail_mb, "total_mb": total_mb, "pct": pct}
    except Exception:
        try:
            with open("/proc/meminfo") as f:
                data = f.read()
            total_line = [l for l in data.splitlines() if "MemTotal" in l][0]
            avail_line = [l for l in data.splitlines() if "MemAvailable" in l][0]
            total_kb = int(total_line.split()[1])
            avail_kb = int(avail_line.split()[1])
            avail_mb = avail_kb // 1024
            total_mb = total_kb // 1024
            pct = int((total_kb - avail_kb) / total_kb * 100)
            ok = pct < 90
            mem_result = {"ok": ok, "output": f"{avail_mb}/{total_mb} MB free ({pct}% used)", "available_mb": avail_mb, "total_mb": total_mb, "pct": pct}
        except Exception:
            mem_result = {"ok": False, "output": "unavailable", "available_mb": 0, "total_mb": 0, "pct": 0}
    checks["memory"] = mem_result

    # 6. LLM Providers (check which API keys are configured, without revealing values)
    llm_result = {"ok": False, "output": "", "providers": []}
    try:
        providers = []
        for var, name in [
            ("DEEPSEEK_API_KEY", "deepseek"), ("OPENROUTER_API_KEY", "openrouter"),
            ("ANTHROPIC_API_KEY", "anthropic"), ("OPENAI_API_KEY", "openai"),
            ("GOOGLE_API_KEY", "google"), ("GEMINI_API_KEY", "gemini"),
            ("GROQ_API_KEY", "groq"), ("TOGETHER_API_KEY", "together"),
        ]:
            if os.environ.get(var):
                providers.append(name)
        if not providers:
            providers.append("none")
        ok = len([p for p in providers if p != "none"]) > 0
        llm_result = {"ok": ok, "output": ", ".join(providers) if providers else "none", "providers": providers}
    except Exception as e:
        llm_result = {"ok": False, "output": str(e), "providers": []}
    checks["llm"] = llm_result

    # 7. Service Status
    ok, out = check('Service', 'systemctl is-active gotchi')
    checks["service"] = {"ok": ok, "output": out}

    # 8. Display Driver
    display_result = {"ok": False, "output": "", "driver": "unknown"}
    try:
        _src = os.path.join(os.path.dirname(__file__), "..")
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from config import MOCK_HARDWARE
        if MOCK_HARDWARE:
            display_result = {"ok": True, "output": "Mock EPD (MOCK_HARDWARE=1)", "driver": "mock"}
        else:
            from hardware.display import _epd_initialized
            if _epd_initialized:
                display_result = {"ok": True, "output": "Waveshare 2.13 E-Ink (hardware)", "driver": "real"}
            else:
                display_result = {"ok": False, "output": "Simulator mode (no hardware)", "driver": "simulator"}
    except Exception as e:
        display_result = {"ok": False, "output": str(e), "driver": "error"}
    checks["display"] = display_result

    # 9. Recent Errors
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

    # 4. Uptime
    c = checks["uptime"]
    if c["ok"]:
        print(f"[✅] Uptime: {c['output']}")
    else:
        print(f"[⚠️] Uptime: {c['output']}")

    # 5. Memory
    c = checks["memory"]
    if c["ok"]:
        print(f"[✅] RAM: {c['output']}")
    else:
        print(f"[❌] RAM: {c['output']}")
        all_ok = False

    # 6. LLM Providers
    c = checks["llm"]
    if c["ok"]:
        print(f"[✅] LLM: {c['output']}")
    else:
        print(f"[⚠️] LLM: {c['output']}")

    # 7. Display Driver
    c = checks["display"]
    if c["ok"]:
        print(f"[✅] Display: {c['output']}")
    else:
        print(f"[⚠️] Display: {c['output']}")

    # 8. Service Status
    c = checks["service"]
    if c["output"] == "active":
        print("[✅] Service: Active")
    else:
        print(f"[❌] Service: {c['output']}")
        all_ok = False

    # 9. Recent Errors
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
