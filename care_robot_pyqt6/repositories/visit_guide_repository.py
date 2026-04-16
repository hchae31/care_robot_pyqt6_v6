from db.connection import get_connection


class VisitGuideRepository:
    def _get_member_columns(self, cur):
        cur.execute("SHOW COLUMNS FROM member")
        return {row["Field"] for row in cur.fetchall()}

    @staticmethod
    def _pick(columns, *candidates):
        for candidate in candidates:
            if candidate in columns:
                return candidate
        return None

    def find_patient(self, keyword: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                columns = self._get_member_columns(cur)

                name_col = self._pick(columns, "MEMBER_NAME", "PATIENT_NAME", "NAME", "USER_NAME", "MEMBER_ID")
                room_col = self._pick(columns, "ROOM_NO", "ROOM_NUMBER", "ROOM", "ADMISSION_ROOM", "ADMISSION_DATE")
                location_col = self._pick(columns, "CURRENT_LOCATION", "LOCATION", "WARD_NAME", "ROOM_NO", "ROOM_NUMBER", "ROOM")
                visit_col = self._pick(columns, "VISIT_AVAILABLE_YN", "VISIT_STATUS", "VISITABLE_YN")
                grade_col = self._pick(columns, "MEMBER_GRADE", "ROLE", "MEMBER_TYPE")
                id_col = self._pick(columns, "MEMBER_ID", "PATIENT_ID", "ID")

                if not name_col:
                    return None

                select_parts = [f"{name_col} AS patient_name"]
                if id_col:
                    select_parts.append(f"{id_col} AS member_id")
                if room_col:
                    select_parts.append(f"{room_col} AS room_no")
                if location_col:
                    select_parts.append(f"{location_col} AS location_text")
                if visit_col:
                    select_parts.append(f"{visit_col} AS visit_status")
                if grade_col:
                    select_parts.append(f"{grade_col} AS member_grade")

                where_parts = [f"{name_col} LIKE %s"]
                params = [f"%{keyword}%"]
                if id_col and id_col != name_col:
                    where_parts.append(f"{id_col} LIKE %s")
                    params.append(f"%{keyword}%")
                if room_col:
                    where_parts.append(f"{room_col} LIKE %s")
                    params.append(f"%{keyword}%")

                query = f"""
                    SELECT {', '.join(select_parts)}
                    FROM member
                    WHERE {' OR '.join(where_parts)}
                    ORDER BY {name_col}
                    LIMIT 1
                """
                cur.execute(query, tuple(params))
                row = cur.fetchone()
                if not row:
                    return None

                location = row.get("location_text") or row.get("room_no") or "위치 정보 없음"
                visit_status = row.get("visit_status")
                if visit_status is None:
                    visit_status = "면회 가능 여부 확인 필요"
                elif str(visit_status) in {"1", "Y", "y", "True", "true", "가능"}:
                    visit_status = "면회 가능"
                elif str(visit_status) in {"0", "N", "n", "False", "false", "불가"}:
                    visit_status = "면회 불가"

                return {
                    "name": row.get("patient_name") or "-",
                    "member_id": row.get("member_id") or "-",
                    "room": row.get("room_no") or "-",
                    "location": location,
                    "status": visit_status,
                    "member_grade": row.get("member_grade") or "-",
                }
        finally:
            conn.close()

    def create_robot_guide_event(self, patient_name: str, room_no: str, member_id=None):
        description = f"[면회 안내] 대상={patient_name}, 목적지={room_no or '미지정'}, 안내 시작 요청"

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
                    (description, str(member_id) if member_id else None, 3),
                )
                conn.commit()
                return True, "로봇 안내 요청이 접수되었습니다."
        except Exception as exc:
            conn.rollback()
            return False, f"로봇 안내 요청 등록 중 오류가 발생했습니다: {exc}"
        finally:
            conn.close()
