import time

import socketio
from datetime import datetime
import psutil

from nvidia.helper import nvidia_utilization, nvidia_temperature

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('cpuUsage', {'id': str(datetime.now()), 'type': 'USAGE', 'value': data})


@sio.event
def disconnect():
    print('disconnected from server')


sio.connect('http://localhost:4444')

# my_message(psutil.cpu_percent(interval=1))
# sio.emit('cpuUsage', {'id': str(datetime.now()), 'type': 'USAGE', 'value': psutil.cpu_percent()})
# print(nvidia_temperature())
while True:
    sio.emit('cpu', {'id': str(datetime.now()), 'usage': psutil.cpu_percent(), 'temp': psutil.sensors_temperatures().get('k10temp')[0].current - 10})  # ryzxen 2700x minus offset
    sio.emit('memory', {'id': str(datetime.now()), 'usage': psutil.virtual_memory().percent})
    sio.emit('gpu', {'id': str(datetime.now()), 'usage': nvidia_utilization().get('Gpu')[:-2], 'temp': nvidia_temperature().get('GPU Current Temp')[:-2], 'memory': nvidia_utilization().get('Memory')[:-2]})
    time.sleep(1)

# sio.wait()
