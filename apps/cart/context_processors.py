from .cart import Cart

def cart_total_items(request):
    if request.session.get('cart'):
        cart = Cart(request)
        return {'cart_total_items': len(cart)}
    return {'cart_total_items': 0}