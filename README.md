# Virtual Mirror Distributed Web Service
This repository contains the source code and the docker images developed in the context of Use Case 4 of the CLEVER project. The application is a virtual mirror application, allowing the users to combine their own pictures, acquired through webcam, with selected garments, virtually trying them on. The application is developed as a distributed service, displaced between two edge nodes. The two nodes 

## Node 1
Is dedicated to interacting with the user, collecting images and pre-processing them before combining users’ pictures with garments.
1. **Web application** enables the https web service that allows the users to upload their pictures, take snapshots with their own webcam and use the provided service.
2. **Pre-processing** is necessary to map the images, recognizing poses and body areas. It uses openpose and 2D human parsing services. Openpose has been optimized to exploit a GPU virtualization service, allowing Node 1 to use Node 2    hardware resources, specifically its GPU.
3. **rdma** provides low-latency communication between Node 1 and Node 2, allowing to distribute the computational load as needed without compromising the Quality of Service.

## Node 2
Is where backend services are activated, both for rdma and gpu virtualization. These services are necessary to create communication channels between Node 1 and Node 2, are activated at startup and allow low-latency communication and hardware resources exploitation by the service deployed at Node 1.

## VITON
This service is what merges images and garments and is deployed as an isolated container. In standard configuration is deployed on Node 2, but it may be deployed on Node 1 if local deployment is necessary.

## Environment Setting
1. **Download Node 1 and Node 2 directories**
   All the executable in this projects are designed to run inside containers but they expect a basic structure on the host and they need access to specific folders on the host. To be sure to have the correct setup on your directories, download Node1 repository on your Node1 and Node2 repository on Node2. Then, rename the two directories so that they have the same filepath (es. /home/username/virtual_mirror/), as the application expects that. At this point, you may pull the necessary images on your servers.

On Node 1:
```bash
docker pull ghcr.io/mike9277/virtual_mirror_node_1:latest
```

On Node 2:
```bash
docker pull ghcr.io/mike9277/virtual_mirror_node_2:latest
```

```bash
docker pull ghcr.io/mike9277/virtual_mirror_viton:latest
```
If you want to test the local deployment you may want to pull virtual_mirror_viton docker also on Node 1.

Finally, you will need to edit env_config.json to set your own filepaths and addresses. This file sets all the environmental variables necessary to run the application and to allow communication between Node 1 and Node 2. 

## Set GPU Virtualization
The application leverages on GPU virtualization service provided by GVirtus. GVirtus is handled as an external service, and it needs its own setup procedure. Download the necessary repository both on Node 1 and Node 2 folders,

## Run the application 
You may run the application on Node 1, with the following command:
```bash
./start_application.sh
```
