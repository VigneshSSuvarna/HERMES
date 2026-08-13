import asyncio
from modules.safety_core import HermesSafetyCore
from modules.connectors.system_connector import SystemConnector
from modules.connectors.web_connector import WebConnector
from modules.connectors.office_connector import OfficeConnector
from modules.connectors.gui_connector import GUIConnector

class HermesOrchestrator:
    def __init__(self, brain_module):
        self.is_running = True
        self.brain = brain_module
        self.safety = HermesSafetyCore()
        
        # Load ALL Plugins dynamically
        self.connectors = [
            SystemConnector(), 
            WebConnector(), 
            OfficeConnector(), 
            GUIConnector()
        ]
        
        # Map actions to their respective connectors
        self.action_routing = {}
        for connector in self.connectors:
            for action in connector.get_supported_actions():
                self.action_routing[action] = connector

    def _parse_plan(self, llm_output: str) -> list:
        """Parses the Brain's output into a list of executable actions."""
        plan = []
        for line in llm_output.split('\n'):
            if "COMMAND:" in line and "TARGET:" in line:
                parts = line.split("|")
                action = parts[0].replace("COMMAND:", "").strip().lower()
                target = parts[1].replace("TARGET:", "").strip()
                plan.append({"action": action, "target": target})
        return plan

    async def execute_goal(self, user_goal: str, context: str = ""):
        """Translates natural language to actions and executes them step-by-step."""
        print(f"\n[Orchestrator]: Synthesizing execution plan for: '{user_goal}'")
        
        # ⚡ CRITICAL FIX: Teach the Brain exactly what tools are available
        tool_instructions = """
        You are HERMES's execution planner. Break the user's goal into a strict sequence of commands.
        CRITICAL: You must ONLY choose from these exact action types:
        - type_notepad : Opens Notepad and types the text. (TARGET: the text to type)
        - write_excel : Writes to an Excel file. (TARGET format MUST BE exactly: filepath|cell|value)
        - web_search : Searches DuckDuckGo silently. (TARGET: the search query)
        - scrape_url : Reads text from a webpage. (TARGET: the url)
        - open_website : Opens a website in the default browser. (TARGET: the url)
        - wait : Pauses execution. (TARGET: seconds)
        - open_app : Opens a standard application by name. (TARGET: app name)
        - run_terminal : Runs a powershell command. (TARGET: command)
        """
        
        # 1. Ask the Brain to generate the steps
        prompt = f"{tool_instructions}\nFormat EVERY step as: COMMAND: [action] | TARGET: [value]. Context: {context}. Goal: {user_goal}"
        llm_response = self.brain.think(prompt, max_retries=2) 
        
        plan = self._parse_plan(llm_response)
        if not plan:
            print("[Orchestrator Error]: Failed to generate a valid action plan.")
            return

        print(f"[Orchestrator]: Plan generated with {len(plan)} steps.")
        
        # 2. Step-by-Step Execution Engine
        for i, step in enumerate(plan):
            action = step["action"]
            target = step["target"]
            print(f"\n--- Executing Step {i+1}/{len(plan)}: {action} ---")
            
            # 3. Safety Check
            if not self.safety.validate_action(action, target):
                print("[Orchestrator]: Plan aborted due to safety constraints.")
                break
                
            # 4. Routing & Execution
            connector = self.action_routing.get(action)
            if not connector:
                print(f"[Orchestrator]: No connector found for action '{action}'. Aborting.")
                break
                
            try:
                result = connector.execute(action, target)
                print(f"[Success]: {result}")
                
                # Use ASYNC sleep so the rest of the system doesn't freeze between steps
                await asyncio.sleep(1) 
            except Exception as e:
                print(f"[Execution Failed]: {e}")
                print("[Orchestrator]: Engaging Self-Healing Protocol...")
                break

    async def sensory_input_loop(self):
        """Placeholder for Week 1 Wake-Word (Hermes) and Speech-to-Text."""
        while self.is_running:
            # Short sleep to allow other background tasks to run concurrently
            await asyncio.sleep(0.1) 

    async def core_loop(self):
        """Coordinates communication between internal modules."""
        print("[System]: HERMES Core Neural Pipeline Initialized. Systems Nominal.")
        
        while self.is_running:
            await asyncio.sleep(1)

    async def start(self):
        """Run sensory input and core processing loops concurrently without lag."""
        await asyncio.gather(
            self.core_loop(),
            self.sensory_input_loop()
        )