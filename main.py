"""
Application Entry Point for Mercy Dental Care - Attendance & HR Management System (QT6).
"""

import sys
import os
import traceback

# Ensure working directory is always this script's directory
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)
sys.path.insert(0, app_dir)

# Catch any unexpected startup error and log it
def exception_hook(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    with open(os.path.join(app_dir, "crash.log"), "w", encoding="utf-8") as f:
        f.write(err_msg)
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import database
from main_window import MainWindow

def main():
    try:
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setApplicationName("Mercy Dental Care HR")
        app.setApplicationDisplayName("Mercy Dental Care - HR & Attendance System")

        from theme import APP_STYLE
        from PyQt6.QtGui import QPalette, QColor
        app.setStyleSheet(APP_STYLE)

        # Enforce clean light palette (prevents OS dark mode from blackening popups/menus)
        palette = app.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#F8FAFC"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F1F5F9"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#5648A6"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        app.setPalette(palette)

        # Set application icon
        ico_path = os.path.join(app_dir, "assets", "logo.ico")
        if os.path.exists(ico_path):
            app.setWindowIcon(QIcon(ico_path))

        # Initialize database
        database.init_db()

        # Start Mobile Web Attendance Server (Port 5000)
        try:
            import mobile_server
            mobile_server.start_mobile_server(port=5000)
        except Exception as se:
            print("Warning: Could not start mobile server:", se)

        # Show Login Dialog on startup
        from components.login_dialog import LoginDialog
        login_dlg = LoginDialog()
        if login_dlg.exec():
            window = MainWindow(current_user=login_dlg.user_data)
            window.show()
            window.raise_()
            window.activateWindow()
            sys.exit(app.exec())
        else:
            sys.exit(0)
    except Exception as e:
        err_msg = traceback.format_exc()
        with open(os.path.join(app_dir, "crash.log"), "w", encoding="utf-8") as f:
            f.write(err_msg)
        try:
            from PyQt6.QtWidgets import QMessageBox
            if QApplication.instance():
                QMessageBox.critical(None, "Mercy Dental Care - កំហុសប្រព័ន្ធ", f"មានបញ្ហាក្នុងការបើកកម្មវិធី៖\n\n{e}\n\nសូមពិនិត្យមើល crash.log សម្រាប់ព័ត៌មានបន្ថែម។")
            else:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, f"មានបញ្ហាក្នុងការបើកកម្មវិធី៖\n\n{e}\n\nសូមពិនិត្យមើល crash.log សម្រាប់ព័ត៌មានបន្ថែម។", "Mercy Dental Care", 0x10)
        except Exception:
            pass

if __name__ == "__main__":
    main()
