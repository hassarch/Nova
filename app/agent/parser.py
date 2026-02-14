import json
from app.core.tool_registry import ALLOWED_TOOLS
from app.core.tool_normalizer import normalize_tool


class PlanParser:

    def validate(self, raw_response: str):

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from the response
            import re
            # Look for JSON starting with { and ending with }
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_response, re.DOTALL)
            if json_match:
                try:
                    # Clean up the JSON string - remove control characters
                    json_str = json_match.group()
                    # Remove newlines and extra whitespace within strings
                    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    parsed = json.loads(json_str)
                except json.JSONDecodeError:
                    raise Exception(f"Invalid JSON returned by LLM: {e}")
            else:
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

            # Validate tool-specific required fields
            if step["tool"] == "filesystem":
                if "file_path" not in step:
                    raise Exception("Missing field 'file_path' in filesystem step")
                if "content" not in step:
                    raise Exception("Missing field 'content' in filesystem step")
            elif step["tool"] == "terminal":
                if "command" not in step:
                    raise Exception("Missing field 'command' in terminal step")
            elif step["tool"] == "docker":
                if "command" not in step:
                    raise Exception("Missing field 'command' in docker step")

        return parsed
