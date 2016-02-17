from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    return render(request, 'cardbox/index.html')


def login_view(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return render(request, 'cardbox/login.html')

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('cardbox:collection'))
        else:
            return render(request, 'cardbox/login.html', {'error_message': 'User not active!'})
    else:
        return render(request, 'cardbox/login.html', {'error_message': 'User not found!'})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('cardbox:index'))


@login_required(login_url='/cardbox/login/')
def collection(request):
    return render(request, 'cardbox/welcome.html')
