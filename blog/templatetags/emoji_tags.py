from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from blog.models import CustomEmoji
import re

register = template.Library()

@register.filter
def render_emojis(text):
    emojis = {e.name: e for e in CustomEmoji.objects.all()}
    escaped = escape(text)

    def replace(match):
        name = match.group(1)
        if name in emojis:
            emoji = emojis[name]
            url = emoji.image.url
            return f'<img src="{url}" alt=":{name}:" title=":{name}:" class="custom-emoji">'
        return match.group(0)

    result = re.sub(r':([a-zA-Z0-9_]+):', replace, escaped)
    return mark_safe(result)