from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name == 'admin_dashboard':  # only run for this app
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        staff_group, _ = Group.objects.get_or_create(name='Staff')

        # Give Admin all permissions
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)

        # Staff will have limited permissions (only view + check-in/out)
        view_permissions = Permission.objects.filter(codename__startswith='view_')
        staff_group.permissions.set(view_permissions)

        print("✅ Default groups created: Admin & Staff")
