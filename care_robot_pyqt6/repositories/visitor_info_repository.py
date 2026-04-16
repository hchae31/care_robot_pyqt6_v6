from db.connection import get_connection


class VisitorInfoRepository:
    def _get_member_columns(self, cur):
        cur.execute("SHOW COLUMNS FROM member")
        return {row["Field"] for row in cur.fetchall()}

    @staticmethod
    def _pick(columns, *candidates):
        for candidate in candidates:
            if candidate in columns:
                return candidate
        return None

    def get_visitor_patient_info(self, keyword: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                columns = self._get_member_columns(cur)

                name_col = self._pick(columns, "MEMBER_NAME", "PATIENT_NAME", "NAME", "USER_NAME", "MEMBER_ID")
                room_col = self._pick(columns, "ROOM_NO", "ROOM_NUMBER", "ROOM", "ADMISSION_ROOM", "ADMISSION_DATE")
                visit_col = self._pick(columns, "VISIT_AVAILABLE_YN", "VISIT_STATUS", "VISITABLE_YN")
                note_col = self._pick(columns, "NOTE", "MEMO", "SPECIAL_NOTE", "CAUTION_NOTE")
                meal_col = self._pick(columns, "MEAL_STATUS", "DIET_STATUS")
                med_col = self._pick(columns, "MEDICATION_STATUS", "MEDICINE_STATUS")
                fall_col = self._pick(columns, "FALL_RISK", "SAFETY_STATUS", "RISK_LEVEL")

                if not name_col:
                    return None

                select_parts = [f"{name_col} AS patient_name"]
                if room_col:
                    select_parts.append(f"{room_col} AS room_no")
                if visit_col:
                    select_parts.append(f"{visit_col} AS visit_status")
                if note_col:
                    select_parts.append(f"{note_col} AS note_text")
                if meal_col:
                    select_parts.append(f"{meal_col} AS meal_status")
                if med_col:
                    select_parts.append(f"{med_col} AS medication_status")
                if fall_col:
                    select_parts.append(f"{fall_col} AS fall_risk")

                where_parts = [f"{name_col} LIKE %s"]
                params = [f"%{keyword}%"]
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

                visit_status = row.get("visit_status")
                if visit_status is None:
                    visit_status_text = "확인 필요"
                elif str(visit_status) in {"1", "Y", "y", "True", "true", "가능"}:
                    visit_status_text = "가능"
                elif str(visit_status) in {"0", "N", "n", "False", "false", "불가"}:
                    visit_status_text = "불가"
                else:
                    visit_status_text = str(visit_status)

                return {
                    "name": row.get("patient_name") or "-",
                    "room": row.get("room_no") or "-",
                    "meal_status": row.get("meal_status") or "정보 없음",
                    "medication_status": row.get("medication_status") or "정보 없음",
                    "fall_risk": row.get("fall_risk") or "정보 없음",
                    "visit_status": visit_status_text,
                    "notes": row.get("note_text") or "등록된 안내 메모가 없습니다.",
                }
        finally:
            conn.close()
