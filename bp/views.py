import csv
import io

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, FormView

from bp.forms import AGGradeForm, ProjectImportForm
from bp.models import BP, Project, Student, TL
from bp.pretix import get_order_secret


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


class IndexView(ActiveBPMixin, TemplateView):
    template_name = "bp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.get_active()
        context['tls'] = TL.get_active()
        context['students'] = Student.get_active()
        context['students_without_project'] = Student.get_active().filter(project=None)
        return context


class ProjectListView(FilterByActiveBPMixin, ListView):
    model = Project
    template_name = "bp/project_overview.html"
    context_object_name = "projects"


class ProjectView(DetailView):
    model = Project
    template_name = "bp/project.html"
    context_object_name = "project"


class TLListView(FilterByActiveBPMixin, ListView):
    model = TL
    template_name = "bp/tl_overview.html"
    context_object_name = "tls"


class TLView(DetailView):
    model = TL
    template_name = "bp/tl.html"
    context_object_name = "tl"


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
        # Get secret from Pretix Order URL of form
        # https://<pretix-host>/<organizer>/<event>/order/<order_id>/<secret>/open/<hash>/
        return self.request.GET["login"].split("/")[-4]

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


class ProjectImportView(FormView):
    template_name = "bp/projects_import.html"
    form_class = ProjectImportForm
    success_url = reverse_lazy("bp:project_list")

    def form_valid(self, form):
        import_count = 0
        reader = csv.DictReader(io.TextIOWrapper(form.cleaned_data.get("csvfile").file), delimiter=";")
        for row in reader:
            try:
                Project.objects.create(**{
                    "nr": row["nr"],
                    "ag": row["ag"],
                    "ag_mail": row["ag_mail"],
                    "title": row["title"],
                    "order_id": row["order_id"],
                    "bp": BP.get_active(),
                })
                print(f"Projekt {row['title']} importiert")
                import_count += 1
            except IntegrityError:
                print(f"Projekt {row['title']} existiert bereits")
        messages.add_message(self.request, messages.SUCCESS, f"{import_count} Projekt(e) erfolgreich importiert")
        return super().form_valid(form)
