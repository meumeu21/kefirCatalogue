from django.test import TestCase
from django.urls import reverse
from catalog.models import Kefir, KefirType, KefirBrand
from http import HTTPStatus

class RouteTests(TestCase):
    def setUp(self):
        self.type = KefirType.objects.create(name="Классический")
        self.brand = KefirBrand.objects.create(name="Простоквашино")
        self.kefir = Kefir.objects.create(
            article="1234",
            brand=self.brand,
            fat_content=2.5,
            volume=500,
            shelf_life=10,
            kefir_type=self.type,
            price=79.99
        )

    def test_home_route(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_kefir_detail_route(self):
        response = self.client.get(reverse('kefir_detail', args=[self.kefir.pk]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_route(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
