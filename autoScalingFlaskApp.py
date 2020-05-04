import psutil
from subprocess import Popen, PIPE
import time

def addServer(port, serverN):
    output = Popen('docker run -d -p '+port+':5000 project-phase-2:latest', shell=True, stdout=PIPE)
    dockerId = output.communicate()[0].decode('utf-8')
    output = Popen('set server flaskAppBackend/docker'+str(serverN)+' addr 127.0.0.1 port '+port, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    output = Popen('set server flaskAppBackend/docker'+str(serverN)+' state ready', shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    return dockerId

def removeServer(port, serverN, dockerId):
    output = Popen('set server flaskAppBackend/docker'+str(serverN)+' state maint', shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    output = Popen('docker stop '+dockerId, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    output = Popen('docker rm '+dockerId, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    pass

# Generating maximum possible list of ports that we can use
dockerPortsList = []
for i in range(1,10):
    dockerPortsList += ['500'+str(i)]
dockerPortsList += ['5010']

# Creating a list than will maintain the ports and Ids of containers that are currently running
dockerPortsInUse = []
dockerIds = []

while(True):
    # Finding CPU load
    cpuUtil = psutil.cpu_percent(interval=5)

    # Finding the number of containers that can exist
    N = int(cpuUtil // 10)
    N = 1 if N < 2 else N
    Nc = len(dockerPortsInUse)

    # Adding Containers if current number of containers are less than the required number
    for i in range( N - Nc ):
        dId = addServer(dockerPortsList[Nc + i], Nc + i + 1)
        dockerIds += [dId]
        dockerPortsInUse += [dockerPortsList[Nc + i]]

    # Removing Containers if current number of containers are greater than the required number
    for i in range( Nc - N ):
        removeServer(dockerPortsInUse[Nc - i - 1], Nc - i, dockerIds[Nc - i - 1])
        del dockerIds[Nc - i - 1]
        del dockerPortsInUse[Nc - i - 1]
    time.sleep(10)

    print('In this iteration ',N-Nc if N-Nc > 0 else 0,'containers were created and ',Nc-N if Nc-N > 0 else 0,'containers were removed')
    print()
