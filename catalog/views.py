from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Kefir, KefirType, Cart, CartItem
from .forms import KefirForm


# Кефиры
def kefir_list(request):
    sort_by = request.GET.get('sort', 'brand')
    direction = request.GET.get('direction', 'asc')
    filter_type = request.GET.get('type')
    flavor_filter = request.GET.get('flavor')

    kefirs = Kefir.objects.all()

    if filter_type:
        kefirs = kefirs.filter(kefir_type__id=filter_type)

    if flavor_filter:
        kefirs = kefirs.filter(extra_flavor=flavor_filter)

    order_prefix = '' if direction == 'asc' else '-'

    if sort_by == 'brand':
        kefirs = kefirs.order_by(f'{order_prefix}brand__name')
    elif sort_by == 'fat_content':
        kefirs = kefirs.order_by(f'{order_prefix}fat_content')
    elif sort_by == 'extra_flavor':
        kefirs = kefirs.order_by(f'{order_prefix}extra_flavor')

    flavors = Kefir.objects.exclude(extra_flavor__isnull=True).exclude(
        extra_flavor__exact='').values_list('extra_flavor', flat=True).distinct()
    kefir_types = KefirType.objects.all()

    return render(request, 'catalog/home.html', {
        'kefirs': kefirs,
        'kefir_types': kefir_types,
        'flavors': flavors,
        'current_sort': sort_by,
        'current_dir': direction,
        'current_type': int(filter_type) if filter_type else None,
        'current_flavor': flavor_filter,
    })


def kefir_detail(request, pk):
    kefir = get_object_or_404(Kefir, pk=pk)
    can_delete = request.user.is_authenticated and hasattr(request.user, 'userprofile') and \
        (request.user.userprofile.role == 'admin' or
         (request.user.userprofile.role == 'merchandiser' and kefir.created_by == request.user))

    return render(request, 'catalog/kefir_detail.html', {
        'kefir': kefir,
        'can_delete': can_delete
    })


def about(request):
    return render(request, 'catalog/about.html')


# Менеджер по продажам (корзина)
@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['sales_manager', 'admin'])
def add_to_cart(request, pk):
    kefir = get_object_or_404(Kefir, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(cart=cart, kefir=kefir)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    messages.success(request, f'Добавлено {quantity} шт. товара в корзину')
    return redirect('cart_view')


@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['sales_manager', 'admin'])
def cart_view(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if not cart:
        cart = Cart.objects.create(user=request.user, is_active=True)
    return render(request, 'catalog/cart.html', {'cart': cart})


@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['sales_manager', 'admin'])
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество товара обновлено')
        else:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')

    return redirect('cart_view')


@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['sales_manager', 'admin'])
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart_view')


@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['sales_manager', 'admin'])
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    cart.is_active = False
    cart.save()
    messages.success(request, 'Заказ успешно оформлен')
    return render(request, 'catalog/order_confirmation.html', {'cart': cart})


# Мерчендайзер (манипуляции с товарами)
@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['merchandiser', 'admin'])
def add_kefir(request):
    if request.user.userprofile.role == 'sales_manager':
        raise PermissionDenied

    if request.method == 'POST':
        form = KefirForm(request.POST, request.FILES)
        if form.is_valid():
            kefir = form.save(commit=False)
            kefir.save(user=request.user)
            messages.success(request, 'Товар успешно добавлен')
            return redirect('kefir_detail', pk=kefir.pk)
    else:
        form = KefirForm()
    return render(request, 'catalog/edit_kefir.html', {'form': form})


@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['merchandiser', 'admin'])
def edit_kefir(request, pk):
    kefir = get_object_or_404(Kefir, pk=pk)

    # проверка прав на редактирование
    if request.user.userprofile.role == 'merchandiser' and kefir.created_by != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = KefirForm(request.POST, request.FILES, instance=kefir)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect('kefir_detail', pk=pk)
    else:
        form = KefirForm(instance=kefir)

    can_delete = request.user.userprofile.role == 'admin' or \
        (request.user.userprofile.role == 'merchandiser' and kefir.created_by == request.user)

    return render(request, 'catalog/edit_kefir.html', {
        'form': form,
        'kefir': kefir,
        'can_delete': can_delete
    })


# удаление на домашней странице
@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['merchandiser', 'admin'])
def delete_selected_kefirs(request):
    if request.method == 'POST':
        kefir_ids = request.POST.get('kefir_ids', '')

        if not kefir_ids:
            messages.error(request, 'Не выбрано ни одного товара для удаления')
            return redirect('home')

        try:
            kefir_ids = [int(id.strip()) for id in kefir_ids.split(',') if id.strip().isdigit()]
        except (ValueError, AttributeError):
            messages.error(request, 'Некорректный список товаров')
            return redirect('home')

        if not kefir_ids:
            messages.error(request, 'Некорректный список товаров')
            return redirect('home')

        if request.user.userprofile.role == 'merchandiser':
            kefirs_to_delete = Kefir.objects.filter(
                id__in=kefir_ids,
                created_by=request.user
            )
            deleted_count = kefirs_to_delete.count()
            kefirs_to_delete.delete()
        else:  # админ может удалять любые товары
            deleted_count, _ = Kefir.objects.filter(id__in=kefir_ids).delete()

        messages.success(request, f'Удалено {deleted_count} товаров')
        return redirect('home')

    return redirect('home')


# удаление на странице товара
@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role in ['merchandiser', 'admin'])
def delete_kefir(request, pk):
    kefir = get_object_or_404(Kefir, pk=pk)

    # проверка прав на удаление
    if request.user.userprofile.role == 'merchandiser' and kefir.created_by != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        kefir.delete()
        messages.success(request, 'Товар успешно удален')
        return redirect('home')

    return redirect('kefir_detail', pk=pk)


# поиск
def search_kefir(request):
    query = request.GET.get('q', '')

    if query:
        results = Kefir.objects.filter(
            Q(brand__name__icontains=query) |
            Q(kefir_type__name__icontains=query) |
            Q(volume__icontains=query) |
            Q(fat_content__icontains=query)
        ).distinct()
    else:
        results = Kefir.objects.none()

    context = {
        'results': results,
        'query': query,
    }
    return render(request, 'catalog/search_results.html', context)
