import boto3
import requests
import os
import io
from botocore.exceptions import NoCredentialsError, ClientError

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('SUPABASE_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SUPABASE_SECRET_ACCESS_KEY'),
        region_name=os.getenv('SUPABASE_REGION'),  # Убедись, что указан правильный регион
        endpoint_url=os.getenv('SUPABASE_ENDPOINT_URL')
    )


from botocore.exceptions import NoCredentialsError, ClientError


def upload_file_to_supabase(file, bucket_name, file_name):
    supabase_url = os.getenv('SUPABASE_URL').strip('/')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Используем Service Role Key

    # Формируем URL для загрузки файла
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/{file_name}"

    # Перемещаем указатель в начало файла
    file.seek(0)

    # Читаем файл в байты
    file_data = file.read()

    # Логируем размер файла
    print(f"📊 Размер файла: {len(file_data)} байтов")

    # Определяем MIME-Type
    if file_name.endswith(".webp"):
        content_type = "image/webp"
    elif file_name.endswith(".png"):
        content_type = "image/png"
    elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
        content_type = "image/jpeg"
    else:
        content_type = "application/octet-stream"

    # Делаем запрос на Supabase
    headers = {
        "Content-Type": content_type,
        "Authorization": f"Bearer {service_role_key}"
    }

    response = requests.put(url, headers=headers, data=file_data)

    if response.status_code == 200:
        print(f"✅ Файл {file_name} успешно загружен в бакет {bucket_name}.")
        return True
    else:
        print(f"❌ Ошибка загрузки файла: {response.status_code} - {response.text}")
        return False


