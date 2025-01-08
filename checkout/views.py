from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_POST
import stripe

# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY

@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            'Sorry, your payment cannot be processed right now.Try again Later'
        )
        return HttpResponse(content=e, status=400)

def checkout(request):
    if request.method == 'POST':
        # Collect order details from POST data
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        address = request.POST['address']
        city = request.POST['city']
        postal_code = request.POST['postal_code']
        country = request.POST['country']

        # Calculate order total
        bag = request.session.get('bag', {})
        total = sum(Product.objects.get(id=item_id).price * quantity for item_id, quantity in bag.items())

        # Create an Order object
        order = Order.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            city=city,
            postal_code=postal_code,
            country=country,
            total=total
        )

        # Create OrderItems and attach to the order
        for item_id, quantity in bag.items():
            product = Product.objects.get(id=item_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                item_total=product.price * quantity
            )

        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),  # Stripe expects cents
            currency='usd',
            metadata={'order_id': order.id}
        )

        # Pass data to the template
        return render(request, 'checkout/checkout.html', {
            'order': order,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.client_secret
        })
    
    return render(request, 'checkout/checkout.html')

def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f'Order successfully processed! Your order number is {order_number}. '
        f'A confirmation email will be sent to {order.email}.'
    )

    if 'bag' in request.session:
        del request.session['bag']


    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)