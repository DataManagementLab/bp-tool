from django import template
from django.apps import apps
from django.conf import settings
from django.utils.safestring import mark_safe

from bp.models import TLLog

from bp.pretix import get_pretix_projectinfo_url

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

@register.inclusion_tag('bp/project_info_table_ag_info.html', takes_context=True)
def ag_info(context):
    return {
        'ag'      : context['project'].ag,
        'ag_mail' : context['project'].ag_mail,
    }

@register.inclusion_tag('bp/project_info_table_pretix_info.html', takes_context=True)
def pretix_info(context):
    return {
        'info_url' : get_pretix_projectinfo_url(context['project']),
    }

@register.inclusion_tag('bp/project_info_table_grade_info.html', takes_context=True)
def grade_info(context):
    return {
        'show_aggrade'            : context['project'].ag_points >= 0,
        'ag_points'               : context['project'].ag_points,
        'ag_points_justification' : context['project'].ag_points_justification,
    }

@register.inclusion_tag('bp/project_info_table_hours_info.html', takes_context=True)
def hours_info(context):
    return {
        'project'           : context['project'],
        'total_hours_spent' : context['project'].total_hours,
    }