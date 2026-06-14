from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Конкретные префиксы — до каталога на '', иначе /cart/ станет slug категории
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('users/', include('apps.users.urls')),
    path('', include('apps.catalog.urls')),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += staticfiles_urlpatterns()
    # запасной путь к static/ (если finders не сработали)
    urlpatterns += [
        re_path(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': settings.BASE_DIR / 'static'},
        ),
    ]

# Картинки товаров лежат в media/ и должны отдаваться и на хостинге (DEBUG=False).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)