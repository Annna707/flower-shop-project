from .models import Category


def catalog_nav(request):
    return {
        'categories': Category.objects.all(),
        'search_query': request.GET.get('q', ''),
    }
