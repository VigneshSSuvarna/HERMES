from modules.automation import HermesHands
import time

hands = HermesHands()

print("--- TESTING OS AUTOMATION ---")
time.sleep(1)

print("1. Opening Notepad...")
print(hands.execute_action("open_app", "notepad"))
time.sleep(2)

print("2. Adjusting Volume Up...")
print(hands.execute_action("volume_up"))
time.sleep(1)

print("3. Opening YouTube...")
print(hands.execute_action("open_website", "https://www.youtube.com"))

print("--- TEST COMPLETE ---")