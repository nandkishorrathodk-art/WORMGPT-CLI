"""
Comprehensive tests for StateManager.
"""
import pytest
import os
import tempfile
import json
from wormgpt_hive.shared.state_manager import StateManager


class TestStateManagerComprehensive:
    """Test StateManager functionality comprehensively."""
    
    def test_init_without_encryption(self):
        """Test StateManager initialization without encryption."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            assert sm.file_path == temp_file
            assert not sm.encryption_key or sm.encryption_key == ""
            assert sm.fernet is None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_init_with_encryption(self):
        """Test StateManager initialization with encryption."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key="test_key_1234567890123456")
            
            assert sm.file_path == temp_file
            assert sm.encryption_key == "test_key_1234567890123456"
            assert sm.fernet is not None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_load_state_creates_default_if_missing(self):
        """Test loading state creates default state if file doesn't exist."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        os.remove(temp_file)
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            state = sm.load_state()
            
            assert "version" in state
            assert "missions" in state
            assert isinstance(state["missions"], list)
            assert len(state["missions"]) == 0
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_save_and_load_state_without_encryption(self):
        """Test saving and loading state without encryption."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            test_state = {
                "version": "0.11.0",
                "missions": [{"id": 1, "goal": "Test"}],
                "created_at": "2024-01-01",
                "last_updated": "2024-01-01"
            }
            
            success = sm.save_state(test_state)
            assert success is True
            
            loaded_state = sm.load_state()
            assert loaded_state["version"] == "0.11.0"
            assert len(loaded_state["missions"]) == 1
            assert loaded_state["missions"][0]["goal"] == "Test"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_save_and_load_state_with_encryption(self):
        """Test saving and loading state with encryption."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key="test_key_1234567890123456")
            
            test_state = {
                "version": "0.11.0",
                "missions": [{"id": 1, "goal": "Encrypted mission"}],
                "created_at": "2024-01-01",
                "last_updated": "2024-01-01"
            }
            
            success = sm.save_state(test_state)
            assert success is True
            
            with open(temp_file, 'rb') as f:
                content = f.read()
                assert len(content) > 0
                assert b"Encrypted mission" not in content
            
            loaded_state = sm.load_state()
            assert loaded_state["version"] == "0.11.0"
            assert len(loaded_state["missions"]) == 1
            assert loaded_state["missions"][0]["goal"] == "Encrypted mission"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_add_mission(self):
        """Test adding a mission to state."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            mission = {
                "goal": "Test mission",
                "status": "pending",
                "steps": []
            }
            
            success = sm.add_mission(mission)
            assert success is True
            
            state = sm.load_state()
            assert len(state["missions"]) == 1
            assert state["missions"][0]["goal"] == "Test mission"
            assert state["missions"][0]["id"] == 1
            assert "timestamp" in state["missions"][0]
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_add_multiple_missions(self):
        """Test adding multiple missions."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            sm.add_mission({"goal": "Mission 1"})
            sm.add_mission({"goal": "Mission 2"})
            sm.add_mission({"goal": "Mission 3"})
            
            state = sm.load_state()
            assert len(state["missions"]) == 3
            assert state["missions"][0]["id"] == 1
            assert state["missions"][1]["id"] == 2
            assert state["missions"][2]["id"] == 3
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_get_mission_history(self):
        """Test retrieving mission history."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            for i in range(15):
                sm.add_mission({"goal": f"Mission {i+1}"})
            
            history = sm.get_mission_history(limit=10)
            assert len(history) == 10
            assert history[0]["goal"] == "Mission 6"
            assert history[-1]["goal"] == "Mission 15"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_get_mission_history_empty(self):
        """Test getting mission history when no missions exist."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            history = sm.get_mission_history()
            assert history == []
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_get_last_mission(self):
        """Test getting the last mission."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            sm.add_mission({"goal": "First mission"})
            sm.add_mission({"goal": "Last mission"})
            
            last = sm.get_last_mission()
            assert last is not None
            assert last["goal"] == "Last mission"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_get_last_mission_empty(self):
        """Test getting last mission when no missions exist."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            last = sm.get_last_mission()
            assert last is None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_update_mission_status(self):
        """Test updating a mission's status."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            sm.add_mission({"goal": "Test mission"})
            
            success = sm.update_mission_status(1, "completed", {"output": "success"})
            assert success is True
            
            state = sm.load_state()
            assert state["missions"][0]["status"] == "completed"
            assert state["missions"][0]["result"] == {"output": "success"}
            assert "updated_at" in state["missions"][0]
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_update_mission_status_nonexistent(self):
        """Test updating status of non-existent mission."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            success = sm.update_mission_status(999, "completed")
            assert success is False
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_clear_history(self):
        """Test clearing mission history."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            sm.add_mission({"goal": "Mission 1"})
            sm.add_mission({"goal": "Mission 2"})
            
            success = sm.clear_history()
            assert success is True
            
            state = sm.load_state()
            assert len(state["missions"]) == 0
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_state_last_updated_timestamp(self):
        """Test that last_updated timestamp is updated on save."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            sm = StateManager(file_path=temp_file, encryption_key=None)
            
            test_state = sm.load_state()
            sm.save_state(test_state)
            
            loaded = sm.load_state()
            assert "last_updated" in loaded
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
