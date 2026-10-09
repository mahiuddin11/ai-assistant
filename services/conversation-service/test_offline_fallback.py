import os
import sys
import unittest
from unittest.mock import patch

# Ensure paths
sys.path.append(os.path.dirname(__file__))

import llm_client
from llm_client import _call_offline_fallback, send_message

class TestOfflineFallback(unittest.TestCase):
    def test_offline_intent_greetings(self):
        resp_en = _call_offline_fallback("Hello there!")
        self.assertIn("offline", resp_en.lower())
        
        resp_bn = _call_offline_fallback("আসসালামু আলাইকুম")
        self.assertIn("ওয়ালাইকুম আসসালাম", resp_bn)

    def test_offline_intent_time(self):
        resp = _call_offline_fallback("এখন কয়টা বাজে?")
        self.assertIn("লোকাল বর্তমান সময়", resp)

    def test_offline_intent_math(self):
        resp = _call_offline_fallback("What is 15 * 4?")
        self.assertIn("60.0", resp)

    def test_offline_network_drop_simulation(self):
        """Simulate all cloud providers raising timeouts/API errors."""
        def mock_failing_retry(provider, user_message, system_prompt):
            raise RuntimeError(f"Simulated network outage for provider {provider['name']}")

        with patch("llm_client._call_provider_with_retry", side_effect=mock_failing_retry):
            result = send_message("Hello AI, is internet working?")
            
            self.assertEqual(result.get("provider_used"), "local_offline")
            self.assertTrue(result.get("offline_fallback_active"))
            self.assertIn("reply", result)
            self.assertIn("upstream_errors", result)
            print("\n[Simulation] Network Disconnect Test Passed!")
            print("Fallback Result:", result)

if __name__ == "__main__":
    unittest.main()
