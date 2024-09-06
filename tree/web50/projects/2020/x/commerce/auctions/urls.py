from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create', views.create_auction_listing, name='create'),
    path('<int:id>', views.list, name='list'),
    path('<int:id>/comment', views.comments, name='add_comment'),
    path('<int:id>/close', views.close_auction, name='close_auction'),
    path('<int:id>/add_to_watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('<int:id>/remove_from_watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:category_id>/", views.category_listings, name="category_listings"),  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
