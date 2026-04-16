from db.connection import get_connection


class PatientRepository:
    def find_member_by_name_and_room(self, name: str, room_no: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        MEMBER_ID,
                        NAME,
                        ROOM_NO,
                        ADMISSION_DATE
                    FROM member
                    WHERE NAME = %s
                      AND ROOM_NO = %s
                    LIMIT 1
                """
                cur.execute(query, (name, room_no))
                return cur.fetchone()
        finally:
            conn.close()

    def get_recent_events(self, member_id: str, limit: int = 20):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        EVENT_AT,
                        DESCRIPTION
                    FROM event
                    WHERE MEMBER_ID = %s
                    ORDER BY EVENT_AT DESC, EVENT_ID DESC
                    LIMIT %s
                """
                cur.execute(query, (member_id, limit))
                return cur.fetchall()
        finally:
            conn.close()

    def get_preference(self, member_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        PREFERENCE,
                        DISLIKE,
                        COMMENT
                    FROM preference
                    WHERE MEMBER_ID = %s
                    LIMIT 1
                """
                cur.execute(query, (member_id,))
                return cur.fetchone()
        finally:
            conn.close()

    def get_prescriptions(self, member_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        IMAGE_PATH
                    FROM prescription
                    WHERE MEMBER_ID = %s
                    ORDER BY PRESCRIPTION_ID DESC
                """
                cur.execute(query, (member_id,))
                return cur.fetchall()
        finally:
            conn.close()
