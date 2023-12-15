import win32gui

def get_all_window_titles():
    def callback(hwnd, titles):
        if win32gui.IsWindowVisible(hwnd):
            titles.append(win32gui.GetWindowText(hwnd))

    titles = []
    win32gui.EnumWindows(callback, titles)
    return titles

if __name__ == "__main__":
    window_titles = get_all_window_titles()

    print("Currently active window titles:")
    for title in window_titles:
        print(title)
