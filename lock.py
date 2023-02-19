import threading
import time
import sys
import random
import webview
import pyautogui
import pyvda
import subprocess
authorized = False

def switchDesktop(name):
        for desktop in pyvda.get_virtual_desktops():
            if desktop.name == name:
                desktop.go()
                break

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window
    def unlock(self, pin):
        global authorized
        if pin == "2424":
            authorized = True
            switchDesktop("Main")
            self._window.destroy()
            return {'message': 'SUCCESS'}
        else:
            return {'message': 'INVALID'}
    def toggle_fullscreen(self):
        #self._window.show()
        pyautogui.hotkey('win', 'ctrl', 't')
        #pyautogui.click()
        self._window.toggle_fullscreen()

    def sleep_computer(self):
        subprocess.call('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')

    def shutdown_computer(self):
        subprocess.run(["shutdown", "-s"])


def create_lockscreen():
    api = Api()
    size = pyautogui.size()
    while True:
        global authorized
        if not authorized:
            window = webview.create_window('LOGIN UI', background_color="#000", min_size=size, text_select=False, on_top =True, url="http://localhost:3000/lockscreen", js_api=api)
            api.set_window(window)
            def alwaysOntop():
                switchDesktop("Lockscreen")
            webview.start(alwaysOntop(), debug=False)
        else:
            break
if __name__ == '__main__':
    create_lockscreen()