import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from generation.synthesize import generate_answer
import generation.synthesize as synth

class TestCitationExtraction(unittest.TestCase):
    def setUp(self):
        self.valid_uuid_1 = "123e4567-e89b-12d3-a456-426614174000"
        self.valid_uuid_2 = "98765432-1234-4321-b456-426614174000"
        self.invalid_uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        self.chunks = [
            {"chunk_id": self.valid_uuid_1, "metadata": {"ticker": "T1", "filing_type": "10-K", "section_heading": "H1"}, "text": "foo"},
            {"chunk_id": self.valid_uuid_2, "metadata": {"ticker": "T2", "filing_type": "10-Q", "section_heading": "H2"}, "text": "bar"}
        ]
        synth.GENERATION_BACKEND = "openrouter"
        import os
        os.environ["OPENROUTER_API_KEY"] = "dummy"

    def run_with_mock_response(self, mock_text):
        with patch('generation.synthesize.openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = mock_text
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            return generate_answer("test query", self.chunks)

    def test_a_valid_citation(self):
        text = f"This is a valid citation [{self.valid_uuid_1}]."
        result = self.run_with_mock_response(text)
        self.assertEqual(len(result['citations']), 1)
        self.assertIn(self.valid_uuid_1, result['raw_chunks_used'])

    def test_b_full_width_brackets(self):
        text = f"This is invalid ?{self.valid_uuid_1}?."
        result = self.run_with_mock_response(text)
        self.assertEqual(len(result['citations']), 0)
        self.assertEqual(len(result['raw_chunks_used']), 0)

    def test_c_colon_format(self):
        text = f"This is invalid [chunk_id: {self.valid_uuid_1}]."
        result = self.run_with_mock_response(text)
        self.assertEqual(len(result['citations']), 0)

    def test_d_unknown_uuid(self):
        text = f"This is invalid [{self.invalid_uuid}]."
        result = self.run_with_mock_response(text)
        self.assertEqual(len(result['citations']), 0)
        self.assertEqual(len(result['raw_chunks_used']), 0)
        self.assertIn(self.invalid_uuid, result['invalid_citations'])

    def test_e_multiple_valid(self):
        text = f"First [{self.valid_uuid_1}] and second [{self.valid_uuid_2}]."
        result = self.run_with_mock_response(text)
        self.assertEqual(len(result['citations']), 2)
        self.assertEqual(len(result['raw_chunks_used']), 2)

if __name__ == '__main__':
    unittest.main()
