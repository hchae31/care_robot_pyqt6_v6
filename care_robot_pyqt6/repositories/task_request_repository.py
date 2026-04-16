from db.connection import get_connection

class DeliveryRequestRepository:
    def get_all_products(self):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        PRODUCT_ID,
                        ITEM_NAME,
                        QUANTITY,
                        SUPPLY_DATE,
                        CREATED_AT,
                        UPDATED_AT
                    FROM product
                    ORDER BY ITEM_NAME
                """
                cur.execute(query)
                return cur.fetchall()
        finally:
            conn.close()

    def get_product_by_name(self, item_name, conn=None):
        own_conn = False

        if conn is None:
            conn = get_connection()
            own_conn = True

        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        PRODUCT_ID,
                        ITEM_NAME,
                        QUANTITY,
                        SUPPLY_DATE,
                        CREATED_AT,
                        UPDATED_AT
                    FROM product
                    WHERE ITEM_NAME = %s
                    LIMIT 1
                """
                cur.execute(query, (item_name,))
                return cur.fetchone()
        finally:
            if own_conn:
                conn.close()

    def create_delivery_request(
        self,
        item_name,
        quantity,
        destination,
        priority,
        detail,
        member_id
    ):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                product = self.get_product_by_name(item_name, conn=conn)

                if not product:
                    conn.rollback()
                    return False, "선택한 물품이 존재하지 않습니다."

                product_id = product["PRODUCT_ID"]
                current_qty = product["QUANTITY"]

                if quantity > current_qty:
                    conn.rollback()
                    return False, f"재고가 부족합니다. 현재 재고: {current_qty}"

                update_product_query = """
                    UPDATE product
                    SET
                        QUANTITY = QUANTITY - %s,
                        UPDATED_AT = NOW()
                    WHERE PRODUCT_ID = %s
                """
                cur.execute(update_product_query, (quantity, product_id))

                description = (
                    f"[물품 요청] "
                    f"물품종류={item_name}, "
                    f"수량={quantity}, "
                    f"목적지={destination}, "
                    f"우선순위={priority}, "
                    f"설명={detail.strip() if detail and detail.strip() else '없음'}"
                )

                event_query = """
                    INSERT INTO `event` (
                        DESCRIPTION,
                        EVENT_AT,
                        MEMBER_ID,
                        EVENT_TYPE_CODE
                    )
                    VALUES (%s, NOW(), %s, %s)
                """
                cur.execute(event_query, (description, str(member_id), 1))

                robot_event_query = """
                    INSERT INTO robot_event (
                        ROBOT_EVENT_TYPE_CODE,
                        DESCRIPTION,
                        EVENT_DATETIME,
                        OPERATION
                    )
                    VALUES (%s, %s, NOW(), %s)
                """
                cur.execute(robot_event_query, (1, description, 1))

                conn.commit()
                return True, "물품 요청이 접수되었습니다."

        except Exception as e:
            conn.rollback()
            return False, f"물품 요청 등록 중 오류가 발생했습니다: {e}"
        finally:
            conn.close()