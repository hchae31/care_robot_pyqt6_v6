from db.connection import get_connection

class UserRepository:
    def find_user_for_login(self, member_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        MEMBER_ID,
                        PASSWORD,
                        MEMBER_GRADE,
                        CARE_GRADE_CODE
                    FROM member
                    WHERE MEMBER_ID = %s
                    LIMIT 1
                """
                cur.execute(query, (member_id,))
                return cur.fetchone()
        finally:
            conn.close()