from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from rfx_backend.settings import DEFAULT_FROM_EMAIL



def send_verification_email(to_email, key, name):
    import pdb; pdb.set_trace()
    ctx = {
        'link': 'http://18.118.115.142/verify-email?token=' + key,
        'name': name
    }

    html_content = render_to_string(template_name='send_verification_email.html', context=ctx)
    text_content = render_to_string(template_name='send_verification_email.html', context=ctx)

    # create the email, and attach the HTML version as well.
    try:
        msg = EmailMultiAlternatives('Veirfy Email', text_content, DEFAULT_FROM_EMAIL, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = 'related'
        msg.send()
    except Exception as e:
        print("error", e)