import os
import subprocess
import traceback

class HermesAgent:
    def __init__(self, brain):
        self.brain = brain
        self.sandbox_dir = "sandbox"
        os.makedirs(self.sandbox_dir, exist_ok=True)
        print("[Agent]: Universal Autonomous Script Synthesizer Initialized.")

    def execute_task(self, user_goal: str) -> str:
        print(f"[Agent]: Synthesizing execution plan for goal: '{user_goal}'")
        
        prompt = (
            f"You are a strict, silent code-generating compiler. The user wants to accomplish this goal: '{user_goal}'.\n"
            f"Write a complete, self-contained Python script to accomplish this using standard libraries (os, shutil, datetime, glob, etc.).\n"
            f"CRITICAL RULES:\n"
            f"1. Output ONLY valid, executable Python code.\n"
            f"2. DO NOT output any conversational text, greetings, or explanations whatsoever.\n"
            f"3. Wrap the code in standard ```python ... ``` markdown blocks.\n"
            f"4. If you need to output a status message, use standard Python print() statements."
        )
        
        response = self.brain.think(prompt)
        code = self._extract_code(response)
        
        if not code or len(code) < 10:
            return "Agent failed to synthesize a valid code script, Sir."

        script_path = os.path.join(self.sandbox_dir, "dynamic_task.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        max_retries = 2
        attempt = 0
        while attempt <= max_retries:
            try:
                print(f"[Agent Sandbox]: Running script (Attempt {attempt + 1})...")
                res = subprocess.run(["python", script_path], capture_output=True, text=True, timeout=60)
                
                if res.returncode == 0:
                    output = res.stdout.strip()
                    return f"SUCCESS. Output:\n{output if output else 'Autonomous Plan Executed, Sir.'}"
                else:
                    raise Exception(res.stderr.strip())
                    
            except Exception as e:
                attempt += 1
                err_trace = str(e)
                print(f"[Agent Error]: Script crashed: {err_trace}")
                
                if attempt > max_retries:
                    return f"Agent execution failed permanently after {max_retries} healing attempts. Error: {err_trace}"

                print("[Agent Watchdog]: Engaging Self-Healing Patch...")
                
                healing_prompt = (
                    f"This Python script crashed:\n\n```python\n{code}\n```\n\n"
                    f"It threw this error:\n{err_trace}\n\n"
                    f"Fix the bug. Output ONLY the corrected Python code inside a ```python ... ``` block. DO NOT include any conversational text."
                )
                
                fix_response = self.brain.think(healing_prompt)
                code = self._extract_code(fix_response)
                
                if code:
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(code)

    def _extract_code(self, text: str) -> str:
        """Regex-Free Code Extraction to prevent syntax errors."""
        extracted = text.strip()
        
        if "```python" in extracted:
            parts = extracted.split("```python")
            if len(parts) > 1:
                extracted = parts[1].split("```")[0].strip()
        elif "```" in extracted:
            parts = extracted.split("```")
            if len(parts) > 1:
                extracted = parts[1].strip()
        
        # BULLETPROOF CHECK: If it doesn't have basic Python keywords, it's not code!
        if not any(kw in extracted for kw in ["import ", "def ", "print(", "os."]):
            return "" # Returning empty forces the system to say "failed to synthesize" instead of crashing
            
        return extracted