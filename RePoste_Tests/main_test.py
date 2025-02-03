import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

from RePoste.gui import MainWindow


@pytest.fixture()
def mock_app_and_window():
    with (patch("PyQt6.QtWidgets.QApplication") as mock_app,
          patch("RePoste.gui.MainWindow") as mock_main_window):

        # Mock QApplication
        mock_app_instance = MagicMock(spec=QApplication)

        # Mock MainWindow Class
        mock_window_instance = MagicMock(spec=MainWindow)

        mock_app.return_value = mock_app_instance
        mock_main_window.return_value = mock_window_instance

        yield (mock_app, mock_app_instance,
               mock_main_window, mock_window_instance)


def test_main(mock_app_and_window):
    # Arrange
    (mock_app, mock_app_instance,
     mock_main_window, mock_window_instance) = mock_app_and_window

    # Act
    with patch('sys.exit') as mock_exit:
        from RePoste.main import main

        main()

        # Assert
        mock_app.assert_called_once_with([]), (
            "❌ Expected QApplication to be called once w/ empty list as arg.")
        mock_main_window.assert_called_once(), (
            "❌ Expected MainWindow to be instantiated once during execution.")

        mock_window_instance.show.assert_called_once(), (
            "❌ Expected the show() method of MainWindow to be called once.")

        mock_exit.assert_called_once_with(mock_app_instance.exec.return_value),
        (f"Expected sys.exit to be called with the result of app.exec(), "
         f"but got {mock_exit.call_args}.")
