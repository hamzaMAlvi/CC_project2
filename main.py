from autoScalingFlaskApp import AutoScaleContainers

containerName = 'project-phase-2:latest'
haproxyCfgFileName = 'flaskAppLBhaproxy'
waitPeriod = 5

autoScale = AutoScaleContainers(containerName=containerName, waitPeriod=waitPeriod, haproxyCfgFile=haproxyCfgFileName)
autoScale.start()
