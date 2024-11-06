# home/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect

@login_required
def home_view(request):
    return render(request, 'home.html', {'username': request.user.username})

def redirect_to_home(request):
    return redirect('/home/')