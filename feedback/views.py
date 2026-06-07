from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from .models import Feedback
from admin_manager.mixins import AdminRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from services.models import Service
from .forms import FeedbackForm
from django.contrib import messages


class ReviewView(LoginRequiredMixin, ListView):
    model = Feedback
    context_object_name = 'reviews'
    template_name = 'feedback/reviews.html'


# @login_required(login_url='users:login')
# def service_review(request, service_id):
#     service = get_object_or_404(Service, id=service_id)
    # reviews = Feedback.objects.filter(service=service, approved=True).order_by('-created_at')
#     return render(request, 'services/reviews.html', {'reviews': reviews})

class ServiceReviewView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'feedback/reviews.html'
    slug_url_kwarg = 'service_slug'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['reviews'] = Feedback.objects.filter(
            service=self.object,
            approved=True
        ).order_by('-created_at')
        context['service'] = self.get_object()

        return context

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:

            Feedback.objects.create(
                user=request.user,
                service=self.object,
                rating=int(rating),
                comment=comment
            )

            messages.success(request, 'Review submitted successfully.')

        return redirect(
            'feedback:service-reviews',
            service_slug=self.object.slug
        )


def service_review(request, service_slug):
    service = get_object_or_404(Service, slug=service_slug)
    reviews = Feedback.objects.filter(
        service=service, approved=True).order_by('-created_at')
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Feedback.objects.create(
                user=request.user,
                service=service,
                comment=comment,
                rating=rating
            )
            messages.success(request, 'Review submitted successfully.')
            return redirect('feedback:service-reviews', service_slug=service.slug)
    return render(request, 'feedback/reviews.html', {'reviews': reviews, 'service': service})


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback/create-review.html'

    def form_valid(self, form):
        service = get_object_or_404(Service, slug=self.kwargs['service_slug'])
        form.instance.service = service
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'services:service-reviews',
            kwargs={'service_slug': self.kwargs['service_slug']}
        )


