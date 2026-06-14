import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Add src/ to PYTHONPATH programmatically
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from extensions.pwn.tether import tether_scan, tether_pair, tether_up, tether_status
from core.tether_watchdog import TetherWatchdog


def test_tether_scan():
    with patch("subprocess.run") as mock_run:
        # Mocking hcitool/bluetoothctl scan and devices
        scan_mock = MagicMock()
        scan_mock.stdout = "Device AA:BB:CC:DD:EE:FF iPhone"
        scan_mock.returncode = 0
        
        devices_mock = MagicMock()
        devices_mock.stdout = "Device AA:BB:CC:DD:EE:FF iPhone"
        devices_mock.returncode = 0
        
        mock_run.side_effect = [scan_mock, devices_mock]
        
        res = tether_scan()
        assert "Device AA:BB:CC:DD:EE:FF iPhone" in res
        assert mock_run.call_count == 2


def test_tether_pair_success():
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.stdout = "Pairing successful"
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        
        res = tether_pair("AA:BB:CC:DD:EE:FF")
        assert "Bond Established" in res
        mock_run.assert_called_once()


def test_tether_pair_failure():
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.stdout = "Failed to pair: org.bluez.Error.Failed"
        mock_proc.returncode = 1
        mock_run.return_value = mock_proc
        
        res = tether_pair("AA:BB:CC:DD:EE:FF")
        assert "Pairing might have failed" in res
        mock_run.assert_called_once()


def test_tether_up_already_online():
    with patch("subprocess.run") as mock_run:
        mock_ip = MagicMock()
        mock_ip.stdout = "3: bnep0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000\n    inet 172.20.10.2/28 brd 172.20.10.15 scope global dynamic bnep0"
        mock_ip.returncode = 0
        mock_run.return_value = mock_ip
        
        res = tether_up("AA:BB:CC:DD:EE:FF")
        assert "ALREADY ONLINE" in res
        # Should only call ip addr show and return
        mock_run.assert_called_once()


def test_tether_up_activation_success():
    with patch("subprocess.run") as mock_run, patch("time.sleep") as mock_sleep:
        # 1. ip addr show bnep0 (fails/offline)
        # 2. nmcli connection delete (success)
        # 3. bluetoothctl connect (success)
        # 4. nmcli connection add (success)
        # 5. nmcli con up (success)
        # 6. ip addr show bnep0 (success)
        
        m1 = MagicMock(returncode=1, stdout="")
        m2 = MagicMock(returncode=0)
        m3 = MagicMock(returncode=0)
        m4 = MagicMock(returncode=0)
        m5 = MagicMock(returncode=0, stdout="Connection successfully activated")
        m6 = MagicMock(returncode=0, stdout="inet 172.20.10.2/28")
        
        mock_run.side_effect = [m1, m2, m3, m4, m5, m6]
        
        res = tether_up("AA:BB:CC:DD:EE:FF")
        assert "Tether Active!" in res
        assert mock_run.call_count == 6


def test_tether_status_online():
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.stdout = "inet 172.20.10.2"
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        
        assert "Tether ONLINE" in tether_status()


def test_tether_status_offline():
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_run.return_value = mock_proc
        
        assert "Tether OFFLINE" in tether_status()


def test_watchdog_internet_check():
    watchdog = TetherWatchdog()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert watchdog._has_internet() is True
        
        mock_run.side_effect = Exception("error")
        assert watchdog._has_internet() is False


def test_watchdog_get_mac():
    watchdog = TetherWatchdog()
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.stdout = "AA:BB:CC:DD:EE:FF\n"
        mock_run.return_value = mock_proc
        assert watchdog._get_tether_mac() == "AA:BB:CC:DD:EE:FF"


def test_watchdog_attempt_tether():
    watchdog = TetherWatchdog()
    with patch("subprocess.run") as mock_run, patch("time.sleep") as mock_sleep:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "inet 172.20.10.5/28"  # Mock IP address allocation
        mock_run.return_value = mock_proc
        watchdog._attempt_tether("AA:BB:CC:DD:EE:FF")
        assert mock_run.call_count == 11
        mock_run.assert_any_call(["sudo", "bluetoothctl", "connect", "AA:BB:CC:DD:EE:FF"], capture_output=True, timeout=25)
        mock_run.assert_any_call(["sudo", "nmcli", "con", "up", "iPhoneHotspot"], capture_output=True, timeout=15)
        mock_run.assert_any_call(["ip", "link", "show", "bnep0"], capture_output=True)
        mock_run.assert_any_call(["ip", "-4", "addr", "show", "dev", "bnep0"], capture_output=True, text=True)
