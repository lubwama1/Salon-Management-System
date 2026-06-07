from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from .models import Service, ServiceCategory
from django.contrib.auth.decorators import login_required
from .forms import ServiceCategoryForm, ServiceForm
from django.contrib import messages
from django.db.models import Count
from admin_manager.decorators import superuser_required
from django.db.models import Q
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from admin_manager.mixins import AdminRequiredMixin
from django.db.models import Prefetch
from feedback.models import Feedback

# SERVICES
@superuser_required
def add_service(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.service_category = category
            service.save()
            messages.success(
                request, f'Service ({service.name}) created successfully.')
            return redirect('services:service-detail', category.id)
        else:
            messages.error(request, 'An ERROR occured creating a service')
            return redirect('services:service-add', category.id)
    else:
        form = ServiceForm()
    form.fields['service_category'].initial = category
    form.fields['service_category'].disabled = True
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'services/add-service.html', context)


class AddServiceView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/add-service.html'
    # context_data_name = 'category'

    def test_func(self):
        return self.request.user.is_superuser

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        category = get_object_or_404(
            ServiceCategory,
            slug=self.kwargs['category_slug']
        )

        form.fields['service_category'].initial = category
        form.fields['service_category'].disabled = True
        return form

    def form_valid(self, form):
        service = form.instance
        service.service_category = get_object_or_404(
            ServiceCategory,
            slug=self.kwargs['category_slug']
        )

        messages.success(
            self.request,
            f'Service ({service.name}) created successfully.'
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'services:service-detail',
            kwargs={'category_slug': self.kwargs['category_slug']}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            ServiceCategory, slug=self.kwargs['category_slug']
        )

        return context


@superuser_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    category = service.service_category
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            updated_service = form.save(commit=False)
            updated_service.service_category = category
            updated_service.save()
            messages.success(request, 'Service updated successfully.')

            return redirect('services:service-detail', category.id)
        else:
            messages.error(request, 'ERROR updating service.')
    else:
        form = ServiceForm(instance=service)
    form.fields['service_category'].disabled = True
    return render(request, 'services/edit-service.html', {
        'form': form,
        'category': category,
        'service': service,
    })


class EditServiceView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Service
    slug_url_kwarg = 'service_slug'
    form_class = ServiceForm
    template_name = 'services/edit-service.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['service_category'].disabled = True
        return form

    def form_valid(self, form):
        service = form.instance

        service.service_category = service.service_category

        messages.success(
            self.request,
            f'Service - ({service.name.upper()}) updated successfully.'
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'services:service-detail',
            kwargs={'category_slug': self.object.service_category.slug}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        service = self.get_object()

        context['category'] = service.service_category

        return context


@superuser_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    category_id = service.service_category.id
    service.delete()
    messages.success(request, 'Service deleted successfully.')
    return redirect('services:service-detail', category_id)


class DeleteServiceView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Service
    slug_url_kwarg = 'service_slug'

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        service = self.get_object()
        return reverse_lazy(
            'services:service-detail',
            kwargs={'category_slug': service.service_category.slug}
        )

    def delete(self, request, *args, **kwargs):
        service = self.get_object()
        messages.success(
            request,
            f'Service ({service.name.upper()}) deleted successfully.'
        )
        return super().delete(request, *args, **kwargs)


def service_list(request, category_id=None):
    query = request.GET.get('search', '').strip()
    category = None
    if category_id:
        category = get_object_or_404(ServiceCategory, id=category_id)

    services = Service.objects.all().order_by('-created_at')

    if category:
        services = services.filter(service_category=category)

    if query:
        filters = (
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(service_category__name__icontains=query)
        )
        if query.isdigit():
            filters |= Q(price__lte=query)
        services = services.filter(filters).distinct()
    context = {
        'services': services,
        'category': category,
        'query': query,
    }
    return render(request, 'services/service_list.html', context)


class ServiceListView(ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get('search', '').strip()
        category_id = self.kwargs.get('category_id')

        # services = Service.objects.all().order_by('-created_at')
        services = Service.objects.prefetch_related(
            Prefetch(
                'reviews', queryset=Feedback.objects.filter(approved=True)
            )
        ).order_by('-created_at')
        # CATEGORY FILTER
        if category_id:
            category = get_object_or_404(ServiceCategory, id=category_id)
            services = services.filter(service_category=category)

        # SEARCH FILTER
        if query:
            filters = (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(service_category__name__icontains=query)
            )

            if query.isdigit():
                filters |= Q(price__lte=query)

            services = services.filter(filters).distinct()

        return services

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = self.kwargs.get('category_slug')

        context['query'] = self.request.GET.get('search', '')

        if category_slug:
            context['category'] = get_object_or_404(
                ServiceCategory,
                slug=category_slug
            )
        else:
            context['category'] = None

        return context


@superuser_required
def service_overview(request, category_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug)
    services = Service.objects.filter(
        service_category=category).order_by('-created_at')
    context = {
        'services': services,
        'category_slug': category.slug
    }
    return render(request, 'services/services-overview.html', context)


class ServiceDetailView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Service
    template_name = 'services/services-overview.html'
    context_object_name = 'services'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            ServiceCategory,
            slug=category_slug
        )

        return Service.objects.filter(
            service_category=category
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            ServiceCategory,
            slug=self.kwargs['category_slug']
        )
        return context
# SERVICE CATEGORY


@superuser_required
def add_service_category(request):
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Service Category ({form.cleaned_data["name"]}) created successfully.')
            return redirect('services:category-list')
        else:
            messages.error(request, 'An ERROR occured creating category!')
            return redirect('services:category-add')
    else:
        form = ServiceCategoryForm()
    context = {
        'form': form
    }
    return render(request, 'services/add-category.html', context)


class AddServiceCategoryView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = ServiceCategory
    template_name = 'services/add-category.html'
    form_class = ServiceCategoryForm
    success_url = reverse_lazy('services:category-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        category = form.instance

        messages.success(
            self.request,
            f'Service Category ({category.name}) created successfully.'
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'An error occurred creating category!'
        )
        return super().form_invalid(form)


@superuser_required
def edit_category(request, category_id):
    category_instance = get_object_or_404(ServiceCategory, id=category_id)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, instance=category_instance)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'The Service Category ({form.cleaned_data["name"]}) is updated successfully.')
            return redirect('services:category-list')
        else:
            messages.error(
                request, f'An ERROR occured editing the Service: {category_instance.name}')
            return redirect('services:category-list')
    else:
        form = ServiceCategoryForm(instance=category_instance)
    context = {
        'form': form,
        'category': category_instance,
    }
    return render(request, 'services/edit-category.html', context)


class EditCategoryView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ServiceCategory
    template_name = 'services/edit-category.html'
    form_class = ServiceCategoryForm
    slug_url_kwarg = 'category_slug'
    context_object_name = 'category'

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        category = form.instance

        messages.success(
            self.request,
            f'The Service Category ({category.name}) is updated successfully.'
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            f'An error occurred editing the Service: {form.instance.name}'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('services:category-list')


@superuser_required
def delete_category(request, category_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug)
    category.delete()
    messages.success(
        request, f'Category ({category.name}) deleted successfully.')
    return redirect('services:category-list')


class DeleteCategoryView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = ServiceCategory
    slug_url_kwarg = 'category_slug'
    success_url = reverse_lazy('services:category-list')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category_name = category.name

        response = super().delete(request, *args, **kwargs)

        messages.success(
            request,
            f'Category ({category_name}) deleted successfully.'
        )

        return response


@superuser_required
def category_overview(request):
    service_categories = ServiceCategory.objects.annotate(
        service_count=Count('services')
    ).order_by('-created_at')
    context = {
        'service_categories': service_categories,
    }
    return render(request, 'services/category-overview.html', context)


class CategoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = ServiceCategory
    template_name = 'services/category-overview.html'
    context_object_name = 'service_categories'

    def get_queryset(self):
        return ServiceCategory.objects.prefetch_related('services').annotate(
            service_count=Count('services')
        ).order_by('-created_at')

    def test_func(self):
        return self.request.user.is_superuser

