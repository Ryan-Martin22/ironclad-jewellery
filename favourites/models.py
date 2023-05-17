from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# I used Stack Overflow to help with putting this model together.
# Link in README Credits


class Favourites(models.Model):
    """Favourites model so the user can save items to their favourites"""

    class Meta:
        """Removes extra 's' from Model name"""
        verbose_name_plural = 'Favourites'

    products = models.ManyToManyField(Product, blank=True)
    username = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return object string"""
        return f"{self.username}'s Favourites"
