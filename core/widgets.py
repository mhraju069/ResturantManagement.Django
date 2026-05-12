from django.forms.widgets import ClearableFileInput


class PremiumImageUpload(ClearableFileInput):
    """
    A premium drag-and-drop image upload widget for the Unfold admin.
    Uses the custom template at templates/admin/widgets/custom_image_upload.html
    """
    template_name = "admin/widgets/custom_image_upload.html"

    class Media:
        # Google Material Symbols for the icons used inside the widget
        css = {
            "all": [
                "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0"
            ]
        }
