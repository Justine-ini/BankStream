from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from loguru import logger


def send_otp_email(email, otp):
    """
    Sends a One-Time Password (OTP) email to the specified recipient.
    Args:
        email (str): The recipient's email address.
        otp (str): The OTP code to be sent.
    Description:
        This function renders an HTML email template with the provided OTP and site information,
        sends the email to the recipient, and logs the result. If sending fails, an error is logged.
    Raises:
        Exception: If the email fails to send, the exception is caught and logged.
    """
    subject = _("Your OTP code for Login")
    from_email = settings.DEFAULT_FROM_EMAIL
    recepient_list = [email]
    context = {
        "otp": otp,
        "expiry_time": settings.OTP_EXPIRATION,
        "site_name": settings.SITE_NAME
    }
    html_email = render_to_string("emails/otp_email.html", context)
    plain_email = strip_tags(html_email)
    email = EmailMultiAlternatives(
        subject, plain_email, from_email, recepient_list)
    email.attach_alternative(html_email, "text/html")

    try:
        email.send()
        logger.info(f"OTP email sent successfully to: {email}")

    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: Error: {str(e)}")


def send_account_locked_email(self):
    """
    Sends an email notification to the user when their account has been locked due
      to security reasons.
    The email includes information about the lockout duration and the site name. Both
      HTML and plain text versions of the email are sent.
    Logs the result of the email sending process.
    Raises:
        Logs an error if the email fails to send.
    Context:
        user (object): The user whose account is locked.
        lockout_duration (int): Duration of the lockout in minutes.
        site_name (str): Name of the site.
    """
    subject = _("Youraccount has been locked")
    from_email = settings.DEFAULT_FROM_EMAIL
    recepient_list = [self.email]
    context = {
        "user": self,
        "lockout_duration": int(settings.LOCKOUT_DURATION.total_seconds() // 60),
        "site_name": settings.SITE_NAME
    }
    html_email = render_to_string("emails/account_locked.html", context)
    plain_email = strip_tags(html_email)
    email = EmailMultiAlternatives(
        subject, plain_email, from_email, recepient_list)
    email.attach_alternative(html_email, "text/html")

    try:
        email.send()
        logger.info(f"Account locked email sent to: {email}")

    except Exception as e:
        logger.error(
            f"Failed to send account locked email to {self.email}: Error: {str(e)}")
