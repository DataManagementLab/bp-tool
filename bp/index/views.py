from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseServerError
from django.views.generic import TemplateView

from bp.models import BP, Project, Student, TL, TLLog
from bp.roles import is_tl, is_student, is_orga

class ActiveBPMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bp'] = BP.get_active()
        return context


class IndexView():

    def as_callable(request, *args, **kwargs):
        if is_orga(request.user):
            view = OrgaIndexView
        elif is_tl(request.user):
            view = TLIndexView
        elif is_student(request.user):
            view = StudentIndexView
        else:
            view = LoginView
        return view.as_view()(request, *args, **kwargs)

class OrgaIndexView(LoginRequiredMixin, ActiveBPMixin, TemplateView):
    template_name = "bp/index/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.get_active()
        context['projects_count'] = context['projects'].count()
        context['projects_graded_count'] = context['projects'].annotate(early_grades=Count('aggradebeforedeadline')).filter(Q(early_grades__gt=0) | Q(ag_grade__isnull=False)).count()
        context['tls'] = TL.get_active()
        context['tls_count'] = context['tls'].count()
        context['tls_unconfirmed_count'] = TL.objects.filter(bp__active=True, confirmed=False).count()
        context['students'] = Student.get_active()
        context['students_without_project'] = Student.get_active().filter(project=None)
        context['logs'] = TLLog.get_active()
        context['logs_count'] = context['logs'].count()
        context['logs_unread_count'] = context['logs'].filter(read=False).count()
        context['logs_attention_count'] = context['logs'].filter(requires_attention=True, handled=False).count()
        context['projects_without_recent_logs_count'] = Project.without_recent_logs().count()
        context['log_period'] = settings.LOG_REMIND_PERIOD_DAYS
        return context

class TLIndexView(LoginRequiredMixin, TemplateView):
    template_name = "bp/index/index_tl.html"

    def get(self, request, *args, **kwargs):
        if not is_tl(request.user):
            print(f"User {request.user} is no TL, but got the TL index page")
            return HttpResponseServerError("Http Error 500: Wrong index page (TL)")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tl = self.request.user.tl
        context['tl'] = tl
        context['bp'] = tl.bp
        context['projects'] = tl.project_set.all()
        context['projects_count'] = context['projects'].count()
        context['projects_without_intervals'] = context['projects'].annotate(nr_intervals=Count('timeinterval')).filter(nr_intervals=0).count()
        context['logs'] = tl.tllog_set.all()
        context['logs_count'] = context['logs'].count()
        context['projects_without_recent_logs_count'] = Project.without_recent_logs(context['projects']).count() if context['projects'] else 0
        context['log_period'] = settings.LOG_REMIND_PERIOD_DAYS
        return context

class StudentIndexView(LoginRequiredMixin, ActiveBPMixin, TemplateView):
    template_name = "bp/index/index_student.html"

    def get(self, request, *args, **kwargs):
        if not is_student(request.user):
            print(f"User {request.user} is no student, but got the student index page")
            return HttpResponseServerError("Http Error 500: Wrong index page (student)")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student
        context['student'] = student
        context['bp'] = student.bp
        context['group'] = student.project
        context['current_interval'] = context['group'].get_past_and_current_intervals.latest('start')
        context['most_recently_passed_interval'] = context['group'].get_past_and_current_intervals[1]
        return context


class LoginView(TemplateView):
    template_name = "bp/index/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(settings, "MOODLE_LOGIN_URL"):
            context["login_button_show"] = True
            context["login_button_url"] = settings.MOODLE_LOGIN_URL

        return context
