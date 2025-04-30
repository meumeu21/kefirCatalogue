from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Kefir, UserProfile, KefirType, KefirBrand
from http import HTTPStatus

class ProductManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kefir_type = KefirType.objects.create(name='Обычный')
        cls.kefir_brand = KefirBrand.objects.create(name='Тестовый бренд')
        
        cls.merchandiser = User.objects.create_user(username='merchandiser', password='password')
        UserProfile.objects.create(user=cls.merchandiser, role='merchandiser')
        
        cls.admin = User.objects.create_user(username='admin', password='password')
        UserProfile.objects.create(user=cls.admin, role='admin')

    def test_add_product(self):
        self.client.login(username='merchandiser', password='password')
        
        response = self.client.post(reverse('add_kefir'), {
        'article': 'NEW123',
        'brand': self.kefir_brand.id,
        'fat_content': 2.5,
        'volume': 500,
        'kefir_type': self.kefir_type.id,
        'price': 100,
        'small_wholesale_price': 90,
        'small_wholesale_min_qty': 10,
        'large_wholesale_price': 80,
        'large_wholesale_min_qty': 50,
        'is_lactose_free': False,
        'shelf_life': 7,
    }, follow=True)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Kefir.objects.filter(article='NEW123').exists())
        
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'NEW123')

    def test_delete_product(self):
        kefir = Kefir.objects.create(
            article='TODELETE',
            brand=self.kefir_brand,
            fat_content=2.5,
            volume=500,
            kefir_type=self.kefir_type,
            created_by=self.merchandiser
        )
        
        self.client.login(username='merchandiser', password='password')
        
        response = self.client.post(reverse('delete_kefir', args=[kefir.pk]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Kefir.objects.filter(article='TODELETE').exists())
        
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'TODELETE')

    def test_admin_can_delete_any_product(self):
        kefir = Kefir.objects.create(
            article='ADMINDELETE',
            brand=self.kefir_brand,
            fat_content=2.5,
            volume=500,
            kefir_type=self.kefir_type,
            created_by=self.merchandiser
        )
        
        self.client.login(username='admin', password='password')
        
        response = self.client.post(reverse('delete_kefir', args=[kefir.pk]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Kefir.objects.filter(article='ADMINDELETE').exists())