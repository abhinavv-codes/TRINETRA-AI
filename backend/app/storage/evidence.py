"""Evidence storage manager - S3/MinIO backend"""

import logging
from typing import Optional
import boto3

logger = logging.getLogger(__name__)


class EvidenceStorage:
    """Manager for evidence image storage"""
    
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, bucket: str):
        """
        Initialize S3/MinIO client
        
        Args:
            endpoint_url: S3/MinIO endpoint
            access_key: Access key
            secret_key: Secret key
            bucket: Bucket name
        """
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self.bucket = bucket
    
    def upload_evidence(
        self,
        image_bytes: bytes,
        key: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload evidence image to S3/MinIO
        
        Args:
            image_bytes: Image binary data
            key: S3 object key (path)
            metadata: Optional metadata
        
        Returns:
            S3 URI
        """
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=image_bytes,
                Metadata=metadata or {},
            )
            
            uri = f"s3://{self.bucket}/{key}"
            logger.info(f"Uploaded evidence: {uri}")
            return uri
        
        except Exception as e:
            logger.warning(f"Failed to upload evidence to S3, falling back to local file storage: {e}")
            import os
            # Ensure key is safe
            local_path = os.path.join("data", key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(image_bytes)
            
            # Normalize to web path
            web_key = key.replace("\\", "/")
            uri = f"/static/{web_key}"
            logger.info(f"Saved evidence locally at: {uri}")
            return uri
    
    def download_evidence(self, key: str) -> bytes:
        """Download evidence image"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.warning(f"Failed to download from S3, trying local file: {e}")
            import os
            local_path = os.path.join("data", key)
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    return f.read()
            raise e
