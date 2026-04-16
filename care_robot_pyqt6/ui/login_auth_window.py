import json
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QProcess
from session.session_manager import SessionManager, UserSession


class LoginAuthWindow(QWidget):
    def __init__(self, role: str, previous_window=None):
        super().__init__()
        self.role = role
        self.previous_window = previous_window
        self.main_window = None
        self.login_btn = None
        self.login_process = None

        self.setWindowTitle("로그인")
        self.resize(640, 520)
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("loginAuthRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(20)

        panel = QFrame()
        panel.setObjectName("glassPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(36, 36, 36, 36)
        panel_layout.setSpacing(18)

        role_text = "보호사" if self.role == "caregiver" else "방문객"

        title = QLabel(f"{role_text} 로그인")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("아이디와 비밀번호를 입력해 주세요.")
        subtitle.setObjectName("subTitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        id_label = QLabel("아이디")
        id_label.setObjectName("fieldLabel")
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디 입력")
        self.id_input.setObjectName("inputField")

        pw_label = QLabel("비밀번호")
        pw_label.setObjectName("fieldLabel")
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 입력")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setObjectName("inputField")

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        back_btn = QPushButton("뒤로가기")
        back_btn.setObjectName("secondaryButton")
        back_btn.clicked.connect(self.go_back)

        self.login_btn = QPushButton("로그인")
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.clicked.connect(self.handle_login)

        btn_row.addWidget(back_btn)
        btn_row.addWidget(self.login_btn)

        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        panel_layout.addSpacing(6)
        panel_layout.addWidget(id_label)
        panel_layout.addWidget(self.id_input)
        panel_layout.addWidget(pw_label)
        panel_layout.addWidget(self.pw_input)
        panel_layout.addSpacing(10)
        panel_layout.addLayout(btn_row)

        root.addStretch()
        root.addWidget(panel)
        root.addStretch()

    def handle_login(self):
        login_id = self.id_input.text().strip()
        password = self.pw_input.text().strip()

        if not login_id or not password:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 입력하세요.")
            return

        if self.login_process is not None:
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("로그인 중...")
        self.id_input.setEnabled(False)
        self.pw_input.setEnabled(False)

        self.login_process = QProcess(self)
        self.login_process.finished.connect(self._handle_login_process_finished)
        self.login_process.errorOccurred.connect(self._handle_login_process_error)
        self.login_process.start(
            sys.executable,
            ["-m", "services.login_cli", login_id, password, self.role]
        )

    def _handle_login_process_finished(self, exit_code, exit_status):
        try:
            if self.login_process is None:
                return

            raw_stdout = bytes(self.login_process.readAllStandardOutput()).decode("utf-8", errors="replace").strip()
            raw_stderr = bytes(self.login_process.readAllStandardError()).decode("utf-8", errors="replace").strip()

            if not raw_stdout:
                error_text = raw_stderr or f"로그인 프로세스가 비정상 종료되었습니다. exit_code={exit_code}"
                QMessageBox.critical(self, "오류", error_text)
                return

            response = json.loads(raw_stdout)

            if not response.get("ok"):
                QMessageBox.warning(self, "로그인 실패", str(response.get("error", "로그인에 실패했습니다.")))
                return

            session_data = response["session"]
            SessionManager.login(UserSession(
                user_id=session_data["user_id"],
                name=session_data["name"],
                role=session_data["role"]
            ))

            if session_data["role"] == "caregiver":
                from ui.caregiver_main_window import CaregiverMainWindow
                self.main_window = CaregiverMainWindow()
            else:
                from ui.visitor_main_window import VisitorMainWindow
                self.main_window = VisitorMainWindow()

            self.main_window.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그인 후 화면 전환 중 오류가 발생했습니다.\n{e}")

        finally:
            if self.isVisible():
                self.login_btn.setEnabled(True)
                self.login_btn.setText("로그인")
                self.id_input.setEnabled(True)
                self.pw_input.setEnabled(True)
            self._clear_login_process()

    def _handle_login_process_error(self, error):
        _ = error
        if self.login_process is None:
            return

        error_text = bytes(self.login_process.readAllStandardError()).decode("utf-8", errors="replace").strip()
        QMessageBox.critical(self, "오류", error_text or "로그인 프로세스 실행 중 오류가 발생했습니다.")
        self.login_btn.setEnabled(True)
        self.login_btn.setText("로그인")
        self.id_input.setEnabled(True)
        self.pw_input.setEnabled(True)
        self._clear_login_process()

    def _clear_login_process(self):
        if self.login_process is not None:
            self.login_process.deleteLater()
        self.login_process = None

    def go_back(self):
        if self.previous_window is not None:
            self.previous_window.show()
        self.close()
