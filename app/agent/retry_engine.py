from app.agent.planner import Planner
from app.agent.parser import PlanParser
from app.database.models import Retry, ExecutionResult
from app.core.tool_normalizer import normalize_tool


MAX_RETRIES = 3


class RetryEngine:

    def __init__(self, db, dispatcher, metrics=None):
        self.db = db
        self.dispatcher = dispatcher
        self.planner = Planner()
        self.parser = PlanParser()
        self.metrics = metrics

    def handle_failure(self, db_step, original_step, error_message):

        retry_count = 0

        while retry_count < MAX_RETRIES:

            retry_count += 1
            if self.metrics:
                self.metrics.track_retry()

            print(f"\n Retry Attempt {retry_count}")

            fix_prompt = self._build_fix_prompt(original_step, error_message)

            raw_fix = self.planner.generate_plan(fix_prompt)

            try:
                parsed_fix = self.parser.validate(raw_fix)
            except Exception as e:
                print("Retry validation failed:", e)
                continue

            # Take first corrected step
            corrected_step = parsed_fix["steps"][0]

            corrected_step["tool"] = normalize_tool(corrected_step["tool"])

            # Store retry plan
            retry_entry = Retry(
                step_id=db_step.id,
                retry_plan=parsed_fix,
                retry_number=retry_count
            )

            self.db.add(retry_entry)
            self.db.commit()

            # Execute corrected step
            result = self.dispatcher.dispatch(corrected_step, self.metrics)

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

                if result.return_code == 0:
                    print("Step fixed successfully.")
                    return

                error_message = result.stderr

        print("Step failed after max retries.")

    def _build_fix_prompt(self, original_step, error_message):

        return f"""
The following step failed:

Tool: {original_step['tool']}
Command: {original_step['command']}

Error:
{error_message}

Provide a corrected single step in strict JSON format.
Return only JSON.
"""
