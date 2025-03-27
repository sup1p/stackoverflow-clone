import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('SUPABASE_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SUPABASE_SECRET_ACCESS_KEY'),
        region_name=os.getenv('SUPABASE_REGION'),
        endpoint_url=os.getenv('SUPABASE_ENDPOINT_URL')
    )

def upload_file_to_supabase(file, bucket_name, file_name):
    s3 = get_s3_client()
    try:
        s3.upload_fileobj(file, bucket_name, file_name)
        return True
    except (NoCredentialsError, ClientError) as e:
        print(f"Ошибка загрузки файла: {e}")
        return False

def generate_presigned_url(file_name, bucket_name, expiration=3600):
    s3 = get_s3_client()
    try:
        response = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Ошибка создания ссылки: {e}")
        return None
