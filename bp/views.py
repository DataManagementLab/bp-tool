import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.defaults import bad_request, permission_denied, server_error, page_not_found
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, FormView, CreateView, DeleteView

from bp.forms import AGGradeForm, ProjectImportForm, StudentImportForm, TLLogForm, TLLogUpdateForm
from bp.models import BP, Project, Student, TL, TLLog
from bp.pretix import get_order_secret


def error_400(request, exception):
    return bad_request(request, exception, template_name="bp/400.html")

def error_403(request, exception):
    return permission_denied(request, exception, template_name="bp/403.html")

def error_404(request, exception):
    return page_not_found(request, exception, template_name="bp/404.html")

def error_500(request,):
    return server_error(request, template_name="bp/500.html")


class ActiveBPMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bp'] = BP.get_active()
        return context


class FilterByActiveBPMixin:
    def __init__(self) -> None:
        self.active_bp = BP.get_active()
        super().__init__()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bp'] = self.active_bp
        return context

    def get_queryset(self):
        return super().get_queryset().filter(bp=self.active_bp)


class IndexView(LoginRequiredMixin, ActiveBPMixin, TemplateView):
    template_name = "bp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.get_active()
        context['projects_graded_count'] = context['projects'].filter(ag_points__gt=-1).count()
        context['tls'] = TL.get_active()
        context['students'] = Student.get_active()
        context['students_without_project'] = Student.get_active().filter(project=None)
        return context


class ProjectListView(PermissionRequiredMixin, FilterByActiveBPMixin, ListView):
    model = Project
    template_name = "bp/project_overview.html"
    context_object_name = "projects"
    permission_required = 'bp.view_project'

    def get_queryset(self):
        return super().get_queryset().select_related('tl')


class ProjectView(PermissionRequiredMixin, DetailView):
    model = Project
    template_name = "bp/project.html"
    context_object_name = "project"
    permission_required = 'bp.view_project'


class TLListView(PermissionRequiredMixin, FilterByActiveBPMixin, ListView):
    model = TL
    template_name = "bp/tl_overview.html"
    context_object_name = "tls"
    permission_required = 'bp.view_tl'

    def get_queryset(self):
        return super().get_queryset().filter(confirmed=True)


class TLView(PermissionRequiredMixin, DetailView):
    model = TL
    template_name = "bp/tl.html"
    context_object_name = "tl"
    permission_required = 'bp.view_tl'


class LogListView(PermissionRequiredMixin, FilterByActiveBPMixin, ListView):
    model = TLLog
    template_name = "bp/log_overview.html"
    context_object_name = "logs"
    permission_required = "bp.view_tllog"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('group', 'tl')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Logs"
        return context


class LogAttentionListView(LogListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Logs (Aufmerksamkeit nötig)"
        return context

    def get_queryset(self):
        return super().get_queryset().filter(requires_attention=True)


class LogView(PermissionRequiredMixin, FilterByActiveBPMixin, DetailView):
    model = TLLog
    template_name = "bp/log.html"
    context_object_name = "log"
    permission_required = "bp.view_tllog"


class ProjectByOrderIDMixin:
    def get_object(self, queryset=None):
        return Project.objects.get(order_id=self.kwargs["order_id"])


class AGGradeView(ProjectByOrderIDMixin, UpdateView):
    model = Project
    form_class = AGGradeForm
    template_name = "bp/project_grade.html"
    context_object_name = "project"

    def get_success_url(self):
        return reverse("bp:ag_grade_success", kwargs={"order_id": self.object.order_id})

    def _get_secret_from_url(self):
        return self.kwargs.get("secret", "")

    def get(self, request, *args, **kwargs):
        # Redirect if secret is invalid
        object = self.get_object()
        if self._get_secret_from_url() != get_order_secret(object.order_id):
            return redirect("bp:ag_grade_invalid")

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initials = super().get_initial()

        # Show empty field instead of default value of -1 as this might confuse the AGs
        if self.object.ag_points == -1:
            initials["ag_points"] = ""

        # Populate information fields for AG (will not be used for updating)
        initials["project"] = self.object.title
        initials["name"] = self.object.ag

        # Populate hidden secret field
        initials["secret"] = self._get_secret_from_url()
        return initials


class AGGradeSuccessView(ProjectByOrderIDMixin, DetailView):
    model = Project
    context_object_name = "project"
    template_name = "bp/project_grade_success.html"


@permission_required("bp.view_student")
def grade_export_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Bewertung-AG.csv"'

    writer = csv.writer(response, delimiter=",")
    writer.writerow(['ID', 'Vollständiger Name', 'E-Mail-Adresse', 'Status', 'Gruppe', 'Bewertung', 'Bestwertung', 'Bewertung kann geändert werden', 'Zuletzt geändert (Bewertung)', 'Feedback als Kommentar'])

    for student in Student.get_active().filter(project__isnull=False):
        writer.writerow([student.moodle_id, student.name, student.mail, "", student.project.moodle_name, student.project.ag_points, 100, "Ja", "-", student.project.ag_points_justification])

    return response


class ProjectImportView(PermissionRequiredMixin, FormView):
    template_name = "bp/projects_import.html"
    form_class = ProjectImportForm
    success_url = reverse_lazy("bp:project_list")
    permission_required = "bp.add_project"

    def form_valid(self, form):
        import_count = 0
        reader = csv.DictReader(io.TextIOWrapper(form.cleaned_data.get("csvfile").file), delimiter=";")
        active_bp = BP.get_active()
        for row in reader:
            try:
                Project.objects.create(**{
                    "nr": row["nr"],
                    "ag": row["ag"],
                    "ag_mail": row["ag_mail"],
                    "title": row["title"],
                    "order_id": row["order_id"],
                    "bp": active_bp,
                })
                print(f"Projekt {row['title']} importiert")
                import_count += 1
            except IntegrityError:
                print(f"Projekt {row['title']} existiert bereits")
        messages.add_message(self.request, messages.SUCCESS, f"{import_count} Projekt(e) erfolgreich importiert")
        return super().form_valid(form)


class StudentListView(PermissionRequiredMixin, FilterByActiveBPMixin, ListView):
    model = Student
    template_name = "bp/student_overview.html"
    context_object_name = "students"
    permission_required = 'bp.view_student'

    def get_queryset(self):
        return super().get_queryset().select_related('project')


class StudentImportView(PermissionRequiredMixin, FormView):
    template_name = "bp/students_import.html"
    form_class = StudentImportForm
    success_url = reverse_lazy("bp:student_list")
    permission_required = "bp.add_student"

    def form_valid(self, form):
        import_count = 0
        reader = csv.DictReader(io.TextIOWrapper(form.cleaned_data.get("csvfile").file), delimiter=",")
        active_bp = BP.get_active()
        for row in reader:
            try:
                if not row["Gruppe"].startswith("Nicht Mitglied einer Gruppe"):
                    project = Project.objects.get(nr=row["Gruppe"].split("_")[0])
                    Student.objects.create(**{
                        "name": row["Vollständiger Name"],
                        "moodle_id": row["ID"],
                        "mail": row["E-Mail-Adresse"],
                        "project": project,
                        "bp": active_bp,
                    })
                    print(f"Teilnehmer*in {row['Vollständiger Name']} importiert")
                    import_count += 1
            except IntegrityError:
                print(f"Teilnehmer*in {row['Vollständiger Name']} existiert bereits")
        messages.add_message(self.request, messages.SUCCESS, f"{import_count} Teilnehmende erfolgreich importiert")
        return super().form_valid(form)


class LogTLOverview(LoginRequiredMixin, TemplateView):
    template_name = "bp/log_tl_overview.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect("bp:index")
        return super().get(request, *args, **kwargs)


class LogTLCreateView(LoginRequiredMixin, CreateView):
    model = TLLog
    form_class = TLLogForm
    template_name = "bp/log_tl_create_update.html"

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display projects that belong to a given user"""

        kwargs = super(LogTLCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Log gespeichert")
        return reverse_lazy('bp:log_tl_start')

    def get_project_by_request(self, request):
        return get_object_or_404(Project, nr=self.kwargs.get("group", -1), bp=BP.get_active())

    def get(self, request, *args, **kwargs):
        project = self.get_project_by_request(request)
        if self.request.user.tl != project.tl:
            messages.add_message(request, messages.WARNING, "Du darfst für diese Gruppe kein Log anlegen")
            return redirect("bp:log_tl_start")
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initials = super().get_initial()

        project = self.get_project_by_request(self.request)

        # Populate hidden form fields
        initials["group"] = project
        initials["bp"] = project.bp
        initials["tl"] = self.request.user.tl

        return initials


class LogTLUpdateView(LoginRequiredMixin, UpdateView):
    model = TLLog
    form_class = TLLogUpdateForm
    template_name = "bp/log_tl_create_update.html"

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Log aktualisiert")
        return reverse_lazy('bp:log_tl_start')


class LogTLDeleteView(LoginRequiredMixin, DeleteView):
    model = TLLog
    template_name = "bp/log_tl_delete.html"

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Log gelöscht")
        return reverse_lazy('bp:log_tl_start')
