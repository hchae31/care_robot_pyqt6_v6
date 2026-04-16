from db.connection import get_connection


class CaregiverRepository:
    def get_dashboard_summary(self):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM robot r
                            JOIN robot_status_code rsc
                              ON r.ROBOT_STATUS_CODE = rsc.ROBOT_STATUS_CODE
                            WHERE r.WORKING_YN = 1
                              AND rsc.ROBOT_STATUS IN ('대기', 'IDLE')
                        ) AS available_robot_count,
                        (
                            SELECT COUNT(*)
                            FROM robot_event
                            WHERE DESCRIPTION LIKE '%대기%'
                        ) AS waiting_job_count,
                        (
                            SELECT COUNT(*)
                            FROM robot r
                            JOIN robot_status_code rsc
                              ON r.ROBOT_STATUS_CODE = rsc.ROBOT_STATUS_CODE
                            WHERE r.WORKING_YN = 1
                              AND rsc.ROBOT_STATUS IN ('작업중', 'RUNNING')
                        ) AS running_job_count;
                """
                cur.execute(query)
                return cur.fetchone()
        finally:
            conn.close()

    def get_robot_board(self):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        r.ROBOT_ID,
                        r.ROBOT_TYPE_NAME,
                        r.CURRENT_LOCATION,
                        r.WORKING_YN,
                        rsc.ROBOT_STATUS,
                        (
                            SELECT re.DESCRIPTION
                            FROM robot_event re
                            WHERE re.ROBOT_ID = r.ROBOT_ID
                            ORDER BY re.EVENT_DATETIME DESC
                            LIMIT 1
                        ) AS CURRENT_TASK
                    FROM robot r
                    LEFT JOIN robot_status_code rsc
                      ON r.ROBOT_STATUS_CODE = rsc.ROBOT_STATUS_CODE
                    ORDER BY r.ROBOT_ID;
                """
                cur.execute(query)
                return cur.fetchall()
        finally:
            conn.close()

    def get_timeline(self, limit=20):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        DATE_FORMAT(re.EVENT_DATETIME, '%%H:%%i:%%s') AS timeline_time,
                        re.ROBOT_EVENT_ID AS work_id,
                        CASE re.ROBOT_EVENT_TYPE_CODE
                            WHEN 1 THEN 'READY HELP'
                            WHEN 2 THEN 'ASSIGNED'
                            WHEN 3 THEN 'RUNNING'
                            WHEN 4 THEN 'DONE'
                            ELSE 'UNKNOWN'
                        END AS event_name,
                        CONCAT(re.ROBOT_ID, ' - ', re.DESCRIPTION) AS detail
                    FROM robot_event re
                    ORDER BY re.EVENT_DATETIME DESC
                    LIMIT %s;
                """
                cur.execute(query, (limit,))
                return cur.fetchall()
        finally:
            conn.close()

    def get_flow_board_events(self, limit=50):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT
                        re.ROBOT_EVENT_ID,
                        re.ROBOT_EVENT_TYPE_CODE,
                        re.DESCRIPTION,
                        re.EVENT_DATETIME,
                        re.ROBOT_ID
                    FROM robot_event re
                    ORDER BY re.EVENT_DATETIME DESC
                    LIMIT %s;
                """
                cur.execute(query, (limit,))
                return cur.fetchall()
        finally:
            conn.close()