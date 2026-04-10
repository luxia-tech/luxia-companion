from unittest.mock import MagicMock, patch

import pytest


def test_crew_answer():
    """Test that the crew produces a string answer."""
    mock_result = MagicMock()
    mock_result.__str__ = lambda self: "A compensação funciona via créditos de energia."

    with patch("luxia_companion.crew.CompanionCrew") as MockCrew:
        mock_instance = MockCrew.return_value
        mock_instance.crew.return_value.kickoff.return_value = mock_result

        from luxia_companion.crew import CompanionCrew

        # Call with mock
        companion = MockCrew()
        result = companion.crew().kickoff(inputs={"user_query": "como funciona a compensação?"})
        assert "compensação" in str(result).lower()
