from django.shortcuts import redirect, render
import requests
from services.models import ServiceCategory
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView, CreateView
from django.views import View
from .models import Contact, TeamMember
from django.contrib import messages
from .forms import ContactForm
# @login_required(login_url='users:login')


def home(request):
    service_categories = ServiceCategory.objects.all()
    return render(request, 'core/home.html', {'service_categories': service_categories})


class HomeView(ListView):
    model = ServiceCategory
    template_name = 'core/home.html'
    context_object_name = 'service_categories'


class AboutView(ListView):
    model = TeamMember
    template_name = 'core/about.html'
    context_object_name = 'team_members'
    # def get(self, request):
    #     return render(request, self.template_name)

    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by('display_order')

# def about_us(request):
#     return render(request, 'core/about.html')


class ContactView(CreateView):
    model = Contact
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/'


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            formspree_url = 'https://formspree.io/f/xkgvpzve'
            data = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
                "_subject": "New Contact Message from Elite Saloon Website",
                "_captcha": "false",
            }
            try:
                requests.post(formspree_url, data=data)

            except requests.RequestException as e:
                messages.error(
                    request, "An error occurred while submitting the form. Please try again.")

            messages.success(
                request, "Thank you for contacting us! We'll get back to you soon.")
            return redirect('core:home')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'
