from app.agent.planner import Planner
from app.agent.parser import PlanParser
from app.database.models import Retry, ExecutionResult
from app.core.tool_normalizer import normalize_tool


MAX_RETRIES = 3


class RetryEngine:

    def __init__(self, db, dispatcher):
        self.db = db
        self.dispatcher = dispatcher
        self.planner = Planner(db)  # ✅ Context-aware planner
        self.parser = PlanParser()

    def handle_failure(self, db_step, original_step, error_message, session_id):

        retry_count = 0

        while retry_count < MAX_RETRIES:

            retry_count += 1
            print(f"\n🔁 Retry Attempt {retry_count}")

            # Build fix prompt
            fix_prompt = self._build_fix_prompt(original_step, error_message)

            # 🔥 Context-aware retry planning
            raw_fix = self.planner.generate_plan(
                fix_prompt,
                session_id
            )

            try:
                parsed_fix = self.parser.validate(raw_fix)
            except Exception as e:
                print("Retry validation failed:", e)
                continue

            # Ensure steps exist
            if not parsed_fix.get("steps"):
                print("No steps returned in retry.")
                continue

            # Take first corrected step
            corrected_step = parsed_fix["steps"][0]

            # Normalize tool name
            corrected_step["tool"] = normalize_tool(
                corrected_step.get("tool")
            )

            # Store retry plan in DB
            retry_entry = Retry(
                step_id=db_step.id,
                retry_plan=parsed_fix,
                retry_number=retry_count
            )

            self.db.add(retry_entry)
            self.db.commit()

            # Execute corrected step
            result = self.dispatcher.dispatch(corrected_step)

            if result:
                db_result = ExecutionResult(
                    step_id=db_step.id,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.return_code
                )

                self.db.add(db_result)
                self.db.commit()

                print("Retry STDOUT:", result.stdout)
                print("Retry STDERR:", result.stderr)
                print("Retry RETURN CODE:", result.return_code)

                # If fixed, exit retry loop
                if result.return_code == 0:
                    print("Step fixed successfully.")
                    return

                # Update error message for next retry
                error_message = result.stderr

        print("Step failed after max retries.")

    def _build_fix_prompt(self, original_step, error_message):

        return f"""
The following execution step failed:

Tool: {original_step.get('tool')}
Action: {original_step.get('action')}
Command: {original_step.get('command')}
File Path: {original_step.get('file_path')}

Error Output:
{error_message}

Provide ONE corrected step in strict JSON format.
Return ONLY valid JSON.
"""
