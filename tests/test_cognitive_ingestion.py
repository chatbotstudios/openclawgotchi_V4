import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the src directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.events import emit, _listeners
from core.cognitive_ingestor import init_cognitive_ingestor

class TestCognitiveIngestor(unittest.TestCase):
    def setUp(self):
        _listeners.clear()
        init_cognitive_ingestor()

    @patch('core.cognitive_ingestor.add_fact')
    @patch('core.cognitive_ingestor.save_pending_task')
    @patch('core.cognitive_ingestor.get_admin_id', return_value=123)
    def test_handle_handshake_captured(self, mock_get_admin, mock_save_task, mock_add_fact):
        emit('handshake_captured', ssid='TestNetwork', bssid='00:11:22:33:44:55')
        
        mock_add_fact.assert_called_once_with(
            content="Captured handshake for SSID 'TestNetwork' (BSSID: 00:11:22:33:44:55)",
            category="pwn"
        )
        
        mock_save_task.assert_called_once()
        kwargs = mock_save_task.call_args.kwargs
        self.assertEqual(kwargs['chat_id'], 123)
        self.assertIn("fresh handshake for the Wi-Fi network 'TestNetwork'", kwargs['user_text'])
        self.assertEqual(kwargs['sender_name'], "System")

    @patch('core.cognitive_ingestor.save_pending_task')
    @patch('core.cognitive_ingestor.get_admin_id', return_value=123)
    def test_handle_hunt_completed_with_handshakes(self, mock_get_admin, mock_save_task):
        emit('hunt_completed', new_handshakes=5, duration_minutes=15)
        
        mock_save_task.assert_called_once()
        kwargs = mock_save_task.call_args.kwargs
        self.assertEqual(kwargs['chat_id'], 123)
        self.assertIn("captured 5 new handshakes", kwargs['user_text'])

    @patch('core.cognitive_ingestor.save_pending_task')
    @patch('core.cognitive_ingestor.get_admin_id', return_value=123)
    def test_handle_hunt_completed_no_handshakes(self, mock_get_admin, mock_save_task):
        emit('hunt_completed', new_handshakes=0, duration_minutes=10)
        
        mock_save_task.assert_called_once()
        kwargs = mock_save_task.call_args.kwargs
        self.assertEqual(kwargs['chat_id'], 123)
        self.assertIn("didn't capture any handshakes", kwargs['user_text'])

if __name__ == '__main__':
    unittest.main()
