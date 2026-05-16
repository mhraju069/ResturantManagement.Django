from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
from authentication.image_optimizer import convert_to_webp

class Command(BaseCommand):
    help = 'Converts all existing images in the database to WebP format'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting image conversion to WebP..."))
        
        # Iterate through all registered models
        for model in apps.get_models():
            # Find fields that are ImageFields
            image_fields = [f for f in model._meta.fields if isinstance(f, models.ImageField)]
            
            if not image_fields:
                continue

            self.stdout.write(f"Checking model: {model.__name__}")
            
            instances = model.objects.all()
            for instance in instances:
                updated = False
                for field in image_fields:
                    image_attr = getattr(instance, field.name)
                    
                    # Skip if no image or already webp
                    if image_attr and not image_attr.name.lower().endswith('.webp'):
                        self.stdout.write(f"  Converting {field.name} for {instance}...")
                        new_file = convert_to_webp(image_attr)
                        if new_file:
                            setattr(instance, field.name, new_file)
                            updated = True
                
                if updated:
                    # Save the instance to trigger the change in storage and DB
                    instance.save()
                    self.stdout.write(self.style.SUCCESS(f"  Successfully updated {instance}"))

        self.stdout.write(self.style.SUCCESS("All images have been processed!"))
