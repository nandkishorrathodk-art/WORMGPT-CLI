import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from cryptography.fernet import Fernet
import base64

from .config import STATE_FILE_PATH, STATE_ENCRYPTION_KEY


class StateManager:
    
    def __init__(self, file_path: str = STATE_FILE_PATH, encryption_key: Optional[str] = None):
        self.file_path = file_path
        self.encryption_key = encryption_key or STATE_ENCRYPTION_KEY
        self.fernet = None
        
        if self.encryption_key:
            key = base64.urlsafe_b64encode(self.encryption_key.encode().ljust(32)[:32])
            self.fernet = Fernet(key)
    
    def load_state(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return self._get_default_state()
        
        try:
            with open(self.file_path, 'rb' if self.fernet else 'r') as f:
                if self.fernet:
                    encrypted_data = f.read()
                    decrypted_data = self.fernet.decrypt(encrypted_data)
                    return json.loads(decrypted_data.decode())
                else:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load state: {e}")
            return self._get_default_state()
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        try:
            state["last_updated"] = datetime.now().isoformat()
            
            json_data = json.dumps(state, indent=2)
            
            with open(self.file_path, 'wb' if self.fernet else 'w') as f:
                if self.fernet:
                    encrypted_data = self.fernet.encrypt(json_data.encode())
                    f.write(encrypted_data)
                else:
                    f.write(json_data)
            
            return True
        except Exception as e:
            print(f"Failed to save state: {e}")
            return False
    
    def add_mission(self, mission: Dict[str, Any]) -> bool:
        state = self.load_state()
        
        if "missions" not in state:
            state["missions"] = []
        
        mission["id"] = len(state["missions"]) + 1
        mission["timestamp"] = datetime.now().isoformat()
        
        state["missions"].append(mission)
        
        return self.save_state(state)
    
    def get_mission_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        state = self.load_state()
        missions = state.get("missions", [])
        return missions[-limit:] if missions else []
    
    def get_last_mission(self) -> Optional[Dict[str, Any]]:
        state = self.load_state()
        missions = state.get("missions", [])
        return missions[-1] if missions else None
    
    def clear_history(self) -> bool:
        state = self._get_default_state()
        return self.save_state(state)
    
    def update_mission_status(self, mission_id: int, status: str, result: Any = None) -> bool:
        state = self.load_state()
        missions = state.get("missions", [])
        
        for mission in missions:
            if mission.get("id") == mission_id:
                mission["status"] = status
                mission["updated_at"] = datetime.now().isoformat()
                if result is not None:
                    mission["result"] = result
                return self.save_state(state)
        
        return False
    
    def _get_default_state(self) -> Dict[str, Any]:
        return {
            "version": "0.11.0",
            "missions": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
