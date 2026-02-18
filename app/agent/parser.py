import json

from app.core.tool_normalizer import normalize_tool
from app.core.tool_registry import ALLOWED_TOOLS


class PlanParser:
    def validate(self, raw_response: str):
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response using bracket matching
            # Find the first opening brace
            start_idx = raw_response.find("{")
            if start_idx == -1:
                raise Exception(f"Invalid JSON returned by LLM: {e}")

            # Match braces to find the complete JSON object
            brace_count = 0
            end_idx = -1
            for i in range(start_idx, len(raw_response)):
                if raw_response[i] == "{":
                    brace_count += 1
                elif raw_response[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            if end_idx == -1:
                raise Exception(f"Invalid JSON returned by LLM: {e}")

            json_str = raw_response[start_idx:end_idx]

            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError as parse_error:
                raise Exception(f"Invalid JSON returned by LLM: {parse_error}")

        # -------------------------
        # Validate top-level keys
        # -------------------------

        if "task_id" not in parsed:
            raise Exception("Missing task_id in LLM response")

        # -------------------------
        # Backward Compatibility
        # -------------------------

        # If flat plan detected, wrap into one subtask
        if "steps" in parsed and "subtasks" not in parsed:
            parsed = {
                "task_id": parsed.get("task_id"),
                "goal": "Auto-wrapped flat plan",
                "message": parsed.get("message"),
                "subtasks": [{"objective": "Single-step task", "steps": parsed["steps"]}],
            }

        # -------------------------
        # Validate hierarchical format
        # -------------------------

        if "subtasks" not in parsed:
            raise Exception("Missing 'subtasks' in LLM response")

        if not isinstance(parsed["subtasks"], list):
            raise Exception("'subtasks' must be a list")

        for subtask in parsed["subtasks"]:
            if "objective" not in subtask:
                raise Exception("Each subtask must have an 'objective'")

            if "steps" not in subtask:
                raise Exception("Each subtask must contain 'steps'")

            if not isinstance(subtask["steps"], list):
                raise Exception("'steps' must be a list inside each subtask")

            # -------------------------
            # Validate each step
            # -------------------------

            for step in subtask["steps"]:
                required_fields = [
                    "step_id",
                    "tool",
                    "action",
                ]

                for field in required_fields:
                    if field not in step:
                        raise Exception(f"Missing field '{field}' in step")

                step["tool"] = normalize_tool(step["tool"])

                if step["tool"] not in ALLOWED_TOOLS:
                    raise Exception(f"Invalid tool '{step['tool']}'. " f"Allowed tools: {ALLOWED_TOOLS}")

                # Tool-specific validation
                if step["tool"] == "filesystem":
                    if "file_path" not in step:
                        raise Exception("Missing 'file_path' in filesystem step")
                    # Ensure content exists (can be empty string)
                    if "content" not in step:
                        step["content"] = ""

                elif step["tool"] == "terminal":
                    if "command" not in step:
                        raise Exception("Missing 'command' in terminal step")

                elif step["tool"] == "docker":
                    if "command" not in step:
                        raise Exception("Missing 'command' in docker step")

        return parsed
