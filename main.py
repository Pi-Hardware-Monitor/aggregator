import time
import os

import socketio
from datetime import datetime
import psutil

import clr, json, platform, os

from nvidia.helper import nvidia_utilization, nvidia_temperature

OHM_hwtypes = ['Mainboard', 'SuperIO', 'CPU', 'RAM', 'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'HDD']
OHM_sensortypes = [
    'Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level', 'Factor', 'Power', 'Data', 'SmallData'
]

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


def init_OHM():
    clr.AddReference(os.path.abspath(os.path.dirname(__file__)) + R'\LibreHardwareMonitorLib.dll')

    from LibreHardwareMonitor import Hardware
    hw = Hardware.Computer()

    hw.IsCpuEnabled = True

    hw.Open()
    return hw


def fetch_data(handle):
    out = []
    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            thing = parse_sensor(sensor)
            if thing is not None:
                out.append(thing)
        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                thing = parse_sensor(subsensor)
                out.append(thing)
    return out


def parse_sensor(snsr):
    if snsr.Value is not None:
        if snsr.SensorType == OHM_sensortypes.index('Temperature'):
            HwType = OHM_hwtypes[snsr.Hardware.HardwareType]
            return {"Type": HwType, "Name": snsr.Hardware.Name, "Sensor": snsr.Name, "Reading": u'%s\xb0C' % snsr.Value}


def parse_cpu(raw):
    for data in raw:
        if data.get('Type') == 'CPU':
            if 'AMD' in data.get('Name') and 'Tctl' in data.get('Sensor'):
                return float(data.get('Reading')[:-2])
            else:
                return float(data.get('Reading')[:-2])


sio.connect('http://localhost:4444')

while True:
    sio.emit('memory', {'id': str(datetime.now()), 'usage': psutil.virtual_memory().percent})
    sio.emit('gpu', {'id': str(datetime.now()), 'usage': nvidia_utilization().get('Gpu')[:-2],
                     'temp': nvidia_temperature().get('GPU Current Temp')[:-2],
                     'memory': nvidia_utilization().get('Memory')[:-2]})
    if os.name == 'posix':
        sio.emit('cpu', {'id': str(datetime.now()), 'usage': psutil.cpu_percent(),
                         'temp': psutil.sensors_temperatures().get('k10temp')[
                                     0].current - 10})
    if os.name == 'nt':
        sio.emit('cpu', {'id': str(datetime.now()), 'usage': psutil.cpu_percent(),
                         'temp': parse_cpu(fetch_data(init_OHM()))})
    time.sleep(1)

# sio.wait()
