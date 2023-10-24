import boto3
import os
import logging
from datetime import datetime

# 設置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_elasticache_snapshots(filter_names):
    client = boto3.client('elasticache', region_name='ap-east-1')
    response = client.describe_snapshots()
    filtered_snapshots = [snapshot for snapshot in response['Snapshots'] if any(fn in snapshot['SnapshotName'] for fn in filter_names)]
    return filtered_snapshots

def export_snapshot_to_s3(snapshot_name, bucket_name, prefix):
    client = boto3.client('elasticache', region_name='ap-east-1')
    try:
        response = client.copy_snapshot(
            SourceSnapshotName=snapshot_name,
            TargetBucket=bucket_name,
            TargetSnapshotName=prefix + snapshot_name
        )
        return response
    except Exception as e:
        logger.error(f"Error exporting snapshot {snapshot_name} to S3: {e}")
        return None

def is_snapshot_ready(snapshot_name):
    client = boto3.client('elasticache', region_name='ap-east-1')
    try:
        response = client.describe_snapshots(SnapshotName=snapshot_name)
        # 檢查快照狀態
        if response['Snapshots'][0]['SnapshotStatus'] == 'available':
            return True
    except Exception as e:
        logger.error(f"Error checking snapshot {snapshot_name}: {e}")
    return False

def is_object_exists(bucket_name, object_key):
    s3 = boto3.client('s3', region_name='ap-east-1')
    try:
        s3.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except Exception as e:
        return False

def list_files_from_s3(bucket_name, prefix):
    s3 = boto3.client('s3', region_name='ap-east-1')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        logger.warning(f"No contents found in bucket {bucket_name} with prefix {prefix}")
        return []
    return [item['Key'] for item in response['Contents']]

def download_file(bucket_name, object_key, destination_path):
    s3 = boto3.client('s3', region_name='ap-east-1')
    try:
        s3.download_file(bucket_name, object_key, destination_path)
        logger.info(f"Downloaded {object_key} to {destination_path}")
    except Exception as e:
        logger.error(f"Error downloading {object_key}: {e}")

def sort_and_filter_files(files):
    # Extract dates from filenames and sort them
    sorted_files = sorted(files, key=lambda f: datetime.strptime('-'.join(f.split('-')[3:8]), "%Y-%m-%d-%H-%M"), reverse=True)
    return sorted_files[0], sorted_files[1:]

def delete_file(bucket_name, object_key):
    s3 = boto3.client('s3', region_name='ap-east-1')
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        logger.info(f"Deleted {object_key} from S3.")
    except Exception as e:
        logger.error(f"Error deleting {object_key}: {e}")

def generate_public_url(bucket_name, object_key):
    return f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

def generate_presigned_url(bucket_name, object_key, expiration=3600):
    s3 = boto3.client('s3', region_name='ap-east-1')
    try:
        response = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name,
                                                    'Key': object_key},
                                            ExpiresIn=expiration)
        return response
    except Exception as e:
        logger.error(f"Error generating presigned URL for {object_key}: {e}")
        return None

if __name__ == '__main__':
    filter_names = ["automatic.redis-game-001", "automatic.redis-db-002"]
    bucket_name = "apple-redis-rbd"
    prefix = "backup/"

    snapshots = get_elasticache_snapshots(filter_names)
    for snapshot in snapshots:
        logger.info(f"Exporting snapshot: {snapshot['SnapshotName']} to S3...")
        response = export_snapshot_to_s3(snapshot['SnapshotName'], bucket_name, prefix)
        if response:
            #等待快照可用
            while not is_snapshot_ready(snapshot['SnapshotName']):
                logger.info(f"Waiting for snapshot {snapshot['SnapshotName']} to be ready...")
                time.sleep(30)  # 每30秒檢查一次
                logger.info(f"Snapshot {snapshot['SnapshotName']} exported successfully.")

        # 下載已經上傳的備份檔案
        files_in_s3 = list_files_from_s3(bucket_name, prefix)
        for filter_name in filter_names:
            filtered_files = [file_key for file_key in files_in_s3 if file_key.startswith(prefix + filter_name)]

        if filtered_files:
            latest_file, older_files = sort_and_filter_files(filtered_files)

            # 檢查最新的文件是否存在
            while not is_object_exists(bucket_name, latest_file):
                logger.info(f"Waiting for file {latest_file} to be available...")
                time.sleep(30)  # 每30秒檢查一次

            # Download the latest file
            destination_path = os.path.join("/tmp", os.path.basename(latest_file))
            download_file(bucket_name, latest_file, destination_path)

            # Delete older files
            for old_file in older_files:
                delete_file(bucket_name, old_file)
