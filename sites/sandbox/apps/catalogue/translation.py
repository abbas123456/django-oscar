from modeltranslation.translator import translator, TranslationOptions
from apps.catalogue.models import Product, Category, ProductClass

class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    
class ProductClassTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Product, ProductTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(ProductClass, ProductClassTranslationOptions)