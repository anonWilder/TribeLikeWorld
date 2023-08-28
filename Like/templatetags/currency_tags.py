from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def assign_request(context):
    return context['request']
