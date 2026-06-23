from pathlib import Path
import hashlib
from dataclasses import dataclass
import imagehash
from PIL import Image, UnidentifiedImageError

@dataclass (frozen= True)
class ImageValidationResult: 
    is_valid: bool
    width: int = 0
    height: int = 0
    file_size_bytes: int = 0
    sha256: str = ''
    perceptual_hash: str = ''
    rejection_reason: str = ''

def compute_sha256 (path: Path): 
    '''
    This func hash the file bytes of images
    1024 x 1024 means chunk each 1mB
    '''
    hasher = hashlib.sha256()
    with path.open ('rb', ) as handle: 
        for chunk in iter(lambda: handle.read (1024 * 1024), b""): 
            hasher.update (chunk)
    return hasher.hexdigest() 

def validate_image (path: Path, min_size =  224): 
    if not path.exists() or path.stat().st_size == 0: 
        return ImageValidationResult(
            is_valid=False, 
            rejection_reason='missing_or_empty_file',
        )
    
    try: 
        with Image.open (path) as image:
            image = image.convert('RGB')
            width, height = image.size 
            if width < min_size or height < min_size: 
                return ImageValidationResult( 
                    is_valid = False, 
                    width = width, 
                    height = height, 
                    file_size_bytes=path.stat().st_size, 
                    rejection_reason='image_too_small', 
                )
            return ImageValidationResult(
                is_valid = True, 
                width=width,
                height=height,
                file_size_bytes=path.stat().st_size,
                sha256=compute_sha256(path),
                perceptual_hash=str(imagehash.phash(image)),
            )
    except: 
        return ImageValidationResult (
            is_valid = False, 
            rejection_reason='invalid_image', 
        )
