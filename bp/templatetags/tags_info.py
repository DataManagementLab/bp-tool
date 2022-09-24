from django import template
from django.apps import apps
from django.conf import settings
from django.utils.safestring import mark_safe

from bp.models import TLLog

register = template.Library()

@register.inclusion_tag('bp/project_info_table_tl_info.html', takes_context=True)
def tl_info(context):
    return {
        'tl' : context['project'].tl,
    }

@register.inclusion_tag('bp/project_info_table_member_info.html', takes_context=True)
def member_info(context):
    return {
        'student_list'  : context['project'].student_list,
        'student_mails' : context['project'].student_mail,
    }