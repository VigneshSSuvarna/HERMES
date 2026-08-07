import time
from modules.tools import execute_python_code

class HermesPlanner:
    def __init__(self, client):
        self.client = client
        # Groq high-speed LPU models
        self.models_to_try = ["llama-3.3-70b-versatile"]

    def run_multi_step_plan(self, high_level_goal: str) -> str:
        """
        Single-Shot Synthesis with Auto-Fallback: 
        Instructs Groq to write a self-contained Python script to solve the goal,
        distinguishing between 'Just Search' and 'Search & Play' for YouTube.
        """
        print(f"\n[Planner Agent]: Initializing Single-Shot Synthesis for: '{high_level_goal}'...")
        
        if not self.client:
            return "Sir, cloud API client is offline. Cannot execute autonomous plan."

        prompt = (
            "You are HERMES, an advanced Autonomous Desktop OS Agent addressing the user as 'Sir'.\n"
            "The user has given a workflow. You must write a complete, self-contained Python script to accomplish it.\n\n"
            "--- CRITICAL YOUTUBE PROTOCOLS ---\n"
            "SCENARIO A - ONLY SEARCHING: If the user just asks to 'search' for something on YouTube (without asking to play it), simply open the search results:\n"
            "```python\n"
            "import webbrowser, urllib.parse\n"
            "query = urllib.parse.quote('SEARCH_QUERY_HERE')\n"
            "webbrowser.open('[https://www.youtube.com/results?search_query=](https://www.youtube.com/results?search_query=)' + query)\n"
            "print('YouTube search opened, Sir.')\n"
            "```\n\n"
            "SCENARIO B - SEARCH AND PLAY: If the user explicitly asks to 'play' a video, silently scrape YouTube and open the video directly:\n"
            "```python\n"
            "import urllib.request, urllib.parse, re, webbrowser\n"
            "query_string = urllib.parse.quote('SEARCH_QUERY_HERE')\n"
            "url = '[https://www.youtube.com/results?search_query=](https://www.youtube.com/results?search_query=)' + query_string\n"
            "req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})\n"
            "html_content = urllib.request.urlopen(req).read().decode()\n"
            "video_ids = re.findall(r'watch\\?v=(\\S{11})', html_content)\n"
            "if video_ids:\n"
            "    webbrowser.open('[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)' + video_ids[0])\n"
            "    print('Video playing, Sir.')\n"
            "```\n\n"
            "CRITICAL: Output ONLY valid executable Python code inside standard markdown triple backticks (```python ... ```). "
            "Do not include conversational filler outside the code block."
            f"\n\nUser Goal: {high_level_goal}"
        )

        for model_name in self.models_to_try:
            try:
                print(f"[Planner Agent]: Attempting synthesis using Groq neural pathway '{model_name}'...")
                
                completion = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are HERMES Autonomous Task Synthesizer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=2048
                )
                
                if not completion or not completion.choices or not completion.choices[0].message.content:
                    print(f"[Planner Warning]: No response from '{model_name}'.")
                    continue

                text = completion.choices[0].message.content.strip()
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
                
                return f"Autonomous Plan Executed, Sir.\n\nExecution Output:\n{execution_result}"

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"\n[Planner Quota Notice]: Groq rate limit hit on '{model_name}'.")
                    time.sleep(2.0)
                    continue
                else:
                    print(f"\n[Planner Error]: {err_str}\n")
                    return f"Sir, the autonomous planner encountered an exception: {e}"

        return "Sir, the planner was unable to complete the synthesis."