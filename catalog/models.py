from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class KefirType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Тип кефира")

    def __str__(self):
        return self.name


class KefirBrand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Бренд кефира", default="Вкусвилл")

    def __str__(self):
        return self.name


class Kefir(models.Model):
    article = models.CharField(max_length=20, unique=True, verbose_name="Артикул", null=False, blank=False)
    brand = models.ForeignKey(KefirBrand, on_delete=models.PROTECT, verbose_name="Бренд")
    fat_content = models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                      max_digits=3, decimal_places=1, verbose_name="Жирность (%)",
                                      default=2.5)
    volume = models.PositiveIntegerField(validators=[MinValueValidator(0)],
                                         verbose_name="Объем (мл)", default=500)
    is_lactose_free = models.BooleanField(default=False, verbose_name="Безлактозный")
    shelf_life = models.PositiveIntegerField(validators=[MinValueValidator(0)],
                                             verbose_name="Срок годности (дни)", default=7)
    kefir_type = models.ForeignKey(KefirType, on_delete=models.PROTECT, verbose_name="Тип кефира")
    extra_flavor = models.CharField(max_length=100, verbose_name="Дополнительный вкус",
                                    blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='kefir_images/', verbose_name="Изображение", blank=True, null=True)

    price = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=6, decimal_places=2,
                                verbose_name="Розничная цена", default=250)
    small_wholesale_price = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=6,
                                                decimal_places=2, verbose_name="Мелкооптовая цена",
                                                default=220)
    small_wholesale_min_qty = models.PositiveIntegerField(verbose_name="Мин. кол-во для мелкого опта",
                                                          default=10)
    large_wholesale_price = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=6,
                                                decimal_places=2, verbose_name="Крупнооптовая цена",
                                                default=200)
    large_wholesale_min_qty = models.PositiveIntegerField(verbose_name="Мин. кол-во для крупного опта",
                                                          default=50)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, verbose_name="Создатель")

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if not self.pk and user:
            self.created_by = user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.volume}мл, {self.fat_content}%"


class UserProfile(models.Model):
    USER_ROLES = (
        ('admin', 'Администратор'),
        ('merchandiser', 'Товаровед'),
        ('sales_manager', 'Менеджер по продажам'),
        ('guest', 'Гость'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='guest')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def total_price(self):
        """Общая стоимость всех товаров в корзине с учетом оптовых цен"""
        return sum(item.total_price() for item in self.items.all())

    def get_items_count(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    kefir = models.ForeignKey(Kefir, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_current_price(self):
        """Возвращает цену за единицу в зависимости от количества"""
        if self.quantity >= self.kefir.large_wholesale_min_qty:
            return self.kefir.large_wholesale_price
        elif self.quantity >= self.kefir.small_wholesale_min_qty:
            return self.kefir.small_wholesale_price
        return self.kefir.price

    def total_price(self):
        """Общая стоимость позиции с учетом оптовых цен"""
        return self.quantity * self.get_current_price()

    def get_price_type(self):
        """Тип цены (розница, мелкий опт, крупный опт)"""
        if self.quantity >= self.kefir.large_wholesale_min_qty:
            return "крупный опт"
        elif self.quantity >= self.kefir.small_wholesale_min_qty:
            return "мелкий опт"
        return "розница"

    def __str__(self):
        return f"{self.quantity} x {self.kefir} ({self.get_price_type()})"
