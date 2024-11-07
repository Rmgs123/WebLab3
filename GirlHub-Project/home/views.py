# home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Profile, Message
from django.contrib import messages

from django.http import JsonResponse

@login_required
def check_new_messages(request):
    contacts_with_unread = []
    for contact in request.user.profile.contacts.all():
        unread_messages = Message.objects.filter(sender=contact.user, receiver=request.user, is_read=False)
        if unread_messages.exists():
            contacts_with_unread.append(contact.user.username)
    return JsonResponse({'contacts_with_unread': contacts_with_unread})

@login_required
def get_new_messages(request, chat_user):
    sender = User.objects.get(username=chat_user)
    new_messages = Message.objects.filter(sender=sender, receiver=request.user, is_read=False)
    message_data = [{'content': msg.content, 'timestamp': msg.timestamp} for msg in new_messages]
    new_messages.update(is_read=True)  # Отметить все сообщения как прочитанные
    return JsonResponse({'new_messages': message_data})

@login_required
def home_view(request):
    chat_user = request.GET.get('chat_with')
    messages = []

    if chat_user:
        try:
            chat_partner = User.objects.get(username=chat_user)
            # Получаем все сообщения между текущим пользователем и выбранным контактом
            sent_messages = Message.objects.filter(sender=request.user, receiver=chat_partner)
            received_messages = Message.objects.filter(sender=chat_partner, receiver=request.user)
            messages = sorted(
                list(sent_messages) + list(received_messages),
                key=lambda msg: msg.timestamp
            )
        except User.DoesNotExist:
            chat_user = None

    return render(request, 'home.html', {
        'username': request.user.username,
        'messages': messages,
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
        image = request.FILES.get('image')  # Получаем загруженное изображение, если есть

        try:
            receiver_user = User.objects.get(username=receiver_name)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver_user,
                content=message_content if message_content else None,
                image=image if image else None  # Сохраняем изображение, если оно есть
            )
            message.save()
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Получатель не найден'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})