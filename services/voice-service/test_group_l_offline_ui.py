import os
import sys
import unittest
from unittest.mock import patch

# Ensure paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "conversation-service"))

import llm_client
from llm_client import _call_offline_fallback, send_message

class TestGroupL(unittest.TestCase):
    def test_01_offline_fallback_bengali_english(self):
        """Task 48: Test offline rule-based / intent engine responses."""
        resp_hello = _call_offline_fallback("hello")
        self.assertIn("offline", resp_hello.lower())

        resp_bn_greet = _call_offline_fallback("আসসালামু আলাইকুম")
        self.assertIn("ওয়ালাইকুম আসসালাম", resp_bn_greet)

        resp_time = _call_offline_fallback("এখন কয়টা বাজে?")
        self.assertIn("সময়", resp_time)

        resp_math = _call_offline_fallback("calculate 12 * 8")
        self.assertIn("96.0", resp_math)

    def test_02_network_outage_simulation(self):
        """Task 48: Simulate complete internet disconnection and assert fallback activation."""
        def mock_failing_retry(provider, user_message, system_prompt):
            raise RuntimeError(f"Network timeout: {provider['name']} unreachable")

        with patch("llm_client._call_provider_with_retry", side_effect=mock_failing_retry):
            result = send_message("Hi, are you there?")
            self.assertEqual(result.get("provider_used"), "local_offline")
            self.assertTrue(result.get("offline_fallback_active"))
            self.assertIn("reply", result)

    def test_03_web_ui_voice_ptt_elements(self):
        """Task 49: Validate chat.html contains Voice button, visualizer, live transcript, and Voice Live Modal."""
        chat_html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "web-ui", "chat.html"))
        self.assertTrue(os.path.exists(chat_html_path), "chat.html must exist")

        with open(chat_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for Voice button & Voice Live Modal
        self.assertIn('id="voiceBtn"', content)
        self.assertIn('openVoiceLiveMode', content)
        self.assertIn('id="voiceLiveModal"', content)
        self.assertIn('id="voiceOrb"', content)

        # Check for Visualizer Canvas & Voice Panel
        self.assertIn('id="voicePanel"', content)
        self.assertIn('id="voiceCanvas"', content)
        self.assertIn('id="voiceSubtitleText"', content)

        # Check for Greeting & Realtime Voice Loop
        self.assertIn('GREETING_TEXT', content)
        self.assertIn('আসসালামু আলাইকুম', content)
        self.assertIn('SpeechRecognition', content)
        self.assertIn('speechSynthesis', content)


if __name__ == "__main__":
    unittest.main()
