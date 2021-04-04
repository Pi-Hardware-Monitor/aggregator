import socketio
from datetime import datetime
import psutil

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('cpuUsage', {'id': str(datetime.now()), 'type':'USAGE' ,'value':data})

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:4444')

for i in range(100):
    my_message(psutil.cpu_percent(interval=1))

sio.wait()
