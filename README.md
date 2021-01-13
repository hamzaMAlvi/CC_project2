# CC_project2

This repo contains the files submitted for the completion of project 2 given in course CS-579 Cloud Computing, which was offered in Spring 2020 at FAST-NU.

### Description given for project

Auto Scale and Load Balance a Web Application Using Open Source Tools. For this, complete the following tasks:

1. Write a simple Flask Application
2. Write a Dockerfile for creating a docker image for this application
3. Setup HAproxy on your machine and configure it to balance the between the application containers
4. Write a python script to monitor cpu utilization of system. This script should create and remove a container based on utilization (number of containers = %cpu_utilization / 10), and add it in HAProxy config so that newly created docker container can also balance the load.
