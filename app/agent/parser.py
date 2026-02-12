import json


class PlanParser:

    def validate(self, raw_response: str):

        print("\nRAW LLM RESPONSE:\n", raw_response)

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON returned by LLM: {e}")

        if "task_id" not in parsed:
            raise Exception("Missing task_id in LLM response")

        if "steps" not in parsed:
            raise Exception("Missing steps in LLM response")

        return parsed
