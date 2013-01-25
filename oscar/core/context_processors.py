from django.conf import settings


def get_display_direction(request):
    if request.LANGUAGE_CODE == 'ar':
        return 'rtl'
    else:
        return 'ltr'

def metadata(request):
    """
    Add some generally useful metadata to the template context
    """
    return {'display_version': getattr(settings, 'DISPLAY_VERSION', False),
            'version': getattr(settings, 'VERSION', 'N/A'),
            'shop_name': settings.OSCAR_SHOP_NAME,
            'shop_tagline': settings.OSCAR_SHOP_TAGLINE,
            'use_less': getattr(settings, 'USE_LESS', True),
            'google_analytics_id': getattr(settings,
                                           'GOOGLE_ANALYTICS_ID', None),
            'display_direction': get_display_direction(request)}
