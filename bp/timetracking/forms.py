from datetime import timedelta

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import TimeInterval, TimeTrackingEntry


class TimeIntervalForm(forms.ModelForm):
    class Meta:
        model = TimeInterval
        fields = ['group', 'name', 'start', 'end']

        widgets = {
            'group': forms.HiddenInput,
            'start': forms.DateInput(attrs={'type': 'date'}),
            'end'  : forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that only projects of the current user
        are given as options"""

        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = self.request.user.tl.project_set.all()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('end', None) and cleaned_data.get('start', None):
            if cleaned_data['end'] < cleaned_data['start']:
                self.add_error('end', "Ende muss später als Beginn sein")

        return cleaned_data

class NameGeneratorFactory():
    def kw_start(start, end):
        return f"KW {start.isocalendar().week}"
    def kw_end(start, end):
        return f"KW {end.isocalendar().week}"
    def full_name(start, end):
        return f"{start.strftime('%d.%m.%y')} - {end.strftime('%d.%m.%y')}"
    def end_date_only(start, end):
        return f"{end.strftime('%d.%m.%y')}"

    generators = {
        "kw_end" : (kw_end, "KW nach Enddatum: KW 2"),
        "kw_start" : (kw_start, "KW nach Startdatum: KW 1"),
        "full_name" : (full_name, "Voller Name: 01.01.04 - 07.01.04"),
        "end_date_only" : (end_date_only, "Enddatum: 07.01.04"),
    }

    @classmethod
    def get_choices(cls):
        return ((key, label) for key, (gen, label) in cls.generators.items())

    @classmethod
    def get_name_generator(cls, choice):
        return cls.generators.get(choice, (None, None))[0]

class TimeIntervalGenerationForm(forms.Form):
    group = forms.ModelChoiceField(queryset=None, widget=forms.HiddenInput)
    interval_length = forms.IntegerField(label="Länge der Intervalle (Tage)",
                                         widget=forms.NumberInput(attrs={'min': 1, 'max': 999, 'required': True, 'type': 'number',}))
    name_generator = forms.TypedChoiceField(label="Namensvergabe", choices=NameGeneratorFactory.get_choices(), coerce=NameGeneratorFactory.get_name_generator)
    start = forms.DateField(label="Beginn des ersten Intervalls",
                            widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(label="Ende des letzten Intervalls",
                            widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that only projects of the current user
        are given as options"""

        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = self.request.user.tl.project_set.all()

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('group', None) and not cleaned_data['group'] in self.request.user.tl.project_set.all():
            raise ValidationError("Ungültige Gruppe")

        if cleaned_data.get('end', None) and cleaned_data.get('start', None):
            if cleaned_data['end'] < cleaned_data['start']:
                self.add_error('end', "Ende muss später als Beginn sein")
            elif cleaned_data['end'] > cleaned_data['start'] + timedelta(weeks=30):
                self.add_error('end', "Es können nur maximal 30 Wochen generiert werden")

        if cleaned_data.get('interval_length', None) != None:
            if cleaned_data['interval_length'] < 1:
                self.add_error('interval_length', "Intervall muss mindestens 1 Tag lang sein")
            else:
                cleaned_data['timedelta'] = timedelta(days=cleaned_data['interval_length'])

        return cleaned_data

    def save(self):
        def generate_intervals(start_date, end_date, delta):
            next_start = start_date + delta
            while next_start - timedelta(days=1) < end_date:
                # end date is included in interval
                yield start_date, next_start - timedelta(days=1)
                start_date = next_start
                next_start = next_start + delta
            yield start_date, end_date

        generate_name = self.cleaned_data['name_generator']
        group = self.cleaned_data['group']
        created_intervals = 0
        for start, end in generate_intervals(self.cleaned_data['start'], self.cleaned_data['end'], self.cleaned_data['timedelta']):
            try:
                interval = TimeInterval.objects.create(**{
                    "name" : generate_name(start, end),
                    "start" : start,
                    "end" : end,
                    "group" : group,
                    })
                interval.save()
                created_intervals += 1
            except IntegrityError:
                messages.add_message(self.request, messages.ERROR,
                                     f"Intervall von {start} bis {end} mit Namen '{generate_name(start, end)}' konnte nicht erstellt werden")
        messages.add_message(self.request, messages.SUCCESS, f"{created_intervals} Intervalle gespeichert!")

class TimeIntervalUpdateForm(forms.ModelForm):
    class Meta:
        model = TimeInterval
        fields = ['name', 'start', 'end']

class TimeIntervalEntryForm(forms.ModelForm):
    class Meta:
        model = TimeTrackingEntry
        fields = ['category', 'hours', 'interval']

        widgets = {
            'interval': forms.HiddenInput,
            'hours'   : forms.NumberInput(attrs={'min': 0, 'max': 999, 'step' : 0.25, 'required': True, 'type': 'number',})
        }

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that only projects of the current user
        are given as options"""

        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['interval'].queryset = self.request.user.student.project.timeinterval_set.order_by('-start')

    def clean(self):
        cleaned_data = super().clean()

        cleaned_data['student'] = self.request.user.student
        try:
            if cleaned_data['student'] not in cleaned_data['interval'].group.student_set.all():
                raise ValidationError("Ungültiges Intervall angegeben")
        except KeyError:
            raise ValidationError("Ungültiges Intervall angegeben")

        if cleaned_data.get('hours', 0) < 0:
            self.add_error('hours', "Stundenzahl muss nicht-negativ sein")

        if not cleaned_data.get('category', None):
            self.add_error('category', "Bitte gib eine Kategorie an")

        return cleaned_data

    def save(self):
        obj, created = TimeTrackingEntry.objects.update_or_create(student =self.cleaned_data['student'],
                                                                  interval=self.cleaned_data['interval'],
                                                                  category=self.cleaned_data['category'],
                                                                  defaults={'hours' : self.cleaned_data['hours']})

        self.instance = obj

class TLTimeIntervalEntryCorrectionForm(forms.ModelForm):
    class Meta:
        model = TimeTrackingEntry
        fields = ['student', 'category', 'hours', 'interval']

        widgets = {
            'interval': forms.HiddenInput,
            'hours'   : forms.NumberInput(attrs={'min': 0, 'max': 999, 'step' : 0.25, 'required': True, 'type': 'number',})
        }

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that only projects of the current user
        are given as options"""

        self.interval = kwargs.pop('interval')
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.interval.group.student_set

    def clean(self):
        cleaned_data = super().clean()

        student = cleaned_data.get('student', None)
        if not student:
            self.add_error('student', "Bitte gib das betreffende Teammitglied an")
        try:
            if student and student not in cleaned_data['interval'].group.student_set.all():
                raise ValidationError("Ungültiges Intervall angegeben")
        except KeyError:
            raise ValidationError("Ungültiges Intervall angegeben")

        if cleaned_data.get('hours', 0) < 0:
            self.add_error('hours', "Stundenzahl muss nicht-negativ sein")

        if not cleaned_data.get('category', None):
            self.add_error('category', "Bitte gib eine Kategorie an")

        return cleaned_data

    def save(self):
        obj, created = TimeTrackingEntry.objects.update_or_create(student =self.cleaned_data['student'],
                                                                  interval=self.cleaned_data['interval'],
                                                                  category=self.cleaned_data['category'],
                                                                  defaults={'hours' : self.cleaned_data['hours']})

        self.instance = obj