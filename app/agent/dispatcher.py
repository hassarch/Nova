class ToolDispatcher:

    def dispatch(self, plan: dict):
        for step in plan["steps"]:
            print(f"Dispatching step {step['step_id']} using tool {step['tool']}")
