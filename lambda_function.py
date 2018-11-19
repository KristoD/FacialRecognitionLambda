import boto3
import logging
import os
import json

s3 = boto3.client('s3')
rekog = boto3.client('rekognition')
sns = boto3.client('sns')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # retrieve bucket name and file key from the s3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    # compare uploaded photo to photo in storedimages bucket
    response = rekog.compare_faces(
        SourceImage = {
            'S3Object' : {
                'Bucket' : os.environ['BUCKET_NAME'],
                'Name' : os.environ['FILE_NAME']
            }
        },
        TargetImage = {
            'S3Object' : {
                'Bucket' : bucket_name,
                'Name' : file_key
            }
        },
        SimilarityThreshold=80.0
    )
    
    phone_number = os.environ['PHONE_NUMBER']

    # Send SMS text message to declared phone number
    
    if response['FaceMatches']:
        sns.publish(
            PhoneNumber=phone_number,
            Message="Access granted.",
            Subject="ALERT"
        )
    else:
        sns.publish(
            PhoneNumber=phone_number,
            Message="Access denied. Someone is trying to gain access.",
            Subject="ALERT"
        )
        
    s3.delete_object(
        Bucket=bucket_name,
        Key= file_key
    )

    return
