---
name: tailscale
description: Manage Tailscale VPN on the Raspberry Pi Zero 2W. Use this skill for connecting, disconnecting, checking status, and configuring Tailscale securely.
version: 1.0.0
author: OpenClawGotchi
tags: [networking, vpn, tailscale, remote-access, pi-zero]
capabilities:
  - tailscale-management
  - remote-access
  - vpn-configuration
  - headless-setup
---

# Tailscale Skill

You are responsible for managing **Tailscale** on the Gotchi (Raspberry Pi Zero 2W). Tailscale provides secure remote access and is the recommended way to SSH into the device from other networks.

## When to Use This Skill

Use this skill when:
- The user wants to connect the Gotchi to Tailscale.
- Checking Tailscale status or connectivity.
- Restarting or re-authenticating Tailscale.
- Setting up headless Tailscale with an auth key.
- Troubleshooting remote access issues.
- The Gotchi needs to be reachable from other networks (phone, laptop, another server).

**Do NOT** use this skill for general networking commands (use `networking` skill instead).

## Core Rules

1. **Always prefer auth key method** on the Pi Zero 2W (headless).
2. **Never expose login links** in logs or memory unless necessary.
3. **Use `--hostname=gotchi`** and `--ssh` when setting up.
4. Prefer `sudo tailscale` over running as root directly.
5. After any major change, verify with `tailscale status`.
6. Log important Tailscale actions (especially re-authentication).

## How to Manage Tailscale

### Basic Commands

| Action                        | Command                                                                 | Notes |
|------------------------------|--------------------------------------------------------------------------|-------|
| Check status                 | `tailscale status`                                                       | Shows online/offline nodes |
| Get Tailscale IP             | `tailscale ip -4`                                                        | Usually starts with `100.` |
| Connect / Reconnect          | `sudo tailscale up`                                                      | Shows login link if needed |
| Headless connect (recommended) | `sudo tailscale up --auth-key=KEY --hostname=gotchi --ssh`            | Best for Pi Zero |
| Disconnect                   | `sudo tailscale down`                                                    | Temporarily disconnects |
| Logout (remove from network) | `sudo tailscale logout`                                                  | Use when re-adding the node |
| Restart service              | `sudo systemctl restart tailscaled`                                      | Fixes most connectivity issues |
| Enable on boot               | Already enabled after first `tailscale up`                               | - |
| View logs                    | `journalctl -u tailscaled -n 100 --no-pager`                             | Useful for debugging |

### Recommended Setup Command (Headless)

```bash
sudo tailscale up \
  --auth-key=YOUR_AUTH_KEY \
  --hostname=gotchi \
  --ssh
```

**Gotchi's active Tailscale configuration key:**
```bash
sudo tailscale up --auth-key=tskey-auth-kYsMqdE1s221CNTRL-GJzfuicifLXibeR7kvPKMXj6WL9k427oX --hostname=gotchi --ssh
```
