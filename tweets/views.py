from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Tweet, Follow
from .forms import TweetForm
from django.contrib.auth import logout

@login_required
def home(request):
    if request.user.is_authenticated:
        following = request.user.following.values_list('following_id', flat=True)
        tweets = Tweet.objects.filter(user_id__in=following).order_by('-created_at')
    else:
        tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweets/home.html', {'tweets': tweets})

@login_required
def tweet_detail(request, id):
    tweet = get_object_or_404(Tweet, id=id)
    return render(request, 'tweets/tweet_detail.html', {'tweet': tweet})

@login_required
def user_profile(request, username):
    user = User.objects.get(username=username)
    tweets = Tweet.objects.filter(user=user).order_by('-created_at')
    return render(request, 'tweets/user_profile.html', {'profile_user': user, 'tweets': tweets})

@login_required
def feed(request):
    user = request.user
    following_users = user.following.values_list('following', flat=True)
    tweets = Tweet.objects.all().order_by('-created_at')
    # Incluir também os tweets do próprio usuário no feed
    my_tweets = Tweet.objects.filter(user=user)
    tweets = tweets | my_tweets
    tweets = tweets.order_by('-created_at')
    return render(request, 'tweets/feed.html', {'tweets': tweets})

@login_required
def create_tweet(request):
    if request.method == 'POST':
        content = request.POST['content']
        Tweet.objects.create(user=request.user, content=content)
        return redirect('feed')
    return render(request, 'tweets/create_tweet.html')

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.following.add(user_to_follow)
    return redirect('user_profile', username=user_to_follow.username)

def user_logout(request):
    logout(request)
    return redirect('accounts') 

@login_required
def user_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'tweets/user_profile.html', {'profile_user': user})

@login_required
def follow_user_by_username(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    follow_instance, created = Follow.objects.get_or_create(user=request.user, following=user_to_follow)
    if created:
        return redirect('user_profile', username=username)
    else:
        # Caso o usuário já esteja seguindo o perfil, podemos redirecioná-lo para a página do perfil
        return redirect('user_profile', username=username)

