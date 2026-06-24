from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail

from .models import Task


@receiver(pre_save, sender=Task)
def notify_owner_on_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old.status != instance.status and instance.owner and instance.owner.email:
        send_mail(
            subject=f'Task status changed: {instance.title}',
            message=(
                f'Hello {instance.owner.username},\n\n'
                f'Task "{instance.title}" status has been updated:\n'
                f'  {old.status} \u2192 {instance.status}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.owner.email],
            fail_silently=False,
        )
