import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from generation.synthesize import generate_answer
import generation.synthesize as synth

class TestValidationAndRetry(unittest.TestCase):
    def setUp(self):
        self.valid_uuid_1 = "123e4567-e89b-12d3-a456-426614174000"
        self.chunks = [
            {"chunk_id": self.valid_uuid_1, "metadata": {"ticker": "T1", "filing_type": "10-K", "section_heading": "H1"}, "text": "foo"},
        ]
        synth.GENERATION_BACKEND = "openrouter"
        import os
        os.environ["OPENROUTER_API_KEY"] = "dummy"

    def run_with_mock_responses(self, mock_texts):
        # mock_texts is a list of strings to return sequentially
        with patch('generation.synthesize._call_backend') as mock_backend:
            mock_backend.side_effect = mock_texts
            return generate_answer("test query", self.chunks), mock_backend.call_count

    def test_a_valid_answer(self):
        text = f"Summary: Good.\nKey Findings: Finding [{self.valid_uuid_1}]."
        result, calls = self.run_with_mock_responses([text])
        self.assertEqual(calls, 1)
        self.assertNotIn("Validation Error", result['answer'])

    def test_b_malformed_citation(self):
        text1 = f"Summary: Bad.\nKey Findings: Finding ?{self.valid_uuid_1}?."
        text2 = f"Summary: Good.\nKey Findings: Finding [{self.valid_uuid_1}]."
        result, calls = self.run_with_mock_responses([text1, text2])
        self.assertEqual(calls, 2)
        self.assertNotIn("Validation Error", result['answer'])

    def test_c_unknown_citation(self):
        unknown = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        text1 = f"Summary: Bad.\nKey Findings: Finding [{unknown}]."
        text2 = f"Summary: Good.\nKey Findings: Finding [{self.valid_uuid_1}]."
        result, calls = self.run_with_mock_responses([text1, text2])
        self.assertEqual(calls, 2)
        self.assertNotIn("Validation Error", result['answer'])

    def test_d_reasoning_leakage(self):
        text1 = f"We need to answer the question first...\nSummary: Bad.\nKey Findings: Finding [{self.valid_uuid_1}]."
        text2 = f"Summary: Good.\nKey Findings: Finding [{self.valid_uuid_1}]."
        result, calls = self.run_with_mock_responses([text1, text2])
        self.assertEqual(calls, 2)
        self.assertNotIn("Validation Error", result['answer'])

    def test_e_valid_refusal(self):
        text = "I cannot answer this question."
        result, calls = self.run_with_mock_responses([text])
        self.assertEqual(calls, 1)
        self.assertNotIn("Validation Error", result['answer'])
        self.assertEqual(len(result['citations']), 0)

    def test_f_partial_answer(self):
        text = f"Summary: Partial.\nKey Findings: Finding [{self.valid_uuid_1}].\nRisks/Caveats: Info."
        result, calls = self.run_with_mock_responses([text])
        self.assertEqual(calls, 1)
        self.assertNotIn("Validation Error", result['answer'])

    def test_g_retry_succeeds(self):
        text1 = "Reasoning: something"
        text2 = f"Summary: Good.\nKey Findings: Finding [{self.valid_uuid_1}]."
        result, calls = self.run_with_mock_responses([text1, text2])
        self.assertEqual(calls, 2)
        self.assertNotIn("Validation Error", result['answer'])

    def test_h_retry_exhaustion(self):
        text = "Reasoning: something"
        result, calls = self.run_with_mock_responses([text, text, text])
        self.assertEqual(calls, 3) # max_retries=2, so 3 attempts total
        self.assertIn("Validation Error", result['answer'])

if __name__ == '__main__':
    unittest.main()
