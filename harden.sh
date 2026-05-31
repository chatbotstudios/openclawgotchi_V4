#!/bin/bash
set -e

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║    🔧 OpenClawGotchi V3 — Pi Hardening Script     ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# ============================================
# 1. SWAP (critical for 512MB Pi)
# ============================================
echo "[1/5] Configuring swap (1GB)..."
if ! command -v dphys-swapfile &> /dev/null; then
    echo "  Installing dphys-swapfile..."
    sudo apt update && sudo apt install -y dphys-swapfile > /dev/null 2>&1 || true
fi

if [ -f /etc/dphys-swapfile ]; then
    sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
    sudo systemctl restart dphys-swapfile 2>/dev/null || true
    echo "  ✅ Swap: $(free -h | grep Swap | awk '{print $2}')"
else
    echo "  ⚠️  dphys-swapfile not found, skipping"
fi

# ============================================
# 2. HARDWARE WATCHDOG (auto-reboot on freeze)
# ============================================
echo ""
echo "[2/5] Enabling hardware watchdog..."

# Enable BCM2835 watchdog in boot config
BOOT_CONFIG="/boot/config.txt"
if [ -f "/boot/firmware/config.txt" ]; then
    BOOT_CONFIG="/boot/firmware/config.txt"  # Newer Pi OS
fi

if ! grep -q "dtparam=watchdog=on" "$BOOT_CONFIG" 2>/dev/null; then
    echo "dtparam=watchdog=on" | sudo tee -a "$BOOT_CONFIG" > /dev/null
    echo "  ✅ Hardware watchdog enabled in $BOOT_CONFIG"
else
    echo "  ✅ Hardware watchdog already enabled"
fi

# Configure systemd to use hardware watchdog (15s timeout)
SYSTEMD_CONF="/etc/systemd/system.conf"
if ! grep -q "^RuntimeWatchdogSec=" "$SYSTEMD_CONF" 2>/dev/null; then
    echo "  Configuring systemd watchdog..."
    sudo sed -i 's/^#RuntimeWatchdogSec=.*/RuntimeWatchdogSec=15/' "$SYSTEMD_CONF" 2>/dev/null || \
    echo "RuntimeWatchdogSec=15" | sudo tee -a "$SYSTEMD_CONF" > /dev/null
    echo "  ✅ Systemd watchdog: 15s timeout (reboot on system freeze)"
else
    echo "  ✅ Systemd watchdog already configured"
fi

# ============================================
# 3. BOT SERVICE WATCHDOG (cron backup)
# ============================================
echo ""
echo "[3/5] Adding bot service watchdog (Battery Optimized)..."
CRON_LINE="*/15 * * * * systemctl is-active gotchi.service >/dev/null || systemctl restart gotchi.service"
(sudo crontab -l 2>/dev/null | grep -v "gotchi" ; echo "$CRON_LINE") | sudo crontab -
echo "  ✅ Cron watchdog: checks every 15 min, restarts if dead"

# ============================================
# 4. DISABLE UNNECESSARY SERVICES (~50-80MB saved)
# ============================================
echo ""
echo "[4/5] Disabling unnecessary services..."

# Services to disable (saves RAM on Pi Zero 2W)
SERVICES="
    # Audio (saves ~40MB)
    pipewire pipewire-pulse wireplumber
    pulseaudio
    # Desktop/VNC
    wayvnc wayvnc-control
    # Printing
    cups cups-browsed cups.path cups.socket
    # Mobile/Network discovery
    ModemManager avahi-daemon
    # Package manager background
    packagekit
    # [PRESERVED] Bluetooth & Wi-Fi logic (Required for Pwning/BTPAN)
    # bluetooth hciuart
"

for svc in $SERVICES; do
    [[ "$svc" == \#* ]] && continue  # Skip comments
    sudo systemctl mask "$svc" 2>/dev/null || true
    sudo systemctl stop "$svc" 2>/dev/null || true
done
echo "  ✅ Disabled: audio, printing, vnc, avahi, and background updates."
echo "  🛡️  Preserved: bluetooth, networking (Ready for Pwning/BTPAN)"

# User-level audio services
USER_SERVICES="pipewire pipewire-pulse wireplumber pipewire.socket pipewire-pulse.socket"
for usvc in $USER_SERVICES; do
    systemctl --user mask "$usvc" 2>/dev/null || true
    systemctl --user stop "$usvc" 2>/dev/null || true
done
echo "  ✅ Silenced user-level audio layers"

# ============================================
# 5. ENSURE BOT SERVICE IS READY
# ============================================
echo ""
echo "[5/5] Ensuring bot service is enabled..."
sudo systemctl daemon-reload
sudo systemctl enable gotchi.service 2>/dev/null || true
echo "  ✅ gotchi.service enabled"

# ============================================
# SUMMARY
# ============================================
echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║              ✅ Hardening Complete!               ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "  📊 Status:"
echo "     Swap:     $(free -h | grep Swap | awk '{print $2}')"
echo "     Free RAM: $(free -h | grep Mem | awk '{print $4}')"
echo "     Bot:      $(systemctl is-active gotchi-bot 2>/dev/null || echo 'not running')"
echo ""
echo "  🛡️ Protection:"
echo "     • Hardware watchdog: 15s (reboots on system freeze)"
echo "     • Cron watchdog: 5min (restarts bot if crashed)"
echo "     • Systemd: auto-restart on bot failure"
echo ""
echo "  ⚠️  Reboot required for hardware watchdog!"
echo "     sudo reboot"
echo ""
