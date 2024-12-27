from django.forms import ModelForm
from .models import *

# class signupForm(ModelForm):
#     class Meta:
#         model = Signup
#         fields = '__all__'

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
