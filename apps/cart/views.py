from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        override = cd['override']
        in_cart = cart.get_quantity(product)
        new_total = quantity if override else in_cart + quantity

        if new_total > product.stock:
            available = cart.get_available_stock(product)
            message = (
                f'Доступно только {available} шт.'
                if available
                else 'Товар закончился'
            )
            if _is_ajax(request):
                return JsonResponse({
                    'success': False,
                    'message': message,
                    'available_stock': available,
                    'product_id': product.id,
                }, status=400)
            return redirect('cart:cart_detail')

        cart.add(product=product, quantity=quantity, override_quantity=override)
        available = cart.get_available_stock(product)
        if _is_ajax(request):
            return JsonResponse({
                'success': True,
                'message': f'«{product.name}» добавлен в корзину',
                'cart_total_items': len(cart),
                'product_name': product.name,
                'product_id': product.id,
                'available_stock': available,
                'in_cart_quantity': cart.get_quantity(product),
            })
    if _is_ajax(request):
        return JsonResponse(
            {'success': False, 'message': 'Не удалось добавить товар в корзину'},
            status=400,
        )
    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})