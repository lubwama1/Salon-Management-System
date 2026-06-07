
from django.shortcuts import render
from .forms import SiteSettingsForm
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SiteSettings
from django.urls import reverse_lazy
from admin_manager.mixins import AdminRequiredMixin

class SiteSettingsCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = 'site_settings/site_settings_form.html'
    success_url = reverse_lazy('site_settings:settings')


class SiteSettingsView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = SiteSettings
    template_name = 'site_settings/settings.html'
    context_object_name = 'setting'

    def get_object(self):
        return SiteSettings.objects.first()


class SiteSettingsUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = 'site_settings/update-settings.html'
    success_url = reverse_lazy('site_settings:settings')
    def get_object(self):
        return SiteSettings.objects.first()