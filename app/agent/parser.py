import json
from app.core.tool_registry import ALLOWED_TOOLS
from app.core.tool_normalizer import normalize_tool


class PlanParser:

    def validate(self, raw_response: str):

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON returned by LLM: {e}")

        # Validate top-level keys
        if "task_id" not in parsed:
            raise Exception("Missing task_id in LLM response")

        if "steps" not in parsed:
            raise Exception("Missing steps in LLM response")

        if not isinstance(parsed["steps"], list):
            raise Exception("Steps must be a list")

        # Validate each step
        for step in parsed["steps"]:

            required_fields = [
                "step_id",
                "tool",
                "action",
                "command",
                "file_path",
                "content"
            ]

            for field in required_fields:
                if field not in step:
                    raise Exception(f"Missing field '{field}' in step")

            step["tool"] = normalize_tool(step["tool"])
            if step["tool"] not in ALLOWED_TOOLS:
                raise Exception(
                    f"Invalid tool '{step['tool']}'. "
                    f"Allowed tools: {ALLOWED_TOOLS}"
                )

        return parsed
