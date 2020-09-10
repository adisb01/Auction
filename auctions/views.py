from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Bid, Listing, Comment, Category
from django import forms

class CategoryForm(forms.Form): 
    category = forms.ChoiceField(required = False, choices=Listing.Category)

def index(request):
    return render(request, "auctions/index.html", {
        "active_listings" : Listing.objects.filter(closed = False)
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
def create(request): 

    #submitting data to create a listing
    if request.method == "POST": 
        
        title = request.POST["title"]
        picture = request.POST["picture"]
        description = request.POST["description"]
        category = request.POST["category"]
        starting_bid = request.POST["starting_bid"]
        
        listing = None 
        if category != "None":
            listing = Listing(
                title = title, 
                description = description, 
                auctioneer = request.user, 
                picture = picture, 
                category = category, 
                starting_bid = starting_bid
            )
        else: 
            listing = Listing(
                title = title, 
                description = description, 
                auctioneer = request.user, 
                picture = picture, 
                starting_bid = starting_bid
            )
        
        listing.save()

    return render(request, "auctions/create.html", {
        "categories" : [c.value for c in Category]
    })

def listing(request, listing_id): 

    #bidding, closing, or commenting
    if request.method == "POST": 
        action = request.POST.get("action", "")
        text =request.POST.get("comment", "") 
        listing = Listing.objects.get(id = listing_id)
        #closing 
        if action: 
            listing.closed = True 
            listing.save()
        #comment
        elif text: 
            comment = Comment(text = text, listing = listing, commentor = request.user)
            comment.save()
        #bidding 
        else:  
            bid = float(request.POST.get("bid", 0))
            is_success = listing.processBid(bid, request.user)
            on_watchlist = False

            if not request.user.is_anonymous: 
                on_watchlist = listing in request.user.watchlist.all()

            if not is_success: 
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "on_watchlist": on_watchlist,
                    "is_highest_bidder": listing.isHighestBidder(request.user),
                    "is_owner": request.user == listing.auctioneer,
                    "comments": listing.comments.all(), 
                    "alertMessage": "Invalid bid amount, please bid higher."
                })

    listing = Listing.objects.get(id=listing_id)
    on_watchlist = False
    if not request.user.is_anonymous: 
                on_watchlist = listing in request.user.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "on_watchlist": on_watchlist,
        "comments": listing.comments.all(), 
        "is_highest_bidder": listing.isHighestBidder(request.user),
        "is_owner": request.user == listing.auctioneer
    })


@login_required
def watchlist(request): 
    #user is adding/removing from the watchlist
    if request.method == "POST": 
        
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id = listing_id)
        on_watchlist = listing in request.user.watchlist.all()
        
        if on_watchlist: 
            request.user.watchlist.remove(listing)
        else: 
            request.user.watchlist.add(listing)

        return HttpResponseRedirect(reverse('listing', args = [listing_id]))
    
    else: 

        return render(request, "auctions/watchlist.html", {
            "watchlist" : request.user.watchlist.all()
        })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories" : [c.value for c in Category]
    })

def category(request, category): 
    listings = Listing.objects.filter(category = category, closed = False)
    return render(request, "auctions/category.html", {
        "listings" : listings, 
        "category" : category
    })