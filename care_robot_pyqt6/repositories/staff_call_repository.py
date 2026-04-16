from db.connection import get_connection


class StaffCallRepository:
    EVENT_TYPE_CODE = 2

    def create_staff_call(self, call_type: str, detail: str, member_id=None):
        description = (
            f"[직원 호출] 요청유형={call_type}, "
            f"상세={detail.strip() if detail and detail.strip() else '없음'}"
        )

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `event` (
                        DESCRIPTION,
                        EVENT_AT,
                        MEMBER_ID,
                        EVENT_TYPE_CODE
                    )
                    VALUES (%s, NOW(), %s, %s)
                    """,
                    (description, str(member_id) if member_id else None, self.EVENT_TYPE_CODE),
                )

                conn.commit()
                return True, "직원 호출 요청이 접수되었습니다."
        except Exception as exc:
            conn.rollback()
            return False, f"직원 호출 등록 중 오류가 발생했습니다: {exc}"
        finally:
            conn.close()
