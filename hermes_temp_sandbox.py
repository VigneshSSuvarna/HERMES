import pyautogui
import time
import os

def minimize_window():
    pyautogui.keyDown('win')
    pyautogui.press('down')
    pyautogui.keyUp('win')

def open_notepad():
    os.system('notepad.exe')

def main():
    minimize_window()
    time.sleep(1)
    open_notepad()
    print('Window minimized and Notepad opened, Sir.')

if __name__ == '__main__':
    main()