from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Kefir, UserProfile, KefirType, KefirBrand
from http import HTTPStatus

class PermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kefir_type = KefirType.objects.create(name='Обычный')
        cls.kefir_brand = KefirBrand.objects.create(name='Тестовый бренд')
        
        cls.admin = User.objects.create_user(username='admin', password='password')
        UserProfile.objects.create(user=cls.admin, role='admin')
        
        cls.merchandiser = User.objects.create_user(username='merchandiser', password='password')
        UserProfile.objects.create(user=cls.merchandiser, role='merchandiser')
        
        cls.sales_manager = User.objects.create_user(username='sales_manager', password='password')
        UserProfile.objects.create(user=cls.sales_manager, role='sales_manager')
        
        cls.guest_client = Client()
        cls.admin_client = Client()
        cls.admin_client.login(username='admin', password='password')
        cls.merchandiser_client = Client()
        cls.merchandiser_client.login(username='merchandiser', password='password')
        cls.sales_manager_client = Client()
        cls.sales_manager_client.login(username='sales_manager', password='password')
        
        cls.kefir = Kefir.objects.create(
            article='TEST123',
            brand=cls.kefir_brand,
            fat_content=2.5,
            volume=500,
            is_lactose_free=False,
            shelf_life=7,
            kefir_type=cls.kefir_type,
            price=100,
            small_wholesale_price=90,
            small_wholesale_min_qty=10,
            large_wholesale_price=80,
            large_wholesale_min_qty=50,
            created_by=cls.merchandiser
        )

    def test_guest_permissions(self):
        urls = [
            reverse('add_kefir'),
            reverse('edit_kefir', args=[self.kefir.pk]),
            reverse('delete_kefir', args=[self.kefir.pk]),
            reverse('delete_selected_kefirs'),
            reverse('add_to_cart', args=[self.kefir.pk]),
            reverse('cart_view'),
            reverse('checkout'),
        ]
        
        for url in urls:
            response = self.guest_client.get(url)
            self.assertNotEqual(response.status_code, HTTPStatus.OK)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_merchandiser_permissions(self):
        response = self.merchandiser_client.get(reverse('add_kefir'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        response = self.merchandiser_client.get(reverse('edit_kefir', args=[self.kefir.pk]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        other_kefir = Kefir.objects.create(
            article='OTHER123',
            brand=self.kefir_brand,
            fat_content=1.5,
            volume=300,
            kefir_type=self.kefir_type,
            created_by=self.admin
        )
        response = self.merchandiser_client.get(reverse('edit_kefir', args=[other_kefir.pk]))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_sales_manager_permissions(self):
        response = self.sales_manager_client.get(reverse('cart_view'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        response = self.sales_manager_client.get(reverse('add_kefir'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_admin_permissions(self):
        response = self.admin_client.get(reverse('add_kefir'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        response = self.admin_client.get(reverse('cart_view'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        response = self.admin_client.get(reverse('edit_kefir', args=[self.kefir.pk]))
        self.assertEqual(response.status_code, HTTPStatus.OK)