import time
from google.genai import types
from modules.tools import execute_python_code

class HermesPlanner:
    def __init__(self, client):
        self.client = client
        # Defining primary and backup models to bypass quota locks
        self.models_to_try = ["gemini-2.0-flash", "gemini-flash-latest"]

    def run_multi_step_plan(self, high_level_goal: str) -> str:
        """
        Single-Shot Synthesis with Auto-Fallback: 
        Instructs Gemini to write a self-contained Python script to solve the goal.
        If the primary model is rate-limited, it automatically routes to the backup model.
        """
        print(f"\n[Planner Agent]: Initializing Single-Shot Synthesis for: '{high_level_goal}'...")
        
        if not self.client:
            return "Sir, cloud API client is offline. Cannot execute autonomous plan."

        prompt = (
            "You are HERMES, an advanced Autonomous Desktop OS Agent addressing the user as 'Sir'.\n"
            "The user has given a complex multi-step workflow. Instead of multi-turn tool calling, "
            "you must write a complete, self-contained Python script using standard libraries (like 'urllib.request', 'json', 'math') "
            "that accomplishes the entire goal from start to finish, prints the final answer clearly, and handles its own logic.\n"
            "CRITICAL: Output ONLY valid executable Python code inside standard markdown triple backticks (```python ... ```). "
            "Do not include conversational filler outside the code block."
            f"\n\nUser Goal: {high_level_goal}"
        )

        for model_name in self.models_to_try:
            try:
                print(f"[Planner Agent]: Attempting synthesis using neural pathway '{model_name}'...")
                
                # Exactly 1 API call - highly efficient!
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                
                if not response or not response.text:
                    print(f"[Planner Warning]: No response from '{model_name}'.")
                    continue

                text = response.text.strip()
                print("[Planner Agent]: Script synthesized successfully. Extracting code block...")

                # Extract python code block from response
                code = ""
                if "```python" in text:
                    parts = text.split("```python")
                    if len(parts) > 1:
                        code = parts[1].split("```")[0].strip()
                elif "```" in text:
                    parts = text.split("```")
                    if len(parts) > 1:
                        code = parts[1].split("```")[0].strip()
                else:
                    code = text 

                if not code:
                    return f"Sir, synthesis response received but no executable code block was found:\n{text}"

                print(f"[Planner Agent]: Executing synthesized script locally in sandbox...")
                execution_result = execute_python_code(code)
                
                return f"Autonomous Plan Executed via Single-Shot Synthesis, Sir.\n\nExecution Output:\n{execution_result}"

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"\n[Planner Quota Notice]: Google locked pathway '{model_name}'.")
                    
                    if model_name == self.models_to_try[-1]:
                        return "Sir, free-tier rate limits have been hit across all available neural models. We must wait for the quota to reset."
                    
                    print("[Planner Agent]: Automatically rerouting to backup neural pathway...")
                    time.sleep(1)
                    continue
                else:
                    print(f"\n[Planner Error]: {err_str}\n")
                    return f"Sir, the autonomous planner encountered an exception: {e}"

        return "Sir, the planner was unable to complete the synthesis."