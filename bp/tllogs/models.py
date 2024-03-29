from django.core.mail import EmailMessage
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy


class TLLog(models.Model):
    class Meta:
        verbose_name = "TL-Log"
        verbose_name_plural = "TL-Logs"
        ordering = ['-timestamp']

    STATUS_CHOICES = [
        (-2, 'Schlecht'),
        (-1, 'Eher schlecht'),
        (0, 'Neutral'),
        (1, 'Eher gut'),
        (2, 'Gut'),
    ]

    bp = models.ForeignKey("BP", on_delete=models.CASCADE)
    group = models.ForeignKey("Project", on_delete=models.CASCADE)
    tl = models.ForeignKey("TL", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    rating = models.SmallIntegerField("Bewertung", choices=[(x+1, f'{x+1} Star(s)') for x in range(5)], null=True)
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=0,
        help_text="Wie läuft es bei der Gruppe insgesamt aktuell?"
    )
    current_problems = models.ManyToManyField(verbose_name="Aktuelle Probleme", to="TLLogProblem", blank=True,
                                              help_text="Trifft davon etwas bei der Gruppe zu?")
    text = models.TextField(
        help_text="Berichte kurz: Was war die Aktivität vergangene Woche? Hast du dich mit der Gruppe getroffen? Hattet ihr anderweitig Kontakt? Gab es ein AG Treffen? Gibt es Probleme?"
    )
    requires_attention = models.BooleanField(verbose_name="Besondere Aufmerksamkeit", blank=True, default=False,
                                             help_text="Benötigt diese Gruppe aktuell besondere Aufmerksamkeit durch das Organisationsteam/sollten wir das Log besonders dringend lesen?")
    comment = models.TextField(blank=True, verbose_name="Kommentar",
                               help_text="Interner Kommentar des Orga-Teams zu diesem Eintrag")
    read = models.BooleanField(blank=True, default=False, verbose_name="Gelesen")
    handled = models.BooleanField(blank=True, default=False, verbose_name="Erledigt",
                                  help_text="Das Log forderte eine Reaktion des Orga-Teams, die bereits durchgeführt wurde.")

    @property
    def simple_timestamp(self):
        return self.timestamp.strftime('%d.%m.%y %H:%M')

    @property
    def project_title(self):
        return f"{self.group.nr}: {self.group.short_title_else_title}"

    @property
    def problems(self):
        problems_string = ", ".join(str(p) for p in self.current_problems.all())
        return problems_string if problems_string != "" else "-"

    @staticmethod
    def get_active():
        return TLLog.objects.filter(bp__active=True)

    def __str__(self):
        return f"{self.tl} für Gruppe {self.group.nr} am {self.simple_timestamp}"


class TLLogProblem(models.Model):
    class Meta:
        verbose_name = "TL-Log-Problem"
        verbose_name_plural = "TL-Log-Probleme"

    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


@receiver(post_save, sender=TLLog)
def update_tllog_receiver(sender, instance: TLLog, created, **kwargs):
    if created and settings.SEND_MAILS and instance.requires_attention:
        # Send an email for new important logs
        url = f"{'https://' + settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) > 0 else 'http://localhost'}{reverse_lazy('bp:log_detail', kwargs={'pk': instance.pk})}"
        mail = EmailMessage(
            f"[BP TL Logs] {instance.group} ({instance.simple_timestamp})",
            f"Achtung, folgendes Log von {instance.tl} erfordert besondere Aufmerksamkeit:\n\n{url}\n\n{instance.text}",
            f"{instance.tl} via BP-Tool <{settings.SEND_MAILS_FROM}>",
            [settings.SEND_MAILS_TO],
            reply_to=[instance.tl.user.email]
        )
        mail.send(fail_silently=True)

    @property
    def simple_timestamp(self):
        return self.timestamp.strftime('%d.%m.%y %H:%M')

    def __str__(self):
        return f"{self.simple_timestamp}: {self.group.nr} - {self.tl}"


class TLLogTemplate(models.Model):
    class Meta:
        verbose_name = "TL-Log Vorlage"
        verbose_name_plural = "TL-Log Vorlagen"

    bp = models.OneToOneField("BP", on_delete=models.CASCADE)
    text = models.TextField(blank=True, verbose_name="Vorlagentext",
                            help_text="Text, der den TLs als Vorlage angezeigt wird")

    def __str__(self):
        return f"Vorlage für {self.bp}"
