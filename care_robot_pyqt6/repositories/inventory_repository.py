from db.connection import get_connection


class InventoryRepository:
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
                        UPDATED_AT,
                        OPERATION
                    FROM product
                    ORDER BY ITEM_NAME
                """
                cur.execute(query)
                return cur.fetchall()
        finally:
            conn.close()

    def add_quantity(self, product_id, quantity):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    UPDATE product
                    SET
                        ITEMNAME = %s,
                        QUANTITY = QUANTITY + %s,
                        UPDATED_AT = NOW()
                    WHERE PRODUCT_ID = %s
                """
                cur.execute(query, (quantity, product_id))
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()
