#!/bin/bash
set -e

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║       🤖 OpenClawGotchi — Setup Wizard            ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
USER="$(whoami)"
ENV_FILE="${SCRIPT_DIR}/.env"

# ============================================
# STEP 1: Check Python & Pip
# ============================================
echo "[1/5] Checking Python..."
if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null; then
    echo "  ❌ Python 3 or Pip not found!"
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "  Please install Python 3 using Homebrew: brew install python"
        exit 1
    else
        echo "  Installing core python tools..."
        sudo apt-get update -y -qq
        sudo apt-get install -y -qq python3 python3-pip python3-venv
    fi
fi
echo "  ✅ Python $(python3 --version | cut -d' ' -f2)"

# ============================================
# STEP 1.1: Hardening System Integrity
# ============================================
if [[ "$(uname)" == "Darwin" ]]; then
    echo "  ✅ System Integrity: macOS Detected (Skipping Debian-specific updates)"
else
    if ! dpkg -l | grep -q "locales-all"; then
        echo "[1.1/5] Hardening System Integrity..."
        sudo apt-get update -y -qq
        sudo apt-get install -y -qq locales-all bluez bluez-firmware pi-bluetooth
        sudo locale-gen en_US.UTF-8 > /dev/null 2>&1
        sudo systemctl unmask bluetooth.service > /dev/null 2>&1
        sudo systemctl enable bluetooth.service > /dev/null 2>&1
        sudo systemctl start bluetooth.service > /dev/null 2>&1
        echo "  ✅ Locales stabilized & Bluetooth Unmasked"
    else
        echo "  ✅ System Integrity: OK"
    fi
fi

# ============================================
# STEP 1.5: Check Node.js (For OpenClaw Skills)
# ============================================
echo "[1.5/5] Checking Node.js for OpenClaw Skills (npx)..."
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "  ❌ Node.js or NPM not found!"
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "  Please install Node.js using Homebrew: brew install node"
    else
        echo "  Run: sudo apt update && sudo apt install -y nodejs npm"
    fi
    exit 1
fi
echo "  ✅ Node $(node -v)"

# ============================================
# STEP 2: Configure .env (interactive wizard)
# ============================================
echo ""
echo "[2/5] Configuration..."
node "${SCRIPT_DIR}/src/cli/wizard.mjs"

# ============================================
# STEP 3: Create workspace & Configure Git
# ============================================
echo ""
echo "[3/5] Setting up workspace & git config..."

# Prevent divergent branch errors on 'git pull' by defaulting to rebase
if [ -d "${SCRIPT_DIR}/.git" ]; then
    git -C "${SCRIPT_DIR}" config pull.rebase true
fi

if [ ! -d "${SCRIPT_DIR}/workspace" ]; then
    cp -r "${SCRIPT_DIR}/templates" "${SCRIPT_DIR}/workspace"
    echo "  ✅ Created workspace/ from templates"
else
    echo "  ✅ workspace/ already exists"
fi

# ============================================
# STEP 4: Install dependencies
# ============================================
echo ""
echo "[4/5] Installing dependencies..."

if [[ "$(uname)" == "Darwin" ]]; then
    echo "  [###       ] (1/4) System Libraries: Skipping APT packages on macOS"
else
    if ! command -v bettercap &> /dev/null; then
        echo -n "  [###       ] (1/4) System Libraries..."
        sudo apt-get update -y -qq
        sudo apt-get install -y -qq bettercap aircrack-ng libopenjp2-7 libopenblas-dev libtiff-dev 2>/dev/null || \
        sudo apt-get install -y -qq bettercap aircrack-ng libopenjp2-7 libatlas-base-dev libtiff5 2>/dev/null
        echo -e "\r  [###       ] (1/4) System Libraries: OK               "
    else
        echo "  [###       ] (1/4) System Libraries: ALREADY INSTALLED"
    fi
fi

echo "  Checking Python Packages..."
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    # Check if key modules are importable to make verification robust
    if ! python3 -c "import rich, websockets, qrcode, dpkt, dotenv, discord, litellm, PIL, psutil, click, telegram" &>/dev/null; then
        echo "  Installing packages from requirements.txt..."
        pip3 install --quiet --break-system-packages -r "${SCRIPT_DIR}/requirements.txt" 2>/dev/null || \
        pip3 install --quiet -r "${SCRIPT_DIR}/requirements.txt" 2>/dev/null
        echo "  ✅ Packages Installed"
    else
        echo "  ✅ Packages already healthy"
    fi
else
    echo "  ⚠️  requirements.txt not found! Falling back to core packages..."
    PACKAGES="discord.py psutil litellm Pillow RPi.GPIO spidev python-dotenv requests python-telegram-bot click rich websockets qrcode dpkt"
    pip3 install --quiet --break-system-packages $PACKAGES 2>/dev/null || true
fi

# SPI for E-Ink
if [[ "$(uname)" != "Darwin" ]] && command -v raspi-config &> /dev/null; then
    sudo raspi-config nonint do_spi 0 2>/dev/null || true
fi

# ============================================
# STEP 5: Create systemd service
# ============================================
echo ""
if [[ "$(uname)" == "Darwin" ]]; then
    echo "[5/5] Skipping systemd service setup on macOS"
else
    echo "[5/5] Setting up systemd service..."

    sudo tee /etc/systemd/system/gotchi.service > /dev/null <<EOF
[Unit]
Description=OpenClawGotchi V3 - Tactical AI Agent
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=${USER}
WorkingDirectory=${SCRIPT_DIR}
EnvironmentFile=${SCRIPT_DIR}/.env
ExecStart=${SCRIPT_DIR}/gotchi run-bot
Restart=always
RestartSec=20
StandardOutput=journal
StandardError=journal
MemoryMax=400M
MemoryHigh=350M

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable gotchi.service
fi

# ============================================
# OPTIONAL: HARDENING & SKILLS
# ============================================
echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │  🔧 Skills & CLI Integration                │"
echo "  └─────────────────────────────────────────────┘"

# Inject Skill Wrapper into .bashrc (Linux only)
if [[ "$(uname)" != "Darwin" ]]; then
    BASHRC="/home/${USER}/.bashrc"
    if [ -f "$BASHRC" ] && ! grep -q "function skills()" "$BASHRC"; then
        cat >> "$BASHRC" <<EOF

# 🦋 OpenClawGotchi: Redirect hidden skills to visible agents folder
function skills() {
    npx skills "\$@"
    if [[ "\$1" == "add" ]]; then
        if [ -d ".agents/skills" ]; then
            mkdir -p agents/skills
            mv .agents/skills/* agents/skills/ 2>/dev/null || true
            rm -rf .agents
            echo "🦋 Gotchi: Relocated skills to visible /agents folder."
        fi
    fi
}
export -f skills
EOF
        echo "  ✅ CLI skill wrapper injected into $BASHRC"
    fi
fi

# Link 'gotchi' CLI
sudo ln -sf "${SCRIPT_DIR}/gotchi" /usr/local/bin/gotchi 2>/dev/null || true
if [[ "$(uname)" == "Darwin" ]]; then
    echo "  ✅ Global 'gotchi' command symlinked to /usr/local/bin/gotchi"
fi

# Hardening Prompt (Linux only)
if [[ "$(uname)" != "Darwin" ]]; then
    read -p "  Run hardening script (watchdog, zram, etc)? [Y/n]: " RUN_HARDEN
    RUN_HARDEN=${RUN_HARDEN:-Y}
    if [[ "$RUN_HARDEN" =~ ^[Yy]$ ]]; then
        bash "${SCRIPT_DIR}/harden.sh"
    fi
fi

# ============================================
# START THE BOT / WIZARD CLIENT
# ============================================
echo ""
if [[ "$(uname)" == "Darwin" ]]; then
    read -p "Start Gotchi now? [Y/n]: " START_NOW
    START_NOW=${START_NOW:-Y}

    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        echo "╔═══════════════════════════════════════════════════╗"
        echo "║           🚀 Launching Setup Complete!            ║"
        echo "╚═══════════════════════════════════════════════════╝"
        echo "  Select startup target:"
        echo "    1) Visual Web Dash HUD (gotchi serve --port 8088)"
        echo "    2) Interactive Companion Bot (gotchi run-bot)"
        echo ""
        read -p "  Enter choice [1-2] [1]: " CHOICE
        CHOICE=${CHOICE:-1}
        if [[ "$CHOICE" == "1" ]]; then
            echo "🔗 Launching Visual Dashboard HUD... Open http://localhost:8088 in your browser."
            exec "${SCRIPT_DIR}/gotchi" serve --port 8088
        else
            echo "🦋 Launching Interactive Companion Bot..."
            exec "${SCRIPT_DIR}/gotchi" run-bot
        fi
    fi
else
    read -p "Start the bot now? [Y/n]: " START_NOW
    START_NOW=${START_NOW:-Y}

    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        sudo systemctl restart gotchi.service
        sleep 2
        if systemctl is-active --quiet gotchi.service; then
            echo "╔═══════════════════════════════════════════════════╗"
            echo "║           ✅ Setup Complete!                      ║"
            echo "╚═══════════════════════════════════════════════════╝"
        else
            echo "  ⚠️  Bot failed to start. Check logs: gotchi logs"
        fi
    fi
fi

echo ""
if [[ "$(uname)" == "Darwin" ]]; then
    echo "  📖 macOS Manual Commands:"
    echo "     gotchi serve --port 8088  # Start visual dashboard HUD"
    echo "     gotchi run-bot            # Start the companion bot"
else
    echo "  📖 Linux Manual Commands:"
    echo "     gotchi status          # Check health"
    echo "     gotchi restart         # Reboot daemon"
    echo "     gotchi logs            # View live logs"
fi
echo ""
