from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from enum import Enum 

class Category(Enum): 
    FS = "Fashion"
    TY = "Toys" 
    HM = "Home"
    PD = "Productivity"
    TG = "Technology"
    OT = "Other"

class User(AbstractUser):
    def addToWatchlist(self, listing): 
        self.watchlist.add(listing)

class Listing(models.Model): 
    
    title = models.CharField(max_length = 64)
    description = models.CharField(max_length = 250)
    auctioneer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    picture = models.URLField(blank = True)
    starting_bid = models.DecimalField(max_digits = 8, decimal_places = 2)
    closed = models.BooleanField(default=False)
    watchers = models.ManyToManyField(User, related_name= "watchlist", blank = True)
    category = models.CharField(
        max_length = 64,
        blank = True
    )

    def __str__(self):
        return f"{self.title} posted by {self.auctioneer.username}"
    # #custom initializer to auto create first bid 
    # @classmethod
    # def create(cls, title, description, auctioneer, picture, starting_bid): 
    #     listing = cls(
    #         title = title, 
    #         description = description, 
    #         auctioneer = auctioneer, 
    #         picture = picture, 
    #         starting_bid = starting_bid
    #     )
    #     listing.save()

    #     #creates the starting bid 
    #     bid = Bid(price = starting_bid, listing = listing, bidder = auctioneer)
    #     bid.save()

    #     return listing

    def isHighestBidder(self, user): 
        if hasattr(self, "bid"): 
            return self.bid.bidder == user 
        else: 
            return self.auctioneer == user 


    def getPrice(self): 
        if hasattr(self, "bid"): 
            return self.bid.price
        else: 
            return self.starting_bid
            
    #returns a boolean based on if the bid was successful 
    def processBid(self, price, bidder):
        
        #if a bid currently exists
        if hasattr(self, "bid"): 
            #new bid is greater than older 
            if self.bid.price < price:
                self.bid.delete()
                newBid = Bid(price = price, listing = self, bidder = bidder)
                newBid.save()
                return True 
            else: 
                return False 
        #only the starting bid exists 
        else: 
            if self.starting_bid <= price:  
                newBid = Bid(price = price, listing = self, bidder = bidder)
                newBid.save()
                return True 
            else: 
                return False 

    #predefined choices for listing categories 
    class Category(models.TextChoices): 
        OTHER = 'OT', _('Other')
        FASHION = 'FS', _('Fashion')
        TOYS = 'TY', _('Toys')
        HOME = 'HM', _('Home')
        PRODUCTIVITY = 'PD', _('Productivity')
        TECHNOLOGY = 'TG', _('Technology')

    

class Bid(models.Model): 
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="bid")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.price} posted by {self.bidder.username} for {self.listing.title}"

class Comment(models.Model): 
    text = models.CharField(max_length = 250)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f" \"{self.text}\" posted by {self.commentor.username} for {self.listing.title}"