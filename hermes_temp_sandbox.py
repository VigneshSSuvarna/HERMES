import re

def correct_target(target):
    # Remove any non-alphanumeric characters
    corrected_target = re.sub(r'[^a-zA-Z0-9]', '', target)
    
    # Remove any extra words that are not part of the process name
    keywords = ["Autonomous", "Plan", "Executed", "Sir", "Execution", "Output", "SUCCESS"]
    for keyword in keywords:
        corrected_target = corrected_target.replace(keyword, "")
        
    # Remove any leading or trailing whitespace
    corrected_target = corrected_target.strip()
    
    return corrected_target

target = "Autonomous Plan Executed, Sir. Execution Output: SUCCESS. Output: chrome"
corrected_target = correct_target(target)

print(corrected_target)