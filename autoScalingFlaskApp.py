import psutil
from subprocess import Popen, PIPE
import time

HAproxyCommandPart1 = 'echo "set server flaskAppBackend/docker'
HAproxyCommandPart2 = '" | socat stdio tcp4-connect:127.0.0.1:9999'

def addServer(serverN):
    output = Popen('docker run -d project-phase-2:latest', shell=True, stdout=PIPE)
    dockerId = output.communicate()[0].decode('utf-8')
    output = Popen('docker inspect -f "{{ .NetworkSettings.IPAddress }}" '+dockerId, shell=True, stdout=PIPE)
    dockerIP = output.communicate()[0].decode('utf-8')
    output = Popen(HAproxyCommandPart1 + serverN + ' addr ' + dockerIP + HAproxyCommandPart2, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    output = Popen(HAproxyCommandPart1 + serverN + ' state ready' + HAproxyCommandPart2, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    return dockerId

def removeServer(dockerId, serverN):
    output = Popen(HAproxyCommandPart1 + serverN + ' state maint' + HAproxyCommandPart2, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    output = Popen('docker stop '+dockerId, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    output = Popen('docker rm '+dockerId, shell=True, stdout=PIPE)
    output = output.communicate()[0].decode('utf-8')
    pass

# Creating a list than will maintain the docker numbers and Ids of containers that are currently running
dockersInUse = []
dockerIds = []

while(True):
    # Finding CPU load
    cpuUtil = psutil.cpu_percent(interval=1)

    # Finding the number of containers that can exist
    N = int(cpuUtil // 10)
    N = 1 if N < 2 else N
    Nc = len(dockersInUse)

    # Adding Containers if current number of containers are less than the required number
    for i in range( N - Nc ):
        dId = addServer(str(Nc + i + 1))
        dockerIds += [dId]
        dockersInUse += [Nc + i + 1]

    # Removing Containers if current number of containers are greater than the required number
    for i in range( Nc - N ):
        removeServer(dockerIds[Nc - i - 1], str(Nc - i))
        del dockerIds[Nc - i - 1]
        del dockersInUse[Nc - i - 1]
    time.sleep(5)

    print('In this iteration ',N-Nc if N-Nc > 0 else 0,'containers were created and ',Nc-N if Nc-N > 0 else 0,'containers were removed')
    print()
