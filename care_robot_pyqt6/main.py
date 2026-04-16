import sys
from PyQt6.QtWidgets import QApplication
from core.paths import STYLE_PATH
from ui.login_role_window import LoginRoleWindow


def load_stylesheet() -> str:
    try:
        return STYLE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())

    window = LoginRoleWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()