from django import template

register = template.Library()

@register.filter
def is_list(value):
    print(str(type(value)))
    return str(type(value)) == "<class 'list'>"
