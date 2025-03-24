from datetime import datetime, timedelta, timezone
import os
from typing import Optional
from uuid import UUID

from botocore.signers import CloudFrontSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile
from mypy_boto3_s3 import S3Client

from app.v1.organizations.repositories.organizations_repository import OrganizationsRepository
from app.v1.organizations.schemas.organization import Organization

ALLOWED_FORMATS = ('png', 'jpeg')

_media_cf_endpoint: str = os.environ["MEDIA_ENDPOINT"]
_media_private_key: bytes = os.environb[b"MEDIA_PRIVATE_KEY"]
_media_public_key_id: str = os.environ["MEDIA_PUBLIC_KEY_ID"]

def _rsa_signer(message: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(_media_private_key, password=None, backend=default_backend())
    if isinstance(private_key, RSAPrivateKey):
        return private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA1(),  # noqa: S303
        )
    raise TypeError(f"Private key is not of expected type: {type(private_key)}, RSA expected.")


_cloudfront_signer = CloudFrontSigner(_media_public_key_id, _rsa_signer)

def _url_for(
    file_name: str,
    *,
    expire_seconds: int = 3000
) -> str:
    expire_datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=expire_seconds)
    return _cloudfront_signer.generate_presigned_url(
        f"https://{_media_cf_endpoint}/{file_name}",
        date_less_than=expire_datetime,
    )
    

class OrganizationLogosService:

    def __init__(self, logo_s3_bucket_name: str, organizations_repository: OrganizationsRepository, s3_client: S3Client):
        self.logo_s3_bucket_name = logo_s3_bucket_name
        self.organizations_repository = organizations_repository
        self.s3_client = s3_client
    
    async def _upload_organization_logo(self, organization_id: UUID, logo_file: UploadFile) -> str:
        try:
            image = Image.open(logo_file.file, formats=ALLOWED_FORMATS)
            image.verify()
        except (UnidentifiedImageError, SyntaxError, OSError):
            raise ValueError("Error loading/verifying image")
        
        image_extension = image.format.lower() if image.format is not None else "img"
        timestamp = int(datetime.now().timestamp())
        logo_key = f"org-{organization_id}/logo-{timestamp}.{image_extension}"

        await logo_file.seek(0)
        
        try:
            self.s3_client.put_object(
                Bucket=self.logo_s3_bucket_name,
                Key=logo_key,
                Body=logo_file.file
            )
        except Exception as e:
            raise e
        return logo_key
    
    def _update_organization_logo_path(self, organization_id: UUID, logo_key: str) -> Organization:
        return self.organizations_repository.update_logo_url(organization_id, logo_key)
    
    async def update_organization_logo(self, organization_id: UUID, logo_file: UploadFile) -> Organization:
        logo_key = await self._upload_organization_logo(organization_id, logo_file)
        updated_organization = self._update_organization_logo_path(organization_id, logo_key)
        return updated_organization        

    def get_logo_url(self, organization_id: UUID) -> Optional[str]:
        organization = self.organizations_repository.get(organization_id)
        if organization is None or organization.logo_url is None:
            return None
        return _url_for(organization.logo_url)
