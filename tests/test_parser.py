import pytest
from app.agent.parser import PlanParser


class TestPlanParser:
    
    def setup_method(self):
        self.parser = PlanParser()
    
    def test_valid_plan(self):
        """Test parsing a valid plan"""
        raw_response = '''{
            "task_id": "test_task",
            "steps": [
                {
                    "step_id": "step_1",
                    "tool": "terminal",
                    "action": "test action",
                    "command": "echo test",
                    "file_path": null,
                    "content": null
                }
            ]
        }'''
        
        result = self.parser.validate(raw_response)
        assert result["task_id"] == "test_task"
        assert len(result["steps"]) == 1
    
    def test_invalid_json(self):
        """Test parsing invalid JSON"""
        raw_response = "not valid json"
        
        with pytest.raises(Exception, match="Invalid JSON"):
            self.parser.validate(raw_response)
    
    def test_missing_task_id(self):
        """Test parsing plan without task_id"""
        raw_response = '''{
            "steps": []
        }'''
        
        with pytest.raises(Exception, match="Missing task_id"):
            self.parser.validate(raw_response)
    
    def test_missing_steps(self):
        """Test parsing plan without steps"""
        raw_response = '''{
            "task_id": "test"
        }'''
        
        with pytest.raises(Exception, match="Missing steps"):
            self.parser.validate(raw_response)
