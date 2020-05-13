import psutil, time, threading
from subprocess import Popen, PIPE

class AutoScaleContainers(object):
    """
    AutoScaleContainers object that auto-scales a docker container based on cpu load.
    In other words, the number of container increases and decreases based on cpu load.

    containerName: str
        The name of container that you need to auto scale.
        default value is "project-phase-2:latest".

    waitPeriod: int
        The time period between two checks of cpu load.
        default value is '5' seconds.

    haproxyCfgFile: str
        Name of HAproxy configuration file containing the configuration for load balancer of application.
        default value is "flaskAppLBhaproxy".
    """
    def __init__(self, containerName='project-phase-2:latest', waitPeriod=5, haproxyCfgFile='flaskAppLBhaproxy'):
        self.containerName = containerName
        self.waitPeriod = waitPeriod
        self.haproxyCfgFile = haproxyCfgFile
        self.__maxSize = 0
        self.__HAproxyCommandPart1 = 'echo "set server '
        with open(self.haproxyCfgFile + '.cfg', 'r') as f:
            for l in f:
                if 'default_backend' in l:
                    self.__HAproxyCommandPart1 = self.__HAproxyCommandPart1 + l[20:-1] + '/docker'
                if 'server docker' in l:
                    self.__maxSize += 1
        self.__HAproxyCommandPart2 = '" | socat stdio tcp4-connect:127.0.0.1:9999'
        # Creating a list than will maintain the docker numbers and Ids of containers that are currently running
        self.dockersInUse = []
        self.dockerIds = []
        pass

    def __addServer(self, serverN) -> str:
        '''
        This function starts a new container.
        After starting the container it sets the IP address of dockerx with the IP address of newly started container, and change state of dockerx to be ready.
        (Here x in dockerx is replaced by serverN passed as argument to function)
        '''
        # Starting the container
        output = Popen('docker run -d ' + self.containerName, shell=True, stdout=PIPE)
        dockerId = output.communicate()[0].decode('utf-8')
        # Extracting IP address of newly started container
        output = Popen('docker inspect -f "{{ .NetworkSettings.IPAddress }}" ' + dockerId, shell=True, stdout=PIPE)
        dockerIP = output.communicate()[0].decode('utf-8')
        # set IP address of dockerx (where x = serverN) to IP address of the container
        output = Popen(self.__HAproxyCommandPart1 + serverN + ' addr ' + dockerIP + self.__HAproxyCommandPart2, shell=True, stdout=PIPE)
        output.communicate()
        # change state of dockerx to ready
        output = Popen(self.__HAproxyCommandPart1 + serverN + ' state ready' + self.__HAproxyCommandPart2, shell=True, stdout=PIPE)
        output.communicate()
        return dockerId

    def __removeServer(self, dockerId, serverN) -> None:
        '''
        This function stops and removes the container with the given dockerID.
        Before removing the container it changes state of dockerx to be maint (maintenance).
        (Here x in dockerx is replaced by serverN passed as argument to function)
        '''
        # change state of dockerx to maint
        output = Popen(self.__HAproxyCommandPart1 + serverN + ' state maint' + self.__HAproxyCommandPart2, shell=True, stdout=PIPE)
        output.communicate()
        # Stop the container with the given dockerID
        output = Popen('docker stop ' + dockerId, shell=True, stdout=PIPE)
        output.communicate()
        # Remove the container with the given dockerID
        output = Popen('docker rm ' + dockerId, shell=True, stdout=PIPE)
        output.communicate()
        pass

    def __runHAproxyConfig(self, cfgFileName) -> None:
        '''
        This function starts the HAproxy load blancer with the configurations given in the file provided as input.
        '''
        output = Popen('haproxy -- ' + cfgFileName + '.cfg', shell=True, stdout=PIPE)
        output.communicate()
        pass

    def start(self) -> None:
        # Start HAproxy Load Balancer
        haproxyThread = threading.Thread(target=self.__runHAproxyConfig, args=(self.haproxyCfgFile,))
        haproxyThread.start()

        while(True):
            # Finding CPU load
            cpuUtil = psutil.cpu_percent(interval=1)

            # Finding the number of containers that can exist
            N = int(cpuUtil // 10)
            N = 1 if N < 2 else N if N < self.__maxSize else self.__maxSize
            Nc = len(self.dockersInUse)

            # Adding Containers if current number of containers are less than the required number
            for i in range( N - Nc ):
                dId = self.__addServer(str(Nc + i + 1))
                self.dockerIds += [dId]
                self.dockersInUse += [Nc + i + 1]

            # Removing Containers if current number of containers are greater than the required number
            for i in range( Nc - N ):
                self.__removeServer(self.dockerIds[Nc - i - 1], str(Nc - i))
                del self.dockerIds[Nc - i - 1]
                del self.dockersInUse[Nc - i - 1]
            time.sleep(self.waitPeriod)

            print('In this iteration ',N-Nc if N-Nc > 0 else 0,'containers were created and ',Nc-N if Nc-N > 0 else 0,'containers were removed')
            print()
        pass
