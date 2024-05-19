
# Distributed Image Processing with MPI and Multithreading
This repository contains a project for distributed image processing using MPI (Message Passing Interface) and multithreading in Python. The project leverages OpenCV for various image processing tasks and includes a graphical user interface (GUI) for ease of use.

### Files

main.py: The main script to initialize the MPI environment, distribute tasks, and collect results.

processor.py: Contains the WorkerThread class for handling image processing tasks.

gui.py: Defines the GUI for uploading images and selecting processing operations.

master.py: Orchestrates the distribution and collection of image processing tasks across MPI nodes.

### Requirements
Python 3.x
OpenCV
mpi4py
numpy
boto3
paramiko
customtkinter
Pillow (PIL)


## Installation
You can install the required packages using pip:

```bash
  pip install opencv-python mpi4py numpy boto3 paramiko customtkinter Pillow
```
    
## Usage
Run main.py which will connect to our EC2 instances using Paramiko then initialize gui.py script which launches a graphical user interface that allows you to upload images, select an image processing operation, and start the processing.
Supported operations include: edge detection, color inversion, blurring, thresholding, sharpening, opening, image enhancement, and image rotating.
Image Processing
The processor.py script contains the WorkerThread class which processes each task using OpenCV functions. The operations are defined as follows:

image_rotating: Rotates the image by a specified angle.
edge_detection: Applies edge detection using the Canny algorithm.
color_inversion: Inverts the colors of the image.
blurring: Applies median blurring to the image.
thresholding: Converts the image to grayscale.
sharpening: Sharpens the image using a kernel.
opening: Applies the morphological opening operation to the image.
image_enhancement: Enhances the image by scaling pixel values.
Distributed Processing
master.py handles the distribution of image processing tasks to worker nodes and the merging of results.
main.py initializes the environment, handles the upload of images to an S3 bucket, and orchestrates the MPI processes.
Example Workflow
Upload Image:
The GUI allows users to upload one or more images for processing.

Select Operation:
Users select the desired image processing operation from a dropdown menu.

Process Image:
Clicking the "Process" button starts the processing. The images are uploaded to an S3 bucket, and MPI nodes perform the processing.

Download Results:
The processed images are downloaded from the S3 bucket and saved locally to ./output directory.


