from typing import Dict, List, Any, Optional

class MessageBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            cls._instance.mailboxes: Dict[str, List[Dict[str, Any]]] = {}
        return cls._instance

    def send_message(self, recipient_queen_id: str, message: Dict[str, Any]):
        if recipient_queen_id not in self.mailboxes:
            self.mailboxes[recipient_queen_id] = []
        self.mailboxes[recipient_queen_id].append(message)

    def receive_messages(self, queen_id: str) -> List[Dict[str, Any]]:
        messages = self.mailboxes.get(queen_id, [])
        self.mailboxes[queen_id] = []  # Clear mailbox after reading
        return messages
