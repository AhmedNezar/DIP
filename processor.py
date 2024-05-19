import threading
import queue
import cv2  # OpenCV for image processing
from mpi4py import MPI  # MPI for distributed computing
import numpy as np


class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()

    def run(self):
        while True:
            try:
                task = self.task_queue.get(block=False)
                print(f"Processor {self.rank - 1} received task {task[2]}")
            except queue.Empty:
                task = None
            if task is None:
                print(f'worker {self.rank - 1} exiting')
                break
            image, operation, id = task
            result = self.process_image(image, operation, id)
            self.send_result(result)

    def process_image(self, image, operation, id):
        # Load the image
        # img = cv2.imread(image, cv2.IMREAD_COLOR)
        img = image
        # Perform the specified operation
        if operation == 'image_rotating':
            center = (img.shape[1] // 2, img.shape[0] // 2)
            angle = 30
            scale = 1
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
            result = cv2.warpAffine(img, rotation_matrix, (img.shape[1], img.shape[0]))
        elif operation == 'edge_detection':
            result = cv2.Canny(img, 100, 200)
        elif operation == 'color_inversion':
            result = cv2.bitwise_not(img)
        elif operation == 'blurring':
            result = cv2.medianBlur(img, 21)
        elif operation == 'thresholding':
            result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif operation == 'sharpening':
            sharp_kernel = np.array([[0, -1, 0],
                                     [-1, 5, -1],
                                     [0, -1, 0]])
            result = cv2.filter2D(src=img, ddepth=-1, kernel=sharp_kernel)
        elif operation == 'opening':
            image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(image_gray, kernel, iterations=2)
            eroded = cv2.erode(image_gray, kernel, iterations=2)
            result = cv2.morphologyEx(image_gray, cv2.MORPH_OPEN, kernel)
        elif operation == 'image_enhancement':
            min_val = np.min(img)
            max_val = np.max(img)
            result = cv2.convertScaleAbs(img, alpha=255.0 / (max_val - min_val),
                                         beta=-255.0 * min_val / (max_val - min_val))
        else:
            print("Invalid operation:", operation)
            return None
        return result, id

    def send_result(self, result):
        # Send the result to the master node
        self.comm.send(result, dest=0)
