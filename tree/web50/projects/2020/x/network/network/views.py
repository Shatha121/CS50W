from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import User, Post


def index(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            content = request.POST["content"]  # Access the correct key
            Post.objects.create(user=request.user, content=content)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "You need to log in to post."
            })
    
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = user_profile.posts.all().order_by('-timestamp')
    followers_count = user_profile.followers.count()
    following_count = user_profile.following.count()

    is_following = False
    if request.user.is_authenticated:
        is_following = user_profile.followers.filter(id=request.user.id).exists()

    context = {
        "user_profile": user_profile,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    }
    return render(request, "network/profile.html", context)

def toggle_follow(request, username):
    if request.method == "POST":
        user_profile = get_object_or_404(User, username=username)
        if user_profile != request.user:
            if user_profile.followers.filter(id=request.user.id).exists():
                user_profile.followers.remove(request.user)
            else:
                user_profile.followers.add(request.user)
    return redirect('profile', username=username)

def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")
    

    paginator = Paginator(posts, 10)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

def edit_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        if post.user == request.user:  
            new_content = request.POST.get('content')
            post.content = new_content
            post.save()
            return JsonResponse({"success": True, "new_content": post.content})
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        if request.user.is_authenticated:
            if request.user in post.liked_by.all():
                
                post.liked_by.remove(request.user)
                liked = False
            else:
                
                post.liked_by.add(request.user)
                liked = True
            
            post.save()
            return JsonResponse({
                "success": True,
                "liked": liked,
                "like_count": post.liked_by.count()
            })
        return JsonResponse({"success": False, "message": "User not authenticated"}, status=403)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)