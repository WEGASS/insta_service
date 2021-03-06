from django.shortcuts import render, redirect
from .models import TaskParseLikes, TaskParseSubscribers, Task
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import TaskParseSubscribersForm, TaskParseLikesForm
from payments.models import Transaction
from .tasks import parse


class HomeView(TemplateView):
    template_name = 'insta_app/home.html'


class TasksView(LoginRequiredMixin, TemplateView):
    template_name = 'insta_app/tasks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.request.user.task_set.order_by('-timestamp')
        return context


class CreateTaskView(LoginRequiredMixin, CreateView):
    template_name = 'insta_app/parser.html'
    form_class = TaskParseSubscribersForm
    form_class_2 = TaskParseLikesForm
    success_url = reverse_lazy('main_app:tasks')

    def post(self, request, *args, **kwargs):
        if 'subs' in request.POST['form_type']:
            form = self.form_class(request.POST)
        elif 'likes' in request.POST['form_type']:
            form = self.form_class_2(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        payment_acc = self.request.user.paymentaccount
        if 'subs' in self.request.POST['form_type']:
            total_sum = TaskParseSubscribers(instagram_users=form.instance.instagram_users, quantity_users=form.instance.quantity_users).total_sum()
            if payment_acc.balance >= total_sum:  # is enough balance
                payment = Transaction(user=self.request.user.paymentaccount, reason='SUB', amount=form.instance.quantity_users) #создание транзакции
                payment.save()
                payment_acc.balance -= total_sum  # change balance
                payment_acc.save()
                form.instance.user = self.request.user
                form.instance.name = f'Задача "парсинг подписчиков" №'
                form.instance.payment = payment
            else:
                return render(request=self.request, template_name='payments/not_enough_balance.html')

        elif 'likes' in self.request.POST['form_type']:
            total_sum = TaskParseLikes(posts=form.instance.posts, quantity_users=form.instance.quantity_users).total_sum()
            if payment_acc.balance >= total_sum:  # is enough balance
                payment = Transaction(user=self.request.user.paymentaccount, reason='SUB', amount=form.instance.quantity_users)  # создание транзакции
                payment.save()
                payment_acc.balance -= total_sum  # change balance
                payment_acc.save()
                form.instance.user = self.request.user
                form.instance.name = f'Задача "парсинг лайков" №'
            else:
                return render(request=self.request, template_name='payments/not_enough_balance.html')

        return super().form_valid(form)

    # redo smtime later
    def get_success_url(self):
        parse.delay(self.object.pk)
        return super().get_success_url()


class TaskResultView(LoginRequiredMixin, DetailView):
    template_name = 'insta_app/parser.html'
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['third_stage'] = True
        return context
