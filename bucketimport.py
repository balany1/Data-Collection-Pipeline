import boto3
import os

BUCKET_NAME= "formula1-aicore"

s3 = boto3.client("s3")

def uploadDirectory(path,bucketname):
        for root,dirs,files in os.walk(path):
            for file in files:
                s3.upload_file(os.path.join(root,file),bucketname,file)

uploadDirectory("/home/andrew/AICore_work/Data-Collection-Pipeline/back_up",BUCKET_NAME)
