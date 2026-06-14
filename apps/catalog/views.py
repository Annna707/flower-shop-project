from django.shortcuts import render, get_object_or_404
from apps.cart.cart import Cart
from .models import Category, Product


HERO_FEATURE_SLUGS = (
    'nezhnyj-rassvet',
    'nevesta-belosnezhka',
    'tyulpany-gollandiya',
)


def _annotate_available_stock(products, cart):
    for product in products:
        product.available_stock = cart.get_available_stock(product)
    return products


def _get_hero_features():
    products = Product.objects.filter(slug__in=HERO_FEATURE_SLUGS, available=True)
    by_slug = {product.slug: product for product in products}
    return [by_slug.get(slug) for slug in HERO_FEATURE_SLUGS]


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    # фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q', '').strip()
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search_query:
        products = products.filter(name__icontains=search_query)
    cart = Cart(request)
    _annotate_available_stock(products, cart)
    hero_features = _get_hero_features()
    return render(request, 'catalog/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'hero_hit': hero_features[0],
        'hero_wedding': hero_features[1],
        'hero_promo': hero_features[2],
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    cart = Cart(request)
    product.available_stock = cart.get_available_stock(product)
    return render(request, 'catalog/product_detail.html', {'product': product})