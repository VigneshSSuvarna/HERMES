import os
import sys
import asyncio
from modules.ears import HermesEars
from modules.brain import HermesBrain
from modules.automation import HermesHands
from modules.voice import HermesVoice

async def main_loop():
    print("\n==============================================")
    try:
        ears = HermesEars()
        brain = HermesBrain()
        hands = HermesHands()
        voice = HermesVoice()
    except SystemExit:
        print("[Initialization Failed]: Verify environment variables.")
        return

    print("[System]: HERMES Enterprise Asynchronous Matrix Active.")
    print("==============================================\n")
    
    # Run the initial voice greeting within the async framework thread pool
    await asyncio.to_thread(voice.speak, "All systems are fully operational, Sir. Matrix synchronized.")

    while True:
        try:
            # Yield loop execution control cleanly to background threads to catch voice chunks
            user_input = await asyncio.to_thread(ears.listen)
            
            if not user_input:
                await asyncio.sleep(0.01)
                continue

            print(f"\nUser (Spoken): {user_input}")

            if "shutdown hermes" in user_input.lower() or "exit system" in user_input.lower():
                await asyncio.to_thread(voice.speak, "Disconnecting terminal matrices. Goodbye, Sir.")
                break

            raw_response = await asyncio.to_thread(brain.think, user_input)
            
            if "COMMAND:" in raw_response:
                try:
                    lines = raw_response.split("\n")
                    cmd_line = [l for l in lines if "COMMAND:" in l][0]
                    
                    parts = cmd_line.replace("COMMAND:", "").split("|")
                    action_type = parts[0].strip()
                    target_value = parts[1].replace("TARGET:", "").strip()
                    
                    execution_result = await asyncio.to_thread(hands.execute_system_command, action_type, target_value)
                    await asyncio.to_thread(voice.speak, execution_result)
                except Exception as parse_error:
                    print(f"HERMES Parsing Error: {parse_error}")
            else:
                await asyncio.to_thread(voice.speak, raw_response)
                
        except Exception as loop_error:
            print(f"[Loop Exception]: {loop_error}")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nTerminating structural background loops, Sir.")