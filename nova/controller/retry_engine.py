from nova.controller.parser import PlanParser
from nova.controller.planner import Planner
from nova.database.models import ExecutionResult, Retry
from nova.recovery.failure_classifier import FailureClassifier
from nova.recovery.strategy_engine import StrategyEngine
from nova.utils.tool_normalizer import normalize_tool

MAX_RETRIES = 3


class RetryEngine:
    def __init__(self, db, dispatcher, metrics=None):
        self.db = db
        self.dispatcher = dispatcher
        self.classifier = FailureClassifier()
        self.strategy_engine = StrategyEngine()

        self.planner = Planner(db)  # ✅ Context-aware planner
        self.parser = PlanParser()
        self.metrics = metrics

    def handle_failure(self, db_step, original_step, error_message, session_id):
        retry_count = 0
        tried_strategies = set()  # Track strategies already attempted

        while retry_count < MAX_RETRIES:
            retry_count += 1
            if self.metrics:
                self.metrics.track_retry()

            print(f"\n🔁 Retry Attempt {retry_count}")

            # 1️⃣ Classify the failure type
            failure_type = self.classifier.classify(error_message)
            print(f"📋 Failure Type: {failure_type}")

            # 2️⃣ Get strategy for this failure type
            strategy_step = self.strategy_engine.get_strategy(failure_type, original_step)

            # If strategy exists and hasn't been tried, try it
            if strategy_step and failure_type not in tried_strategies:
                print(f"🛠 Applying strategy for {failure_type}")
                tried_strategies.add(failure_type)

                # Execute strategy step
                strategy_result = self.dispatcher.dispatch(strategy_step, self.metrics)

                if strategy_result and strategy_result.return_code == 0:
                    print("✓ Strategy succeeded. Retrying original step...")

                    # Retry original step after strategy
                    result = self.dispatcher.dispatch(original_step, self.metrics)

                    if result and result.return_code == 0:
                        print("✓ Step fixed successfully after strategy.")
                        return
                    else:
                        # Strategy helped but original still fails
                        error_message = result.stderr if result else "Unknown error"
                        print("⚠ Strategy helped but original step still failed")
                        continue
                else:
                    # Strategy failed, try LLM
                    print("⚠ Strategy failed, falling back to LLM retry...")
                    error_message = strategy_result.stderr if strategy_result else "Strategy execution failed"
            elif strategy_step and failure_type in tried_strategies:
                # Strategy already tried, skip to LLM
                print(f"⏭ Strategy for {failure_type} already attempted, skipping...")

            # 4️⃣ Fallback to LLM-based retry if no strategy or strategy failed
            print("🤖 Using LLM-based retry...")

            # Build fix prompt
            fix_prompt = self._build_fix_prompt(original_step, error_message)

            # Context-aware retry planning
            raw_fix = self.planner.generate_plan(fix_prompt, session_id)

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
            corrected_step["tool"] = normalize_tool(corrected_step.get("tool"))

            # Store retry plan in DB
            retry_entry = Retry(step_id=db_step.id, retry_plan=parsed_fix, retry_number=retry_count)

            self.db.add(retry_entry)
            self.db.commit()

            # Execute corrected step
            result = self.dispatcher.dispatch(corrected_step, self.metrics)

            if result:
                db_result = ExecutionResult(
                    step_id=db_step.id, stdout=result.stdout, stderr=result.stderr, return_code=result.return_code
                )

                self.db.add(db_result)
                self.db.commit()

                print("Retry STDOUT:", result.stdout)
                print("Retry STDERR:", result.stderr)
                print("Retry RETURN CODE:", result.return_code)

                # If fixed, exit retry loop
                if result.return_code == 0:
                    print("Step fixed successfully via LLM retry.")
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
