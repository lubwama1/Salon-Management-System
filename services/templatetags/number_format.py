from django import template

register = template.Library()

@register.filter
def short_number(value):
    try:
        value = int(value)
    except:
        return value

    if value >= 1000000:
        return f"{value/1000000:.1f}M".replace(".0", "")
    elif value >= 1000:
        return f"{value/1000:.1f}K".replace(".0", "")
    return value