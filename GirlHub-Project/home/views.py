# home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import validators
from .models import Profile, Message
from django.contrib import messages

from django.http import JsonResponse

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from PIL import Image, ImageDraw, ImageOps
import io
from django.core.files.base import ContentFile
from django.urls import reverse

from django.db.models import Q  # Добавляем импорт Q

from django.utils.dateparse import parse_datetime

@login_required
def settings(request):
    return render(request, 'account/setting.html')

@login_required
def change_email_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        new_email = request.POST.get('new_email')

        # Проверяем пароль пользователя
        user = authenticate(username=request.user.username, password=password)
        if user is None:
            messages.error(request, "Неверный пароль.")
            return redirect('account_change_email')  # Остаемся на той же странице

        # Проверка корректности нового email
        try:
            validate_email(new_email)
        except ValidationError:
            messages.error(request, "Некорректный формат электронной почты.")
            return redirect('account_change_email')

        # Устанавливаем новый email
        user.email = new_email
        user.save()

        # Сообщение об успешной смене email
        messages.success(request, "Email успешно изменен.")
        return redirect('account_change_email')  # Остаемся на странице изменения email

    return render(request, 'account/email.html', {'user': request.user})


@login_required
def change_username(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        new_username = request.POST.get('new_username')

        # Проверяем пароль пользователя
        user = authenticate(username=request.user.username, password=password)
        if user is None:
            messages.error(request, "Неверный пароль.")
            return redirect('account_change_username')  # Остаемся на той же странице

        if User.objects.filter(username=new_username).exists():
            messages.error(request, "Такой ник уже есть")
            return redirect('account_change_username')  # Остаемся на той же странице
        try:
            validators.UnicodeUsernameValidator(new_username)
            validators.ASCIIUsernameValidator(new_username)  # Не знаю, какой у нас стандарт
        except ValidationError:
            messages.error(request, "Некорректный формат ника.")
            return redirect('account_change_username')

        user.username = new_username
        user.save()

        # Сообщение об успешной смене email
        messages.success(request, "Username успешно изменен.")
        return redirect('account_change_username')  # Остаемся на странице изменения email

    return render(request, 'account/change_username.html', {'user': request.user})

@login_required
def check_new_messages(request):
    contacts_with_unread = []

    for contact in request.user.profile.contacts.all():
        unread_messages = Message.objects.filter(sender=contact.user, receiver=request.user, is_read=False)

        if unread_messages.exists():
            contacts_with_unread.append(contact.user.username)
    return JsonResponse({'contacts_with_unread': contacts_with_unread})

@login_required
def get_new_messages(request, chat_user=None):
    if not chat_user:
        return JsonResponse({"error": "chat_user parameter is missing"}, status=400)

    after_timestamp = request.GET.get('after_timestamp')
    after_id = int(request.GET.get('after_id', 0))

    try:
        chat_partner = User.objects.get(username=chat_user)
        if after_timestamp:
            after_datetime = parse_datetime(after_timestamp)
            if after_datetime is None:
                return JsonResponse({"error": "Invalid timestamp"}, status=400)

            messages_qs = Message.objects.filter(
                Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user)
            ).filter(
                Q(timestamp__gt=after_datetime) | (Q(timestamp=after_datetime) & Q(id__gt=after_id))
            ).order_by('timestamp', 'id')
        else:
            messages_qs = Message.objects.filter(
                Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user),
                is_read=False
            ).order_by('timestamp', 'id')

        new_messages = [{
            "id": message.id,
            "sender": message.sender.username,
            "content": message.content,
            "image_url": message.image.url if message.image else None,
            "timestamp": message.timestamp.isoformat()
        } for message in messages_qs]

        messages_qs.filter(receiver=request.user).update(is_read=True)

        return JsonResponse({"new_messages": new_messages})

    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

@login_required
def home_view(request):
    chat_user = request.GET.get('chat_with')
    messages_list = []

    if chat_user:
        try:
            chat_partner = User.objects.get(username=chat_user)

            initial_load_count = 20

            # Сортируем сообщения в порядке убывания timestamp и id
            messages_qs = Message.objects.filter(
                Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user)
            ).order_by('-timestamp', '-id')[:initial_load_count]

            # Преобразуем QuerySet в список и переворачиваем его
            messages_list = list(messages_qs)[::-1]

            # Помечаем непрочитанные сообщения как прочитанные
            Message.objects.filter(sender=chat_partner, receiver=request.user, is_read=False).update(is_read=True)

        except User.DoesNotExist:
            chat_user = None

    return render(request, 'home.html', {
        'username': request.user.username,
        'messages': messages_list,
        'chat_user': chat_user,
    })

def redirect_to_home(request):
    return redirect('/home/')

@login_required
def add_contact(request):
    if request.method == 'POST':
        contact_name = request.POST.get('contact_name')
        try:
            contact_user = User.objects.get(username=contact_name)
            profile = Profile.objects.get(user=request.user)
            profile.contacts.add(contact_user.profile)
            messages.success(request, f'Контакт {contact_name} успешно добавлен!')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким именем не найден.')
        return redirect('home')
    return redirect('home')

@login_required
def send_message(request):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        receiver_name = request.POST.get('receiver_name')
        image = request.FILES.get('image')

        try:
            receiver_user = User.objects.get(username=receiver_name)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver_user,
                content=message_content if message_content else None,
                image=image if image else None
            )
            message.save()
            return JsonResponse({'status': 'success', 'timestamp': message.timestamp.isoformat(), 'id': message.id})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Получатель не найден'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def change_image(request):
    if request.method == 'POST':
        if request.FILES.get('image'):
            image_file = request.FILES.get('image')
            size = (32, 32)
            # Создаем профиль пользователя с загруженным изображением
            profile = Profile.objects.get(user=request.user)
            profile.image.save(image_file.name, image_file, save=False)

            # Загружаем изображение с помощью PIL
            image = Image.open(profile.image)

            # Уменьшаем изображение до нужного размера
            image = image.resize(size, Image.Resampling.LANCZOS)

            # Создаем маску для обрезки по кругу
            mask = Image.new("L", size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, *size), fill=255)

            # Применяем маску и создаем итоговое изображение
            result = ImageOps.fit(image, size, centering=(0.5, 0.5))
            result.putalpha(mask)

            # Сохраняем изображение в формате PNG для сохранения прозрачности
            buffer = io.BytesIO()
            result.save(buffer, format='PNG')
            profile.image.save('profile_images.png', ContentFile(buffer.getvalue()))
            profile.save()
            image.close()
        return redirect('home')

    return render(request, 'account/change_image.html')

@login_required
def load_old_messages(request, chat_user):
    before_timestamp = request.GET.get('before_timestamp')
    before_id = int(request.GET.get('before_id', 0))
    limit = int(request.GET.get('limit', 20))

    try:
        chat_partner = User.objects.get(username=chat_user)

        # Parse the timestamp
        before_datetime = parse_datetime(before_timestamp)
        if before_datetime is None:
            return JsonResponse({"error": "Invalid timestamp"}, status=400)

        # Corrected filtering logic with proper grouping
        messages_qs = Message.objects.filter(
            Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user)
        ).filter(
            Q(timestamp__lt=before_datetime) | (Q(timestamp=before_datetime) & Q(id__lt=before_id))
        ).order_by('-timestamp', '-id')[:limit]

        # Since we are fetching messages in descending order, we need to reverse them for correct display
        messages = []
        for message in messages_qs:
            messages.append({
                "id": message.id,
                "sender": message.sender.username,
                "content": message.content,
                "image_url": message.image.url if message.image else None,
                "timestamp": message.timestamp.isoformat()
            })

        # Reverse the messages to display them in ascending order
        #messages.reverse() - Эта тварь все ломала! убейте

        return JsonResponse({"messages": messages})

    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)
