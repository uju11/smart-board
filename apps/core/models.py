# Create your models here.
from django.db import models
from django.conf import settings
from apps.core.context import get_current_user
User = settings.AUTH_USER_MODEL

class CustomBaseModel(models.Model):
    """
    Abstract base model that provides self-updating 
    'created_at', 'updated_at', created_by, updated_by fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.SET_NULL, 
        related_name="%(app_label)s_%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name="%(app_label)s_%(class)s_updated"
    )

    class Meta:
        # setting as an abstract model, since it is an abstract model no need to 
        # migrate this model to the database.
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            # If creating a new object, set created_by
            if not self.pk and not self.created_by_id:
                self.created_by = user
            # Always update the updated_by field on every save
            self.updated_by = user
            
        super().save(*args, **kwargs)
