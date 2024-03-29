from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from lti_provider.views import LTIRoutingView

from bp.roles import has_role
from bp.views import BP, TL, Student


class TLRoutingView(LTIRoutingView):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Login happens in dispatch above
        instance = request.user
        if instance and not has_role(instance):
            if not TL.objects.filter(user=instance).first():
                TL.objects.create(user=instance, name=f"{instance.first_name} {instance.last_name}", bp=BP.get_active(),
                                  confirmed=False)
        return response


class StudentRoutingView(LTIRoutingView):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Login happens in dispatch above
        instance = request.user
        if instance and not has_role(instance):
            if instance.email and not Student.objects.filter(user=instance).first():
                associatedStudent = Student.objects.filter(mail=instance.email, bp=BP.get_active()).first()
                if associatedStudent:
                    associatedStudent.user = instance
                    associatedStudent.save()
                else:
                    messages.add_message(self.request, messages.WARNING, "E-Mail-Addresse nicht gefunden. Bitte wende dich per Mail an die Veranstalter unter bp@cs.tu-darmstadt.de.")
        return response
