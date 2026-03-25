import unittest


class UIRegressionTests(unittest.TestCase):
    def test_main_window_material_action_reports_invalid_path(self):
        try:
            from src.ui.main_window import MainWindow
        except ImportError:
            self.skipTest("PySide6 is not installed")

        ok, error = MainWindow._execute_material_file_action(
            lambda: (_ for _ in ()).throw(ValueError("bad path"))
        )
        self.assertIsNone(ok)
        self.assertEqual(error, "bad path")
