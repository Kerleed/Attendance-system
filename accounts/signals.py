# accounts/signals.py
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """Automatically create 'Admin' and 'Staff' groups after migration."""
    groups = ['Admin', 'Staff']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)
