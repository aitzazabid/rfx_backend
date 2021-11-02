from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from rfx_backend.settings import DEFAULT_FROM_EMAIL


def send_verification_email(to_email, key, name):
    ctx = {
        'link': 'http://18.118.115.142/verify-email?token=' + str(key),
        'name': name
    }

    html_content = render_to_string(template_name='send_email.html', context=ctx)
    text_content = render_to_string(template_name='send_email.html', context=ctx)

    try:
        msg = EmailMultiAlternatives('Verify Email', html_content, DEFAULT_FROM_EMAIL, [to_email])
        msg.attach_alternative(text_content, "text/html")
        msg.mixed_subtype = 'related'
        msg.send()
    except Exception as e:
        print("error", e)
