import socketio
import os
import subprocess
import time
import psutil
import threading
#from __future__ import print_function
import pyautogui
from config import SERVER_URL, HOST_TOKEN
from lock import create_lockscreen
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops

def unlock_device():
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.write('2424')  

sio = socketio.Client()
login_token = HOST_TOKEN


@sio.event
def connect():
    print("== Server Connected ==")
    print("beginning [HOST] connection")
    sio.emit('login', {'type': 'HOST', 'token': login_token, 'name': os.environ['COMPUTERNAME']})

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.event
def loggedIn(data):
    if data['status'] == 'OK':
        print("!= HOST CONNECTION ESTABLISHED - NETWORK COMPLETE =!")
        #pyautogui.alert(text='This computer is currently connected to the [HOST] network. Normal user privileges are given.', title='Connection Established', button='OK')
        while True:
            cpu = psutil.cpu_percent()
            mem =  psutil.virtual_memory()[2]
            locked = False
            for x in pyautogui.getAllWindows():  
                if x.title == "LOGIN UI":
                    locked = True
            fdesktops = []
            for desktop in get_virtual_desktops():
                #if desktop.id == VirtualDesktop.current().id:
                payload = {
                    #'id': desktop.id,
                    'name': desktop.name,
                    "active": desktop.id == VirtualDesktop.current().id
                }
                fdesktops.append(payload)
            sio.emit('computerUpdate', {'cpu': cpu, 'mem': mem, 'locked': locked, 'desktops': fdesktops})
            time.sleep(3)
@sio.event
def evaluate(data):
    def switchDesktop(name):
        for desktop in get_virtual_desktops():
            if desktop.name == name:
                desktop.go()
                break
    mousePos = pyautogui.position()
    def moveLeft(px):
        res = mousePos[0] - px
        if res > 0:
            pyautogui.moveTo(res, mousePos[1], 0.5)
    def moveRight(px):
        res = mousePos[0] + px
        if res < pyautogui.size()[0]:
            pyautogui.moveTo(res, mousePos[1], 0.5)
    def moveUp(px):
        res = mousePos[1] - px
        if res > 0:
            pyautogui.moveTo(mousePos[0], res, 0.5)
    def moveDown(px):
        res = mousePos[1] + px
        if res < pyautogui.size()[1]:
            pyautogui.moveTo(mousePos[0], res, 0.5)
    def lock_device():
        #switchDesktop('Lockscreen')
        os.system('python lock.py')
        #while True:
        #    record = False
        #    for x in pyautogui.getAllWindows():  
        #        if x.title == "LOGIN UI":
        #            record = True
        #    if record:
        #        break
        #    time.sleep(0.5)
        #pyautogui.hotkey('win', 'ctrl', 't')
        #pyautogui.click()
    try:
        result = eval(data.get('content'))
        #print(result)
        sio.emit('evaluated', {"content": data.get('content'), 'result': result})
    except Exception as e:
        print(str(e))
        sio.emit('evaluated', {"content": data.get('content'), 'result': str(e), 'error': True})
sio.connect(SERVER_URL)