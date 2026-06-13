import logging
import subprocess
import os
from pathlib import Path

# Setup dedicated forensics logger
_forensics_logger = None

def get_forensics_logger():
    global _forensics_logger
    if _forensics_logger is not None:
        return _forensics_logger
        
    try:
        from config import WORKSPACE_DIR
        mem_dir = WORKSPACE_DIR / "memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        log_path = mem_dir / "tether_forensics.log"
    except ImportError:
        # Fallback if config is unavailable
        log_path = Path("tether_forensics.log")
        
    _forensics_logger = logging.getLogger("Forensics")
    _forensics_logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to root logger (avoid double logging in main gotchi log)
    _forensics_logger.propagate = False
    
    # Millisecond precision format
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    fh = logging.FileHandler(log_path)
    fh.setFormatter(formatter)
    
    # Optional console output for deep dev
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    
    _forensics_logger.addHandler(fh)
    _forensics_logger.addHandler(ch)
    
    return _forensics_logger

def get_bnep_stats() -> dict:
    """Read network interface statistics for bnep0."""
    stats = {"tx_dropped": 0, "tx_bytes": 0}
    try:
        if os.path.exists("/sys/class/net/bnep0/statistics/tx_dropped"):
            with open("/sys/class/net/bnep0/statistics/tx_dropped", "r") as f:
                stats["tx_dropped"] = int(f.read().strip())
        if os.path.exists("/sys/class/net/bnep0/statistics/tx_bytes"):
            with open("/sys/class/net/bnep0/statistics/tx_bytes", "r") as f:
                stats["tx_bytes"] = int(f.read().strip())
    except Exception as e:
        log = get_forensics_logger()
        log.error(f"Failed to read bnep0 stats: {e}")
    return stats

def log_thermal_stats():
    """Log Raspberry Pi CPU temperature and clock speed."""
    log = get_forensics_logger()
    try:
        temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True, timeout=2).stdout.strip()
        clock = subprocess.run(["vcgencmd", "measure_clock", "arm"], capture_output=True, text=True, timeout=2).stdout.strip()
        log.debug(f"[THERMAL] {temp} | {clock}")
    except FileNotFoundError:
        pass # Not running on Raspberry Pi or vcgencmd missing
    except Exception as e:
        log.error(f"Thermal stats failed: {e}")

def dump_kernel_dmesg():
    """Dump the last 30 lines of the kernel ring buffer to forensics log."""
    log = get_forensics_logger()
    log.critical("--- [CRASH DUMP START] KERNEL DMESG ---")
    try:
        res = subprocess.run(["dmesg", "-T"], capture_output=True, text=True, timeout=5)
        # Get last 30 lines
        lines = res.stdout.strip().split("\n")[-30:]
        for line in lines:
            log.critical(line)
    except Exception as e:
        log.error(f"Failed to dump dmesg: {e}")
    log.critical("--- [CRASH DUMP END] ---")
