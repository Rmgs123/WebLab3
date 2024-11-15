import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import validators
from .models import Profile, Message, Group, Post, GroupMemberStatus
from django.contrib import messages

from django.http import JsonResponse, HttpResponseRedirect

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from PIL import Image, ImageDraw, ImageOps
import io
from django.core.files.base import ContentFile
from django.urls import reverse

from django.db.models import Q
from django.utils.dateparse import parse_datetime

from django.utils import timezone
from datetime import timedelta


@login_required
def home_view(request):
    chat_user = request.GET.get('chat_with')
    group_id = request.GET.get('group_with')
    messages_list = []
    posts_list = []
    initial_load_count = 20
    group_object = 0

    if chat_user:
        try:
            chat_partner = User.objects.get(username=chat_user)

            messages_qs = Message.objects.filter(
                Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user)
            ).order_by('-timestamp', '-id')[:initial_load_count]

            messages_list = list(messages_qs)[::-1]

            Message.objects.filter(sender=chat_partner, receiver=request.user, is_read=False).update(is_read=True)
        except User.DoesNotExist:
            chat_user = None

    if group_id:
        try:

            group_object = Group.objects.get(name=group_id)
            profile = Profile.objects.get(user=request.user)
            posts_qs = Post.objects.filter(
                Q(group_sender=group_object)
            ).order_by('-timestamp', '-id')[:initial_load_count]

            posts_list = list(posts_qs)[::-1]

            status = GroupMemberStatus.objects.get(group=group_object, member=profile)
            status.is_read = True
            status.save()
        except (Group.DoesNotExist, GroupMemberStatus.DoesNotExist):
            group_id = None

    return render(request, 'home.html', {
        'user': request.user,
        'username': request.user.username,
        'messages': messages_list,
        'chat_user': chat_user,
        'group_id': group_id,
        'posts': posts_list,
        'group': group_object
    })

@login_required
def home_delete(request):
    chat_user = request.GET.get('chat_with')
    group_id = request.GET.get('group_with')

    if request.method == 'POST':
        if chat_user:
            try:

                chat_partner = User.objects.get(username=chat_user)
                profile = Profile.objects.get(user=request.user)

                profile.contacts.remove(chat_partner.profile)
                profile.save()

                messages.success(request, "Contact deleted")
            except User.DoesNotExist:
                chat_user = None

            return redirect('home')

        if group_id:
            try:
                group = Group.objects.get(name=group_id)
                profile = Profile.objects.get(user=request.user)

                GroupMemberStatus.objects.get(group=group, member=profile).delete()
                profile.groups.remove(group)
                profile.save()
                if group.sender == request.user:
                    new_sender = GroupMemberStatus.objects.filter(group=group)

                    if len(new_sender) != 0:
                        sender_user = User.objects.get(username=new_sender[0].member.user)
                        group.sender = sender_user
                        group.save()
                    else:
                        posts_qs = Post.objects.filter(
                            Q(group_sender=group)
                        )

                        for post in posts_qs:
                            if post.image:
                                os.remove(os.path.join('media', f'{post.image}'))

                        posts_qs.delete()
                        group.delete()


            except (Group.DoesNotExist, GroupMemberStatus.DoesNotExist):
                group_id = None

            return redirect('home')

    return render(request, 'account/delete.html', {
        'user': request.user,
        'username': request.user.username,
        'chat_user': chat_user,
        'group_id': group_id,

    })

@login_required
def home_clear(request):
    chat_user = request.GET.get('chat_with')
    group_id = request.GET.get('group_with')

    if request.method == 'POST':
        if chat_user:
            try:

                chat_partner = User.objects.get(username=chat_user)

                messages_qs = Message.objects.filter(
                    Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user))

                for message in messages_qs:
                    if message.image:
                        os.remove(os.path.join('media', f'{message.image}'))

                messages_qs.delete()

                messages.success(request, "Chat cleared")
            except User.DoesNotExist:
                chat_user = None

            url = f"{reverse('home')}?chat_with={chat_user}"
            return redirect(url)

        if group_id:
            try:
                group = Group.objects.get(name=group_id)

                posts_qs = Post.objects.filter(
                    Q(group_sender=group)
                )

                for post in posts_qs:
                    if post.image:
                        os.remove(os.path.join('media', f'{post.image}'))

                posts_qs.delete()

                messages.success(request, "Chat cleared")
            except (Group.DoesNotExist, GroupMemberStatus.DoesNotExist):
                group_id = None

            url = f"{reverse('home')}?group_with={group_id}"
            return redirect(url)

    return render(request, 'account/clear.html', {
        'user': request.user,
        'username': request.user.username,
        'chat_user': chat_user,
        'group_id': group_id,

    })

@login_required
def home_pop_back(request):
    chat_user = request.GET.get('chat_with')
    group_id = request.GET.get('group_with')

    if request.method == 'POST':
        if chat_user:
            try:

                chat_partner = User.objects.get(username=chat_user)

                message_qs = Message.objects.filter(
                    Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user)
                ).order_by('-timestamp', '-id')

                if len(message_qs) != 0:
                    message = message_qs[0]
                    if message.image:
                        os.remove(os.path.join('media', f'{message.image}'))

                    message.delete()

                messages.success(request, "Message deleted")
            except User.DoesNotExist:
                chat_user = None

            url = f"{reverse('home')}?chat_with={chat_user}"
            return redirect(url)

        if group_id:
            try:
                group = Group.objects.get(name=group_id)

                posts_qs = Post.objects.filter(
                    Q(group_sender=group)
                ).order_by('-timestamp', '-id')

                if len(posts_qs) != 0:
                    post = posts_qs[0]

                    if post.image:
                        os.remove(os.path.join('media', f'{post.image}'))

                    post.delete()

                messages.success(request, "Post deleted")
            except (Group.DoesNotExist, GroupMemberStatus.DoesNotExist):
                group_id = None

            url = f"{reverse('home')}?group_with={group_id}"
            return redirect(url)

    return render(request, 'account/pop_back.html', {
        'user': request.user,
        'username': request.user.username,
        'chat_user': chat_user,
        'group_id': group_id,

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
            messages.success(request, f'Contact {contact_name} has been successfully added!')
        except User.DoesNotExist:
            messages.error(request, 'User with this name not found.')
        return redirect('home')
    return redirect('home')

@login_required
def get_contacts(request):
    contacts = request.user.profile.contacts.all()
    contacts_data = []

    for contact in contacts:
        is_read = False
        unread_messages = Message.objects.filter(sender=contact.user, receiver=request.user, is_read=False)

        if unread_messages.exists():
            is_read = True

        contacts_data.append({
            'username': contact.user.username,
            'profile_image_url': contact.user.profile.image.url if contact.user.profile.image else '',
            'is_read': is_read,
        })

    return JsonResponse({'contacts': contacts_data})

@login_required
def get_groups(request):
    groups = request.user.profile.groups.all()
    groups_data = []
    profile = Profile.objects.get(user=request.user)

    for group in groups:
        is_read = False

        unread_posts = GroupMemberStatus.objects.filter(
            member=profile,
            group=group,
            is_read=False
        )

        if unread_posts.exists():
            is_read = True
        groups_data.append({
            'name': group.name,
            'image_url': group.image.url if group.image else '',
            'is_read': is_read,
        })
    return JsonResponse({'groups': groups_data})

@login_required
def send_message(request):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        receiver_name = request.POST.get('receiver_name')
        image = request.FILES.get('image')

        if not message_content and not image:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'})

        if len(message_content) > 5000:
            return JsonResponse(
                {'status': 'error', 'message': 'The message is too long. The maximum length is 5000 characters.'})

        try:
            receiver_user = User.objects.get(username=receiver_name)

            if request.user not in receiver_user.profile.contacts.all():
                receiver_user.profile.contacts.add(request.user.profile)

            last_message = Message.objects.filter(sender=request.user).order_by('-timestamp').first()
            if last_message:
                time_since_last_message = timezone.now() - last_message.timestamp
                if time_since_last_message < timedelta(seconds=1):
                    return JsonResponse({'status': 'error',
                                         'message': 'You are sending messages too frequently. Please wait a bit.'})

            message = Message.objects.create(
                sender=request.user,
                receiver=receiver_user,
                content=message_content if message_content else None,
                image=image if image else None
            )
            message.save()
            return JsonResponse({'status': 'success', 'timestamp': message.timestamp.isoformat(), 'id': message.id})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recipient not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

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

        if chat_partner != request.user:
            receiver_profile = request.user.profile
            sender_profile = chat_partner.profile
            if not receiver_profile.contacts.filter(id=sender_profile.id).exists():
                receiver_profile.contacts.add(sender_profile)

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
def load_old_messages(request, chat_user):
    before_timestamp = request.GET.get('before_timestamp')
    before_id = int(request.GET.get('before_id', 0))
    limit = int(request.GET.get('limit', 20))

    try:
        chat_partner = User.objects.get(username=chat_user)

        before_datetime = parse_datetime(before_timestamp)
        if before_datetime is None:
            return JsonResponse({"error": "Invalid timestamp"}, status=400)

        messages_qs = Message.objects.filter(
            Q(sender=request.user, receiver=chat_partner) | Q(sender=chat_partner, receiver=request.user)
        ).filter(
            Q(timestamp__lt=before_datetime) | (Q(timestamp=before_datetime) & Q(id__lt=before_id))
        ).order_by('-timestamp', '-id')[:limit]

        messages = []
        for message in messages_qs:
            messages.append({
                "id": message.id,
                "sender": message.sender.username,
                "content": message.content,
                "image_url": message.image.url if message.image else None,
                "timestamp": message.timestamp.isoformat()
            })

        return JsonResponse({"messages": messages})

    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

@login_required
def publish_post(request):
    if request.method == 'POST':

        post_content = request.POST.get('post')
        name_group = request.POST.get('name_group')
        image = request.FILES.get('post_image')

        if not post_content and not image:
            return JsonResponse({'status': 'error', 'message': 'The post cannot be empty.'})

        if len(post_content) > 8000:
            return JsonResponse(
                {'status': 'error', 'message': 'The post is too long. Maximum length is 8000 characters.'})
        try:
            group_sender = Group.objects.get(name=name_group)

            last_post = Post.objects.filter(group_sender=group_sender).order_by('-timestamp').first()

            if last_post:
                time_since_last_message = timezone.now() - last_post.timestamp
                if time_since_last_message < timedelta(seconds=1):
                    return JsonResponse({'status': 'error',
                                         'message': 'You are posting too frequently. Please wait a bit.'})

            post = Post.objects.create(
                group_sender=group_sender,
                content=post_content if post_content else None,
                image=image if image else None
            )
            post.save()

            for member in group_sender.members.all():
                chat_partner = User.objects.get(username=member)

                profile = Profile.objects.get(user=chat_partner)
                status = GroupMemberStatus.objects.get(group=group_sender, member=profile)
                status.is_read = False
                status.save()

            return JsonResponse({'status': 'success', 'timestamp': post.timestamp.isoformat(), 'id': post.id})
        except (Group.DoesNotExist, GroupMemberStatus.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Group not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def check_new_posts(request):
    groups_with_unread = []
    profile = Profile.objects.get(user=request.user)

    for group_user in request.user.profile.groups.all():
        unread_posts = GroupMemberStatus.objects.filter(
            member=profile,
            group=group_user,
            is_read=False
        )

        if unread_posts.exists():
            groups_with_unread.append(group_user.name)
    return JsonResponse({'groups_with_unread': groups_with_unread})

@login_required
def get_new_posts(request, group_id=None):
    if not group_id:
        return JsonResponse({"error": "chat_user parameter is missing"}, status=400)

    after_timestamp = request.GET.get('after_timestamp')
    after_id = int(request.GET.get('after_id', 0))

    try:

        group_sender = Group.objects.get(name=group_id)
        profile = Profile.objects.get(user=request.user)

        if after_timestamp:
            after_datetime = parse_datetime(after_timestamp)
            if after_datetime is None:
                return JsonResponse({"error": "Invalid timestamp"}, status=400)

            posts_qs = Post.objects.filter(
                Q(group_sender=group_sender)
            ).filter(
                Q(timestamp__gt=after_datetime) | (Q(timestamp=after_datetime) & Q(id__gt=after_id))
            ).order_by('timestamp', 'id')
        else:
            posts_qs = Post.objects.filter(
                Q(group_sender=group_sender)
            ).order_by('timestamp', 'id')

        new_posts = [{
            "id": post.id,
            "group_sender": group_id,
            "content": post.content,
            "image_url": post.image.url if post.image else None,
            "timestamp": post.timestamp.isoformat()
        } for post in posts_qs]

        status = GroupMemberStatus.objects.get(group=group_sender, member=profile)

        status.is_read = True
        status.save()

        return JsonResponse({"new_posts": new_posts})

    except (Group.DoesNotExist, GroupMemberStatus.DoesNotExist):
        return JsonResponse({"error": "User does not exist"}, status=404)

@login_required
def load_old_posts(request, group_id):
    before_timestamp = request.GET.get('before_timestamp')
    before_id = int(request.GET.get('before_id', 0))
    limit = int(request.GET.get('limit', 20))

    try:
        group_sender = Group.objects.get(name=group_id)

        # Parse the timestamp
        before_datetime = parse_datetime(before_timestamp)
        if before_datetime is None:
            return JsonResponse({"error": "Invalid timestamp"}, status=400)

        # Corrected filtering logic with proper grouping
        posts_qs = Post.objects.filter(
            Q(group_sender=group_sender)
        ).filter(
            Q(timestamp__lt=before_datetime) | (Q(timestamp=before_datetime) & Q(id__lt=before_id))
        ).order_by('-timestamp', '-id')[:limit]

        # Since we are fetching messages in descending order, we need to reverse them for correct display
        posts = []
        for post in posts_qs:
            posts.append({
                "id": post.id,
                "sender": group_id,
                "content": post.content,
                "image_url": post.image.url if post.image else None,
                "timestamp": post.timestamp.isoformat()
            })

        return JsonResponse({"posts": posts})

    except Group.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

def change_image_1(image_file, size):
    image = Image.open(image_file)

    image = image.resize(size, Image.Resampling.LANCZOS)

    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, *size), fill=255)

    result = ImageOps.fit(image, size, centering=(0.5, 0.5))
    result.putalpha(mask)

    image.close()

    return result

@login_required
def settings(request):
    return render(request, 'account/setting.html')

@login_required
def change_email_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        new_email = request.POST.get('new_email')

        user = authenticate(username=request.user.username, password=password)
        if user is None:
            messages.error(request, "Incorrect password")
            return redirect('account_change_email')

        try:
            validate_email(new_email)
        except ValidationError:
            messages.error(request, "Incorrect email format.")
            return redirect('account_change_email')

        user.email = new_email
        user.save()

        messages.success(request, "Email has been successfully changed!")
        return redirect('account_change_email')

    return render(request, 'account/email.html', {'user': request.user})

@login_required
def change_username(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        new_username = request.POST.get('new_username')

        user = authenticate(username=request.user.username, password=password)
        if user is None:
            messages.error(request, "Incorrect password.")
            return redirect('account_change_username')

        if User.objects.filter(username=new_username).exists():
            messages.error(request, "There is already such a nickname")
            return redirect('account_change_username')
        try:
            validators.UnicodeUsernameValidator(new_username)
            validators.ASCIIUsernameValidator(new_username)
        except ValidationError:
            messages.error(request, "Incorrect nickname format.")
            return redirect('account_change_username')

        user.username = new_username
        user.save()

        messages.success(request, "Username has been successfully changed.")
        return redirect('account_change_username')

    return render(request, 'account/change_username.html', {'user': request.user})

@login_required
def change_image(request):
    if request.method == 'POST':
        if request.FILES.get('image'):
            image_file = request.FILES.get('image')
            size = (32, 32)
            profile = Profile.objects.get(user=request.user)

            result = change_image_1(image_file, size)

            if result.mode != 'RGBA':
                result = result.convert('RGBA')

            buffer = io.BytesIO()
            result.save(buffer, format='PNG')
            profile.image.save('profile_images.png', ContentFile(buffer.getvalue()))
            profile.save()

        return redirect('home')

    return render(request, 'account/change_image.html')


@login_required
def create_group(request):
    if request.method == 'POST':
        new_name = request.POST.get('name_group')

        if Group.objects.filter(name=new_name).exists():
            messages.error(request, "Such a group already exists")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        group = Group(name=new_name, sender=request.user)
        if request.FILES.get('image'):
            image_file = request.FILES.get('image')
            size = (32, 32)
            result = change_image_1(image_file, size)

            if result.mode != 'RGBA':
                result = result.convert('RGBA')

            buffer = io.BytesIO()
            result.save(buffer, format='PNG')
            group.image.save('group_images.png', ContentFile(buffer.getvalue()))

        profile = Profile.objects.get(user=request.user)
        group.save()

        profile.groups.add(group)
        GroupMemberStatus.objects.create(group=group, member=profile)
        messages.success(request, "The group has been created.")
        return redirect('home')
    return render(request, 'account/create_group.html', {'user': request.user})

@login_required
def add_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')

        try:
            group = Group.objects.get(name=group_name)
            profile = Profile.objects.get(user=request.user)
            profile.groups.add(group)
            if group.sender != request.user:
                GroupMemberStatus.objects.create(group=group, member=profile)
            messages.success(request, f'Group {group_name} has been successfully added!')
        except Group.DoesNotExist:
            messages.error(request, 'User with this name not found.')
        return redirect('home')
    return redirect('home')
