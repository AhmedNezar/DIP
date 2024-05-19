import gui
import boto3
import cv2
import numpy as np
import paramiko
import threading

s3 = boto3.resource(
    's3',
    aws_access_key_id="......",
    aws_secret_access_key="......",
    region_name="......"
)
bucket = s3.Bucket('dipimagesbucket')

sqs = boto3.resource(
    'sqs',
    aws_access_key_id="......",
    aws_secret_access_key="......",
    region_name="......"
)
q = sqs.get_queue_by_name(QueueName='......')

ssh = paramiko.SSHClient()
k = paramiko.RSAKey.from_private_key_file("......")


ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname="......", username="ec2-user", pkey=k)


def receive_messages(images, operation):
    images = images.split(",")
    for i in range(0, len(images)):
        app.log(f"Uploading image {i}")
        img = cv2.imread(images[i], cv2.IMREAD_COLOR)
        _, img_bytes = cv2.imencode('.jpg', img)
        bucket.put_object(
            Key=f"image{i}-{operation}",
            Body=img_bytes.tobytes()
        )
    app.update_progress(0.3)
    app.log("Processing images...")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("mpirun -n 3 -hostfile nodefile python master.py")
    output = ssh_stdout.read().decode()
    app.update_progress(0.7)
    app.log(output)
    message_count = 0
    while True:
        messages = q.receive_messages(
            WaitTimeSeconds=20,
            MaxNumberOfMessages=len(images)
        )
        if messages:
            for message in messages:
                img_rcv = message.body
                app.log(f"Downloading image ({img_rcv}) from s3 bucket")
                img = bucket.Object(img_rcv).get().get('Body').read()
                nparray = cv2.imdecode(np.asarray(bytearray(img)), cv2.IMREAD_COLOR)
                cv2.imwrite(f"./output/{img_rcv}.jpg", nparray)
                app.log(f"Image ({img_rcv}) saved to output folder")
                app.log(f"Deleting image ({img_rcv}) from s3 bucket")
                bucket.Object(img_rcv).delete()
                message.delete()
                message_count += 1
        if message_count == len(images):
            break
    app.log("Finished processing images")
    app.update_progress(1)
    app.enable_process_button()


def start(images, operation):
    thread = threading.Thread(target=receive_messages, args=(images,operation,))
    thread.start()


app = gui.GUI(start)
app.run()
progress, logtext = app.get_widgets()
