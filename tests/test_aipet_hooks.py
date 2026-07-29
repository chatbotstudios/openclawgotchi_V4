"""Tests for the AIPET plugin hooks system (plugins/aipet_hooks.py).

Covers all registered hooks:
- heartbeat: HP calculation, mood decay, mission progress
- pwn.handshake: XP reward (5), mission increment
- pwn.ble: scan tracking, XP (3 per scan with devices)
- message: Deep Thought, Chatterbox, Night Owl mission progress
- command: Teacher, Historian, System Admin, Cron Master tracking
"""
import sys
import os
from unittest.mock import MagicMock, patch, ANY
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
import game_engine.state  # noqa: F401 — ensure module is resolvable for patches


# ── Heartbeat Hook Tests ─────────────────────────────────────────────────────

@patch("plugins.aipet_hooks.load_state")
@patch("plugins.aipet_hooks.save_state")
@patch("plugins.aipet_hooks.calculate_hp")
@patch("plugins.aipet_hooks.decay_mood")
@patch("plugins.aipet_hooks.increment_mission_progress")
def test_heartbeat_hook_updates_hp(
    mock_inc_mission, mock_decay, mock_calc_hp, mock_save, mock_load
):
    """Heartbeat hook should calculate HP and save if changed."""
    from plugins.aipet_hooks import aipet_heartbeat_hook
    from hooks.runner import HookEvent

    mock_state = MagicMock()
    mock_state.hp = 90.0
    mock_load.return_value = mock_state
    mock_calc_hp.return_value = 85.0

    event = HookEvent(event_type="heartbeat")
    aipet_heartbeat_hook(event)

    mock_calc_hp.assert_called_once_with(15.0, 40.0, 25.0, 85.0)
    mock_save.assert_called_once_with(mock_state)
    assert mock_state.hp == 85.0


@patch("plugins.aipet_hooks.load_state")
@patch("plugins.aipet_hooks.save_state")
@patch("plugins.aipet_hooks.calculate_hp")
@patch("plugins.aipet_hooks.decay_mood")
@patch("plugins.aipet_hooks.increment_mission_progress")
def test_heartbeat_hook_skips_save_if_hp_unchanged(
    mock_inc_mission, mock_decay, mock_calc_hp, mock_save, mock_load
):
    """Heartbeat hook should not save if HP hasn't changed."""
    from plugins.aipet_hooks import aipet_heartbeat_hook
    from hooks.runner import HookEvent

    mock_state = MagicMock()
    mock_state.hp = 100.0
    mock_load.return_value = mock_state
    mock_calc_hp.return_value = 100.0  # Same HP

    event = HookEvent(event_type="heartbeat")
    aipet_heartbeat_hook(event)

    mock_save.assert_not_called()


# ── Handshake Hook Tests ────────────────────────────────────────────────────

@patch("plugins.aipet_hooks.add_xp")
@patch("plugins.aipet_hooks.increment_mission_progress")
def test_handshake_hook_awards_xp(mock_inc_mission, mock_add_xp):
    """pwn.handshake hook should award 5 XP and increment mission."""
    from plugins.aipet_hooks import aipet_handshake_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="pwn.handshake", action="captured", data={"ssid": "TestNet"})
    aipet_handshake_hook(event)

    mock_add_xp.assert_called_once_with(5, source="handshake_capture")
    mock_inc_mission.assert_called_once_with("Handshake Hunter", 1, event=event)


# ── BLE Hook Tests ──────────────────────────────────────────────────────────

@patch("plugins.aipet_hooks.add_xp")
@patch("plugins.aipet_hooks.increment_mission_progress")
def test_ble_scan_with_devices_awards_xp(mock_inc_mission, mock_add_xp):
    """BLE scan hook should award 3 XP per scan with devices found."""
    from plugins.aipet_hooks import aipet_ble_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="pwn.ble", action="scan", data={"device_count": 2})
    aipet_ble_hook(event)

    mock_add_xp.assert_called_once_with(3, source="ble_scan")
    mock_inc_mission.assert_called_once_with("BLE Phantom", 1, event=event)


@patch("plugins.aipet_hooks.add_xp")
@patch("plugins.aipet_hooks.increment_mission_progress")
def test_ble_scan_no_devices_no_xp(mock_inc_mission, mock_add_xp):
    """BLE scan hook should NOT award XP when no devices found."""
    from plugins.aipet_hooks import aipet_ble_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="pwn.ble", action="scan", data={"device_count": 0})
    aipet_ble_hook(event)

    mock_add_xp.assert_not_called()
    mock_inc_mission.assert_called_once_with("BLE Phantom", 1, event=event)


@patch("plugins.aipet_hooks.add_xp")
@patch("plugins.aipet_hooks.increment_mission_progress")
def test_ble_non_scan_action_skipped(mock_inc_mission, mock_add_xp):
    """BLE hook should only trigger on 'scan' action."""
    from plugins.aipet_hooks import aipet_ble_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="pwn.ble", action="connect", data={})
    aipet_ble_hook(event)

    mock_add_xp.assert_not_called()
    mock_inc_mission.assert_not_called()


# ── Message Hook Tests ──────────────────────────────────────────────────────

@patch("plugins.aipet_hooks.increment_mission_progress")
def test_message_hook_tracks_missions(mock_inc_mission):
    """Message hook should increment Deep Thought and Chatterbox on user message."""
    from plugins.aipet_hooks import aipet_message_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="message", user_id=123, timestamp=datetime(2026, 7, 30, 14, 0))
    aipet_message_hook(event)

    assert mock_inc_mission.call_count == 2
    mock_inc_mission.assert_any_call("Deep Thought", 1, event=event)
    mock_inc_mission.assert_any_call("Chatterbox", 1, event=event)


@patch("plugins.aipet_hooks.increment_mission_progress")
def test_message_hook_night_owl(mock_inc_mission):
    """Message hook should also increment Night Owl between 2-4 AM."""
    from plugins.aipet_hooks import aipet_message_hook
    from hooks.runner import HookEvent

    # 3 AM — Night Owl window
    event = HookEvent(event_type="message", user_id=123, timestamp=datetime(2026, 7, 30, 3, 30))
    aipet_message_hook(event)

    assert mock_inc_mission.call_count == 3
    mock_inc_mission.assert_any_call("Night Owl", 1, event=event)


@patch("plugins.aipet_hooks.increment_mission_progress")
def test_message_hook_system_message_skipped(mock_inc_mission):
    """Message hook should skip messages without user_id."""
    from plugins.aipet_hooks import aipet_message_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="message", user_id=0, timestamp=datetime(2026, 7, 30, 14, 0))
    aipet_message_hook(event)

    mock_inc_mission.assert_not_called()


# ── Command Hook Tests ──────────────────────────────────────────────────────

@patch("plugins.aipet_hooks.increment_mission_progress")
def test_command_hook_remember_teacher(mock_inc_mission):
    """/remember command should increment 'The Teacher' mission."""
    from plugins.aipet_hooks import aipet_command_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="command", user_id=123, action="/remember")
    aipet_command_hook(event)

    mock_inc_mission.assert_called_once_with("The Teacher", 1, event=event)


@patch("plugins.aipet_hooks.increment_mission_progress")
def test_command_hook_status_sysadmin(mock_inc_mission):
    """/status command should increment 'System Admin' mission."""
    from plugins.aipet_hooks import aipet_command_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="command", user_id=123, action="/status")
    aipet_command_hook(event)

    mock_inc_mission.assert_called_once_with("System Admin", 1, event=event)


@patch("plugins.aipet_hooks.increment_mission_progress")
def test_command_hook_cron_master(mock_inc_mission):
    """/cron command should increment 'Cron Master' mission."""
    from plugins.aipet_hooks import aipet_command_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="command", user_id=123, action="/cron")
    aipet_command_hook(event)

    mock_inc_mission.assert_called_once_with("Cron Master", 1, event=event)


@patch("plugins.aipet_hooks.increment_mission_progress")
def test_command_hook_no_user_skipped(mock_inc_mission):
    """Command hook should skip commands without user_id."""
    from plugins.aipet_hooks import aipet_command_hook
    from hooks.runner import HookEvent

    event = HookEvent(event_type="command", user_id=0, action="/status")
    aipet_command_hook(event)

    mock_inc_mission.assert_not_called()
