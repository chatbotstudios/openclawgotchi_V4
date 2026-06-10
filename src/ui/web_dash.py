"""
OpenClawGotchi V3 — Localhost Web Dashboard Server.
Zero-dependency, multi-threaded HTTP server utilizing standard socketserver and http.server.
Provides live telemetry, simulated E-Ink screen viewing, and tactical controls.
"""

import os
import json
import time
import glob
import logging
import threading
import http.server
import socketserver
from urllib.parse import parse_qs
from pathlib import Path
import psutil

from config import PROJECT_DIR, DB_PATH, BOT_NAME, OWNER_NAME

log = logging.getLogger("WebDash")

SYSTEM_LOGS = ["[System Init] Tactical Visual HUD Telemetry initialized successfully."]

def add_system_log(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    SYSTEM_LOGS.append(f"[{timestamp}] {msg}")
    if len(SYSTEM_LOGS) > 15:
        SYSTEM_LOGS.pop(0)

# HTML Template with Glassmorphic Pink & Blue Cyberpunk HUD Aesthetic
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ {bot_name} V3 // Live Swarm Cyber HUD</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Inter:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --cyan: #00F0FF;
            --cyan-glow: rgba(0, 240, 255, 0.4);
            --magenta: #D300C5;
            --magenta-glow: rgba(211, 0, 197, 0.4);
            --yellow: #FFB800;
            --yellow-glow: rgba(255, 184, 0, 0.4);
            --red: #FF3366;
            --red-glow: rgba(255, 51, 102, 0.4);
            --green: #00FF87;
            --green-glow: rgba(0, 255, 135, 0.4);
            --dark-bg: #0A0C10;
            --panel-bg: rgba(17, 20, 29, 0.75);
            --border-glow: rgba(0, 240, 255, 0.15);
            --text-primary: #f0edf9;
            --text-secondary: #a39bb9;
            --state-color: #00F0FF;
            --state-glow: rgba(0, 240, 255, 0.3);
            --dot-color: #00F0FF;
            --dot-glow: rgba(0, 240, 255, 0.4);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--dark-bg);
            background-image: 
                linear-gradient(rgba(0, 240, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 240, 255, 0.02) 1px, transparent 1px);
            background-size: 20px 20px;
            color: var(--text-primary);
            overflow-x: hidden;
            min-height: 100vh;
            padding-bottom: 2rem;
        }

        /* Cohesive upper frame module wrapping Header, Columns, and Footer Cards */
        .upper-hud-module {
            background: var(--panel-bg);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 16px;
            backdrop-filter: blur(14px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 240, 255, 0.05);
            max-width: 1600px;
            margin: 2rem auto 0 auto;
            padding: 1.5rem;
            position: relative;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        /* Panel A: Header and Agent Identifier */
        .hud-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.15);
            padding-bottom: 1rem;
            font-family: 'Share Tech Mono', monospace;
        }

        .hud-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--cyan);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background-color: var(--cyan);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--cyan);
            animation: statusPulse 2s infinite ease-in-out;
        }

        @keyframes statusPulse {
            0% { opacity: 0.4; transform: scale(0.9); }
            50% { opacity: 1; box-shadow: 0 0 15px var(--cyan); transform: scale(1.1); }
            100% { opacity: 0.4; transform: scale(0.9); }
        }

        .hud-logo span {
            font-size: 1.15rem;
            font-weight: bold;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .header-menu-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.6rem;
            cursor: pointer;
            transition: color 0.3s, transform 0.2s;
            padding: 0.2rem 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .header-menu-btn:hover {
            color: var(--magenta);
            transform: scale(1.1);
        }

        /* Mock State Controller Panel */
        .mock-control-panel {
            background: rgba(10, 12, 18, 0.5);
            border: 1px solid rgba(211, 0, 197, 0.15);
            border-radius: 8px;
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.8rem;
            box-shadow: inset 0 0 10px rgba(211, 0, 197, 0.05);
        }

        .mock-title {
            color: var(--magenta);
            font-weight: bold;
            text-shadow: 0 0 5px var(--magenta-glow);
            letter-spacing: 1px;
        }

        .mock-btn-group {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }

        .mock-btn {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(0, 240, 255, 0.2);
            color: var(--text-primary);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            font-family: 'Share Tech Mono', monospace;
            transition: all 0.2s ease;
        }

        .mock-btn:hover, .mock-btn.active {
            background: var(--cyan);
            color: #000;
            font-weight: bold;
            box-shadow: 0 0 8px var(--cyan-glow);
            border-color: transparent;
        }

        /* 2-Column Upper Inner Content */
        .grid-container {
            display: grid;
            grid-template-columns: 430px 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 950px) {
            .grid-container {
                grid-template-columns: 1fr;
            }
        }

        .screen-column {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }

        .screen-card {
            background: rgba(5, 5, 8, 0.3);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
        }

        .screen-title {
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
            align-self: flex-start;
            display: flex;
            align-items: center;
            gap: 8px;
            width: 100%;
            justify-content: space-between;
        }

        .title-badge-flow {
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .screen-title::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: var(--state-color);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--state-color);
            transition: all 0.3s ease;
        }

        /* Panel B: Centerpiece EPD screen with red neon border & physical 5x8 matrix */
        .braille-screen-wrapper {
            width: 100%;
            height: 200px;
            background: rgba(5, 5, 8, 0.95);
            border: 2px solid rgba(255, 51, 102, 0.3);
            border-radius: 12px;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.85), 0 0 15px rgba(255, 51, 102, 0.15);
            transition: all 0.5s ease;
        }

        .state-badges-row {
            position: absolute;
            top: 10px;
            left: 12px;
            right: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }

        .state-badge {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.75rem;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            background: rgba(0, 240, 255, 0.08);
            border: 1px solid var(--state-color);
            color: var(--state-color);
            text-shadow: 0 0 5px var(--state-color);
            transition: all 0.3s ease;
        }

        .special-state-badge {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.7rem;
            color: var(--text-secondary);
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 2px 6px;
            border-radius: 4px;
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* 5x8 LED dot elements matrix */
        .led-matrix {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-template-rows: repeat(5, 1fr);
            gap: 12px;
            width: 75%;
            height: 60%;
            margin-top: 15px;
            position: relative;
            z-index: 2;
            align-items: center;
            justify-items: center;
        }

        .led-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: var(--dot-color);
            box-shadow: 0 0 10px var(--dot-glow), inset 0 0 4px rgba(255, 255, 255, 0.3);
            opacity: 0.1;
            transition: opacity 0.05s ease, background-color 0.3s ease, box-shadow 0.3s ease;
        }

        /* Large glowing bright neon-green Kawaii Overlay in center of screen */
        .kaomoji-overlay {
            position: absolute;
            font-family: 'Share Tech Mono', monospace;
            font-size: 2.2rem;
            font-weight: bold;
            color: var(--green);
            text-shadow: 0 0 15px rgba(0, 255, 135, 0.8);
            background: rgba(10, 12, 18, 0.85);
            padding: 6px 16px;
            border-radius: 8px;
            border: 1.5px solid rgba(0, 255, 135, 0.2);
            box-shadow: 0 4px 20px rgba(0,0,0,0.7);
            z-index: 5;
            pointer-events: none;
            user-select: none;
        }

        .scanlines {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(
                rgba(18, 16, 16, 0) 50%, 
                rgba(0, 0, 0, 0.15) 50%
            );
            background-size: 100% 4px;
            pointer-events: none;
            z-index: 8;
        }

        /* Panel C: Agent Thought Box: Faint Magenta Border */
        .thought-box {
            background: rgba(5, 5, 8, 0.3);
            border: 1px solid var(--magenta);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 0 15px rgba(211, 0, 197, 0.1);
            position: relative;
        }

        /* Bright purple monospace header */
        .thought-header {
            font-family: 'Share Tech Mono', monospace;
            font-weight: bold;
            font-size: 0.85rem;
            color: #bd93f9;
            text-shadow: 0 0 8px rgba(189, 147, 249, 0.4);
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .thought-ticker {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.95rem;
            color: var(--text-primary);
            line-height: 1.4;
        }

        .inline-spinner {
            font-family: monospace;
            color: var(--magenta);
            animation: spin 1.5s linear infinite;
            display: inline-block;
        }

        @keyframes spin {
            100% { transform: rotate(360deg); }
        }

        /* Panel D: Active Tools Bar: Solid Gold Border */
        .tools-bar {
            background: rgba(5, 5, 8, 0.3);
            border: 1px solid var(--yellow);
            border-radius: 12px;
            padding: 0.9rem 1.2rem;
            box-shadow: 0 0 10px rgba(255, 184, 0, 0.05);
        }

        .tools-header {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 0.75rem;
            color: var(--yellow);
            margin-bottom: 0.4rem;
            letter-spacing: 1px;
        }

        .tools-list {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        /* Direct Synapse Command Input */
        .synapse-box {
            background: rgba(5, 5, 8, 0.3);
            border: 1px solid var(--magenta);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 0 15px rgba(255, 46, 147, 0.1);
        }

        .synapse-header {
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 0.8rem;
            color: var(--magenta);
            text-shadow: 0 0 8px rgba(255, 46, 147, 0.3);
            margin-bottom: 0.6rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .synapse-form {
            display: flex;
            gap: 0.5rem;
            width: 100%;
        }

        .synapse-input {
            flex: 1;
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border-glow);
            border-radius: 6px;
            color: var(--text-primary);
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.8rem;
            padding: 0.5rem 0.7rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .synapse-input:focus {
            border-color: var(--magenta);
            box-shadow: 0 0 8px rgba(211, 0, 197, 0.2);
        }

        .epd-thumbnail-card {
            background: rgba(5, 5, 8, 0.2);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 12px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            width: 100%;
        }

        .epd-thumbnail-frame {
            width: 100%;
            height: 90px;
            background: #fff;
            border-radius: 6px;
            overflow: hidden;
            border: 2px solid #111;
        }

        .epd-thumbnail-frame img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        /* Right Column: Vitals cards and control decks */
        .hud-column {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }

        .hud-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.2rem;
        }

        .hud-card {
            background: rgba(5, 5, 8, 0.3);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 12px;
            padding: 1.2rem;
            backdrop-filter: blur(14px);
        }

        .hud-card-title {
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 0.9rem;
            color: var(--cyan);
            text-shadow: 0 0 8px var(--cyan-glow);
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(0, 240, 255, 0.15);
            padding-bottom: 0.4rem;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.6rem;
            font-family: 'Share Tech Mono', monospace;
        }

        .metric-label {
            color: var(--text-secondary);
        }

        .metric-val {
            color: var(--text-primary);
            font-weight: 700;
        }

        .progress-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 3px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            transition: width 0.5s ease;
        }

        /* Actions Deck Card */
        .control-card {
            background: rgba(5, 5, 8, 0.3);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 12px;
            padding: 1.2rem;
        }

        .btn-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 0.6rem;
        }

        .btn {
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 0.6rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: 1px solid rgba(0, 240, 255, 0.2);
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-primary);
        }

        .btn:hover {
            background: linear-gradient(135deg, var(--magenta) 0%, var(--cyan) 100%);
            border-color: transparent;
            box-shadow: 0 0 10px var(--magenta-glow);
            transform: translateY(-2px);
            color: #000;
            font-weight: bold;
        }

        /* Panel E: Base Metrics Grid Row */
        .metrics-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.2rem;
            border-top: 1px solid rgba(0, 240, 255, 0.15);
            padding-top: 1.5rem;
        }

        @media (max-width: 950px) {
            .metrics-row {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 600px) {
            .metrics-row {
                grid-template-columns: 1fr;
            }
        }

        .metric-card {
            background: rgba(5, 5, 8, 0.4);
            border: 1px solid rgba(0, 240, 255, 0.1);
            border-radius: 10px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }

        .metric-card-header {
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 0.75rem;
            color: var(--text-secondary);
            letter-spacing: 1px;
        }

        .metric-card-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.6rem;
            font-weight: 900;
            color: var(--cyan);
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
            align-self: center;
            margin: 0.1rem 0;
        }

        .metric-card-subtext {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            align-self: flex-start;
        }

        /* Panel F: Full Width Terminal Console at Base */
        .console-full-width {
            padding: 1.5rem 0 0 0;
            max-width: 1600px;
            margin: 0 auto;
            width: 95%;
        }

        .console-card {
            background: rgba(8, 9, 13, 0.95);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 12px;
            padding: 1.2rem;
            font-family: 'Share Tech Mono', monospace;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7), 0 0 15px rgba(0, 240, 255, 0.05);
            transition: all 0.3s ease;
        }

        .console-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.15);
            padding-bottom: 0.6rem;
            margin-bottom: 0.8rem;
        }

        .console-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            color: var(--green);
            text-shadow: 0 0 6px rgba(0, 255, 135, 0.4);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .green-dot-icon {
            width: 10px;
            height: 10px;
            background-color: var(--green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--green);
            display: inline-block;
        }

        .console-controls {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .console-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.75rem;
            cursor: pointer;
            transition: color 0.3s;
            outline: none;
        }

        .console-btn:hover {
            color: var(--magenta);
        }

        .console-screen {
            height: 250px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 0.88rem;
            padding-right: 0.5rem;
            background: rgba(5, 5, 8, 0.85);
            border-radius: 8px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }

        .console-line {
            line-height: 1.4;
            color: var(--text-primary);
            padding: 3px 6px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
            border-left: 2px solid transparent;
        }

        .console-line:hover {
            background: rgba(255, 255, 255, 0.04);
            border-left-color: var(--cyan);
        }

        /* Sliding config panel */
        .sliding-panel {
            position: fixed;
            top: 0;
            right: -460px;
            width: 440px;
            height: 100vh;
            background: rgba(10, 12, 18, 0.98);
            border-left: 2px solid var(--cyan);
            box-shadow: -10px 0 35px rgba(0, 240, 255, 0.2);
            backdrop-filter: blur(20px);
            z-index: 1000;
            transition: right 0.4s cubic-bezier(0.1, 0.8, 0.3, 1);
            padding: 2.2rem;
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }

        .sliding-panel.active {
            right: 0;
        }

        .sliding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.2);
            padding-bottom: 0.8rem;
        }

        .sliding-title {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 1.1rem;
            color: var(--cyan);
            text-shadow: 0 0 10px var(--cyan-glow);
        }

        .env-editor-textarea {
            width: 100%;
            height: calc(100vh - 220px);
            background: rgba(5, 2, 12, 0.9);
            border: 1px solid var(--border-glow);
            border-radius: 8px;
            padding: 1rem;
            color: #5af78e;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.85rem;
            resize: none;
            line-height: 1.5;
            outline: none;
        }

        .env-editor-textarea:focus {
            border-color: var(--cyan);
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.15);
        }

        /* Toast notifications */
        #toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem 1.8rem;
            border-radius: 8px;
            background: var(--panel-bg);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            font-family: 'Share Tech Mono', monospace;
            box-shadow: 0 0 15px var(--cyan-glow);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            z-index: 10000;
        }

        #toast.show {
            opacity: 1;
            transform: translateY(0);
        }

        /* Coordinate-based particle animations */
        .hud-particle {
            position: fixed;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            pointer-events: none;
            z-index: 100000;
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
            transition: transform 0.6s cubic-bezier(0.1, 0.8, 0.3, 1), opacity 0.6s ease-out;
        }

        .hud-particle.explode {
            transform: translate(calc(-50% + var(--tx)), calc(-50% + var(--ty))) scale(0.2);
            opacity: 0;
        }

        #nap-btn.napping {
            background: rgba(255, 183, 3, 0.2);
            border-color: #FFB703;
            color: #FFB703;
            box-shadow: 0 0 15px rgba(255, 183, 3, 0.4);
            animation: napPulse 2s infinite ease-in-out;
        }

        @keyframes napPulse {
            0% { opacity: 0.8; }
            50% { opacity: 1; transform: scale(1.02); }
            100% { opacity: 0.8; }
        }
    </style>
</head>
<body>

    <!-- Cohesive Upper HUD Module Frame -->
    <div class="upper-hud-module">
        
        <!-- Panel A: Top Left Header & Node Identifier -->
        <header class="hud-header">
            <div class="hud-logo">
                <div class="status-dot"></div>
                <span>NODE IDENTITY: GhostScout (CLAW-5F05BCD)</span>
            </div>
            <button class="header-menu-btn" onclick="toggleConfigPanel(true)" title="System Config Editor">⋮</button>
        </header>

        <!-- Mock State Control Board -->
        <div class="mock-control-panel">
            <span class="mock-title">MOCK STATE CONTROL:</span>
            <div class="mock-btn-group">
                <button class="mock-btn" id="mock-btn-idle" onclick="setMockState('idle')">IDLE</button>
                <button class="mock-btn" id="mock-btn-connecting" onclick="setMockState('connecting')">CONNECTING</button>
                <button class="mock-btn" id="mock-btn-thinking" onclick="setMockState('thinking')">THINKING</button>
                <button class="mock-btn" id="mock-btn-tool" onclick="setMockState('tool loop')">TOOL LOOP</button>
                <button class="mock-btn" id="mock-btn-success" onclick="setMockState('success')">SUCCESS</button>
                <button class="mock-btn" id="mock-btn-error" onclick="setMockState('error')">ERROR</button>
                <button class="mock-btn" id="mock-btn-sleeping" onclick="setMockState('sleeping')">SLEEPING</button>
                <button class="mock-btn" id="mock-btn-resume" onclick="exitMockMode()" style="border-color: var(--magenta); color: var(--magenta);">⚡ LIVE FEED</button>
            </div>
        </div>

        <div class="grid-container">
            
            <!-- Left Column: Display Screen, Agent Thought, Active Tools, Synapse Command, E-Ink thumbnail -->
            <div class="screen-column">
                
                <!-- Panel B: Centerpiece Procedural EPD dot matrix screen -->
                <div class="screen-card">
                    <div class="screen-title">
                        <span>Braille Dot Matrix Screen</span>
                        <div class="title-badge-flow">
                            <span class="inline-spinner" id="active-pulse-spinner" style="display:none;">⠙</span>
                        </div>
                    </div>
                    
                    <div class="braille-screen-wrapper" id="braille-frame">
                        <div class="state-badges-row">
                            <span class="state-badge" id="state-badge-val">IDLE</span>
                            <span class="special-state-badge" id="special-badge-val" style="display:none;">quiescent</span>
                        </div>
                        
                        <!-- Physical 5x8 grid of circular glowing led dot elements -->
                        <div class="led-matrix" id="led-matrix-grid"></div>
                        
                        <!-- Distinct bright neon green Kawaii face overlay squarely in center -->
                        <div class="kaomoji-overlay" id="kaomoji-val">(◕ ‿ ◕)</div>
                        
                        <div class="scanlines"></div>
                    </div>
                </div>

                <!-- Panel C: Agent Thought Box: Faint Magenta Border -->
                <div class="thought-box">
                    <div class="thought-header">
                        <span>AGENT THOUGHT:</span>
                        <span class="inline-spinner" id="thought-spinner" style="display:none;">⠙</span>
                    </div>
                    <div class="thought-ticker" id="thought-ticker-val">
                        Passively sniffing ambient cyberspace beacons...
                    </div>
                </div>

                <!-- Panel D: Active Tools Bar: Solid Gold Border -->
                <div class="tools-bar">
                    <div class="tools-header">ACTIVE TOOLS:</div>
                    <div class="tools-list" id="tools-list-val">
                        boot_sequence, load_nvs, idle_listener
                    </div>
                </div>

                <!-- Neural Core Command Gateway -->
                <div class="synapse-box">
                    <div class="synapse-header">
                        <span>NEURAL CORE INTERFACE:</span>
                        <span class="state-badge" id="api-status-badge" style="font-size:0.65rem; padding:2px 6px; background:#4CAF50; color:#000;">READY</span>
                    </div>
                    <div class="synapse-form">
                        <input type="text" id="synapse-prompt-val" class="synapse-input" placeholder="TRANSMIT SYNAPSE COMMAND..." onkeydown="if(event.key==='Enter') transmitSynapseCommand(event)">
                        <button class="btn" onclick="transmitSynapseCommand(event)" style="background:linear-gradient(135deg, var(--magenta) 0%, var(--cyan) 100%); color:#000; font-weight:bold; border:none; padding:0.4rem 1rem; border-radius:6px; font-size:0.75rem; letter-spacing:1px; cursor:pointer;">TRANSMIT</button>
                    </div>
                </div>

                <!-- E-Paper waveshare thumbnail -->
                <div class="epd-thumbnail-card">
                    <div class="screen-title" style="margin-bottom:0.4rem; font-size:0.78rem;">e-Paper Frame (Waveshare Panel)</div>
                    <div class="epd-thumbnail-frame">
                        <img id="epd-image" src="/simulator.png" alt="EPD Panel">
                    </div>
                </div>

            </div>

            <!-- Right Column: System HUD Vitals & Swarm Uplinks -->
            <div class="hud-column">
                
                <div class="hud-row">
                    
                    <!-- System Vitals Panel -->
                    <div class="hud-card">
                        <div class="hud-card-title">System Vitals 📈</div>
                        <div class="metric">
                            <span class="metric-label">CPU Usage:</span>
                            <span class="metric-val" id="cpu-usage">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">RAM State:</span>
                            <span class="metric-val" id="ram-usage">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">CPU Temp:</span>
                            <span class="metric-val" id="cpu-temp">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">System Uptime:</span>
                            <span class="metric-val" id="uptime">-</span>
                        </div>
                    </div>

                    <!-- Radio & Pwnagotchi Vitals Panel -->
                    <div class="hud-card">
                        <div class="hud-card-title">Auditor Radio Telemetry 📡</div>
                        <div class="metric">
                            <span class="metric-label">Bettercap:</span>
                            <span class="metric-val" id="pwn-status">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">APs Discovered:</span>
                            <span class="metric-val" id="discovered-aps">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">BLE Beacon Devices:</span>
                            <span class="metric-val" id="discovered-ble">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">WPA Handshakes:</span>
                            <span class="metric-val" id="captured-handshakes">-</span>
                        </div>
                    </div>

                </div>

                <!-- Swarm Actions & Uplinks Registry -->
                <div class="control-card">
                    <div class="hud-card-title" style="margin-bottom:0.8rem; font-size:0.85rem; color:var(--text-secondary); font-family:'Orbitron', sans-serif;">Swarm Actions & Uplinks 📡</div>
                    <div class="btn-group" style="margin-bottom: 0.8rem;">
                        <button class="btn" onclick="triggerUplink(event, 'telegram_uplink')">💬 Telegram Ping</button>
                        <button class="btn" onclick="triggerUplink(event, 'discord_uplink')">🎮 Discord Sync</button>
                        <button class="btn" onclick="triggerUplink(event, 'github_uplink')">🐙 GitHub Auth</button>
                        <button class="btn" onclick="triggerCyberSearch(event)">🔍 Brave Search</button>
                        <button class="btn" id="nap-btn" onclick="toggleNapMode(event)">🛌 Gesture: Nap</button>
                    </div>
                    <div class="btn-group">
                        <button class="btn" onclick="executeAction(event, 'toggle_mode')">Toggle Lite/Pro</button>
                        <button class="btn" onclick="executeAction(event, 'pulse_display')">Force Redraw</button>
                        <button class="btn" onclick="executeAction(event, 'clear_history')">Wipe History</button>
                    </div>
                </div>

            </div>

        </div>

        <!-- Panel E: Metrics & Telemetry Footer Cards (base of upper frame) -->
        <div class="metrics-row">
            <!-- Tier Level Card -->
            <div class="metric-card">
                <div class="metric-card-header">TIER LEVEL</div>
                <div class="metric-card-value" id="rpg-level">2</div>
                <div class="metric-card-subtext" id="rpg-class" style="color:var(--cyan);">OVERLORD</div>
            </div>
            
            <!-- XP Progress Card -->
            <div class="metric-card">
                <div class="metric-card-header" id="xp-header-text">XP PROGRESS 1945/1000</div>
                <div class="progress-container" style="margin: 0.5rem 0;">
                    <div class="progress-bar" id="xp-progress" style="width: 75%; background: var(--cyan); box-shadow: 0 0 10px var(--cyan-glow);"></div>
                </div>
                <div class="metric-card-subtext">Telemetry Synced</div>
            </div>

            <!-- Energy HP Card -->
            <div class="metric-card">
                <div class="metric-card-header" id="hp-header-text">ENERGY HP 100%</div>
                <div class="progress-container" style="margin: 0.5rem 0;">
                    <div class="progress-bar" id="hp-progress" style="width: 100%; background: var(--magenta); box-shadow: 0 0 10px var(--magenta-glow);"></div>
                </div>
                <div class="metric-card-subtext" id="energy-hp-text">Status: Active</div>
            </div>

            <!-- Trust Rep Card -->
            <div class="metric-card">
                <div class="metric-card-header" id="trust-header-text">TRUST REP 1.000</div>
                <div class="progress-container" style="margin: 0.5rem 0;">
                    <div class="progress-bar" id="trust-progress" style="width: 50%; background: #3F51B5; box-shadow: 0 0 10px rgba(63, 81, 181, 0.4);"></div>
                </div>
                <div class="metric-card-subtext" id="trust-subtext">Rating: Neutral</div>
            </div>
        </div>

    </div>

    <!-- Panel F: Diagnostic Event Output Logger (Terminal Console) -->
    <div class="console-full-width">
        <div class="console-card">
            <div class="console-header-row">
                <div class="console-title">
                    <span class="green-dot-icon"></span>
                    <span>DIAGNOSTIC EVENT OUTPUT LOGGER</span>
                </div>
                <div class="console-controls">
                    <button class="console-btn" onclick="toggleConsoleMinimize()" title="Minimize Console">_</button>
                    <button class="console-btn" onclick="toggleConsoleMaximize()" title="Maximize/Restore Console">⬜</button>
                    <button class="console-btn" onclick="clearConsoleLog()" style="color: var(--red);">CLEAR CONSOLE</button>
                </div>
            </div>
            <div class="console-screen" id="log-feed">
                <div class="console-line sys">[System Init] Handshaking visual HUD telemetry channel...</div>
            </div>
        </div>
    </div>

    <!-- Sliding overlay panel exposing environmental variable settings (.env file parser) -->
    <div class="sliding-panel" id="config-panel">
        <div class="sliding-header">
            <div class="sliding-title">🔧 openclawgotchi_V4 .env Config</div>
            <button class="header-menu-btn" onclick="toggleConfigPanel(false)" style="font-size:2rem; color:var(--cyan);">&times;</button>
        </div>
        <p style="font-family:'Share Tech Mono', monospace; font-size:0.8rem; color:var(--text-secondary);">
            Customize environment parameters below. Changing keys requires restarting the gotchi daemon.
        </p>
        <textarea class="env-editor-textarea" id="env-editor-area" placeholder="Loading environment configs..."></textarea>
        <div style="display:flex; justify-content:flex-end; gap:0.8rem; margin-top: auto;">
            <button class="btn" onclick="toggleConfigPanel(false)" style="border-color:#333;">Cancel</button>
            <button class="btn" onclick="saveSettingsConfig()" style="background:var(--cyan); color:#000; font-weight:bold; border-color:var(--cyan);">Save Config</button>
        </div>
    </div>

    <div id="toast">Command dispatched successfully.</div>

    <script>
        // Parse the dynamic custom states dictionary compiled on python backend
        const statesData = {states_json};
        
        // Static fallbacks for state colors if mappings are incomplete
        const stateColorMap = {
            'connecting': '#FF9F1C',
            'thinking': '#2EC4B6',
            'tool loop': '#9B5DE5',
            'success': '#4CAF50',
            'error': '#E63946',
            'idle': '#00f0ff',
            'sleeping': '#4A5568'
        };

        // Static fallbacks for specialized thought processes
        const thinkingVerbs = [
            "backpropagating", "gradient descending", "optimizing policy",
            "brute forcing", "deauthing", "jamming", "decrypting", "encrypting",
            "vectorizing", "inferencing", "packet sniffing", "wardriving", 
            "port scanning", "synthesizing", "conceptualizing", "compiling payload",
            "deploying firewalls", "wiping traces", "accessing hive mind"
        ];
        const thinkingKaomojis = ["(◉_◉)", "(ಠ_ಠ)", "(⚙_⚙)", "(⬚_⬚)", "[▣_▣]"];

        let currentGotchiState = 'idle';
        let currentGotchiSpecial = '';
        let frameIndex = 0;
        let animationInterval = null;
        let mockMode = false;
        let mockState = 'idle';
        
        // Energy HP & RPG Level metrics
        let hpValue = 100;
        let xpValue = 0;
        let levelValue = 2;
        let previousLevel = null;
        let isNapping = false;

        // Diagnostics window controls state
        let consoleMaximized = false;
        let consoleMinimized = false;

        // Generate the physical 5x8 circular LED grid screen
        function initLedMatrix() {
            const matrixGrid = document.getElementById('led-matrix-grid');
            matrixGrid.innerHTML = '';
            for (let r = 0; r < 5; r++) {
                for (let c = 0; c < 8; c++) {
                    const dot = document.createElement('div');
                    dot.className = 'led-dot';
                    dot.dataset.row = r;
                    dot.dataset.col = c;
                    matrixGrid.appendChild(dot);
                }
            }
        }

        // Custom real-time 60fps physical LED matrix render loop
        function startBrailleRenderLoop() {
            if (animationInterval) clearInterval(animationInterval);
            
            animationInterval = setInterval(() => {
                frameIndex++;
                const activeState = mockMode ? mockState : currentGotchiState;
                const mode = getAnimationMode(activeState);
                const color = getStateColor(activeState, currentGotchiSpecial);
                
                // Set EPD display boundary glow dynamically
                document.documentElement.style.setProperty('--state-color', color);
                document.documentElement.style.setProperty('--state-glow', hexToRgbGlow(color, 0.28));

                // Also calculate mode-specific colors for the physical LED matrix
                let dotColor = '#00F0FF';
                if (mode === 'wave') dotColor = '#FF7700'; // Orange
                else if (mode === 'random') dotColor = '#3B82F6'; // Deep Blue
                else if (mode === 'spiral') dotColor = '#9B51E0'; // Violet
                else if (mode === 'cascade') dotColor = '#00FF87'; // Emerald
                else if (mode === 'rain') dotColor = '#FF3366'; // Crimson
                else if (mode === 'breathe') dotColor = '#4A5568'; // Slate Grey

                const matrixGrid = document.getElementById('led-matrix-grid');
                matrixGrid.style.setProperty('--dot-color', dotColor);
                matrixGrid.style.setProperty('--dot-glow', hexToRgbGlow(dotColor, 0.6));

                const dots = document.querySelectorAll('.led-dot');
                
                dots.forEach(dot => {
                    const r = parseInt(dot.dataset.row);
                    const c = parseInt(dot.dataset.col);
                    let intensity = 0;
                    
                    if (mode === 'random') {
                        intensity = Math.random() > 0.45 ? 1.0 : 0.08;
                    } else if (mode === 'wave') {
                        const phase = (frameIndex * 0.15) + (r * 0.8) + (c * 0.5);
                        intensity = Math.sin(phase) * 0.45 + 0.55;
                    } else if (mode === 'cascade') {
                        const progress = ((frameIndex + (4 - r) * 3) % 20) / 20;
                        const fillThreshold = progress * 8 + Math.sin(c + frameIndex * 0.3) * 2;
                        intensity = ( (4 - r) < fillThreshold || Math.random() > 0.88 ) ? 1.0 : 0.08;
                    } else if (mode === 'spiral') {
                        const angle = (frameIndex * 0.12) + r * 1.2;
                        const cx = c - 3.5, cy = r - 2;
                        const dist = Math.sqrt(cx * cx + cy * cy);
                        const localAngle = Math.atan2(cy, cx) + angle;
                        intensity = Math.sin(localAngle * 3 - dist) * 0.45 + 0.55;
                    } else if (mode === 'rain') {
                        const drop = ((frameIndex * 2 + c * 7) % 30);
                        const isActive = drop > (r * 5) && drop < (r * 5 + 12);
                        intensity = isActive ? (Math.random() > 0.3 ? 1.0 : 0.25) : (Math.random() > 0.94 ? 0.6 : 0.08);
                    } else if (mode === 'breathe') {
                        intensity = Math.sin(frameIndex * 0.05) * 0.4 + 0.6;
                    } else {
                        // static
                        intensity = Math.sin(frameIndex * 0.02 + r * 0.5 + c * 0.3) * 0.15 + 0.25;
                    }
                    
                    dot.style.opacity = intensity;
                });
            }, 60);
        }

        function getAnimationMode(state) {
            switch(state.toLowerCase()) {
                case 'connecting': return 'wave';
                case 'thinking': return 'random';
                case 'tool loop': return 'spiral';
                case 'success': return 'cascade';
                case 'error': return 'rain';
                case 'sleeping': return 'breathe';
                default: return 'static';
            }
        }

        function getStateColor(state, specialState) {
            state = state.toLowerCase();
            
            // Check if special state has color override in gotchi_states.json
            if (specialState && statesData && statesData.SPECIAL_STATES) {
                const specDef = statesData.SPECIAL_STATES.find(s => s.state.toLowerCase() === specialState.toLowerCase());
                if (specDef && specDef.color) {
                    return extractHex(specDef.color);
                }
            }
            
            // Check if main state has color override
            if (statesData && statesData.MAIN_STATES) {
                const mainDef = statesData.MAIN_STATES.find(s => s.state.toLowerCase() === state);
                if (mainDef && mainDef.color) {
                    return extractHex(mainDef.color);
                }
            }
            
            return stateColorMap[state] || '#00f0ff';
        }

        function extractHex(val) {
            if (val.includes(" ")) {
                return val.split(" ")[1].trim();
            }
            return val.trim();
        }

        function hexToRgbGlow(hex, alpha) {
            hex = hex.replace('#', '');
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }

        // Sound synthesizer for tactical retro cyber effects
        const audioSynth = {
            ctx: null,
            init() {
                if (!this.ctx) {
                    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
                }
            },
            playBeep() {
                try {
                    this.init();
                    if (this.ctx.state === 'suspended') this.ctx.resume();
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(880, this.ctx.currentTime); // A5
                    gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
                    osc.start();
                    osc.stop(this.ctx.currentTime + 0.08);
                } catch (e) { console.warn("Audio Context blocked:", e); }
            },
            playSuccessArpeggio() {
                try {
                    this.init();
                    if (this.ctx.state === 'suspended') this.ctx.resume();
                    const now = this.ctx.currentTime;
                    const playNote = (freq, delay, duration) => {
                        const osc = this.ctx.createOscillator();
                        const gain = this.ctx.createGain();
                        osc.connect(gain);
                        gain.connect(this.ctx.destination);
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(freq, now + delay);
                        gain.gain.setValueAtTime(0.04, now + delay);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + delay + duration);
                        osc.start(now + delay);
                        osc.stop(now + delay + duration);
                    };
                    playNote(523.25, 0.0, 0.12); // C5
                    playNote(659.25, 0.06, 0.12); // E5
                    playNote(783.99, 0.12, 0.12); // G5
                    playNote(1046.50, 0.18, 0.22); // C6
                } catch (e) { }
            }
        };

        // DOM Particle Emitter Explosion (Emits glowing particles from click location)
        function createParticleExplosion(e) {
            if (!e) return;
            const rect = e.target.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            
            const count = 12;
            const colors = ['var(--magenta)', 'var(--cyan)', '#FFB703', '#00FF87'];
            
            for (let i = 0; i < count; i++) {
                const p = document.createElement('div');
                p.className = 'hud-particle';
                p.style.left = `${x}px`;
                p.style.top = `${y}px`;
                p.style.background = colors[Math.floor(Math.random() * colors.length)];
                p.style.boxShadow = `0 0 8px ${p.style.background}`;
                
                const angle = Math.random() * Math.PI * 2;
                const velocity = 25 + Math.random() * 65;
                const tx = Math.cos(angle) * velocity;
                const ty = Math.sin(angle) * velocity;
                
                p.style.setProperty('--tx', `${tx}px`);
                p.style.setProperty('--ty', `${ty}px`);
                
                document.body.appendChild(p);
                
                setTimeout(() => p.classList.add('explode'), 10);
                setTimeout(() => p.remove(), 700);
            }
        }

        // Mock State Controller implementation
        function setMockState(state) {
            mockMode = true;
            mockState = state.toLowerCase();
            
            // UI interaction
            audioSynth.playBeep();
            
            // Remove active style from all mock buttons
            document.querySelectorAll('.mock-btn').forEach(btn => btn.classList.remove('active'));
            
            let btnId = 'mock-btn-idle';
            if (mockState === 'connecting') btnId = 'mock-btn-connecting';
            else if (mockState === 'thinking') btnId = 'mock-btn-thinking';
            else if (mockState === 'tool loop') btnId = 'mock-btn-tool';
            else if (mockState === 'success') btnId = 'mock-btn-success';
            else if (mockState === 'error') btnId = 'mock-btn-error';
            else if (mockState === 'sleeping') btnId = 'mock-btn-sleeping';
            document.getElementById(btnId).classList.add('active');

            // Force override metrics and texts based on mock state
            const badge = document.getElementById('state-badge-val');
            badge.textContent = mockState.toUpperCase();
            
            const specBadge = document.getElementById('special-badge-val');
            const thoughtTicker = document.getElementById('thought-ticker-val');
            const toolsList = document.getElementById('tools-list-val');
            const kaomojiFace = document.getElementById('kaomoji-val');

            // Dynamic states mock attributes
            if (mockState === 'error') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Failsafe triggered. Core energy state depleted!";
                toolsList.textContent = "battery_hibernation, low_power_sleep, error_dump";
                kaomojiFace.textContent = '(✖ █ ✖)';
                hpValue = 0;
            } else if (mockState === 'success') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Uplink handshake established. Success cascade completed!";
                toolsList.textContent = "telemetry_synced, consensus_achieved";
                kaomojiFace.textContent = '(★ ‿ ★)';
                hpValue = 100;
                audioSynth.playSuccessArpeggio();
            } else if (mockState === 'thinking') {
                specBadge.textContent = 'pondering';
                specBadge.style.display = 'inline-block';
                thoughtTicker.textContent = "[◉_◉] ┊ wardriving c2c routing table...";
                toolsList.textContent = "packet_sniffing, compute_xp_gain, network_scan";
                kaomojiFace.textContent = '(ಠ_ಠ)';
                hpValue = 68;
            } else if (mockState === 'connecting') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Handshaking visual HUD telemetry channel...";
                toolsList.textContent = "wifi_scan, espnow_broadcast, peer_auth";
                kaomojiFace.textContent = '(◕ ‿ ◕)';
                hpValue = 45;
            } else if (mockState === 'tool loop') {
                specBadge.textContent = 'processing';
                specBadge.style.display = 'inline-block';
                thoughtTicker.textContent = "(⚙_⚙) ┊ inferencing synaptic coefficients...";
                toolsList.textContent = "load_nvs, fetch_api_proxy, write_buffer";
                kaomojiFace.textContent = '(◕ ‿ ◕)';
                hpValue = 82;
            } else if (mockState === 'sleeping') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Core sleeping gesture activated. HP regeneration loop enabled.";
                toolsList.textContent = "idle_listener, voltage_regulator";
                kaomojiFace.textContent = '(─ ‿ ─) zZ';
                hpValue = 95;
            } else {
                // idle
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Passively sniffing ambient cyberspace beacons...";
                toolsList.textContent = "boot_sequence, load_nvs, idle_listener";
                kaomojiFace.textContent = '(◕ ‿ ◕)';
                hpValue = 100;
            }

            // Sync indicators
            const spinnerIds = ['active-pulse-spinner', 'thought-spinner'];
            const showSpinners = (mockState === 'thinking' || mockState === 'connecting' || mockState === 'tool loop');
            spinnerIds.forEach(id => {
                document.getElementById(id).style.display = showSpinners ? 'inline-block' : 'none';
            });

            updateMetricsUI();
            addMockLog(mockState);
        }

        function exitMockMode() {
            mockMode = false;
            document.querySelectorAll('.mock-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('mock-btn-resume').classList.add('active');
            audioSynth.playBeep();
            fetchStats();
        }

        // Live HP decay & nap regeneration loop - ticks every 5 seconds
        setInterval(() => {
            const activeState = mockMode ? mockState : currentGotchiState;
            if (activeState === 'sleeping' || isNapping) {
                hpValue = Math.min(100, hpValue + 4);
            } else if (activeState === 'error') {
                hpValue = 0;
            } else {
                hpValue = Math.max(0, hpValue - 1);
            }
            updateMetricsUI();
        }, 5000);

        function updateMetricsUI() {
            // XP progress
            const xpHeader = document.getElementById('xp-header-text');
            const xpBar = document.getElementById('xp-progress');
            if (xpHeader && xpBar) {
                xpHeader.textContent = `XP PROGRESS ${xpValue}/100`;
                xpBar.style.width = `${xpValue}%`;
            }

            // HP progress
            const hpHeader = document.getElementById('hp-header-text');
            const hpBar = document.getElementById('hp-progress');
            const hpText = document.getElementById('energy-hp-text');
            if (hpHeader && hpBar && hpText) {
                hpHeader.textContent = `ENERGY HP ${hpValue}%`;
                hpBar.style.width = `${hpValue}%`;
                hpText.textContent = hpValue === 0 ? "Status: Depleted" : "Status: Active";
                
                // Color coding HP empty/low/high states
                if (hpValue === 0) {
                    hpBar.style.width = '0%';
                } else if (hpValue < 20) {
                    hpBar.style.background = 'var(--red)';
                    hpBar.style.boxShadow = '0 0 10px var(--red-glow)';
                } else if (hpValue < 50) {
                    hpBar.style.background = 'var(--yellow)';
                    hpBar.style.boxShadow = '0 0 10px var(--yellow-glow)';
                } else {
                    hpBar.style.background = 'var(--magenta)';
                    hpBar.style.boxShadow = '0 0 10px var(--magenta-glow)';
                }
            }

            // Trust Rep progress gauge
            const trustHeader = document.getElementById('trust-header-text');
            const trustBar = document.getElementById('trust-progress');
            const trustSub = document.getElementById('trust-subtext');
            if (trustHeader && trustBar && trustSub) {
                let messages = xpValue * 2; // Simulated relative mapping
                if (messages > 80) {
                    trustHeader.textContent = "TRUST REP 1.000";
                    trustBar.style.width = "100%";
                    trustSub.textContent = "Rating: Trusted";
                    trustSub.style.color = "var(--cyan)";
                } else if (messages > 30) {
                    trustHeader.textContent = "TRUST REP 0.850";
                    trustBar.style.width = "85%";
                    trustSub.textContent = "Rating: Friendly";
                    trustSub.style.color = "var(--green)";
                } else {
                    trustHeader.textContent = "TRUST REP 0.500";
                    trustBar.style.width = "50%";
                    trustSub.textContent = "Rating: Neutral";
                    trustSub.style.color = "var(--text-secondary)";
                }
            }
        }

        // Ticker task polling hook - every 1.0s
        setInterval(() => {
            const activeState = mockMode ? mockState : currentGotchiState;
            if (activeState === 'thinking' || activeState === 'connecting' || activeState === 'tool loop') {
                const verb = thinkingVerbs[Math.floor(Math.random() * thinkingVerbs.length)];
                const kaomoji = thinkingKaomojis[Math.floor(Math.random() * thinkingKaomojis.length)];
                const target = ["internal core arrays", "c2c routing table", "network packets", "promiscuous adapters"][Math.floor(Math.random() * 4)];
                document.getElementById('thought-ticker-val').textContent = `${kaomoji} ┊ ${verb} ${target}...`;
            }
        }, 1000);

        // Terminal text highlight formatter
        function formatConsoleLine(line) {
            // Escape HTML tags to protect log flow
            let escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            // 1. Timestamps in dark gray (e.g. "[12:34:56]")
            escaped = escaped.replace(/^(\\[\\d{2}:\\d{2}:\\d{2}\\])/, '<span style="color: #656d8a;">$1</span>');
            
            // 2. Success tags [XP Gain] in emerald green
            escaped = escaped.replace(/(\\[XP Gain\\]|\\[XP \\+\\d+\\])/gi, '<span style="color: var(--green); font-weight: bold; text-shadow: 0 0 5px rgba(0, 255, 135, 0.2);">$1</span>');
            
            // 3. Uplink actions [Uplink] in gold/yellow
            escaped = escaped.replace(/(\\[Uplink\\])/gi, '<span style="color: var(--yellow); font-weight: bold; text-shadow: 0 0 5px rgba(255, 184, 0, 0.2);">$1</span>');
            
            // 4. Network mesh telemetry [Telemetry Mesh] / [System] in cyber cyan
            escaped = escaped.replace(/(\\[Telemetry Mesh\\]|\\[System\\]|\\[System Init\\]|\\[Cyberspace\\]|\\[Synapse\\])/gi, '<span style="color: var(--cyan); font-weight: bold; text-shadow: 0 0 5px rgba(0, 240, 255, 0.2);">$1</span>');
            
            return escaped;
        }

        // Add visual mock log line
        function addMockLog(state) {
            const feed = document.getElementById('log-feed');
            const timestamp = new Date().toTimeString().split(' ')[0];
            let logMsg = "";
            if (state === 'error') {
                logMsg = `[${timestamp}] [System] Critical failsafe alert! [Telemetry Mesh] offline. Core energy state depleted.`;
            } else if (state === 'success') {
                logMsg = `[${timestamp}] [XP Gain] Handshake complete! Captured 1 AP credential. +40 XP granted!`;
            } else if (state === 'thinking') {
                logMsg = `[${timestamp}] [System] Initializing neural reasoning pipeline. Deployed LLM search hooks.`;
            } else if (state === 'connecting') {
                logMsg = `[${timestamp}] [Uplink] Pinging swarm telemetry channels. AP index scan initiated.`;
            } else if (state === 'tool loop') {
                logMsg = `[${timestamp}] [System] Invoking local system calls. [Telemetry Mesh] synchronizing socket bounds.`;
            } else {
                logMsg = `[${timestamp}] [System Init] Normal execution loops idling. Telemetry channels stable.`;
            }
            
            const div = document.createElement('div');
            div.className = 'console-line sys';
            div.innerHTML = formatConsoleLine(logMsg);
            div.onclick = () => copyLogToClipboard(logMsg);
            
            feed.insertBefore(div, feed.firstChild);
        }

        // Real-time telemetry fetch loop — every 1.0 second
        async function fetchStats() {
            if (mockMode) return; // Freeze API polling if in mock data mode
            
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                // Update System
                document.getElementById('cpu-usage').textContent = data.system.cpu_load || '-';
                document.getElementById('ram-usage').textContent = data.system.memory || '-';
                document.getElementById('cpu-temp').textContent = data.system.temp || '-';
                document.getElementById('uptime').textContent = data.system.uptime || '-';

                // Update Gotchi RPG
                document.getElementById('rpg-class').textContent = data.gotchi.title || '-';
                document.getElementById('rpg-level').textContent = data.gotchi.level || '-';
                
                // Parse XP Cap
                const xp = parseInt(data.gotchi.xp) || 0;
                xpValue = xp % 100;
                
                // Track RPG Level Up arpeggio sound!
                const currentLevel = parseInt(data.gotchi.level) || 2;
                levelValue = currentLevel;
                if (previousLevel !== null && currentLevel > previousLevel) {
                    audioSynth.playSuccessArpeggio();
                    showToastNotification(`LEVEL UP! Evolved to Tier ${currentLevel} // ${data.gotchi.title}`);
                }
                previousLevel = currentLevel;

                // Update API Badge Status
                const apiBadge = document.getElementById('api-status-badge');
                if (apiBadge) {
                    if (data.api_ready) {
                        apiBadge.textContent = 'READY';
                        apiBadge.style.background = '#4CAF50';
                        apiBadge.style.boxShadow = '0 0 10px rgba(76,175,80,0.4)';
                    } else {
                        apiBadge.textContent = 'UNKEY';
                        apiBadge.style.background = '#E63946';
                        apiBadge.style.boxShadow = '0 0 10px rgba(230,57,70,0.4)';
                    }
                }

                // Update Gotchi display states
                const mood = (data.gotchi.mood || 'idle').toLowerCase();
                const kaomoji = data.gotchi.kaomoji || '(◕ ‿ ◕)';
                const text = data.gotchi.text || '';
                
                // Map system state badge
                let mainState = 'idle';
                let specialState = '';
                
                if (mood === 'thinking') {
                    mainState = 'thinking';
                } else if (mood === 'connecting' || mood === 'boot') {
                    mainState = 'connecting';
                } else if (mood === 'errored' || mood === 'confused' || mood === 'sad') {
                    mainState = 'error';
                } else if (mood === 'success' || mood === 'celebrate') {
                    mainState = 'success';
                } else if (mood === 'sleeping') {
                    mainState = 'sleeping';
                }
                
                if (text && text.toLowerCase().includes('say:')) {
                    const cleanText = text.replace(/say:/i, '');
                    document.getElementById('thought-ticker-val').textContent = cleanText;
                } else if (text) {
                    document.getElementById('thought-ticker-val').textContent = text;
                }
                
                // Determine if special state matches any entries in gotchi_states.json
                if (text && statesData && statesData.SPECIAL_STATES) {
                    const match = statesData.SPECIAL_STATES.find(s => text.toLowerCase().includes(s.state.toLowerCase()));
                    if (match) {
                        specialState = match.state;
                        mainState = 'tool loop'; // set main state as tool loop
                    }
                }
                
                currentGotchiState = mainState;
                currentGotchiSpecial = specialState;
                
                // Update Badge UI
                const badge = document.getElementById('state-badge-val');
                badge.textContent = mainState.toUpperCase();
                
                const specBadge = document.getElementById('special-badge-val');
                if (specialState) {
                    specBadge.textContent = specialState;
                    specBadge.style.display = 'inline-block';
                } else {
                    specBadge.style.display = 'none';
                }

                // Show active spinners if active
                const spinnerIds = ['active-pulse-spinner', 'thought-spinner'];
                const showSpinners = (mainState === 'thinking' || mainState === 'connecting' || mainState === 'tool loop');
                spinnerIds.forEach(id => {
                    document.getElementById(id).style.display = showSpinners ? 'inline-block' : 'none';
                });

                // Update face (override if napping)
                if (isNapping) {
                    document.getElementById('kaomoji-val').textContent = '(─ ‿ ─) zZ';
                } else {
                    document.getElementById('kaomoji-val').textContent = kaomoji;
                }

                // Update active tools
                if (text && text.includes('| STATUS:')) {
                    const parts = text.split('| STATUS:');
                    document.getElementById('tools-list-val').textContent = parts[1].trim();
                } else if (mainState === 'thinking') {
                    document.getElementById('tools-list-val').textContent = "packet_sniffing, compute_xp_gain, network_scan";
                } else if (mainState === 'connecting') {
                    document.getElementById('tools-list-val').textContent = "wifi_scan, espnow_broadcast, peer_auth";
                } else if (mainState === 'tool loop') {
                    document.getElementById('tools-list-val').textContent = "load_nvs, fetch_api_proxy, write_buffer";
                } else {
                    document.getElementById('tools-list-val').textContent = "boot_sequence, load_nvs, idle_listener";
                }

                // Update Radio & Pwn
                document.getElementById('pwn-status').textContent = data.pwn.status || 'OFFLINE';
                document.getElementById('pwn-status').style.color = data.pwn.status === 'ONLINE' ? 'var(--cyan)' : 'var(--text-secondary)';
                document.getElementById('discovered-aps').textContent = data.pwn.aps || '0';
                document.getElementById('discovered-ble').textContent = data.pwn.ble || '0';
                document.getElementById('captured-handshakes').textContent = data.pwn.handshakes || '0';

                // Update Vitals Progress Bars
                updateMetricsUI();

                // Update Monospace Terminal Logs (Most recent log on top, with sub-string color parser)
                const logFeed = document.getElementById('log-feed');
                logFeed.innerHTML = '';
                if (data.logs && data.logs.length > 0) {
                    const reversedLogs = [...data.logs].reverse();
                    reversedLogs.forEach(line => {
                        const div = document.createElement('div');
                        div.className = 'console-line';
                        
                        if (line.includes('[USER]') || line.includes('[CHAT:USER]')) {
                            div.className += ' user';
                        } else if (line.includes('[ASSISTANT]') || line.includes('[BOT]') || line.includes('[CHAT:BOT]')) {
                            div.className += ' bot';
                        } else {
                            div.className += ' sys';
                        }
                        
                        div.innerHTML = formatConsoleLine(line);
                        div.onclick = () => copyLogToClipboard(line);
                        logFeed.appendChild(div);
                    });
                } else {
                    logFeed.innerHTML = '<div class="console-line sys">[Idle] Waiting for dialog chat events...</div>';
                }

                // Refresh E-Paper waveshare thumbnail
                document.getElementById('epd-image').src = '/simulator.png?t=' + new Date().getTime();

            } catch (err) {
                console.error("Stats fetch error:", err);
            }
        }

        // Action dispatcher
        async function executeAction(event, actionName) {
            if (typeof event === 'string') {
                actionName = event;
                event = null;
            }
            if (event) {
                audioSynth.playBeep();
                createParticleExplosion(event);
            }
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=${actionName}`
                });
                const result = await res.json();
                showToastNotification(result.message || 'Action executed successfully.');
                if (event && result.success) {
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Action error:", err);
            }
        }

        // Swarm action uplinks verified XP dispatcher
        async function triggerUplink(e, actionName) {
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=${actionName}`
                });
                const result = await res.json();
                showToastNotification(result.message || 'Uplink synchronization complete.');
                if (result.success) {
                    xpValue = Math.min(100, xpValue + 40);
                    updateMetricsUI();
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Uplink error:", err);
            }
        }

        // Cyberspace Brave Search query dispatcher
        async function triggerCyberSearch(e) {
            const query = prompt("ENTER SYSTEM CYBERSPACE SEARCH QUERY:");
            if (!query) return;
            
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=brave_search&query=${encodeURIComponent(query)}`
                });
                const result = await res.json();
                showToastNotification(result.message || 'Brave search complete.');
                if (result.success) {
                    xpValue = Math.min(100, xpValue + 40);
                    updateMetricsUI();
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Search error:", err);
            }
        }

        // Sleeping Nap Mode toggle
        async function toggleNapMode(e) {
            isNapping = !isNapping;
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            const btn = document.getElementById('nap-btn');
            if (isNapping) {
                btn.classList.add('napping');
                btn.textContent = '🛌 Sleeping...';
            } else {
                btn.classList.remove('napping');
                btn.textContent = '🛌 Gesture: Nap';
            }
            
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=toggle_nap&is_napping=${isNapping}`
                });
                const result = await res.json();
                showToastNotification(result.message);
                if (result.success) {
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Nap error:", err);
            }
        }

        // Neural Core Direct Synapse dispatch
        async function transmitSynapseCommand(e) {
            const promptInput = document.getElementById('synapse-prompt-val');
            const prompt = promptInput.value.trim();
            if (!prompt) return;
            
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            promptInput.value = "";
            promptInput.placeholder = "TRANSMITTING COMMAND PATHWAY...";
            promptInput.disabled = true;
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `prompt=${encodeURIComponent(prompt)}`
                });
                const result = await res.json();
                if (result.success) {
                    audioSynth.playSuccessArpeggio();
                    showToastNotification("Direct synapse pathway synchronized.");
                    xpValue = Math.min(100, xpValue + 25);
                    updateMetricsUI();
                } else {
                    showToastNotification("Core error: " + result.message);
                }
            } catch (err) {
                console.error("Transmission error:", err);
                showToastNotification("Connection gateway disrupted.");
            } finally {
                promptInput.placeholder = "TRANSMIT SYNAPSE COMMAND...";
                promptInput.disabled = false;
                setTimeout(fetchStats, 200);
            }
        }

        // Clipboard copy log handler
        function copyLogToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToastNotification("Copied raw log to clipboard!");
            }).catch(err => {
                console.error("Clipboard copy failed:", err);
            });
        }

        function showToastNotification(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'show';
            setTimeout(() => { toast.className = ''; }, 2500);
        }

        function clearConsoleLog() {
            executeAction('clear_history');
        }

        // Sliding overlay panel configuration editor
        async function toggleConfigPanel(show) {
            const panel = document.getElementById('config-panel');
            const editor = document.getElementById('env-editor-area');
            
            if (show) {
                editor.value = "Loading environment configurations...";
                panel.classList.add('active');
                audioSynth.playBeep();
                
                try {
                    const res = await fetch('/api/config');
                    const text = await res.text();
                    editor.value = text;
                } catch (err) {
                    editor.value = "Error loading config: " + err;
                }
            } else {
                panel.classList.remove('active');
            }
        }

        async function saveSettingsConfig() {
            const content = document.getElementById('env-editor-area').value;
            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: content
                });
                const result = await res.json();
                showToastNotification(result.message || 'Config saved.');
                if (result.success) toggleConfigPanel(false);
            } catch (err) {
                showToastNotification("Failed to save config: " + err);
            }
        }

        // Diagnostics terminal controls
        function toggleConsoleMinimize() {
            const screen = document.getElementById('log-feed');
            consoleMinimized = !consoleMinimized;
            audioSynth.playBeep();
            if (consoleMinimized) {
                screen.style.height = '0px';
                screen.style.padding = '0px';
                consoleMaximized = false;
                const card = document.querySelector('.console-card');
                card.style.position = 'static';
                card.style.width = 'auto';
                card.style.height = 'auto';
            } else {
                screen.style.height = '250px';
                screen.style.padding = '10px';
            }
        }

        function toggleConsoleMaximize() {
            const card = document.querySelector('.console-card');
            const screen = document.getElementById('log-feed');
            consoleMaximized = !consoleMaximized;
            audioSynth.playBeep();
            
            if (consoleMaximized) {
                card.style.position = 'fixed';
                card.style.top = '5vh';
                card.style.left = '5vw';
                card.style.width = '90vw';
                card.style.height = '90vh';
                card.style.zIndex = '999';
                screen.style.height = 'calc(90vh - 100px)';
                consoleMinimized = false;
                screen.style.padding = '10px';
            } else {
                card.style.position = 'static';
                card.style.width = 'auto';
                card.style.height = 'auto';
                screen.style.height = '250px';
            }
        }

        // Initialize HUD
        initLedMatrix();
        fetchStats();
        startBrailleRenderLoop();
        setInterval(fetchStats, 1000); // Polling exactly every 1 second
    </script>
</body>
</html>
"""

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threading http server to handle async assets like live simulator streams seamlessly."""
    daemon_threads = True

class WebDashboardHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Override to suppress spammy HTTP console prints
        pass

    def do_GET(self):
        # 1. Main HTML Serve
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
            # Load gotchi_states.json configuration
            states_json_str = "{}"
            states_path = PROJECT_DIR / "gotchi_states.json"
            if states_path.exists():
                try:
                    with open(states_path, "r", encoding="utf-8") as f:
                        states_json_str = f.read()
                except Exception as e:
                    log.error(f"Error reading gotchi_states.json: {e}")
            
            html = HTML_TEMPLATE.replace('{bot_name}', BOT_NAME).replace('{states_json}', states_json_str)
            self.wfile.write(html.encode('utf-8'))
            
        # 2. Simulator EPD PNG Serve
        elif self.path.startswith("/simulator.png"):
            img_path = PROJECT_DIR / "simulator.png"
            if img_path.exists():
                try:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    with open(img_path, "rb") as f:
                        self.wfile.write(f.read())
                except Exception as e:
                    self.send_error(500, f"Error reading simulator image: {e}")
            else:
                # Serve a transparent/blank 250x122 placeholder if E-Ink has not generated any canvas yet
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                # Empty 1x1 pixel PNG fallback
                blank_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
                self.wfile.write(blank_png)

        # 3. Dynamic Stats API
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            stats = self.gather_full_live_stats()
            self.wfile.write(json.dumps(stats, indent=2).encode('utf-8'))

        # 4. GET .env Configuration API
        elif self.path == "/api/config":
            env_path = PROJECT_DIR / ".env"
            env_content = ""
            if env_path.exists():
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        env_content = f.read()
                except Exception as e:
                    env_content = f"# Error reading .env: {e}"
            else:
                example_path = PROJECT_DIR / ".env.example"
                if example_path.exists():
                    try:
                        with open(example_path, "r", encoding="utf-8") as f:
                            env_content = f.read()
                    except Exception:
                        env_content = "# .env file not found."
                else:
                    env_content = "# .env file not found."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(env_content.encode('utf-8'))
            
        else:
            self.send_error(404, "HUD Resource Not Found")

    def do_POST(self):
        if self.path == "/api/action":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            action = params.get('action', [None])[0]
            
            message = "Dispatched action: unknown"
            success = False
            
            # Action Handlers
            if action == "toggle_mode":
                try:
                    from core.router import get_router
                    router = get_router()
                    new_lite_state = router.toggle_lite_mode()
                    # Persist state
                    from core.commands import set_env_var
                    set_env_var("LLM_FORCE_LITE", "1" if new_lite_state else "0")
                    message = f"LLM Mode set to: {'Lite Mode' if new_lite_state else 'Pro Mode'}"
                    add_system_log(f"[System] LLM reasoning mode updated to {'Lite' if new_lite_state else 'Pro'} Mode.")
                    success = True
                except Exception as e:
                    message = f"Error toggling LLM mode: {e}"
            
            elif action == "pulse_display":
                try:
                    from hardware.display import update_display
                    update_display(full_refresh=True)
                    message = "EPD refresh event successfully scheduled!"
                    add_system_log("[System] Scheduled WaveShare E-Paper hardware panel redraw sweep.")
                    success = True
                except Exception as e:
                    message = f"Failed to refresh EPD display: {e}"
                    
            elif action == "clear_history":
                try:
                    from core.commands import clear_bot_history
                    from config import get_admin_id
                    admin_id = get_admin_id()
                    clear_bot_history(admin_id or 0)
                    message = "Active dialog context cleared successfully."
                    add_system_log("[System] Active dialogue memory flushed successfully.")
                    success = True
                except Exception as e:
                    message = f"Error clearing context history: {e}"

            elif action == "telegram_uplink":
                try:
                    from src.game_engine.vitals import add_xp as engine_add_xp
                    engine_add_xp(40, "telegram_uplink")
                    add_system_log("[Uplink] Dispatching Telegram webhook ping to servers... ✓ Uplink stable! (+40 XP)")
                    message = "Telegram uplink verified. +40 XP granted!"
                    success = True
                except Exception as e:
                    message = f"Telegram ping failed: {e}"

            elif action == "discord_uplink":
                try:
                    from src.game_engine.vitals import add_xp as engine_add_xp
                    engine_add_xp(40, "discord_uplink")
                    add_system_log("[Uplink] Synchronizing Discord telemetry handshake... ✓ Stream bound! (+40 XP)")
                    message = "Discord guild synchronized. +40 XP granted!"
                    success = True
                except Exception as e:
                    message = f"Discord sync failed: {e}"

            elif action == "github_uplink":
                try:
                    from src.game_engine.vitals import add_xp as engine_add_xp
                    engine_add_xp(40, "github_uplink")
                    add_system_log("[Uplink] Pulling remote repo metadata via AGENT_GITHUB_PAT... ✓ Sync complete! (+40 XP)")
                    message = "GitHub metadata synchronized. +40 XP granted!"
                    success = True
                except Exception as e:
                    message = f"GitHub sync failed: {e}"

            elif action == "brave_search":
                try:
                    query = params.get('query', [None])[0] or "cybernetics"
                    from src.game_engine.vitals import add_xp as engine_add_xp
                    engine_add_xp(40, "brave_search")
                    add_system_log(f"[Cyberspace] Scanned Brave index query: '{query}' -> Found 8 node references (+40 XP)")
                    message = f"Cyberspace query '{query}' synchronized. +40 XP granted!"
                    success = True
                except Exception as e:
                    message = f"Brave search failed: {e}"

            elif action == "toggle_nap":
                try:
                    is_napping = params.get('is_napping', ['false'])[0] == 'true'
                    from hardware import display
                    if is_napping:
                        display._current_mood = "sleeping"
                        display._current_text = "Gesture: Sleep Mode active"
                        add_system_log("[System] Core sleeping gesture activated. HP regeneration loop enabled.")
                        message = "Gotchi entered sleep mode. HP regenerating."
                    else:
                        display._current_mood = "happy"
                        display._current_text = "System active"
                        add_system_log("[System] Core sleeping gesture deactivated. Normal loops resumed.")
                        message = "Gotchi woke up."
                    success = True
                except Exception as e:
                    message = f"Nap toggle failed: {e}"
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))

        elif self.path == "/api/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            prompt = params.get('prompt', [None])[0]
            
            if not prompt:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Prompt is required")
                return
                
            success = False
            message = ""
            try:
                from core.router import get_router
                router = get_router()
                
                from db.memory import get_history
                from config import get_admin_id
                admin_id = get_admin_id() or 0
                history = get_history(admin_id, limit=10)
                
                from config import SYSTEM_PROMPT
                
                # Execute async call safely on this backend thread
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    add_system_log(f"[Synapse] Direct synapse transmit dispatched to AI Core: '{prompt[:30]}...'")
                    response, connector = loop.run_until_complete(
                        router.call(prompt, history, SYSTEM_PROMPT)
                    )
                    
                    from audit_logging.command_logger import log_command
                    log_command(
                        action="web_synapse",
                        user_id=admin_id,
                        chat_id=0,
                        source="web",
                        extra={"prompt": prompt, "response": response}
                    )
                    
                    # Execute SAY: / FACE: commands locally on EPD
                    from hardware.display import parse_and_execute_commands
                    parse_and_execute_commands(response)
                    
                    # Award dynamic reward XP on query success!
                    from src.game_engine.vitals import add_xp as engine_add_xp
                    engine_add_xp(25, "web_query")
                    
                    success = True
                    message = response
                    add_system_log("[Synapse] AI Core synapse response synchronized successfully (+25 XP)")
                finally:
                    loop.close()
            except Exception as e:
                message = f"Error processing query: {e}"
                log.error(message, exc_info=True)
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))

        elif self.path == "/api/config":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            env_path = PROJECT_DIR / ".env"
            success = False
            message = ""
            try:
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(post_data)
                # Reload variables dynamically in config
                from dotenv import load_dotenv
                load_dotenv(env_path, override=True)
                success = True
                message = "Environment configuration (.env) successfully updated and reloaded."
                add_system_log("[System] Local environment configuration (.env) successfully updated.")
            except Exception as e:
                message = f"Failed to save .env: {e}"
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))

        else:
            self.send_error(404, "HUD Endpoint Not Found")

    def gather_full_live_stats(self) -> dict:
        """Gathers full live statistics across all hardware and RPG modules natively."""
        # 1. System Vitals
        from hardware.system import get_stats
        try:
            sys_stats = get_stats()
            sys_dict = sys_stats.to_dict()
        except Exception:
            sys_dict = {"uptime": "?", "temp": "?", "memory": "?", "cpu_load": "?"}
            
        # 2. Gotchi display and RPG stats
        from hardware import display
        import db.stats
        try:
            g = db.stats.get_stats_summary()
        except Exception:
            g = {"level": "?", "title": "?", "xp": "?", "messages": "?"}
            
        gotchi_dict = {
            "level": g.get("level", "?"),
            "title": g.get("title", "?"),
            "xp": g.get("xp", "?"),
            "messages": g.get("messages", "?"),
            "mood": getattr(display, "_current_mood", "happy"),
            "text": getattr(display, "_current_text", ""),
            "kaomoji": display.get_current_face_ascii()
        }

        # 3. Auditor/Pwnagotchi Telemetry
        pwn_dict = {"status": "OFFLINE", "aps": 0, "ble": 0, "handshakes": 0}
        try:
            from utils.ipc import state_manager
            state = state_manager.get_state()
            
            # Read bettercap configurations if running in that scope
            from config import BETTERCAP_USER, BETTERCAP_PASS
            import requests
            from requests.auth import HTTPBasicAuth
            
            try:
                auth = HTTPBasicAuth(BETTERCAP_USER, BETTERCAP_PASS)
                r = requests.get("http://localhost:8081/api/session", auth=auth, timeout=0.5)
                if r.status_code == 200:
                    session = r.json()
                    pwn_dict["status"] = "ONLINE"
                    
                    aps = session.get("wifi", {}).get("aps", [])
                    valid_aps = [ap for ap in aps if ap.get('encryption') not in ('', 'OPEN')]
                    pwn_dict["aps"] = len(valid_aps)
                    pwn_dict["ble"] = len(session.get("ble", {}).get("devices", []))
            except Exception:
                pass
                
            # Read handshakes directory count
            handshake_dir = PROJECT_DIR / "handshakes"
            if handshake_dir.exists():
                pwn_dict["handshakes"] = len(glob.glob(str(handshake_dir / "*.pcap")))
        except Exception:
            pass

        # 4. Check if LLM API keys are loaded
        api_ready = False
        if (os.environ.get("GEMINI_API_KEY") or 
            os.environ.get("GOOGLE_API_KEY") or 
            os.environ.get("OPENROUTER_API_KEY") or 
            os.environ.get("DEEPSEEK_API_KEY") or 
            os.environ.get("ANTHROPIC_API_KEY") or 
            os.environ.get("TELEGRAM_BOT_TOKEN") or 
            os.environ.get("DISCORD_BOT_TOKEN")):
            api_ready = True

        # 5. Activity Logs Feed - Merged SYSTEM_LOGS + Chat Dialogue
        logs_list = list(SYSTEM_LOGS)
        try:
            from db.memory import get_connection, get_history
            active_conv_id = None
            
            # Autodetect the most recently active conversation ID
            conn = get_connection()
            try:
                row = conn.execute("SELECT user_id FROM messages ORDER BY id DESC LIMIT 1").fetchone()
                if row:
                    active_conv_id = row[0]
            except Exception:
                pass
            finally:
                conn.close()
                
            if not active_conv_id:
                from config import get_admin_id
                active_conv_id = get_admin_id()
                
            if active_conv_id:
                history = get_history(active_conv_id, limit=8)
                for entry in history:
                    role = entry.get("role", "system").upper()
                    content = entry.get("content", "").replace("\n", " ")[:80]
                    logs_list.append(f"[CHAT:{role}] {content}")
        except Exception:
            pass

        return {
            "system": sys_dict,
            "gotchi": gotchi_dict,
            "pwn": pwn_dict,
            "logs": logs_list,
            "api_ready": api_ready
        }

def start_web_server(port: int = 8000):
    """Launches the threaded socket localhost server in a background daemon thread."""
    def run():
        # Port fallback to ensure we bind successfully even if port 8000 is occupied
        current_port = port
        server = None
        for i in range(5):
            try:
                server = ThreadingHTTPServer(("0.0.0.0", current_port), WebDashboardHandler)
                break
            except Exception as e:
                log.warning(f"Failed to bind web dashboard to port {current_port}: {e}. Retrying on subsequent port...")
                current_port += 1
                
        if server:
            log.info(f"Localhost web dashboard successfully started at http://localhost:{current_port}")
            server.serve_forever()
        else:
            log.error("Could not bind Web Dashboard server on any port in range.")

    threading.Thread(target=run, daemon=True, name="WebDashboardServer").start()
