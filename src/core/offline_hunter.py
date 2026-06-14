import time
import os
import json
import subprocess
import logging
from pathlib import Path

# Fix paths
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
STATE_PATH = PROJECT_DIR / "gotchi_states.json"
ENV_PATH = PROJECT_DIR / ".env"

log = logging.getLogger("OfflineHunter")

CHUNK_SLEEP = 15  # Sleep in 15-second chunks for responsiveness

class OfflineHunter:
    """
    Handles the orchestration of a timed offline hunt session:
    - Persists session state to gotchi_states.json
    - Inverts the E-Ink screen to Dark Mode (sets DARK_MODE=1 in .env)
    - Puts wlan0 into Monitor Mode
    - Runs Bettercap auditing autonomously
    - Re-establishes connectivity and restores original settings
    """
    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or PROJECT_DIR
        self.state_file = self.project_dir / "gotchi_states.json"
        self.env_file = self.project_dir / ".env"

    def _read_state(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception:
                pass
        return {}

    def _write_state(self, state: dict):
        self.state_file.write_text(json.dumps(state, indent=2))

    def _get_env_var(self, key: str, default: str = "") -> str:
        if not self.env_file.exists():
            return default
        lines = self.env_file.read_text().splitlines()
        for line in lines:
            if line.startswith(f"{key}="):
                return line.partition("=")[2].strip()
        return default

    def _set_env_var(self, key: str, value: str):
        lines = []
        if self.env_file.exists():
            lines = self.env_file.read_text().splitlines()
            
        new_line = f"{key}={value}"
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = new_line
                found = True
                break
        if not found:
            lines.append(new_line)
            
        self.env_file.write_text("\n".join(lines) + "\n")

    def _trigger_ui_refresh(self, mood: str, status: str):
        """Forces the E-Ink display to update with a face and message."""
        try:
            # We call the CLI command for ui show-face safely
            cmd = ["python3", "-m", "core.cli.entry", "show_face", "--mood", mood, "--text", status]
            subprocess.run(cmd, cwd=str(self.project_dir), capture_output=True)
        except Exception as e:
            log.warning(f"UI update failed: {e}")

    def run_hunt(self, duration_seconds: int, mission_id: str = "handshake_hunter_v1"):
        """
        Launches the offline hunt. Designed to run as a non-blocking background task.
        Sleeps in 15-second chunks so the loop can be responsive to abort signals.
        """
        from game_engine.state import state_manager
        from game_engine.vitals import add_xp
        
        orig_dark = self._get_env_var("DARK_MODE", "0")
        
        # 1. Update State
        state = self._read_state()
        was_target_locked = bool(state.get("target_lock"))
        state["is_offline_hunting"] = True
        state["hunt_duration_seconds"] = duration_seconds
        state["offline_hunt_start_time"] = time.time()
        state["original_dark_mode"] = orig_dark
        state["active_mission_id"] = mission_id
        self._write_state(state)
        
        state_manager.enter_offline_hunt()
        
        # 2. UI Dark Mode Inversion
        self._set_env_var("DARK_MODE", "1")
        self._trigger_ui_refresh("hunting", f"DEEP DIVE: Sniffing for {duration_seconds // 60}m offline...")
        
        # 3. Enter Monitor Mode
        log.info("Transitioning wlan0 to monitor mode...")
        
        handshake_dir = PROJECT_DIR / "handshakes"
        def get_handshake_count():
            try:
                if handshake_dir.exists():
                    return len(list(handshake_dir.glob("*.pcap*")) + list(handshake_dir.glob("*.2500*")))
            except Exception:
                pass
            return 0
            
        initial_handshakes = get_handshake_count()
        last_handshakes = initial_handshakes
        
        try:
            # Put wlan0 into monitor mode using the radio wrapper
            subprocess.run(["python3", "-m", "core.cli.entry", "network", "wifi", "off"], cwd=str(self.project_dir), capture_output=True)
            
            # 4. Wait/Sleep in 15-second chunks for the duration of the hunt
            log.info(f"Offline hunt active. Sleeping in {CHUNK_SLEEP}s chunks for {duration_seconds}s total...")
            chunks = max(1, duration_seconds // CHUNK_SLEEP)
            
            # Base XP for participating in the hunt
            add_xp(5, source="offline_hunt_start")
            
            for i in range(chunks):
                time.sleep(CHUNK_SLEEP)
                
                # Retrieve current vitals
                aipet_state = state_manager.load_state()
                
                # Check Self-Preservation (Abort if HP is critical)
                if aipet_state.hp < 20.0:
                    log.warning("Critical HP reached! Aborting offline hunt early to save hardware.")
                    self._trigger_ui_refresh("exhausted", "CRITICAL HP: Aborting dive early!")
                    break
                    
                # Thermal Decay (Monitor mode uses heavy CPU/Radio)
                # Deduct 0.1 HP per 15s chunk (0.4 HP per minute)
                aipet_state.hp = max(0.0, aipet_state.hp - 0.1)
                state_manager.save_state(aipet_state)
                
                # Every 1 minute (4 chunks), check for new handshakes and update UI
                if i > 0 and i % 4 == 0:
                    current_handshakes = get_handshake_count()
                    new_handshakes = current_handshakes - last_handshakes
                    
                    if new_handshakes > 0:
                        xp_gain = new_handshakes * 10
                        add_xp(xp_gain, source="offline_handshake_capture")
                        self._trigger_ui_refresh("smart", f"Captured {new_handshakes} new handshakes! (+{xp_gain} XP)")
                        last_handshakes = current_handshakes
                    else:
                        if "ble" in mission_id.lower():
                            self._trigger_ui_refresh("hunting", f"BLE scan running... HP: {aipet_state.hp:.1f}")
                        else:
                            self._trigger_ui_refresh("hunting", f"Sniffing the void... HP: {aipet_state.hp:.1f}")
            
        finally:
            # 5. Restore managed mode and client connectivity
            log.info("Restoring network connectivity...")
            subprocess.run(["python3", "-m", "core.cli.entry", "network", "wifi", "on"], cwd=str(self.project_dir), capture_output=True)
            
            # Give NetworkManager a moment to grab an IP
            time.sleep(15)
            
            state_manager.exit_offline_hunt()
            
            # 6. Restore original dark mode setting
            self._set_env_var("DARK_MODE", orig_dark)
            self._trigger_ui_refresh("happy", "Back online!") if orig_dark == "0" else self._trigger_ui_refresh("intense", "Stealth mode...")
            
            # 7. Clear hunt state
            state["is_offline_hunting"] = False
            state["original_dark_mode"] = orig_dark
            state["active_mission_id"] = ""
            self._write_state(state)
            
            # Post-process handshakes / reporting
            self.report_results(duration_seconds, mission_id, was_target_locked)

    def report_results(self, duration: int, mission_id: str, was_target_locked: bool = False):
        """
        Parses session handshakes, processes rewards, and sends completion logs.
        """
        # Determine captures
        captured = 0
        try:
            # Check captured PCAP/handshake counts
            handshake_dir = PROJECT_DIR / "handshakes"
            if handshake_dir.exists():
                files = list(handshake_dir.glob("*.pcap*")) + list(handshake_dir.glob("*.2500*"))
                captured = len(files)
        except Exception:
            pass
            
        report_msg = (
            f"📡 **Offline Hunt Complete!**\n"
            f"> Duration: {duration // 60} minutes\n"
            f"> Handshakes captured during dive: {captured}\n"
            f"> Screen inverted back to normal. Uplink restored!"
        )
        
        # Log and write update to daily journal
        log.info(report_msg)
        
        # Fire cognitive event hook to inform the LLM and memory
        try:
            from core.events import emit
            emit('hunt_completed', new_handshakes=captured, duration_minutes=duration // 60, was_target_locked=was_target_locked)
        except ImportError as e:
            log.warning(f"Could not emit event: {e}")
            
        log.info("Post-hunt reporting completed successfully.")
        
# Global instance
offline_hunter = OfflineHunter()
