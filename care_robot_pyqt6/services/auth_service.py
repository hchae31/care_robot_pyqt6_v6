from repositories.user_repository import UserRepository

from session.session_manager import SessionManager, UserSession

class AuthService:
    def __init__(self):
        self.auth_repository = UserRepository()

    def authenticate(self, login_id: str, password: str, role: str):
        try:
            user = self.auth_repository.find_user_for_login(login_id)

            if not user:
                return False, "존재하지 않는 아이디입니다."

            db_password = str(user["PASSWORD"])

            if db_password != password:
                return False, "비밀번호가 일치하지 않습니다."

            return True, {
                "user_id": str(user["MEMBER_ID"]),
                "name": str(user["MEMBER_ID"]),
                "role": role.strip().lower(),
            }

        except Exception as e:
            return False, f"로그인 처리 중 오류가 발생했습니다: {e}"

    def login(self, login_id: str, password: str, role: str):
        ok, result = self.authenticate(login_id, password, role)

        if not ok:
            return False, result

        session_user = UserSession(
            user_id=result["user_id"],
            name=result["name"],
            role=result["role"]
        )
        SessionManager.login(session_user)
        return True, session_user

    def logout(self):
        SessionManager.logout()
