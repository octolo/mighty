from django.test import TestCase

# Create your tests here.
class FileSystemTestCase(TestCase):
    def test_tenant_file_version(self):
        from easyshares.models import Tenant
        tenant = Tenant.objects.first()
        print(tenant.file_version())