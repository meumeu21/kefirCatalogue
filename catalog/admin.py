from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Kefir, KefirType, KefirBrand, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    
    def get_role(self, obj):
        return obj.userprofile.role
    get_role.short_description = 'Роль'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(KefirType)
class KefirTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(KefirBrand)
class KefirBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Kefir)
class KefirAdmin(admin.ModelAdmin):
    list_display = ('brand', 'fat_content', 'volume', 'price', 'is_lactose_free')
    list_filter = ('is_lactose_free', 'kefir_type')
    search_fields = ('brand', 'article')
    fieldsets = (
        (None, {
            'fields': ('article', 'brand', 'kefir_type')
        }),
        ('Характеристики', {
            'fields': ('fat_content', 'volume', 'is_lactose_free', 'shelf_life', 'extra_flavor')
        }),
        ('Цены', {
            'fields': ('price', 'small_wholesale_price', 'small_wholesale_min_qty', 
                      'large_wholesale_price', 'large_wholesale_min_qty')
        }),
        ('Дополнительно', {
            'fields': ('description', 'image')
        }),
    )