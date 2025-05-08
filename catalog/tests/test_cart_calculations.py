from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Kefir, Cart, CartItem, UserProfile, KefirType, KefirBrand


class CartCalculationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kefir_type = KefirType.objects.create(name='Обычный')
        cls.kefir_brand = KefirBrand.objects.create(name='Тестовый бренд')

        cls.user = User.objects.create_user(username='testuser', password='password')
        UserProfile.objects.create(user=cls.user, role='sales_manager')

        cls.kefir1 = Kefir.objects.create(
            article='TEST1',
            brand=cls.kefir_brand,
            fat_content=2.5,
            volume=500,
            kefir_type=cls.kefir_type,
            price=100,
            small_wholesale_price=90,
            small_wholesale_min_qty=10,
            large_wholesale_price=80,
            large_wholesale_min_qty=50
        )

        cls.kefir2 = Kefir.objects.create(
            article='TEST2',
            brand=cls.kefir_brand,
            fat_content=1.5,
            volume=300,
            kefir_type=cls.kefir_type,
            price=200,
            small_wholesale_price=180,
            small_wholesale_min_qty=5,
            large_wholesale_price=150,
            large_wholesale_min_qty=20
        )

        cls.kefir3 = Kefir.objects.create(
            article='TEST3',
            brand=cls.kefir_brand,
            fat_content=3.2,
            volume=1000,
            kefir_type=cls.kefir_type,
            price=300,
            small_wholesale_price=270,
            small_wholesale_min_qty=8,
            large_wholesale_price=240,
            large_wholesale_min_qty=30
        )

    def setUp(self):
        self.client.login(username='testuser', password='password')
        self.cart = Cart.objects.create(user=self.user, is_active=True)

    def test_cart_calculations(self):
        CartItem.objects.create(cart=self.cart, kefir=self.kefir1, quantity=1)  # розница
        CartItem.objects.create(cart=self.cart, kefir=self.kefir2, quantity=5)  # мелкий опт (5+)
        CartItem.objects.create(cart=self.cart, kefir=self.kefir3, quantity=30)  # крупный опт (20+)

        response = self.client.get(reverse('cart_view'))

        self.assertEqual(self.cart.total_price(), (1*100) + (5*180) + (30*240))

        items = self.cart.items.all()
        self.assertEqual(items[0].get_price_type(), 'розница')
        self.assertEqual(items[1].get_price_type(), 'мелкий опт')
        self.assertEqual(items[2].get_price_type(), 'крупный опт')

        self.assertContains(response, f"{self.cart.total_price()} руб.")
