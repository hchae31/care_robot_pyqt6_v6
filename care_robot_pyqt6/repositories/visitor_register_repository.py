from db.connection import get_connection


class VisitorRegisterRepository:
    EVENT_TYPE_CODE = 4

    def create_visitor_registration(
        self,
        visitor_name: str,
        phone: str,
        patient_name: str,
        relation: str,
        purpose: str,
        member_id=None,
    ):
        description = (
            f"[방문 등록] 방문객={visitor_name}, 연락처={phone}, "
            f"대상어르신={patient_name}, 관계={relation}, 목적={purpose}"
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
                return True, "방문 등록이 완료되었습니다."
        except Exception as exc:
            conn.rollback()
            return False, f"방문 등록 중 오류가 발생했습니다: {exc}"
        finally:
            conn.close()
