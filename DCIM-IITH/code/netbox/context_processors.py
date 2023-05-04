from django.conf import settings as django_settings

from netbox.config import get_config
from netbox.registry import registry


def settings_and_registry(request):
    """
    Expose Django settings and NetBox registry stores in the template context. Example: {{ settings.DEBUG }}
    """
    return {
        'settings': django_settings,
        'config': get_config(),
        'registry': registry,
        'preferences': request.user.config if request.user.is_authenticated else {},
    }
