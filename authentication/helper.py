from django.utils import timezone
from .models import OTP, User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_otp(email, task="verification"):
    try:
        user = User.objects.get(email=email)
        otp_obj = OTP.generate_otp(user)
        
        subject = f"Your OTP for {task}"
        
        # Render the HTML OTP template with context
        context = {'otp': otp_obj.otp}
        html_content = render_to_string('emails/otp.html', context)
        text_content = f"Your OTP code is {otp_obj.otp}. It will expire in 3 minutes."
        
        print("Before send_mail")

        email_message = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email_message.attach_alternative(html_content, "text/html")
        result = email_message.send(fail_silently=False)

        print("After send_mail:", result)
                
        return {"status": True, "log": f"OTP sent successfully to {email}"}
    except User.DoesNotExist:
        return {"status": False, "log": "User with this email does not exist."}
    except Exception as e:
        return {"status": False, "log": str(e)}


def verify_otp(email, otp_code):
    try:
        otp_obj = OTP.objects.filter(user__email=email).latest('created_at')
    except OTP.DoesNotExist:
        return {"status": False, "log": "Invalid OTP or email."}

    # Check expiry
    if otp_obj.is_expired():
        return {"status": False, "log": "OTP has expired."}

    # Verify OTP
    if otp_obj.otp != otp_code:
        return {"status": False, "log": "Invalid OTP."}

    # OTP verified, activate user & delete OTP
    user = otp_obj.user
    user.is_active = True
    user.save()
    otp_obj.delete()

    return {"status": True, "log": "OTP verified statusfully."}
