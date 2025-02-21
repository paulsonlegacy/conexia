import asyncio
import io
import unittest
from contextlib import redirect_stdout

from conexia.cli import main

class TestCLI(unittest.TestCase):
    def test_cli_output(self):
        """Test that CLI prints expected output."""
        captured_output = io.StringIO()
        # Redirect stdout to capture prints from the main() function.
        with redirect_stdout(captured_output):
            asyncio.run(main())
        output = captured_output.getvalue()

        # Assert that output contains expected STUN result
        self.assertIn("STUN Result:", output)  # Ensure CLI prints the expected format

        # Ensure output contains expected network info keys (modify as per actual response)
        expected_keys = ["ip", "port", "nat_type"]
        for key in expected_keys:
            self.assertIn(key, output.lower())  # Convert to lowercase for case-insensitive matching

if __name__ == '__main__':
    unittest.main()
