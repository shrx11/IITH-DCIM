from unittest import skipIf

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from extras.plugins import PluginMenu, get_plugin_config
from extras.tests.dummy_plugin import config as dummy_config
from netbox.graphql.schema import Query
from netbox.registry import registry


@skipIf('extras.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
class PluginTest(TestCase):

    def test_config(self):

        self.assertIn('extras.tests.dummy_plugin.DummyPluginConfig', settings.INSTALLED_APPS)

    def test_models(self):
        from extras.tests.dummy_plugin.models import DummyModel

        # Test saving an instance
        instance = DummyModel(name='Instance 1', number=100)
        instance.save()
        self.assertIsNotNone(instance.pk)

        # Test deleting an instance
        instance.delete()
        self.assertIsNone(instance.pk)

    def test_admin(self):

        # Test admin view URL resolution
        url = reverse('admin:dummy_plugin_dummymodel_add')
        self.assertEqual(url, '/admin/dummy_plugin/dummymodel/add/')

    def test_views(self):

        # Test URL resolution
        url = reverse('plugins:dummy_plugin:dummy_models')
        self.assertEqual(url, '/plugins/dummy-plugin/models/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_api_views(self):

        # Test URL resolution
        url = reverse('plugins-api:dummy_plugin-api:dummymodel-list')
        self.assertEqual(url, '/api/plugins/dummy-plugin/dummy-models/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_registered_views(self):

        # Test URL resolution
        url = reverse('dcim:site_extra', kwargs={'pk': 1})
        self.assertEqual(url, '/dcim/sites/1/other-stuff/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_menu(self):
        """
        Check menu registration.
        """
        menu = registry['plugins']['menus'][0]
        self.assertIsInstance(menu, PluginMenu)
        self.assertEqual(menu.label, 'Dummy Plugin')

    def test_menu_items(self):
        """
        Check menu_items registration.
        """
        self.assertIn('Dummy plugin', registry['plugins']['menu_items'])
        menu_items = registry['plugins']['menu_items']['Dummy plugin']
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(len(menu_items[0].buttons), 2)

    def test_template_extensions(self):
        """
        Check that plugin TemplateExtensions are registered.
        """
        from extras.tests.dummy_plugin.template_content import SiteContent

        self.assertIn(SiteContent, registry['plugins']['template_extensions']['dcim.site'])

    def test_user_preferences(self):
        """
        Check that plugin UserPreferences are registered.
        """
        self.assertIn('dummy_plugin', registry['plugins']['preferences'])
        user_preferences = registry['plugins']['preferences']['dummy_plugin']
        self.assertEqual(type(user_preferences), dict)
        self.assertEqual(list(user_preferences.keys()), ['pref1', 'pref2'])

    def test_middleware(self):
        """
        Check that plugin middleware is registered.
        """
        self.assertIn('extras.tests.dummy_plugin.middleware.DummyMiddleware', settings.MIDDLEWARE)

    def test_queues(self):
        """
        Check that plugin queues are registered with the accurate name.
        """
        self.assertIn('extras.tests.dummy_plugin.testing-low', settings.RQ_QUEUES)
        self.assertIn('extras.tests.dummy_plugin.testing-medium', settings.RQ_QUEUES)
        self.assertIn('extras.tests.dummy_plugin.testing-high', settings.RQ_QUEUES)

    def test_min_version(self):
        """
        Check enforcement of minimum NetBox version.
        """
        with self.assertRaises(ImproperlyConfigured):
            dummy_config.validate({}, '0.9')

    def test_max_version(self):
        """
        Check enforcement of maximum NetBox version.
        """
        with self.assertRaises(ImproperlyConfigured):
            dummy_config.validate({}, '10.0')

    def test_required_settings(self):
        """
        Validate enforcement of required settings.
        """
        class DummyConfigWithRequiredSettings(dummy_config):
            required_settings = ['foo']

        # Validation should pass when all required settings are present
        DummyConfigWithRequiredSettings.validate({'foo': True}, settings.VERSION)

        # Validation should fail when a required setting is missing
        with self.assertRaises(ImproperlyConfigured):
            DummyConfigWithRequiredSettings.validate({}, settings.VERSION)

    def test_default_settings(self):
        """
        Validate population of default config settings.
        """
        class DummyConfigWithDefaultSettings(dummy_config):
            default_settings = {
                'bar': 123,
            }

        # Populate the default value if setting has not been specified
        user_config = {}
        DummyConfigWithDefaultSettings.validate(user_config, settings.VERSION)
        self.assertEqual(user_config['bar'], 123)

        # Don't overwrite specified values
        user_config = {'bar': 456}
        DummyConfigWithDefaultSettings.validate(user_config, settings.VERSION)
        self.assertEqual(user_config['bar'], 456)

    def test_graphql(self):
        """
        Validate the registration and operation of plugin-provided GraphQL schemas.
        """
        from extras.tests.dummy_plugin.graphql import DummyQuery

        self.assertIn(DummyQuery, registry['plugins']['graphql_schemas'])
        self.assertTrue(issubclass(Query, DummyQuery))

    @override_settings(PLUGINS_CONFIG={'extras.tests.dummy_plugin': {'foo': 123}})
    def test_get_plugin_config(self):
        """
        Validate that get_plugin_config() returns config parameters correctly.
        """
        plugin = 'extras.tests.dummy_plugin'
        self.assertEqual(get_plugin_config(plugin, 'foo'), 123)
        self.assertEqual(get_plugin_config(plugin, 'bar'), None)
        self.assertEqual(get_plugin_config(plugin, 'bar', default=456), 456)
