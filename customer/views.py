
from django.http import HttpResponse
from django.http import HttpResponse
from django.utils import timezone
from users.models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomerAppointment
from .forms import AppointmentForm, CustomerProfileForm
from django.contrib import messages
from services.models import Service
from admin_manager.models import AdminAppointmentApproval
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views import View
from notifications.models import Notification
from admin_manager.forms import AdminAppointmentApprovalForm
from feedback.models import Feedback
from notifications.notify_helper import notify


@login_required(login_url='users:login')
def booking(request, service_slug=None):
    if service_slug:
        selected_service = get_object_or_404(Service, slug=service_slug)
    else:
        selected_service = None
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if selected_service:
                appointment.service = selected_service
            appointment.user = request.user
            appointment.save()
            messages.success(request, 'Appointment submitted successfully.')
            return redirect('customer:appointment_confirmation')
        else:
            messages.error(
                request, 'There was an error submitting your appointment. Please check the form and try again.')
            return redirect('customer:booking')
    else:
        form = AppointmentForm()
        if selected_service:
            form.fields['service'].initial = selected_service
            form.fields['service'].disabled = True
        context = {
            'form': form
        }
    return render(request, 'customer/booking.html', context)


class BookingView(LoginRequiredMixin, CreateView):
    model = AppointmentForm
    form_class = AppointmentForm
    template_name = 'customer/booking.html'
    success_url = reverse_lazy('customer:appointment-confirmation')

    def dispatch(self, request, *args, **kwargs):
        self.service_slug = kwargs.get('service_slug')
        self.selected_service = None

        if self.service_slug:
            self.selected_service = get_object_or_404(
                Service, slug=self.service_slug)

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.selected_service:
            form.fields['service'].initial = self.selected_service
            form.fields['service'].disabled = True

        return form

    def form_valid(self, form):
        form.instance.user = self.request.user

        if self.selected_service:
            form.instance.service = self.selected_service
        admin = CustomUser.objects.filter(
            role=CustomUser.UserRoleChoices.ADMIN).first()

        if admin:
            # Notification.objects.create(
            #     sender=self.request.user,
            #     receiver=admin,
            #     notification_type=Notification.NotificationTypes.APPOINTMENT,
            #     link=reverse('admin_manager:dashboard'),
            # message=(
            #     f"{self.request.user.username} has booked an appointment for "
            #     f"{form.instance.service} on {form.instance.appointment_date} at {form.instance.time_slot}. "
            #     f"Please review and approve."
            # )
            # )

            notify(
                sender=self.request.user,
                receiver=admin,
                message=(
                    f"{self.request.user.username} has booked an appointment for "
                    f"{form.instance.service} on {form.instance.appointment_date} at {form.instance.time_slot}. "
                    f"Please review and approve."
                ),
                notification_type=Notification.NotificationTypes.APPOINTMENT,
                link=reverse('admin_manager:dashboard'),
            )
        messages.success(self.request, 'Appointment submitted successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'There was an error submitting your appointment. Please check the form and try again.'
        )
        return super().form_invalid(form)


@login_required(login_url='users:login')
def appointment_confirmation(request):
    appointments = CustomerAppointment.objects.last()
    print(appointments)
    context = {
        'approval': appointments,
    }
    return render(request, 'customer/appointment_confirmation.html', context)


class AppointmentConfirmationView(LoginRequiredMixin, DetailView):
    model = CustomerAppointment
    template_name = 'customer/appointment_confirmation.html'
    context_object_name = 'approval'

    def get_object(self):
        return CustomerAppointment.objects.filter(
            user=self.request.user
        ).last()


class AppointmentHistoryView(LoginRequiredMixin, ListView):
    model = CustomerAppointment
    template_name = 'customer/appointment_history.html'
    context_object_name = 'appointments'
    paginate_by = 3

    def get_queryset(self):
        return CustomerAppointment.objects.filter(
            user=self.request.user
        ).select_related(
            'admin_approval',
            'service'
        ).order_by('-appointment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        appointments = context['appointments']  # actual queryset (paginated)
        base_qs = self.get_queryset()
        context['status'] = CustomerAppointment.AppointmentStatusChoices

        appointment = CustomerAppointment.objects.filter(
            user=self.request.user
        ).select_related('service').last()

        if appointment:
            context['user_reviews'] = Feedback.objects.filter(
                user=self.request.user,
                service=appointment.service,
                approved=True
            )
        else:
            context['user_reviews'] = Feedback.objects.none()
        context['ADMIN'] = CustomUser.UserRoleChoices.ADMIN
        context['approved_count'] = base_qs.filter(
            status=CustomerAppointment.AppointmentStatusChoices.APPROVED).count()
        context['pending_count'] = base_qs.filter(
            status=CustomerAppointment.AppointmentStatusChoices.PENDING).count()
        context['completed_count'] = base_qs.filter(
            status=CustomerAppointment.AppointmentStatusChoices.COMPLETED).count()
        context['form'] = AdminAppointmentApprovalForm(user=self.request.user)
        context['total_appointments'] = base_qs.count()

        return context


@login_required(login_url='users:login')
def appointment_history(request):
    appointments = CustomerAppointment.objects.filter(
        user=request.user
    ).select_related(
        'admin_approval').order_by('-appointment_date')
    admin_app = AdminAppointmentApproval.objects.filter(
        customer_appointment__in=appointments)
    status = CustomerAppointment.AppointmentStatusChoices
    admin = CustomUser.UserRoleChoices.ADMIN
    form = AppointmentForm()
    paginated_by = Paginator(appointments, 3)
    page_number = request.GET.get('page')
    try:
        page_obj = paginated_by.page(page_number)
    except PageNotAnInteger:
        page_obj = paginated_by.page(1)
    except EmptyPage:
        page_obj = paginated_by.page(paginated_by.num_pages)
    context = {
        'appointments': page_obj,
        'status': status,
        'admin_app': admin_app,
        'page_obj': page_obj,
        'admin': admin,
        'form': form,
    }
    return render(request, 'customer/appointment_history.html', context)


def resubmit_appointment(request, appointment_id):
    appointment = get_object_or_404(CustomerAppointment, id=appointment_id)
    if appointment.status != CustomerAppointment.AppointmentStatusChoices.REJECTED:
        messages.error(
            request, 'Only rejected appointments can be resubmitted.')
        return redirect('customer:appointment_history')
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment resubmitted successfully.')
            return redirect('customer:appointment_history')
        else:
            messages.error(
                request, 'There was an error resubmitting your appointment. Please check the form and try again.')
            return redirect('customer:resubmit_appointment', appointment_id=appointment_id)
    else:
        form = AppointmentForm(instance=appointment)
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'customer/resubmit_appointment.html', context)


class ResubmitAppointmentView(LoginRequiredMixin, UpdateView):
    model = CustomerAppointment
    template_name = 'customer/resubmit_appointment.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('customer:appointment-list')

    def dispatch(self, request, *args, **kwargs):
        appointment = self.get_object()

        if appointment.status != CustomerAppointment.AppointmentStatusChoices.REJECTED:
            messages.error(
                request, 'Only rejected appointments can be resubmitted.')
            return redirect('customer:appointment-list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Appointment resubmitted successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'There was an error resubmitting your appointment. Please check the form and try again.'
        )
        return super().form_invalid(form)


def costumer_cancel_appointment(request, appointment_id):
    user = request.user
    appointment = get_object_or_404(CustomerAppointment, id=appointment_id)
    admin_approval = get_object_or_404(
        AdminAppointmentApproval, customer_appointment=appointment)
    status = CustomerAppointment.AppointmentStatusChoices
    admin_status = AdminAppointmentApproval.StatusChoices
    admin = CustomUser.objects.filter(
        role=CustomUser.UserRoleChoices.ADMIN).first()

    if not user.is_authenticated:
        return redirect('users:login')

    if request.method == 'POST':
        form = AdminAppointmentApprovalForm(request.POST, user=user)

        if appointment.status in [status.PENDING.value, status.APPROVED.value]:
            if form.is_valid():
                cancellation_reason = form.cleaned_data['cancellation_reason']
            else:
                # If form is invalid, use default reason
                cancellation_reason = 'customer_request'
                # Optionally log the form errors
                print(f"Form errors: {form.errors}")

            # Update AdminAppointmentApproval
            admin_approval.status = admin_status.CANCELED
            admin_approval.cancelled_by = user if user.role == CustomUser.UserRoleChoices.CUSTOMER else None
            admin_approval.cancelled_at = timezone.now()
            admin_approval.cancellation_reason = cancellation_reason
            admin_approval.save()

            appointment.status = status.CANCELED
            appointment.save()

            if admin:
                # Notification.objects.create(
                #     sender=user,
                #     receiver=admin,
                #     notification_type=Notification.NotificationTypes.CANCELED_APPOINTMENT,
                #     link=reverse('admin_manager:appointment-review',
                #                  args=[appointment.id]),
                #     message=(
                #         f"{user.username} has canceled their appointment for "
                #         f"{appointment.service} on {appointment.appointment_date} at {appointment.time_slot}. "
                #         f"Reason: {dict(admin_approval.CANCELLED_REASON.choices).get(cancellation_reason, cancellation_reason)} "
                #         f"Please review the cancellation."
                #     )
                # )
                notify(
                    sender=user,
                    receiver=admin,
                    message=(
                        f"{user.username} has canceled their appointment for "
                        f"{appointment.service} on {appointment.appointment_date} at {appointment.time_slot}. "
                        f"Reason: {dict(admin_approval.CANCELLED_REASON.choices).get(cancellation_reason, cancellation_reason)} "
                        f"Please review the cancellation."
                    ),
                    notification_type=Notification.NotificationTypes.CANCELED_APPOINTMENT,
                    link=reverse('admin_manager:appointment-review',
                                 args=[appointment_id]),
                )
            messages.success(request, 'Appointment canceled successfully.')
            return redirect('customer:appointment-list')
        else:
            messages.error(
                request, f'This appointment cannot be canceled. Current status: {appointment.status}')
            return redirect('customer:appointment-list')
    else:
        # If not POST, redirect back
        messages.error(request, 'Invalid request method.')
        return redirect('customer:appointment-list')


def customer_profile_view(request):
    user = request.user
    customer = CustomUser.objects.filter(
        id=user.id, role=CustomUser.UserRoleChoices.CUSTOMER).first()
    if not user.is_authenticated:
        return redirect('users:login')
    if not customer:
        return redirect('core:home')
    profile = user
    return render(request, 'customer/customer-profile.html', {'profile': profile})


class CustomerProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = 'customer/customer-profile.html'
    context_object_name = 'profile'

    def get_object(self):
        self.request.user

    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.CUSTOMER


def edit_profile(request):
    user_instance = request.user
    if request.method == 'POST':
        form = CustomerProfileForm(
            request.POST or None, request.FILES or None, instance=user_instance)
        if form.is_valid():
            # user = form.save()
            # employee_number = form.cleaned_data.get('employee_number')
            # if user.role != CustomUser.UserRoleChoices.ADMIN:
            #     form.fields.pop('employee_number')
            # if employee_number:
            #     admin_profile, created = AdminProfile.objects.get_or_create(user=user)
            #     admin_profile.employee_number = employee_number
            #     admin_profile.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('customer:customer-profile')
        else:
            messages.error(request, 'An error occured during profile update!')
            return redirect('customer:edit-profile')
    else:
        form = CustomerProfileForm(instance=user_instance)
    context = {
        'form': form
    }
    return render(request, 'customer/customer-edit-profile.html', context)


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'customer/customer-edit-profile.html'
    form_class = CustomerProfileForm
    success_url = reverse_lazy('customer:profile')

    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.CUSTOMER

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'An error occurred during profile update!')
        return super().form_invalid(form)


def notifications(request):
    customer = CustomUser.UserRoleChoices.CUSTOMER
    notifications = Notification.objects.filter(
        receiver=customer
    ).order_by('-timestamp')
    return render(request, 'admin_manager/notifications.html', {'notifications': notifications})


class NotificationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Notification
    template_name = 'customer/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(
            receiver=self.request.user
        ).order_by('-timestamp')

    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.CUSTOMER


def delete_selected_notification(request):
    if request.method == 'POST':
        notification_ids = request.POST.getlist(
            'selected_notifications'
        )
        if notification_ids:
            notifications = Notification.objects.filter(
                id__in=notification_ids, receiver=request.user
            )
            deleted_count = notifications.count()
            notifications.delete()
            messages.success(
                request,
                f"{deleted_count} notification{'s' if deleted_count > 1 else ''} deleted successfully."
            )
            return redirect('customer:notifications')

        return HttpResponse('No notifications selected.')


def delete_all_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(
            receiver=request.user
        ).delete()
        messages.success(
            request,
            f"All notifications deleted successfully."
        )

        return redirect('customer:notifications')
    return HttpResponse('No notifications selected.')
