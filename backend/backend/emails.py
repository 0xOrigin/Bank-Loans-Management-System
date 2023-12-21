from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(subject, template, context, to):
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        f"{settings.EMAIL_HOST_NAME} <{settings.EMAIL_HOST_USER}>",
        [to,]
    )
    email.attach_alternative(html_content, "text/html")
    return email.send(fail_silently=True)
