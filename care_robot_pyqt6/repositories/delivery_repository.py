from db.connection import get_connection


class DeliveryRepository:
    def create_request(self, item_type: str, destination: str, priority: str, detail: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO product (
                        ITEM_NAME,
                        destination,
                        priority,
                        detail,
                        request_status
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(query, (
                    item_type,
                    destination,
                    priority,
                    detail,
                    "요청접수"
                ))
                conn.commit()

                return {
                    "request_id": cur.lastrowid,
                    "item_type": item_type,
                    "destination": destination,
                    "priority": priority,
                    "detail": detail,
                    "request_status": "요청접수"
                }
        finally:
            conn.close()

    def get_recent_requests(self, limit: int = 5):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        request_id,
                        item_type,
                        destination,
                        priority,
                        detail,
                        request_status,
                        created_at
                    FROM delivery_request
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                cur.execute(query, (limit,))
                return cur.fetchall()
        finally:
            conn.close()