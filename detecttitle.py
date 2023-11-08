import pygetwindow as gw
import pyautogui

# Function to get the title of the active Chrome browser window
def get_active_chrome_title():
    chrome_windows = [window for window in gw.getWindowsWithTitle("") if "Google Chrome" in window.title]
    if chrome_windows:
        active_window = chrome_windows[0]
        return active_window.title
    else:
        return None

# Example usage
active_chrome_title = get_active_chrome_title()
if active_chrome_title is not None:
    print(f"Active Chrome browser title: {active_chrome_title}")
else:
    print("No active Chrome browser window found.")
# browser_title = "Screen monitoring with Python. - Google Chrome"