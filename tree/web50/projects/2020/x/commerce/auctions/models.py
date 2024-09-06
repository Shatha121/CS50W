from django.contrib.auth.models import AbstractUser
from django.db import models
import time
from datetime import timedelta
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

def get_default_seller():
    return User.objects.get(username="sha").id

class User(AbstractUser):
    pass

class auction_listings(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    item_image = models.ImageField(upload_to='images/', blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Auction duration in hours")
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_auctions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions')
    is_active = models.BooleanField(default=True)
    def start_auction(self):
        if not self.end_time:
            self.end_time = timezone.now() + timedelta(hours=self.duration_hours)
            self.save()
    def get_remaining_time(self):
        if not self.end_time:
            return None
        
        remaining = self.end_time - timezone.now()
        return max(remaining, timedelta(0))
    def has_auction_ended(self):
        if not self.end_time:
            return False

        return timezone.now() >= self.end_time
    def get_highest_bid(self):
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.amount if highest_bid else self.starting_bid
    def __str__(self):
        return f"{self.name} - Remaining: {self.get_remaining_time()}"
class Bid(models.Model):
    auction_listing = models.ForeignKey(auction_listings, related_name='bids', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} bid {self.amount} on {self.auction_listing.name}"
    
    class Meta:
        ordering = ['-placed_at']

class Comment(models.Model):
    auction_listing = models.ForeignKey(auction_listings, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.auction_listing.name}: {self.content[:20]}..."
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_listing = models.ForeignKey(auction_listings, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'auction_listing')

    def __str__(self):
        return f"{self.user.username} watches {self.auction_listing.name}"
    
