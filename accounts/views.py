from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer
from .forms import ProfileForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def _profile_context(user):
    return {
        'profile': user.profile,
        'comments': user.comment_set.all().order_by('-created_at')[:10],
        'unlocked': user.playerachievement_set.all().select_related('achievement__game'),
    }

def public_profile(request, username):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, username=username)
    return render(request, 'accounts/public_profile.html', _profile_context(user))


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', _profile_context(request.user))

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile_detail(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)