import requests
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from .forms import CreateInvoiceForm
from .ymoney import get_operation_url, is_operation_success
import uuid
from .tasks import check_payment_task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import json

class CreateInvoiceView(LoginRequiredMixin, CreateView):
    form_class = CreateInvoiceForm
    template_name = 'insta_app/payment.html'

    def form_valid(self, form):
        label = uuid.uuid4()
        form.instance.user = self.request.user.paymentaccount
        form.instance.invoice_label = str(label)
        self.success_url = get_operation_url(form.instance.amount, str(label))
        check_payment_task.delay(label)
        return super().form_valid(form)




class YooMoneyNotifications(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        requests.get(f'https://api.telegram.org/bot1296277300:AAFb9LInLUeMRCpQOg0gpG3L2JFX9kImTjM/sendMessage?chat_id=727215391&text={str(request)}')
        return HttpResponse(status=200)