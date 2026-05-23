# yourapp/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import *

@register(FoodItem)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'category', 'short_details', 'description' )  # যেসব field translate করতে চাও

