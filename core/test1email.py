from django.conf import settings
from django.core.mail import send_mail

def func1():
    import pdb; pdb.set_trace()
    subject = 'welcome to GFG world'
    message = f'Hi thank you for registering in geeksforgeeks.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = 'usmansaddiqui.12@gmail.com'
    send_mail(subject, message, email_from, [recipient_list])
