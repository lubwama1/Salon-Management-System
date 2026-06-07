from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import StaffProfile
from .forms import StaffForm
from django.contrib import messages
from django.http import HttpResponse
from users.models import CustomUser
from admin_manager.models import AdminAppointmentApproval
from django.utils import timezone
from django.views.generic import DetailView, UpdateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from notifications.models import Notification
from django.db.models import Q
from django.core.paginator import Paginator
login_required(login_url='users:login')
def staff_profile_view(request):
    user = request.user
    staff = CustomUser.objects.filter(id=user.id, role=CustomUser.UserRoleChoices.STAFF).first()
    if not user.is_authenticated:
        return redirect('users:login')
    if not staff:
        return redirect('core:home')
    profile, _ = StaffProfile.objects.get_or_create(user=request.user)
    return render(request, 'staff/staff-profile.html', {'profile': profile})

class StaffProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = StaffProfile
    template_name = 'staff/staff-profile.html'
    context_object_name = 'profile'

    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.STAFF

    def get_object(self):
        profile, _ = StaffProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
@login_required(login_url='users:login')
# STAFF EDIT PROFILE VIEW
def edit_staff_profile_self(request):
    staff = get_object_or_404(StaffProfile, user=request.user)
    employee_number = staff.employee_number
    staff_role = staff.role
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        # form.fields['employee_number'].disabled = True
        # form.fields['role'].disabled = True
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile updated successfully!")
            return redirect('staff:profile')
    else:
        form = StaffForm(instance=staff)

    return render(request, 'staff/staff-edit-profile.html', {'form': form, 'staff': staff})


class EditStaffProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffProfile
    template_name = 'staff/staff-edit-profile.html'
    form_class = StaffForm
    success_url = reverse_lazy('staff:profile')
    context_object_name = 'staff'
    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.STAFF
    def get_object(self):
        return get_object_or_404(StaffProfile, user=self.request.user)
    def form_valid(self, form):
        messages.success(self.request, "Your profile updated successfully!")
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, "An ERROR occurred updating profile.")
        return super().form_invalid(form)
@login_required(login_url='users:login')
def staff_schedule_view(request):
    STAFF_ROLE = CustomUser.UserRoleChoices.STAFF
    APPROVED_STATUS = AdminAppointmentApproval.StatusChoices.APPROVED
    COMPLETED_STATUS = AdminAppointmentApproval.StatusChoices.COMPLETED
    PENDING_STATUS = AdminAppointmentApproval.StatusChoices.PENDING
    CANCELED_STATUS = AdminAppointmentApproval.StatusChoices.CANCELED
    today = timezone.now().date()
    if request.user.role != STAFF_ROLE:

        return HttpResponse("Unauthorized", status=401)
    appointments = AdminAppointmentApproval.objects.filter(
        assigned_staff__user=request.user,
        status=APPROVED_STATUS).order_by('-approved_time_slot')
    # c_apps = appointments.first()
    # print('TIME: ', c_apps.approved_time_slot)
    # print("DATE: ", c_apps.customer_appointment.appointment_date)
    TODAY_APPOINTMENTS = appointments.filter(customer_appointment__appointment_date=today)
    APPROVED_APPOINTMENTS = appointments.filter(status=APPROVED_STATUS)
    COMPLETED_APPOINTMENTS = appointments.filter(status=COMPLETED_STATUS)
    context = {
        'appointments': appointments,
        'today_appointment': TODAY_APPOINTMENTS,
        'upcoming_appointments': APPROVED_APPOINTMENTS,
        'completed_appointments': COMPLETED_APPOINTMENTS,
        'CANCELED': CANCELED_STATUS,
        'APPROVED': APPROVED_STATUS,
        'PENDING': PENDING_STATUS,
        'COMPLETED': COMPLETED_STATUS,
    }
    return render(request, 'staff/staff-schedule.html', context)

class StaffScheduleView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AdminAppointmentApproval
    template_name = 'staff/staff-schedule.html'
    context_object_name = 'appointments'

    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.STAFF

    def get_queryset(self):
        return AdminAppointmentApproval.objects.filter(
            assigned_staff__user=self.request.user
        ).select_related(
            'customer_appointment'
        ).order_by('-approved_time_slot')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()
        queryset = self.get_queryset()
        paginator = Paginator(context['appointments'], 6)
        page_number = self.request.GET.get('page', '')
        page_obj =paginator.get_page(page_number)
        context['mobile_appointments'] = page_obj
        context['page_obj'] = page_obj
        search_appointment_q = self.request.GET.get('search_appointment', '')
        if search_appointment_q:
            context['appointments'] = context['appointments'].filter(
                Q(customer_appointment__full_name__icontains=search_appointment_q) |
                Q(customer_appointment__service__name__icontains=search_appointment_q) |
                Q(customer_appointment__phone_number__icontains=search_appointment_q)
            )
        context['search_appointment_q'] = search_appointment_q
        context['today_appointment'] = queryset.filter(
            customer_appointment__appointment_date=today
        )

        context['upcoming_appointments'] = queryset.filter(
            status=AdminAppointmentApproval.StatusChoices.APPROVED
        )

        context['completed_appointments'] = queryset.filter(
            status=AdminAppointmentApproval.StatusChoices.COMPLETED
        )

        context['CANCELED'] = AdminAppointmentApproval.StatusChoices.CANCELED
        context['APPROVED'] = AdminAppointmentApproval.StatusChoices.APPROVED
        context['PENDING'] = AdminAppointmentApproval.StatusChoices.PENDING
        context['COMPLETED'] = AdminAppointmentApproval.StatusChoices.COMPLETED

        return context
def staff_appointment_history(request):
    if request.user.role != CustomUser.UserRoleChoices.STAFF:
          return HttpResponse("Unauthorized", status=401)

    COMPLETED_STATUS = AdminAppointmentApproval.StatusChoices.COMPLETED

    COMPLETED = AdminAppointmentApproval.StatusChoices.COMPLETED
    appointments = AdminAppointmentApproval.objects.filter(
        assigned_staff__user=request.user, status=COMPLETED
    ).order_by('-id')
    COMPLETED = appointments.filter(status=COMPLETED_STATUS).all()
    context = {
        'appointments': appointments,
        'completed_appointments': COMPLETED,
    }
    return render(request, 'staff/appointment-history.html', context)


class StaffAppointmentHistoryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AdminAppointmentApproval
    template_name = 'staff/appointment-history.html'
    context_object_name = 'appointments'

    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.STAFF

    def get_queryset(self):
        return AdminAppointmentApproval.objects.filter(
            assigned_staff__user=self.request.user, status=AdminAppointmentApproval.StatusChoices.COMPLETED
        ).select_related('customer_appointment').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_appointment_q = self.request.GET.get('search_appointment', '')
        if search_appointment_q:
            context['appointments'] = context['appointments'].filter(
                Q(customer_appointment__full_name__icontains=search_appointment_q) |
                Q(customer_appointment__service__name__icontains=search_appointment_q) |
                Q(customer_appointment__phone_number__icontains=search_appointment_q)
            )
        context['search_appointment_q'] = search_appointment_q
        context['completed_appointments'] = context['appointments'].filter(
            status=AdminAppointmentApproval.StatusChoices.COMPLETED
        )

        return context

class NotificationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Notification
    context_object_name = 'notifications'
    template_name = 'staff/notifications.html'
    def get_queryset(self):
        return Notification.objects.filter(
            receiver=self.request.user
        ).order_by('-timestamp')
    def test_func(self):
        return self.request.user.role == CustomUser.UserRoleChoices.STAFF


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
            return redirect('staff:notifications')

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

        return redirect('staff:notifications')
    return HttpResponse('No notifications selected.')
