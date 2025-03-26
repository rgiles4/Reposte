import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from RePoste.gui import MainWindow
from RePoste.main import main


@pytest.fixture()
def mock_app_and_window():
    with (
        patch("PyQt6.QtWidgets.QApplication") as mock_app,
        patch("RePoste.gui.MainWindow") as mock_main_window,
        patch(
            "RePoste.scoreboard_manager.ScoreboardManager"
        ) as mock_scoreboard_mgr,
    ):
        # Mock QApplication, MainWindow, and ScoreboardManager classes
        mock_app_instance = MagicMock(spec=QApplication)
        mock_window_instance = MagicMock(spec=MainWindow)
        mock_scoreboard_mgr_instance = MagicMock()

        mock_app.return_value = mock_app_instance
        mock_main_window.return_value = mock_window_instance
        mock_scoreboard_mgr.return_value = mock_scoreboard_mgr_instance

        yield (
            mock_app,
            mock_app_instance,
            mock_main_window,
            mock_window_instance,
            mock_scoreboard_mgr,
            mock_scoreboard_mgr_instance,
        )


def test_main(mock_app_and_window):
    # Arrange
    (
        mock_app,
        mock_app_instance,
        mock_main_window,
        mock_window_instance,
        mock_scoreboard_mgr,
        mock_scoreboard_mgr_instance,
    ) = mock_app_and_window

    # Act
    with patch("sys.exit") as mock_exit:
        main()

    # Assert
    # QApplication initialization
    mock_app.assert_called_once_with(
        []
    ), "❌ Expected QApplication to be called once with an empty list."

    # ScoreboardManager instantiation and method calls
    mock_scoreboard_mgr.assert_called_once(), "❌ Expected ScoreboardManager to be instantiated once."
    mock_scoreboard_mgr_instance.start.assert_called_once(), "❌ Expected ScoreboardManager.start() to be called."

    # MainWindow instantiation and show call
    mock_main_window.assert_called_once(), "❌ Expected MainWindow to be instantiated once."
    mock_window_instance.show.assert_called_once(), "❌ Expected the show() method of MainWindow to be called once."

    # sys.exit() is called with app.exec() return value
    mock_exit.assert_called_once_with(mock_app_instance.exec.return_value), (
        f"❌ Expected sys.exit() to be called with the result of app.exec(), "
        f"but got {mock_exit.call_args}."
    )

    # Assert ScoreboardManager stops on app exit
    mock_scoreboard_mgr_instance.stop.assert_called_once(), "❌ Expected ScoreboardManager.stop() to be called on exit."
