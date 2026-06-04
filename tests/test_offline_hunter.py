import sys
import os
import time
import json
from unittest.mock import MagicMock, patch

# Add src/ to PYTHONPATH programmatically
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from core.offline_hunter import OfflineHunter

def test_offline_hunter_flow(tmp_path):
    # Setup temp paths for testing
    state_file = tmp_path / "gotchi_states.json"
    env_file = tmp_path / ".env"
    
    # Pre-populate state & env
    state_file.write_text(json.dumps({"is_offline_hunting": False}))
    env_file.write_text("DARK_MODE=0\n")
    
    hunter = OfflineHunter(project_dir=tmp_path)
    
    with patch("subprocess.run") as mock_run, patch("time.sleep") as mock_sleep:
        # Mock show_face CLI refreshes and network changes
        mock_run.return_value = MagicMock(returncode=0)
        
        # Run hunt for 120 seconds (2 minutes)
        hunter.run_hunt(120, "handshake_hunter_v2")
        
        # Verify elapsed actions
        # Should verify E-Ink transitions to dark mode and then back to light mode (0)
        env_content = env_file.read_text()
        assert "DARK_MODE=0" in env_content
        
        # Verify status updates on state
        state_data = json.loads(state_file.read_text())
        assert state_data["is_offline_hunting"] is False
        assert state_data["original_dark_mode"] == "0"
        assert state_data["active_mission_id"] == "handshake_hunter_v2"
        
        # Sleep was called with target duration
        mock_sleep.assert_called_with(120)
        
        # Commands run: ui refresh (hunting), wifi off, wifi on, ui refresh (happy)
        assert mock_run.call_count == 4
        
        # Confirm wifi status transitions
        mock_run.assert_any_call(["python3", "-m", "core.cli.entry", "network", "wifi", "off"], cwd=str(hunter.env_file.parent), capture_output=True)
        mock_run.assert_any_call(["python3", "-m", "core.cli.entry", "network", "wifi", "on"], cwd=str(hunter.env_file.parent), capture_output=True)
