from repositories.task_request_repository import DeliveryRequestRepository

class DeliveryRequestService:
    def __init__(self):
        self.repository = DeliveryRequestRepository()

    def get_product_names(self):
        products = self.repository.get_all_products()
        return [product["ITEM_NAME"] for product in products]

    def submit_delivery_request(
        self,
        item_name,
        quantity,
        destination,
        priority,
        detail,
        member_id
    ):
        if not item_name or item_name == "등록된 물품 없음":
            return False, "물품 종류를 선택하세요."

        if quantity <= 0:
            return False, "수량은 1 이상이어야 합니다."

        if not destination:
            return False, "목적지를 선택하세요."

        if not member_id:
            return False, "로그인 사용자 정보가 없습니다."

        return self.repository.create_delivery_request(
            item_name=item_name,
            quantity=quantity,
            destination=destination,
            priority=priority,
            detail=detail,
            member_id=member_id
        )
