from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from catalog.models import Kefir, KefirType, KefirBrand
from django.urls import reverse


class ContentTests(TestCase):
    def setUp(self):
        self.type1 = KefirType.objects.create(name="Классический")
        self.brand1 = KefirBrand.objects.create(name="БиоБаланс")
        self.type2 = KefirType.objects.create(name="Фруктовый")
        self.brand2 = KefirBrand.objects.create(name="Агуша")
        self.type3 = KefirType.objects.create(name="Шоколадный")
        self.brand3 = KefirBrand.objects.create(name="Ю")
        self.kefir1 = Kefir.objects.create(
            article="A1",
            brand=self.brand1,
            fat_content=1.0,
            volume=500,
            shelf_life=7,
            kefir_type=self.type1,
            price=60,
            extra_flavor="Клубника"
        )
        self.kefir2 = Kefir.objects.create(
            article="A2",
            brand=self.brand2,
            fat_content=3.2,
            volume=900,
            shelf_life=10,
            kefir_type=self.type2,
            price=80,
            extra_flavor="Ваниль"
        )
        self.kefir3 = Kefir.objects.create(
            article="A3",
            brand=self.brand3,
            fat_content=2.5,
            volume=1000,
            shelf_life=10,
            kefir_type=self.type3,
            price=80,
            extra_flavor="Шоколад"
        )
    
    # Создание товара
    # Создание правильных товаров
    def test_kefir_creation(self):
        self.assertEqual(Kefir.objects.count(), 3)
        self.assertEqual(self.kefir1.extra_flavor, "Клубника")
        self.assertEqual(self.kefir2.extra_flavor, "Ваниль")
        self.assertEqual(self.kefir3.extra_flavor, "Шоколад")

    # Создание товара без артикула
    def test_missing_article(self):
        kefir = Kefir(
            brand=self.brand1,
            fat_content=2.5,
            volume=500,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
            price=100
        )
        with self.assertRaises(ValidationError):
            kefir.full_clean()

    # Создание товара без бренда
    def test_missing_brand(self):
        with self.assertRaises(IntegrityError):
            Kefir.objects.create(
                article="123",
                fat_content=2.5,
                volume=500,
                is_lactose_free=False,
                shelf_life=10,
                kefir_type=self.type1,
                price=100,
            )

    # Создание товара без типа кефира
    def test_missing_kefir_type(self):
        with self.assertRaises(IntegrityError):
            Kefir.objects.create(
                article="123",
                brand=self.brand1,
                fat_content=2.5,
                volume=500,
                is_lactose_free=False,
                shelf_life=10,
                price=100,
            )

    # не вызовет ошибку из-за default значения
    def test_missing_fat_content(self):
        kefir = Kefir(
            article="123",
            brand=self.brand1,
            volume=500,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
            price=100,
        )
        kefir.full_clean()

    # не вызовет ошибку из-за default значения
    def test_missing_volume(self):
        kefir = Kefir(
            article="123",
            brand=self.brand1,
            fat_content=2.5,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
            price=100,
        )
        kefir.full_clean()

    # не вызовет ошибку из-за default значения
    def test_missing_is_lactose_free(self):
        kefir = Kefir(
            article="123",
            brand=self.brand1,
            fat_content=2.5,
            volume=500,
            shelf_life=10,
            kefir_type=self.type1,
            price=100,
        )
        kefir.full_clean()

    # не вызовет ошибку из-за default значения
    def test_missing_shelf_life(self):
        kefir = Kefir(
            article="123",
            brand=self.brand1,
            fat_content=2.5,
            volume=500,
            is_lactose_free=False,
            kefir_type=self.type1,
            price=100,
        )
        kefir.full_clean()

    # не вызовет ошибку из-за default значения
    def test_missing_price(self):
        kefir = Kefir(
            article="123",
            brand=self.brand1,
            fat_content=2.5,
            volume=500,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
        )
        kefir.full_clean()


    # Отрицательные значения
    # Отрицательный объем
    def test_negative_volume(self):
        kefir = Kefir(
            article="neg1",
            brand=self.brand1,
            fat_content=2.5,
            volume=-500,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
            price=100,
        )
        with self.assertRaises(ValidationError):
            kefir.full_clean()

    # Отрицательная жирность
    def test_negative_fat_content(self):
        kefir = Kefir(
            article="neg2",
            brand=self.brand1,
            fat_content=-1.0,
            volume=500,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
            price=100,
        )
        with self.assertRaises(ValidationError):
            kefir.full_clean()

    # Отрицательный срок годности
    def test_negative_shelf_life(self):
        kefir = Kefir(
            article="neg3",
            brand=self.brand1,
            fat_content=2.5,
            volume=500,
            is_lactose_free=False,
            shelf_life=-1,
            kefir_type=self.type1,
            price=100,
        )
        with self.assertRaises(ValidationError):
            kefir.full_clean()

    # Отрицательная цена
    def test_negative_price(self):
        kefir = Kefir(
            article="neg4",
            brand=self.brand1,
            fat_content=2.5,
            volume=500,
            is_lactose_free=False,
            shelf_life=10,
            kefir_type=self.type1,
            price=-50,
        )
        with self.assertRaises(ValidationError):
            kefir.full_clean()


    # Сортировки
    def test_sort_by_brand(self):
        response = self.client.get(reverse('home') + '?sort=brand')
        kefirs = list(response.context['kefirs'])
        
        expected_order = Kefir.objects.order_by('brand__name')
        expected_brands = [k.brand.name for k in expected_order]
        
        actual_brands = [k.brand.name for k in kefirs]
        self.assertEqual(actual_brands, expected_brands)

    def test_sort_by_fat_descending(self):
        response = self.client.get(reverse('home') + '?sort=fat_content&direction=desc')
        kefirs = list(response.context['kefirs'])
        
        expected_order = Kefir.objects.order_by('-fat_content')
        expected_fats = [k.fat_content for k in expected_order]
        
        actual_fats = [k.fat_content for k in kefirs]
        self.assertEqual(actual_fats, expected_fats)

    def test_filter_by_kefir_type(self):
        response = self.client.get(reverse('home') + f'?type={self.type1.id}')

        kefirs = list(response.context['kefirs'])
        expected_kefirs = Kefir.objects.filter(kefir_type=self.type1)

        self.assertEqual(list(kefirs), list(expected_kefirs))
        self.assertTrue(all(k.kefir_type == self.type1 for k in kefirs))

    def test_sort_by_extra_flavor_ascending(self):
        response = self.client.get(reverse('home') + '?sort=extra_flavor&direction=asc')
        kefirs = list(response.context['kefirs'])
        
        expected_order = Kefir.objects.order_by('extra_flavor')
        expected_flavors = [k.extra_flavor for k in expected_order]
        
        actual_flavors = [k.extra_flavor for k in kefirs]
        self.assertEqual(actual_flavors, expected_flavors)