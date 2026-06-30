from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import requests
from .models import Post

@receiver(post_save, sender=Post)
def notify_discord_on_new_post(sender, instance, created, **kwargs):
    if not (created and instance.published):
        return

    webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', None)
    if not webhook_url:
        return

    site_url = getattr(settings, 'SITE_URL', 'https://yasudevblog.lat')
    post_url = f"{site_url}/blog/{instance.slug}/"

    message = {
        "content": f"📝 **Nuevo post publicado**\n"
                   f"**Título:** {instance.title}\n"
                   f"**Fecha:** {instance.created_at.strftime('%d/%m/%Y %H:%M')}\n"
                   f"🔗 {post_url}"
    }

    try:
        requests.post(webhook_url, json=message, timeout=5)
    except Exception as e:
        # No romper el flujo si falla el webhook
        print(f"Error enviando webhook: {e}")