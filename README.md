# Virtual Mirror Distributed Web Service
This repository contains the source code and the docker images developed in the context of Use Case 4 of the CLEVER project. The application is a virtual mirror application, allowing the users to combine their own pictures, acquired through webcam, with selected garments, virtually trying them on. The application is developed as a distributed service, displaced between two edge nodes. The two nodes 

## Node 1
- ## Node 1
  is dedicated to interacting with the user, collecting images and pre-processing them before combining users’ pictures with garments.
   1. **Web application** enables the https web service that allows the users to upload their pictures, take snapshots with their own webcam and use the provided service.
   2. **Pre-processing** is necessary to map the images, recognizing poses and body areas. It uses openpose and 2D human parsing services. Openpose has been optimized to exploit a GPU virtualization service, allowing Node 1 to use Node 2    hardware resources, specifically its GPU.
   3. **rdma** provides low-latency communication between Node 1 and Node 2, allowing to distribute the computational load as needed without compromising the Quality of Service.
- ## Node 2
  is where backend services are activated, both for rdma and gpu virtualization.
**Bold Text**
*Italic Text*
- List item
1. Numbered item
[Link text](https://example.com)
![Image alt](image.png)
