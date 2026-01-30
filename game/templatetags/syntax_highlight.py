from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='py_highlight')
def py_highlight(text):
    if not text:
        return ""
    
    # Escapamos HTML para evitar conflictos con < >
    text = text.replace('<', '&lt;').replace('>', '&gt;')

    # Reglas de resaltado
    rules = [
        (r'("(.*?)")', 's1'), # Strings en verde
        (r'\b(if|else|while|for|return|using|namespace|include|int|float|std|cout|cin|print)\b', 's3'), # Keywords rosa
        (r'\b(\d+)\b', 's4'), # Números naranja
        (r'(#.*?$|//.*?$)', 's1'), # Comentarios verde
    ]

    highlighted = text
    for pattern, css_class in rules:
        highlighted = re.sub(pattern, rf'<span class="{css_class}">\1</span>', highlighted)
    
    return mark_safe(highlighted)