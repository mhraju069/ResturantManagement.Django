import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

def convert_to_webp(image_field):
    """
    Helper to convert an ImageField file to WebP format.
    """
    if not image_field:
        return None

    try:
        # Open the image using Pillow
        img = Image.open(image_field)
        
        # If it's already WebP, return as is
        if img.format == 'WEBP':
            return image_field

        # Convert to RGB if it has an alpha channel (WebP supports alpha, but RGB is safer for standard photos)
        # Actually WebP supports RGBA, so we can keep it if we want.
        # Let's keep RGBA if it exists.
        
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=80)
        output.seek(0)

        # Generate new filename with .webp extension
        filename = os.path.splitext(os.path.basename(image_field.name))[0]
        new_name = f"{filename}.webp"

        return ContentFile(output.read(), name=new_name)
    except Exception as e:
        print(f"Error converting image to WebP: {e}")
        return image_field

@receiver(pre_save)
def global_image_to_webp(sender, instance, **kwargs):
    """
    Global signal to catch all models with ImageFields and convert them to WebP before saving.
    """
    # Skip conversion if sender is LogEntry or similar system models if needed
    # but generally we want it for our app models.
    
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            image_attr = getattr(instance, field.name)
            
            # We only want to convert if it's a new file being uploaded
            # Checking if the file is currently in memory (UploadedFile) 
            # or if the extension is not webp.
            if image_attr and not image_attr.name.lower().endswith('.webp'):
                new_file = convert_to_webp(image_attr)
                if new_file:
                    setattr(instance, field.name, new_file)
