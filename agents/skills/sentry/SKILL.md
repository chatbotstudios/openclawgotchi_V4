# 🛡️ Sentry: Tactical Wi-Fi Provisioning

The Sentry skill grants the agent the ability to autonomously navigate and pivot through the local Wi-Fi landscape. It allows for rapid provisioning of new network links without requiring an SSH terminal.

## 🛠️ Procedural Knowledge

### 1. Environmental Reconnaissance
Before joining a network, the agent should verify availability.
*   **Action**: `gotchi net scan`
*   **Logic**: Scans for SSIDs and signal strength via `nmcli`.

### 2. Network Provisioning (The Pivot)
Provisioning a new network creates a persistent profile on the unit.
*   **Action**: `gotchi net add <SSID> <PASSWORD>`
*   **Handshake**: The agent will attempt to connect immediately, verify the handshake, and report its new IP address.
*   **Natural Language**: "Sentry, bridge onto the 'Tactical_AP' network using password '12345678'."

### 3. State Awareness
*   **Managed Mode**: Provisioning works natively in this state.
*   **Monitor Mode (Hunting)**: The agent must recognize that its radio is "busy." If asked to join a network while hunting, it should prompt for permission to "Return to Base" (flip to Managed Mode) before connecting.

## 🛡️ Visual Feedback
Upon a successful connection, the agent should:
1.  Display a **success face** (`smart` or `cool`).
2.  Optionally display a **QR Code** on the E-Ink screen containing the network credentials for the operator's phone to join.

## ⚠️ Security Warning
Joining a new network while connected via SSH over Wi-Fi will cause a transient disconnection. The operator should be warned before the handshake is initiated.
