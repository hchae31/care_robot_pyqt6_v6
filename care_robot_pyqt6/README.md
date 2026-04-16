# Care Robot PyQt6 Project

업로드한 HTML/CSS 화면을 기준으로 PyQt6 프로젝트 뼈대를 재구성한 버전입니다.

## 실행 방법

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## 구조

- `main.py`: 앱 실행
- `ui/`: 화면 코드
- `ui/pages/`: 각 HTML에 대응되는 페이지
- `services/`: UI와 DB/외부 통신 사이 로직
- `repositories/`: SQL 담당
- `db/connection.py`: MariaDB 연결
- `session/session_manager.py`: 로그인 상태 유지
- `styles/main.qss`: 공통 스타일

## HTML → PyQt 변환 매핑

- `login_v1.html` → `ui/login_role_window.py`
- `login_v2.html` → `ui/login_auth_window.py`
- `caregiver_main.html` → `ui/caregiver_main_window.py`
- `visitor_main.html` → `ui/visitor_main_window.py`
- `delivery_request.html` → `ui/pages/delivery_request_page.py`
- `robot_call.html` → `ui/pages/robot_call_page.py`
- `emergency_call.html` → `ui/pages/emergency_call_page.py`
- `robot_status.html` → `ui/pages/robot_status_page.py`
- `patient_info.html` → `ui/pages/patient_info_page.py`
- `patient_input.html` → `ui/pages/patient_input_page.py`
- `alert_log.html` → `ui/pages/alert_log_page.py`
- `visitor_register.html` → `ui/pages/visitor_register_page.py`
- `visit_guide.html` → `ui/pages/visit_guide_page.py`
- `visit_guide_v0.html` → `ui/pages/visit_guide_v0_page.py`
- `visitor_info.html` → `ui/pages/visitor_info_page.py`
- `staff_call.html` → `ui/pages/staff_call_page.py`

## DB 연결

현재는 `db/connection.py`에 MariaDB 연결 코드가 있고, 실제 화면은 더미 데이터와 기본 CRUD 뼈대가 섞여 있습니다.
프로토타입 단계에서는 UI를 먼저 확인한 뒤 Repository/Service를 연결하면 됩니다.
