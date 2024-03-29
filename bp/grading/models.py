from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class AGGrade(models.Model):
    class Meta:
        abstract = True

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    ag_points = models.SmallIntegerField(verbose_name="Punkte für den Implementierungsteil", help_text="0-100")
    ag_points_justification = models.TextField(verbose_name="Begründung")
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def simple_timestamp(self):
        return self.timestamp.strftime('%d.%m.%y %H:%M')

    @staticmethod
    def get_active():
        return TLLog.objects.filter(bp__active=True)


class AGGradeBeforeDeadline(AGGrade):
    class Meta:
        verbose_name = "Bewertung"
        verbose_name_plural = "Bewertungen"
        ordering = ['project', 'timestamp']

    def __str__(self):
        return f"Bewertung für Projekt {self.project.nr} am {self.simple_timestamp}"


class AGGradeAfterDeadline(AGGrade):
    class Meta:
        verbose_name = "Bewertung (verspätet)"
        verbose_name_plural = "Bewertungen (verspätet)"
        ordering = ['project', 'timestamp']

    def __str__(self):
        return f"Verspätete Bewertung für Projekt {self.project.nr} am {self.simple_timestamp}"


class PitchGrade(models.Model):
    class Meta:
        verbose_name = "Bewertung der Vorträge"
        verbose_name_plural = "Bewertungen der Vorträge"
        ordering = ['project']

    project = models.OneToOneField("Project", on_delete=models.CASCADE)
    grade_points = models.DecimalField(verbose_name="Punkte für die Vorträge", max_digits=5, decimal_places=2,
                                       validators=[MaxValueValidator(20), MinValueValidator(0)])
    grade_notes = models.TextField(verbose_name="Notiz")

    def __str__(self):
        return f"Bewertung der Vorträge für Projekt {self.project.nr}"


class DocsGrade(models.Model):
    class Meta:
        verbose_name = "Bewertung der Dokumentation"
        verbose_name_plural = "Bewertungen der Dokumentationen"
        ordering = ['project']

    project = models.OneToOneField("Project", on_delete=models.CASCADE)
    grade_points = models.DecimalField(verbose_name="Punkte für die Dokumentation", max_digits=5, decimal_places=2,
                                       validators=[MaxValueValidator(80), MinValueValidator(0)])
    grade_notes = models.TextField(verbose_name="Notiz")

    def __str__(self):
        return f"Bewertung der Dokumentation für Projekt {self.project.nr}"
