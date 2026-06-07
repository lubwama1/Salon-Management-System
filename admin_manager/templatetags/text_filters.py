from django import template

register = template.Library()


@register.filter
def initials(value):
    words = value.split()
    return " ".join(word[0].upper() for word in words if word)