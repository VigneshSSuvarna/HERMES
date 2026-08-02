from modules.automation import HermesHands
import time

hands = HermesHands()

print("--- TESTING OS AUTOMATION ---")
time.sleep(1)

print("1. Testing Volume (You should see/hear volume go up)...")
print(hands.execute_action("volume_up", ""))
time.sleep(2)

print("2. Testing App Launcher (Opening Notepad)...")
print(hands.execute_action("open_app", "notepad"))

print("--- TEST COMPLETE ---")