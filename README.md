# IoT Monitoring lab

In this project I built an IoT application to live monitor sensor data. All services run in a Kubernetes (in following k8s) cluster und communicate through the internal DNS-Service of k8s.

# Initial Setup
before we start writing a single configuration file, we need to install and setup the development environment for k8s. For this Project the following tools are needed: docker, kind, and kubectl. A docker hub account is also required, where the crrated docker images will be pushed. 
### 1. Docker
The official link to install and setup docker on a linux machine is here.
### 2. kubectl
This is the tool for .... To install, run the following 2 commands:
```curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```
