import os
import sys
from modules.ears import HermesEars
from modules.brain import HermesBrain
from modules.automation import HermesHands
from modules.voice import HermesVoice

def main():
    print("\n==============================================")
    try:
        ears = HermesEars()
        brain = HermesBrain()
        hands = HermesHands()
        voice = HermesVoice()
    except SystemExit:
        print("[Initialization Failed]: Verify environment keys.")
        return

    print("[System]: HERMES Fully Autonomous Voice Matrix Online.")
    print("==============================================\n")
    
    voice.speak("All systems are fully operational, Sir. I am listening.")

    while True:
        try:
            # 👂 Step 1: Streams real-time audio through your mic array instead of typing
            user_input = ears.listen()
            
            if not user_input:
                continue

            print(f"\nUser (Spoken): {user_input}")

            if "shutdown hermes" in user_input.lower() or "exit system" in user_input.lower():
                voice.speak("Disconnecting terminal matrices. Goodbye, Sir.")
                break

            # 🧠 Step 2: Cognition Processing Engine
            raw_response = brain.think(user_input)
            
            # ⚙️ Step 3: Structured System Macro Parser
            if "COMMAND:" in raw_response:
                try:
                    lines = raw_response.split("\n")
                    cmd_line = [l for l in lines if "COMMAND:" in l][0]
                    
                    parts = cmd_line.replace("COMMAND:", "").split("|")
                    action_type = parts[0].strip()
                    target_value = parts[1].replace("TARGET:", "").strip()
                    
                    # 🚀 Step 4: Execute Operating System Instruction
                    execution_result = hands.execute_system_command(action_type, target_value)
                    voice.speak(execution_result)
                except Exception as parse_error:
                    print(f"HERMES Parsing Error: {parse_error}")
            else:
                # 🔊 Step 5: Vocal Response Feedback
                voice.speak(raw_response)
                
        except KeyboardInterrupt:
            print("\nTerminating structural background loops, Sir.")
            break

if __name__ == "__main__":
    main()