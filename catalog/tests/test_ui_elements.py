from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Kefir, UserProfile, KefirType, KefirBrand

class UIElementsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.kefir_type = KefirType.objects.create(name='Обычный')
        cls.kefir_brand = KefirBrand.objects.create(name='Тестовый бренд')
        
        cls.admin = User.objects.create_user(username='admin', password='password')
        UserProfile.objects.create(user=cls.admin, role='admin')
        
        cls.merchandiser = User.objects.create_user(username='merchandiser', password='password')
        UserProfile.objects.create(user=cls.merchandiser, role='merchandiser')
        
        cls.sales_manager = User.objects.create_user(username='sales_manager', password='password')
        UserProfile.objects.create(user=cls.sales_manager, role='sales_manager')
        
        cls.kefir = Kefir.objects.create(
            article='TEST123',
            brand=cls.kefir_brand,
            fat_content=2.5,
            volume=500,
            kefir_type=cls.kefir_type,
            created_by=cls.merchandiser
        )

    # функция для счета фраз на странице
    def assert_phrase_count(self, response, phrase, expected_count):
        content = response.content.decode('utf-8')
        actual_count = content.count(phrase)
        self.assertEqual(
            actual_count, expected_count,
            f"'{phrase}' встречается {actual_count} раз(а), ожидалось {expected_count}"
        )

    def test_home_page_elements_for_sales_manager(self):
        self.client.login(username='sales_manager', password='password')
        response = self.client.get(reverse('home'))
        
        self.assertContains(response, 'В корзину')
        self.assertNotContains(response, 'Добавить товар')
        self.assert_phrase_count(response, 'Выбрать товары для удаления', 2)

    def test_home_page_elements_for_merchandiser(self):
        self.client.login(username='merchandiser', password='password')
        response = self.client.get(reverse('home'))
        
        self.assertContains(response, 'Добавить товар')
        self.assert_phrase_count(response, 'Выбрать товары для удаления', 3)
        self.assertNotContains(response, 'В корзину')

    def test_home_page_elements_for_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('home'))
        
        self.assertContains(response, 'Добавить товар')
        self.assert_phrase_count(response, 'Выбрать товары для удаления', 3)
        self.assertContains(response, 'В корзину')

    def test_kefir_detail_page_elements(self):
        self.client.login(username='sales_manager', password='password')
        response = self.client.get(reverse('kefir_detail', args=[self.kefir.pk]))
        self.assertContains(response, 'Добавить в корзину')
        self.assertNotContains(response, 'Редактировать товар')
        
        self.client.login(username='merchandiser', password='password')
        response = self.client.get(reverse('kefir_detail', args=[self.kefir.pk]))
        self.assertContains(response, 'Редактировать товар')
        self.assertContains(response, 'Удалить товар')
        
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('kefir_detail', args=[self.kefir.pk]))
        self.assertContains(response, 'Добавить в корзину')
        self.assertContains(response, 'Редактировать товар')
        self.assertContains(response, 'Удалить товар')