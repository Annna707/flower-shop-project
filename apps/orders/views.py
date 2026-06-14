from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.cart import Cart
from apps.catalog.models import Product
from apps.users.models import Profile

from .forms import DELIVERY_COSTS, OrderCreateForm
from .models import Order, OrderItem


def _checkout_summary(cart, delivery_method=None):
    items_total = cart.get_total_price()
    method = delivery_method or Order.DELIVERY_STANDARD
    delivery_cost = DELIVERY_COSTS.get(method, DELIVERY_COSTS[Order.DELIVERY_STANDARD])
    return {
        'cart_items_total': items_total,
        'cart_items_total_js': str(items_total),
        'delivery_cost': delivery_cost,
        'grand_total': items_total + delivery_cost,
    }


@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('catalog:product_list')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'phone': profile.phone,
        'address': profile.address,
        'delivery_method': Order.DELIVERY_STANDARD,
        'payment_method': Order.PAYMENT_CARD_ONLINE,
    }

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            delivery_cost = form.get_delivery_cost()
            paid = form.cleaned_data['payment_method'] == Order.PAYMENT_CARD_ONLINE
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data.get('postal_code', ''),
                city=form.cleaned_data['city'],
                delivery_method=form.cleaned_data['delivery_method'],
                payment_method=form.cleaned_data['payment_method'],
                delivery_cost=delivery_cost,
                comment=form.cleaned_data.get('comment', ''),
                paid=paid,
            )
            with transaction.atomic():
                for item in cart:
                    product = Product.objects.select_for_update().get(pk=item['product'].pk)
                    if item['quantity'] > product.stock:
                        order.delete()
                        messages.error(
                            request,
                            f'«{product.name}»: доступно только {product.stock} шт.',
                        )
                        return redirect('cart:cart_detail')
                    product.stock -= item['quantity']
                    product.save(update_fields=['stock'])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=item['price'],
                        quantity=item['quantity'],
                    )
            cart.clear()
            messages.success(request, f'Заказ №{order.id} успешно оформлен.')
            return redirect('orders:order_detail', order_id=order.id)
        delivery_method = request.POST.get('delivery_method', Order.DELIVERY_STANDARD)
    else:
        form = OrderCreateForm(initial=initial)
        delivery_method = Order.DELIVERY_STANDARD
    context = {
        'form': form,
        'cart': cart,
        **_checkout_summary(cart, delivery_method),
    }
    return render(request, 'orders/order_create.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_history.html', {'orders': orders})
