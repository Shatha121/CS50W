from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden , HttpResponseBadRequest
from django.shortcuts import render , redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, auction_listings, Comment, Bid, Watchlist, Category
from .forms import auction_listings_Form , Bid_Form
from django.contrib import messages
from django.utils import timezone

def index(request):
    return render(request, "auctions/index.html",{
        "auctions": auction_listings.objects.all()
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required
def create_auction_listing(request):
    if request.method == "POST":
        form = auction_listings_Form(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            form.save()
            return redirect('index') 
    else:
        form = auction_listings_Form()
    
    return render(request, 'auctions/create.html', {'form': form})

@login_required
def list(request, id):
    auction = auction_listings.objects.get(id=id)
    comments = auction.comments.all()
    highest_bid = auction.get_highest_bid()
    is_in_watchlist = Watchlist.objects.filter(user=request.user, auction_listing=auction).exists()

    is_closed = auction.has_auction_ended()

    has_won = is_closed and auction.winner == request.user

    if request.method == "POST":
        bid_form = Bid_Form(request.POST)
        if bid_form.is_valid():
            new_bid = bid_form.cleaned_data['amount']

            if new_bid >= auction.starting_bid and (highest_bid is None or new_bid > highest_bid):
                Bid.objects.create(auction_listing=auction, user=request.user, amount=new_bid)
                messages.success(request, "Your bid was successfully placed!")
                return redirect('list', id=auction.id)
            else:
                messages.error(request, "Your bid must be higher than the current highest bid.")
    else:
        bid_form = Bid_Form()

    return render(request, "auctions/list.html", {
        "auction": auction,
        "comments": comments,
        "bid_form": bid_form,
        "highest_bid": highest_bid,
        "is_closed": is_closed,
        "has_won": has_won,
        "is_in_watchlist": is_in_watchlist,
    })

@login_required
def comments(request,id):
    auction = auction_listings.objects.get(id=id)
    if request.method == "POST":
        comment_text = request.POST["comment"]
        if comment_text:
            comment = Comment(auction_listing=auction, user=request.user, content=comment_text)
            comment.save()
            return HttpResponseRedirect(reverse("list", args=[id]))
    return HttpResponseRedirect(reverse("list", args=[id]))


@login_required
def close_auction(request, id):
    
    auction = get_object_or_404(auction_listings, id=id)

    
    if request.user != auction.seller:
        messages.error(request, "You are not authorized to close this auction.")
        return redirect('list', id=id)

    
    if auction.has_auction_ended():
        messages.error(request, "This auction has already ended.")
        return redirect('list', id=id)

    
    highest_bid = auction.bids.order_by('-amount').first()
    
    
    if highest_bid:
        auction.winner = highest_bid.user
    else:
        auction.winner = None  

    
    auction.end_time = timezone.now()
    auction.save()

    messages.success(request, "Auction closed successfully.")
    return redirect('list', id=id)


@login_required
def add_to_watchlist(request, id):
    auction = get_object_or_404(auction_listings, id=id)


    if Watchlist.objects.filter(user=request.user, auction_listing=auction).exists():
        messages.info(request, "This item is already in your watchlist.")
    else:
        Watchlist.objects.create(user=request.user, auction_listing=auction)
        messages.success(request, "Item added to your watchlist.")

    return redirect('list', id=id)

@login_required
def remove_from_watchlist(request, id):
    auction = get_object_or_404(auction_listings, id=id)


    watchlist_entry = Watchlist.objects.filter(user=request.user, auction_listing=auction).first()
    if watchlist_entry:
        watchlist_entry.delete()
        messages.success(request, "Item removed from your watchlist.")
    else:
        messages.info(request, "This item is not in your watchlist.")

    return redirect('list', id=id)

@login_required
def watchlist(request):
    user_watchlist = Watchlist.objects.filter(user=request.user)
    return render(request, 'auctions/watchlist.html', {
        'watchlist': user_watchlist
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = auction_listings.objects.filter(category=category, is_active=True)
    return render(request, 'auctions/category_listings.html', {
        'category': category,
        'listings': listings
    })