from dataclasses import dataclass


@dataclass(frozen=True)
class TransportRequest:
    item_name: str
    quantity: int
    destination: str
    priority: str
    detail: str
    member_id: str
