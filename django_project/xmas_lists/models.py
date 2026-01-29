from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
    
class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_title = models.CharField(max_length=200, help_text="The name of the event", null=False)
    event_date = models.DateField(help_text = "The date of the event", null=False)
    
    def __str__(self):
        return f'{self.event_title} ({self.event_date})'
    
    class Meta:
        ordering = ['event_date']

class List(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, on_delete=models.RESTRICT, help_text="The event this gift list is for")
    user = models.ForeignKey(User, on_delete=models.RESTRICT, help_text="The user this list is for")
    
    def __str__(self):
        return f"{self.user.first_name}'s list for {self.event.event_title}"
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['event', 'user'],
                name='unique_event_user_pair'
            )
        ]
        ordering = ['created_at']
    
class ListItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, help_text="The title of this giftlist item")
    url = models.URLField('URL', max_length=1000, help_text="The URL where this item can be purchased", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="How much this item costs", null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD', help_text="The currency refered to by 'price'", null=True, blank=True)
    
    PRIORITY = (
        ('1', "Very Low"),
        ('2', "Low"),
        ('3', "Medium"),
        ('4', "High"),
        ('5', "Very High"),
    )
    
    priority = models.CharField(
        max_length=1,
        choices=PRIORITY,
        default='3',
        help_text="The comparative desirability of the item"
    )
    
    list = models.ForeignKey(List, on_delete=models.CASCADE, help_text="The list this item is in")
    
    def __str__(self):
        return f'{self.title} for {self.list.user.first_name}'
    
    class Meta:
        ordering = ["created_at"]
    
class ListItemPurchased(models.Model):
    list_item = models.OneToOneField(ListItem, unique=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    purchased_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    purchase_comments = models.CharField(max_length=1000)
    
    def __str__(self):
        return f'{self.list_item.title} for {self.list_item.list.user.first_name} purchased by {self.purchased_by.first_name} {self.purchased_by.last_name}'
    
    class Meta:
        verbose_name = "List Item Purchased"
        verbose_name_plural = "List Items Purchased"
    