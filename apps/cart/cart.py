from decimal import Decimal
from django.conf import settings
from apps.catalog.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self._remove_stale_items()
        self._sanitize_cart_items()

    def _sanitize_cart_items(self):
        dirty = False
        for product_id, item in list(self.cart.items()):
            if set(item.keys()) != {'quantity', 'price'}:
                dirty = True
            self.cart[product_id] = {
                'quantity': int(item['quantity']),
                'price': str(item['price']),
            }
        if dirty:
            self.save()

    def _remove_stale_items(self):
        if not self.cart:
            return
        product_ids = [pid for pid in self.cart if str(pid).isdigit()]
        if not product_ids:
            self.clear()
            return
        valid_ids = {
            str(pk) for pk in Product.objects.filter(
                id__in=product_ids,
            ).values_list('id', flat=True)
        }
        stale_ids = [pid for pid in self.cart if pid not in valid_ids]
        for product_id in stale_ids:
            del self.cart[product_id]
        if stale_ids:
            self.save()

    def get_quantity(self, product):
        item = self.cart.get(str(product.id))
        return item['quantity'] if item else 0

    def get_available_stock(self, product):
        return max(0, product.stock - self.get_quantity(product))

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        if not self.cart:
            return
        products = Product.objects.filter(id__in=self.cart.keys())
        product_map = {str(product.id): product for product in products}
        for product_id, item in self.cart.items():
            product = product_map.get(str(product_id))
            if not product:
                continue
            price = Decimal(item['price'])
            quantity = item['quantity']
            yield {
                'product': product,
                'price': price,
                'quantity': quantity,
                'total_price': price * quantity,
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()