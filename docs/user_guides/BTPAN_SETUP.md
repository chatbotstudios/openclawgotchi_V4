# OpenClawGotchi: Bluetooth Tethering (BTPAN) Setup

Because the Raspberry Pi Zero has only **one** Wi-Fi chip, putting it into Monitor Mode for hacking will completely sever its internet connection. To keep the LLM online, we will route its internet through your smartphone's Bluetooth connection.

## The Problem with `airmon-ng check kill`
The standard `airmon-ng check kill` command forcefully kills `NetworkManager`. We *need* `NetworkManager` to stay alive to manage our Bluetooth connection! 

Instead of killing the manager, we must instruct it to **ignore** the Wi-Fi chip, allowing it to stay focused solely on Bluetooth.

---

## Step 1: Tell NetworkManager to Ignore Wi-Fi
Run the following bash script to configure NetworkManager to permanently ignore `wlan0` so it doesn't interfere with Bettercap:

```bash
sudo bash -c 'cat > /etc/NetworkManager/conf.d/99-unmanaged-devices.conf << EOF
[keyfile]
unmanaged-devices=interface-name:wlan0
EOF'

sudo systemctl restart NetworkManager
```

*Note: After running this, your Pi will instantly drop off your home Wi-Fi because it is now "unmanaged". You must be connected via a physical serial cable or USB Gadget mode (`raspconnect`) for the next steps!*

---

## Step 2: Pair Your Phone via Bluetooth
1. Turn on **Personal Hotspot** and **Bluetooth** on your iPhone/Android. Stay on the Bluetooth settings screen so your phone is "discoverable."
2. Open a terminal on the Pi and launch the bluetooth tool:
   ```bash
   sudo bluetoothctl
   ```
3. Inside the `bluetoothctl` prompt, type the following commands:
   ```text
   agent on
   default-agent
   scan on
   ```
4. Wait until you see your phone's name and its MAC address (e.g., `AA:BB:CC:DD:EE:FF`). Once you see it, type:
   ```text
   scan off
   pair AA:BB:CC:DD:EE:FF
   ```
   *(Your phone will ask to pair. Accept it!)*
5. Trust the device so it auto-connects in the future:
   ```text
   trust AA:BB:CC:DD:EE:FF
   quit
   ```

---

## Step 3: Connect the BTPAN Network
Now that the devices are paired and trusted, we tell NetworkManager to bridge the internet connection over Bluetooth.

Run this command, replacing the MAC with your phone's MAC address:
```bash
sudo nmcli device connect AA:BB:CC:DD:EE:FF
```

If successful, you will see a new network interface called `bnep0` when you type `ifconfig` or `ip a`. 
You can test your internet connection by running:
```bash
ping google.com
```

---

## Step 4: Automate the Auto-Connect (Systemd)
To ensure the Pi automatically reconnects to your phone's Bluetooth whenever it boots up, we will create a lightweight systemd service.

1. Create the service file:
```bash
sudo nano /etc/systemd/system/btpan-auto.service
```

2. Paste the following configuration (Replace the MAC address with your phone's MAC!):
```ini
[Unit]
Description=Auto-Connect Bluetooth PAN Tethering
After=bluetooth.service NetworkManager.service
Requires=bluetooth.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/nmcli device connect AA:BB:CC:DD:EE:FF
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable btpan-auto.service
sudo systemctl start btpan-auto.service
```

## You are done!
Your Raspberry Pi now gets its internet purely from your phone's Bluetooth! 
You can now safely put `wlan0` into Monitor mode without losing Discord access:

```bash
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
sudo bettercap -iface wlan0 -api-rest -api-websocket
```
