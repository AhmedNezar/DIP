import queue
import time

from processor import WorkerThread
import cv2  # OpenCV for image processing
from mpi4py import MPI  # MPI for distributed computing
import boto3
import numpy as np


def encode_queue(q):
    lst = []
    while not q.empty():
        lst.append(q.get())
    return lst


def decode_queue(lst):
    q = queue.Queue()
    for item in lst:
        q.put(item)
    return q


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def split_to_half(img):
    org_image, operation, id = img
    img1 = org_image[:len(org_image) // 2]
    img2 = org_image[len(org_image) // 2:]
    return (img1, operation, str(id) + "_1"), (img2, operation, str(id) + "_2")


def merge_images(images):
    img1, img2 = images
    return np.concatenate((img1, img2), axis=0)


def distribute(imgs):
    distImages = []
    split_id = "null"
    if len(imgs) == 1:
        half1, half2 = split_to_half(imgs[0])
        distImages = [[half1], [half2]]
        split_id = half1[2].split("_")[0]
    elif len(imgs) % 2 == 0:
        imgs1 = imgs[:len(imgs) // 2]
        imgs2 = imgs[len(imgs) // 2:]
        distImages = [imgs1, imgs2]
    elif len(imgs) % 2 == 1:
        imgs1 = imgs[:len(imgs) // 2]
        imgs2 = imgs[len(imgs) // 2:len(imgs) - 1]
        distImages = [imgs1, imgs2]
        half1, half2 = split_to_half(imgs[-1])
        distImages[0].append(half1)
        distImages[1].append(half2)
        split_id = imgs[-1][2]
    return distImages, split_id


if rank == 0:
    s3 = boto3.resource(
        's3',
        aws_access_key_id="AKIAVRUVR5RVOEOGVI6Y",
        aws_secret_access_key="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",
        region_name="us-east-1"
    )
    bucket = s3.Bucket('dipimagesbucket')
    sqs = boto3.resource(
        'sqs',
        aws_access_key_id="AKIAVRUVR5RVOEOGVI6Y",
        aws_secret_access_key="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",
        region_name="us-east-1"
    )
    q = sqs.get_queue_by_name(QueueName='dip.fifo')

    s3images = bucket.objects.all()
    keys = [image.key for image in s3images]
    images = []
    for i in range(0, len(keys)):
        print(f"Downloading image {keys[i]}")
        img = bucket.Object(keys[i]).get().get('Body').read()
        nparray = cv2.imdecode(np.asarray(bytearray(img)), cv2.IMREAD_COLOR)
        images.append((nparray, keys[i].split("-")[1], i))

    images, split_id = distribute(images)

    for i in range(0, len(keys)):
        print(f"Deleting image {keys[i]}")
        bucket.Object(keys[i]).delete()

    for i in range(size - 1):
        task_queue = queue.Queue()
        for image in images[i]:
            print(f"Sending {image[2]} to Processor {i}")
            task_queue.put(image)
        comm.send(encode_queue(task_queue), dest=i + 1)
    #
    split_images = [None, None]
    received_split = 0
    total_results = len(images[0]) + len(images[1])
    result_no = 0
    for i in range(total_results):
        result, id = comm.recv(source=MPI.ANY_SOURCE)
        print(f'received result {i}')
        if str(id).split("_")[0] == str(split_id):
            received_split += 1
            split_index = int(id.split("_")[1]) - 1
            split_images[split_index] = result
            if received_split == 2:
                result = merge_images(split_images)
                _, img_bytes = cv2.imencode('.jpg', result)
                bucket.put_object(
                    Key=f"result-{result_no}",
                    Body=img_bytes.tobytes()
                )
                print(f"Sending result to queue: {result_no}")
                q.send_message(MessageBody=f"result-{result_no}", MessageGroupId='dip', MessageDeduplicationId=f'{result_no}-{int(time.time())}')
                result_no += 1
        else:
            _, img_bytes = cv2.imencode('.jpg', result)
            bucket.put_object(
                Key=f"result-{result_no}",
                Body=img_bytes.tobytes()
            )
            print(f"Sending result to queue: {result_no}")
            q.send_message(MessageBody=f"result-{result_no}", MessageGroupId='dip',
                           MessageDeduplicationId=f'{result_no}-{int(time.time())}')
            result_no += 1

    MPI.Finalize()

else:
    task_queue = decode_queue(comm.recv(source=0))
    WorkerThread(task_queue).start()
