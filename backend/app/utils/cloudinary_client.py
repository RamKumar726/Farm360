from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)


def upload_file(file_bytes: bytes, folder: str = "farm360", resource_type: str = "auto") -> str:
    """Upload a file to Cloudinary and return the secure URL."""
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type=resource_type,
    )
    return result["secure_url"]


def upload_proof_photo(file_bytes: bytes, farm_id: str) -> str:
    return upload_file(file_bytes, folder=f"farm360/proof/{farm_id}", resource_type="image")


def upload_proof_video(file_bytes: bytes, farm_id: str) -> str:
    return upload_file(file_bytes, folder=f"farm360/proof/{farm_id}", resource_type="video")
