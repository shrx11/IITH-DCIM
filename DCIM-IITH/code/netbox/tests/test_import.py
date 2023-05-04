from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from dcim.models import *
from users.models import ObjectPermission
from utilities.choices import ImportFormatChoices
from utilities.testing import ModelViewTestCase, create_tags


class CSVImportTestCase(ModelViewTestCase):
    model = Region

    @classmethod
    def setUpTestData(cls):
        create_tags('Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo')

    def _get_csv_data(self, csv_data):
        return '\n'.join(csv_data)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_valid_tags(self):
        csv_data = (
            'name,slug,tags',
            'Region 1,region-1,"alpha,bravo"',
            'Region 2,region-2,"charlie,delta"',
            'Region 3,region-3,echo',
            'Region 4,region-4,',
        )

        data = {
            'format': ImportFormatChoices.CSV,
            'data': self._get_csv_data(csv_data),
        }

        # Assign model-level permission
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(self._get_url('import')), 200)

        # Test POST with permission
        self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
        regions = Region.objects.all()
        self.assertEqual(regions.count(), 4)
        region = Region.objects.get(slug="region-4")
        self.assertEqual(
            list(regions[0].tags.values_list('name', flat=True)),
            ['Alpha', 'Bravo']
        )
        self.assertEqual(
            list(regions[1].tags.values_list('name', flat=True)),
            ['Charlie', 'Delta']
        )
        self.assertEqual(
            list(regions[2].tags.values_list('name', flat=True)),
            ['Echo']
        )
        self.assertEqual(regions[3].tags.count(), 0)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_invalid_tags(self):
        csv_data = (
            'name,slug,tags',
            'Region 1,region-1,"Alpha,Bravo"',  # Valid
            'Region 2,region-2,"Alpha,Tango"',  # Invalid
        )

        data = {
            'format': ImportFormatChoices.CSV,
            'data': self._get_csv_data(csv_data),
        }

        # Assign model-level permission
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(self._get_url('import')), 200)

        # Test POST with permission
        self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
        self.assertEqual(Region.objects.count(), 0)
