from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

def about(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # success message to be displayed after form submission
        messages.success(
         request,
         'Thank you for subscribing to our newsletter!'
         )

        # Send a confirmation email
        send_mail(
            'Newsletter Subscription Confirmation',
            f'Thank you for subscribing to our newsletter with the email {email}.',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        # Redirect to the same page to show the message
        return redirect('about') 

        # Redirect to the same page to show the message

    return render(request, 'about/about.html')
