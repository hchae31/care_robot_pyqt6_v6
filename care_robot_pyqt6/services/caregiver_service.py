from repositories.caregiver_repository import CaregiverRepository


class CaregiverService:
    def __init__(self):
        self.repo = CaregiverRepository()

    def get_dashboard_summary(self):
        row = self.repo.get_dashboard_summary()

        return {
            "available_robot_count": row["available_robot_count"] if row else 0,
            "waiting_job_count": row["waiting_job_count"] if row else 0,
            "running_job_count": row["running_job_count"] if row else 0,
        }

    def get_robot_board_data(self):
        rows = self.repo.get_robot_board()
        result = []

        for row in rows:
            status = row["ROBOT_STATUS"] or "UNKNOWN"

            if status in ("대기", "IDLE"):
                chip_type = "green"
            elif status in ("충전중", "CHARGING"):
                chip_type = "yellow"
            elif status in ("오류", "ERROR"):
                chip_type = "red"
            else:
                chip_type = "blue"

            result.append({
                "robot_name": row["ROBOT_ID"],
                "status": status,
                "zone": row["CURRENT_LOCATION"] or "-",
                "battery": "-",
                "current_task": row["CURRENT_TASK"] or "-",
                "chip_type": chip_type,
            })

        return result

    def get_timeline_data(self):
        rows = self.repo.get_timeline(limit=30)
        result = []

        for row in rows:
            result.append([
                row["timeline_time"] or "",
                str(row["work_id"] or ""),
                row["event_name"] or "",
                row["detail"] or "",
            ])

        return result

    def get_flow_board_data(self):
        rows = self.repo.get_flow_board_events(limit=50)

        flow_data = {
            "READY": [],
            "ASSIGNED": [],
            "RUNNING": [],
            "DONE": [],
        }

        for row in rows:
            event_id = row["ROBOT_EVENT_ID"]
            robot_id = row["ROBOT_ID"] or "-"
            desc = row["DESCRIPTION"] or "-"
            event_type = row["ROBOT_EVENT_TYPE_CODE"]

            item_text = f"#{event_id} {desc} / {robot_id}"

            if "대기" in desc:
                flow_data["READY"].append(item_text)
            elif event_type == 1:
                flow_data["ASSIGNED"].append(item_text)
            elif event_type == 2:
                flow_data["RUNNING"].append(item_text)
            elif event_type == 3:
                flow_data["DONE"].append(item_text)

        return flow_data