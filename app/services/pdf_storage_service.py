"""
PDF Cloud Storage Service
Handles PDF storage and retrieval with support for local filesystem and cloud (Azure/S3)
"""

import os
import shutil
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class PDFStorageService:
    """
    Service for storing and retrieving PDF files
    Supports multiple storage backends: local filesystem, Azure Blob Storage, AWS S3
    """
    
    def __init__(self, storage_type: str = "local", config: Optional[Dict] = None):
        """
        Initialize PDF storage service
        
        Args:
            storage_type: "local", "azure", or "s3"
            config: Configuration dict for cloud storage
        """
        self.storage_type = storage_type
        self.config = config or {}
        
        if storage_type == "local":
            self.storage_path = self.config.get('storage_path', '/tmp/zerosite_pdfs')
            self._ensure_storage_directory()
        elif storage_type == "azure":
            self._init_azure_storage()
        elif storage_type == "s3":
            self._init_s3_storage()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    def _ensure_storage_directory(self):
        """Ensure local storage directory exists"""
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Local PDF storage directory: {self.storage_path}")
    
    def _init_azure_storage(self):
        """Initialize Azure Blob Storage client"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            connection_string = self.config.get('azure_connection_string')
            container_name = self.config.get('azure_container_name', 'zerosite-pdfs')
            
            if not connection_string:
                logger.warning("Azure connection string not provided, falling back to local storage")
                self.storage_type = "local"
                self._ensure_storage_directory()
                return
            
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_name = container_name
            
            # Ensure container exists
            try:
                self.blob_service_client.create_container(container_name)
            except:
                pass  # Container already exists
            
            logger.info(f"Azure Blob Storage initialized: {container_name}")
            
        except ImportError:
            logger.warning("Azure SDK not installed, falling back to local storage")
            self.storage_type = "local"
            self._ensure_storage_directory()
    
    def _init_s3_storage(self):
        """Initialize AWS S3 client"""
        try:
            import boto3
            
            aws_access_key = self.config.get('aws_access_key_id')
            aws_secret_key = self.config.get('aws_secret_access_key')
            bucket_name = self.config.get('s3_bucket_name', 'zerosite-pdfs')
            region = self.config.get('aws_region', 'ap-northeast-2')
            
            if not (aws_access_key and aws_secret_key):
                logger.warning("AWS credentials not provided, falling back to local storage")
                self.storage_type = "local"
                self._ensure_storage_directory()
                return
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            self.bucket_name = bucket_name
            
            # Ensure bucket exists
            try:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            except:
                pass  # Bucket already exists
            
            logger.info(f"AWS S3 Storage initialized: {bucket_name}")
            
        except ImportError:
            logger.warning("boto3 not installed, falling back to local storage")
            self.storage_type = "local"
            self._ensure_storage_directory()
    
    def save_pdf(self, pdf_bytes: bytes, filename: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Save PDF file to storage
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename
            metadata: Optional metadata dict
        
        Returns:
            Dict with storage info including file_id, download_url, expires_at
        """
        # Generate unique file ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_hash = hashlib.md5(pdf_bytes).hexdigest()[:8]
        file_id = f"{timestamp}_{file_hash}"
        
        # Generate storage filename
        file_ext = os.path.splitext(filename)[1]
        storage_filename = f"{file_id}{file_ext}"
        
        if self.storage_type == "local":
            return self._save_local(pdf_bytes, storage_filename, file_id, metadata)
        elif self.storage_type == "azure":
            return self._save_azure(pdf_bytes, storage_filename, file_id, metadata)
        elif self.storage_type == "s3":
            return self._save_s3(pdf_bytes, storage_filename, file_id, metadata)
    
    def _save_local(self, pdf_bytes: bytes, storage_filename: str, file_id: str, metadata: Optional[Dict]) -> Dict:
        """Save PDF to local filesystem"""
        file_path = os.path.join(self.storage_path, storage_filename)
        
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Generate download URL (relative to API)
        download_url = f"/api/v24.1/pdf/download/{file_id}"
        
        # Expiration time (24 hours)
        expires_at = datetime.now() + timedelta(hours=24)
        
        logger.info(f"PDF saved locally: {file_path}")
        
        return {
            "file_id": file_id,
            "storage_type": "local",
            "storage_filename": storage_filename,
            "file_path": file_path,
            "download_url": download_url,
            "expires_at": expires_at.isoformat(),
            "file_size_bytes": len(pdf_bytes),
            "metadata": metadata or {}
        }
    
    def _save_azure(self, pdf_bytes: bytes, storage_filename: str, file_id: str, metadata: Optional[Dict]) -> Dict:
        """Save PDF to Azure Blob Storage"""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=storage_filename
        )
        
        # Upload with metadata
        blob_metadata = metadata or {}
        blob_metadata['file_id'] = file_id
        blob_metadata['created_at'] = datetime.now().isoformat()
        
        blob_client.upload_blob(pdf_bytes, metadata=blob_metadata, overwrite=True)
        
        # Generate SAS URL for download (24 hours)
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import timezone
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=storage_filename,
            account_key=self.config.get('azure_account_key'),
            permission=BlobSasPermissions(read=True),
            expiry=expires_at
        )
        
        download_url = f"{blob_client.url}?{sas_token}"
        
        logger.info(f"PDF saved to Azure: {storage_filename}")
        
        return {
            "file_id": file_id,
            "storage_type": "azure",
            "storage_filename": storage_filename,
            "container_name": self.container_name,
            "download_url": download_url,
            "expires_at": expires_at.isoformat(),
            "file_size_bytes": len(pdf_bytes),
            "metadata": metadata or {}
        }
    
    def _save_s3(self, pdf_bytes: bytes, storage_filename: str, file_id: str, metadata: Optional[Dict]) -> Dict:
        """Save PDF to AWS S3"""
        # Upload with metadata
        extra_args = {
            'ContentType': 'application/pdf',
            'Metadata': metadata or {}
        }
        extra_args['Metadata']['file_id'] = file_id
        extra_args['Metadata']['created_at'] = datetime.now().isoformat()
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=storage_filename,
            Body=pdf_bytes,
            **extra_args
        )
        
        # Generate presigned URL (24 hours)
        expires_in = 24 * 3600  # 24 hours in seconds
        download_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': storage_filename
            },
            ExpiresIn=expires_in
        )
        
        expires_at = datetime.now() + timedelta(hours=24)
        
        logger.info(f"PDF saved to S3: {storage_filename}")
        
        return {
            "file_id": file_id,
            "storage_type": "s3",
            "storage_filename": storage_filename,
            "bucket_name": self.bucket_name,
            "download_url": download_url,
            "expires_at": expires_at.isoformat(),
            "file_size_bytes": len(pdf_bytes),
            "metadata": metadata or {}
        }
    
    def get_pdf(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve PDF file from storage
        
        Args:
            file_id: File identifier
        
        Returns:
            PDF bytes or None if not found
        """
        if self.storage_type == "local":
            return self._get_local(file_id)
        elif self.storage_type == "azure":
            return self._get_azure(file_id)
        elif self.storage_type == "s3":
            return self._get_s3(file_id)
    
    def _get_local(self, file_id: str) -> Optional[bytes]:
        """Get PDF from local filesystem"""
        # Find file with matching file_id
        for filename in os.listdir(self.storage_path):
            if filename.startswith(file_id):
                file_path = os.path.join(self.storage_path, filename)
                with open(file_path, 'rb') as f:
                    return f.read()
        return None
    
    def _get_azure(self, file_id: str) -> Optional[bytes]:
        """Get PDF from Azure Blob Storage"""
        # List blobs and find matching file_id
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs()
        
        for blob in blobs:
            if blob.name.startswith(file_id):
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                return blob_client.download_blob().readall()
        return None
    
    def _get_s3(self, file_id: str) -> Optional[bytes]:
        """Get PDF from AWS S3"""
        # List objects and find matching file_id
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].startswith(file_id):
                    response = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    return response['Body'].read()
        return None
    
    def delete_expired_pdfs(self):
        """Delete expired PDF files (older than 24 hours)"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        if self.storage_type == "local":
            for filename in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"Deleted expired PDF: {filename}")
        
        # Note: Azure and S3 can use lifecycle policies for automatic deletion
