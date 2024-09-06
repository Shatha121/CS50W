from django.contrib import admin
from .models import auction_listings, Bid, Comment, Category, User, Watchlist



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(auction_listings)
class AuctionListingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'starting_bid', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'end_time')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction_listing', 'user', 'amount', 'placed_at')
    list_filter = ('auction_listing', 'user')
    search_fields = ('auction_listing__name', 'user__username')
    readonly_fields = ('placed_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('auction_listing', 'user', 'content', 'created_at')
    list_filter = ('auction_listing', 'user')
    search_fields = ('content', 'auction_listing__name', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction_listing')
    list_filter = ('user', 'auction_listing')
    search_fields = ('user__username', 'auction_listing__name')
