from django import forms 
from .models import auction_listings, Bid, Category

class auction_listings_Form(forms.ModelForm):
  
    class Meta:
        model = auction_listings
        fields = ['item_image', 'name', 'description', 'starting_bid', 'duration', 'category']
        widgets = {
            'item_image': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class Bid_Form(forms.ModelForm):
  
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }



