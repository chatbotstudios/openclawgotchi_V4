import sys
import os
import time
import json
from unittest.mock import MagicMock, patch

# Add src/ to PYTHONPATH programmatically
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from core.offline_hunter import OfflineHunter, CHUNK_SLEEP

def test_offline_hunter_flow(tmp_path):
    # Setup temp paths for testing
    state_file = tmp_path / "gotchi_states.json"
    env_file = tmp_path / ".env"
    
    # Pre-populate state & env
    state_file.write_text(json.dumps({"is_offline_hunting": False}))
    env_file.write_text("DARK_MODE=0\n")
    
    hunter = OfflineHunter(project_dir=tmp_path)
    
    with patch("subprocess.run") as mock_run, \
         patch(f"{OfflineHunter.__module__}.time.sleep") as mock_sleep, \
         patch("game_engine.state.state_manager") as mock_state_manager, \
         patch("game_engine.vitals.add_xp") as mock_add_xp:
        
        # Mock show_face CLI refreshes and network changes
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock state manager
        mock_aipet_state = MagicMock()
        mock_aipet_state.hp = 100.0
        mock_state_manager.load_state.return_value = mock_aipet_state
        
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
        assert state_data["active_mission_id"] == ""
        
        # Verify StateManager status transitions
        mock_state_manager.enter_offline_hunt.assert_called_once()
        mock_state_manager.exit_offline_hunt.assert_called_once()
        
        # Sleep was called in 15-second chunks: 120 // 15 = 8 calls
        expected_chunks = 120 // CHUNK_SLEEP
        assert mock_sleep.call_count == expected_chunks + 1  # +1 for the post-hunt 15s wifi wait
        
        # Verify HP thermal decay (0.1 HP per chunk)
        # It gets saved per chunk
        assert mock_state_manager.save_state.call_count == expected_chunks
        
        # Verify Base XP
        mock_add_xp.assert_any_call(5, source="offline_hunt_start")
        
        # Commands run: ui refresh (hunting), wifi off, wifi on, ui refresh (happy)
        # Plus 1 UI refresh because 120 // 15 = 8 chunks. 8 chunks / 4 = 1 UI periodic refresh at i=4
        assert mock_run.call_count == 5
        
        # Confirm wifi status transitions
        mock_run.assert_any_call(["python3", "-m", "core.cli.entry", "network", "wifi", "off"], cwd=str(hunter.env_file.parent), capture_output=True)
        mock_run.assert_any_call(["python3", "-m", "core.cli.entry", "network", "wifi", "on"], cwd=str(hunter.env_file.parent), capture_output=True)
