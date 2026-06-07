from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from .models import AdminProfile, AdminAppointmentApproval
from customer.models import CustomerAppointment
from .forms import AdminAppointmentApprovalForm, AdminProfileForm
from users.models import CustomUser
from django.contrib import messages
from .decorators import superuser_required
from staff.models import StaffProfile
from staff.forms import StaffForm
from django.utils import timezone
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from customer.forms import CustomerProfileForm
from django.views import View
from django.db.models import Q, Count, Avg
from notifications.models import Notification
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import AdminRequiredMixin
from feedback.models import Feedback
import json
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from services.models import Service
from datetime import datetime
from io import StringIO
import csv
from django.core.paginator import Paginator
from notifications.notify_helper import notify
from core.models import TeamMember
from core.forms import TeamMemberForm
# from notifications.services import send_notification


@superuser_required
def dashboard(request):
    appointments = CustomerAppointment.objects.all()
    approved = appointments.filter(
        status=CustomerAppointment.AppointmentStatusChoices.APPROVED).count()
    pending = appointments.filter(
        status=CustomerAppointment.AppointmentStatusChoices.PENDING).count()
    rejected = appointments.filter(
        status=CustomerAppointment.AppointmentStatusChoices.REJECTED).count()
    canceled = appointments.filter(
        status=CustomerAppointment.AppointmentStatusChoices.CANCELED).count()
    completed = appointments.filter(
        status=CustomerAppointment.AppointmentStatusChoices.COMPLETED).count()
    status_choices = CustomerAppointment.AppointmentStatusChoices
    context = {
        'appointments': appointments,
        'status_choices': status_choices,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'canceled': canceled,
    }
    return render(request, 'admin_manager/dashboard.html', context)


class DashboardView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomerAppointment
    template_name = 'admin_manager/dashboard.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return CustomerAppointment.objects.all().order_by('-appointment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        appointments = context['appointments']
        # Search Query
        search_customer_q = self.request.GET.get('search_customer', '').strip()
        if search_customer_q:
            context['appointments'] = appointments.filter(
                Q(user__first_name__icontains=search_customer_q) |
                Q(user__last_name__icontains=search_customer_q) |
                Q(user__username__icontains=search_customer_q)
            )
            context['search_customer_q'] = search_customer_q

        # Mobile Paginator
        paginator = Paginator(context['appointments'], 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['mobile_appointments'] = page_obj
        context['page_obj'] = page_obj
        # Status counts
        context['approved'] = appointments.filter(
            status=CustomerAppointment.AppointmentStatusChoices.APPROVED
        ).count()

        context['pending'] = appointments.filter(
            status=CustomerAppointment.AppointmentStatusChoices.PENDING
        ).count()

        context['rejected'] = appointments.filter(
            status=CustomerAppointment.AppointmentStatusChoices.REJECTED
        ).count()

        context['canceled'] = appointments.filter(
            status=CustomerAppointment.AppointmentStatusChoices.CANCELED
        ).count()

        context['completed'] = appointments.filter(
            status=CustomerAppointment.AppointmentStatusChoices.COMPLETED
        ).count()

        context['status_choices'] = CustomerAppointment.AppointmentStatusChoices

        return context


def get_time_of_day(time):
    hour = time.hour
    if hour < 12:
        return 'Morning'
    elif hour < 17:
        return 'Afternoon'
    else:
        return 'Evening'


@superuser_required
def admin_appointment_review(request, approval_id):
    print("🔥 VIEW HIT:", request.method)
    staffs = StaffProfile.objects.all()
    for staff in staffs:
        print(
            f"Staff: {staff.full_name} (ID: {staff.id}) - User: {staff.user.username if staff.user else 'No user'})")
    approval = get_object_or_404(CustomerAppointment, id=approval_id)

    admin_approval, created = AdminAppointmentApproval.objects.get_or_create(
        customer_appointment=approval
    )
    admin_status = admin_approval.StatusChoices
    time_of_day = get_time_of_day(approval.time_slot)
    ADMIN = CustomUser.UserRoleChoices.ADMIN
    customer = approval.user

    if request.method == 'POST':
        # Check if this is a cancellation request
        if 'cancel_appointment' in request.POST:
            # Handle cancellation
            cancellation_reason = request.POST.get('cancellation_reason')
            if not cancellation_reason:
                messages.error(request, "Please select a cancellation reason.")
                return redirect("admin_manager:appointment-review", approval_id=approval.id)

            admin_approval.status = admin_status.CANCELED
            admin_approval.cancelled_by = request.user
            admin_approval.cancelled_at = timezone.now()
            admin_approval.cancellation_reason = cancellation_reason
            admin_approval.save()

            # Update the main appointment status
            approval.status = 'canceled'
            approval.save()

            # Send notification
            # Notification.objects.create(
            #     receiver=customer,
            #     sender=request.user,
            #     message=f'Your appointment ({approval.service.name}) has been cancelled.',
            #     notification_type=Notification.NotificationTypes.CANCELED_APPOINTMENT,
            #     link=reverse('customer:appointment-list')
            # )
            notify(
                sender=request.user,
                receiver=customer,
                message=f'Your appointment ({approval.service.name}) has been cancelled.',
                notification_type=Notification.NotificationTypes.CANCELED_APPOINTMENT,
                link=reverse('customer:appointment-list')
            )

            # send_notification(notification)

            messages.success(request, "Appointment cancelled successfully.")
            return redirect("admin_manager:dashboard")

        # Regular form submission
        form = AdminAppointmentApprovalForm(
            request.POST, instance=admin_approval, user=request.user
        )

        assigned_staff_id = request.POST.get('assigned_staff')
        if not assigned_staff_id:
            form.add_error(None, "Please select a staff member.")

        if form.is_valid():
            admin_obj = form.save(commit=False)
            admin_obj.assigned_staff_id = assigned_staff_id
            approval.status = admin_obj.status
            approval.save()

            assigned_staff = StaffProfile.objects.get(id=assigned_staff_id)

            # Only set cancellation fields if status is CANCELED
            if admin_obj.status == admin_status.CANCELED:
                admin_obj.cancelled_by = request.user
                admin_obj.cancelled_at = timezone.now()

            admin_obj.save()

            # Send notifications
            if admin_obj.status == admin_status.APPROVED:
                if not assigned_staff.user:
                    messages.error(
                        request, "Selected staff member does not have a user account.")
                    return redirect("admin_manager:dashboard")
                # Notification.objects.create(
                #     receiver=assigned_staff.user,
                #     sender=request.user,
                #     message=f'You have been assigned a new appointment -> ({admin_approval.customer_appointment.service.name}).',
                #     notification_type=Notification.NotificationTypes.ASSIGNED_STAFF,
                #     link=reverse('staff:appointments')
                # )

                notify(
                    sender=request.user,
                    receiver=assigned_staff.user,
                    message=f'You have been assigned a new appointment -> ({admin_approval.customer_appointment.service.name}).',
                    notification_type=Notification.NotificationTypes.ASSIGNED_STAFF,
                    link=reverse('staff:appointments')
                )

                # send_notification(notification)

                # Notification.objects.create(
                #     receiver=customer,
                #     sender=request.user,
                #     message=f'Your appointment ({approval.service.name}) has been approved.',
                #     notification_type=Notification.NotificationTypes.APPROVED,
                #     link=reverse('customer:appointment-list')
                # )

                notify(
                    sender=request.user,
                    receiver=customer,
                    message=f'Your appointment ({approval.service.name}) has been approved.',
                    notification_type=Notification.NotificationTypes.APPROVED,
                    link=reverse('customer:appointment-list')
                )

                # send_notification(notification)
            return redirect("admin_manager:dashboard")
    else:
        form = AdminAppointmentApprovalForm(
            instance=admin_approval, user=request.user)

    return render(request, 'admin_manager/appointment_review.html', {
        'approval': approval,
        'staffs': staffs,
        'form': form,
        'time_of_day': time_of_day,
        'admin_approval': admin_approval,
        'admin_status': admin_status,
        'ADMIN': ADMIN,
    })


@superuser_required
def available_staffs(request):
    # staff_id=None
    # staffs = CustomUser.objects.filter(role=CustomUser.UserRoleChoices.STAFF)
    staffs = StaffProfile.objects.all().order_by('-date_joined')
    # staff_profile = None
    # if staff_id:
    #     # Get a specific staff profile by ID
    #     staff_profile = get_object_or_404(
    #         CustomUser,
    #         id=staff_id,
    #         role=CustomUser.UserRoleChoices.STAFF
    #     )

    context = {
        'staffs': staffs,
        # 'staff_profile': staff_profile
    }
    return render(request, 'admin_manager/staff-management.html', context)


class StaffManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = StaffProfile
    context_object_name = 'staffs'
    template_name = 'admin_manager/staff-management.html'

    def get_queryset(self):
        return StaffProfile.objects.select_related('user').all().order_by(
            '-date_joined'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staffs = self.get_queryset()
        search_staff_q = self.request.GET.get('search_staff', '').strip()

        if search_staff_q:
            context['staffs'] = staffs.filter(
                Q(full_name__icontains=search_staff_q) |
                Q(employee_number__icontains=search_staff_q)
            )
            context['search_staff_q'] = search_staff_q
        else:
            context['staffs'] = staffs

        return context


@superuser_required
def edit_staff_profile_admin(request, staff_id):
    staff = get_object_or_404(StaffProfile, id=staff_id)

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{staff.full_name}'s profile updated successfully!")
            return redirect('admin_manager:staff-detail', staff.id)
    else:
        form = StaffForm(instance=staff)

    return render(request, 'admin_manager/edit-staff.html', {'form': form, 'staff': staff})


class EditStaffProfileAdminView(LoginRequiredMixin, UpdateView):
    model = StaffProfile
    template_name = 'admin_manager/edit-staff.html'
    form_class = StaffForm
    slug_url_kwarg = 'staff_slug'
    context_object_name = 'staff'

    def form_valid(self, form):
        staff_profile = form.save(commit=False)
        staff_profile.save()

        messages.success(
            self.request,
            f"{staff_profile.full_name}'s profile updated successfully!"
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'An error occurred while updating staff profile.'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('admin_manager:staff-detail', kwargs={'staff_slug': self.object.slug})


def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.save()
            messages.success(
                request, f"Staff - f{(staff.full_name)}'s profile created successfully.")
            return redirect('admin_manager:staff-list')
        else:
            messages.error(request, 'An Occured creating NEW STAFF')
            return redirect('admin_manager:staff-list')
    else:
        form = StaffForm()
    context = {
        'form': form
    }
    return render(request, 'admin_manager/add-staff.html', context)


class AddStaffView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = StaffProfile
    template_name = 'admin_manager/add-staff.html'
    form_class = StaffForm
    success_url = reverse_lazy('admin_manager:staff-list')

    def form_valid(self, form):
        staff_profile = form.save()
        messages.success(
            self.request,
            f"Staff {staff_profile.full_name} (EMP: {staff_profile.employee_number}) created successfully."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'An Occured creating NEW STAFF')
        return super().form_invalid(form)


@superuser_required
def delete_staff(request, staff_id):
    staff_profile = get_object_or_404(StaffProfile, id=staff_id)
    staff = staff_profile.user
    if staff_profile:
        staff.is_active = False
        messages.success(
            request, 'Staff deleted successfully')
        return redirect('admin_manager:staff-list')
    else:
        messages.error(request, 'An Error Occured deleting STAFF.')
        return redirect('admin_manager:staff-list')


class DeleteStaffAdminView(LoginRequiredMixin, AdminRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        staff_profile = get_object_or_404(
            StaffProfile, slug=kwargs['staff_slug']
        )
        user = staff_profile.user
        if user:
            user.is_active = False
            user.save()
            messages.success(
                request,
                f'Staff "{user.get_full_name() or user.username}" deactivated successfully.'
            )
        else:
            messages.error(request, 'An error occurred while deleting staff.')
        return redirect('admin_manager:staff-list')


@superuser_required
def staff_detail_admin(request, staff_id):
    staff = get_object_or_404(StaffProfile, id=staff_id)
    context = {
        'staff': staff
    }
    return render(request, 'admin_manager/staff-detail.html', context)


class StaffProfileAdminView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = StaffProfile
    template_name = 'admin_manager/staff-detail.html'
    context_object_name = 'staff'
    slug_url_kwarg = 'staff_slug'


def admin_profile_form(request):
    if request.user.role != 'admin':
        messages.error(request, "Sorry you're not allowed here.")
        return redirect('core:home')
    admin_profile, created = AdminProfile.objects.get_or_create(
        user=request.user)

    if request.method == 'POST':
        form = AdminProfileForm(
            request.POST,
            request.FILES,
            instance=admin_profile
        )
        if form.is_valid():
            form.save()

            messages.success(
                request, f'Mr. {request.user.username} your profile updated successfully.')
            return redirect('admin_manager:admin-profile')
        else:
            messages.error(
                request, 'An Error Occured During Updating Profile!')

    else:
        form = AdminProfileForm(instance=admin_profile)
    context = {
        'form': form,
    }
    return render(request, 'admin_manager/admin-edit-profile.html', context)


class EditAdminProfileFormView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = AdminProfile
    template_name = 'admin_manager/admin-edit-profile.html'
    form_class = AdminProfileForm
    success_url = reverse_lazy('admin_manager:admin-profile')

    def get_object(self):
        profile, _ = AdminProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Mr. {self.request.user.username}, your profile updated successfully.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'An error occurred while updating your profile!'
        )
        return super().form_invalid(form)


def admin_profile_view(request):
    user = request.user
    admin = CustomUser.objects.filter(
        id=user.id, role=CustomUser.UserRoleChoices.ADMIN).first()
    if not user.is_authenticated:
        return redirect('users:login')
    if not admin:
        return redirect('core:home')
    profile, _ = AdminProfile.objects.get_or_create(user=request.user)
    return render(request, 'admin_manager/admin-profile.html', {'profile': profile})


class AdminProfileView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = AdminProfile
    template_name = 'admin_manager/admin-profile.html'
    context_object_name = 'profile'

    def get_object(self):
        profile, _ = AdminProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class CustomerManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomUser
    context_object_name = 'customers'
    template_name = 'admin_manager/customer-management.html'

    def get_queryset(self):
        return CustomUser.objects.filter(
            role=CustomUser.UserRoleChoices.CUSTOMER
        ).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customers = self.get_queryset()
        # Mobile Paginator
        paginator = Paginator(customers, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['mobile_customers'] = page_obj
        context['page_obj'] = page_obj

        # Search Query
        search_customer_q = self.request.GET.get('search_customer', '').strip()

        if search_customer_q:
            context['customers'] = customers.filter(Q(first_name__icontains=search_customer_q) | Q(
                last_name__icontains=search_customer_q) | Q(username__icontains=search_customer_q))
            context['search_customer_q'] = search_customer_q
        else:
            context['customers'] = customers
        return context


class CustomerProfileAdminView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = CustomUser
    context_object_name = 'customer'
    template_name = 'admin_manager/customer-profile-admin.html'
    pk_url_kwarg = 'customer_id'


class CustomerEditProfileAdminView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'admin_manager/edit-customer-profile-admin.html'
    context_object_name = 'customer'
    pk_url_kwarg = 'customer_id'
    # fields = ['username', 'email']
    form_class = CustomerProfileForm
    # success_url = reverse_lazy('admin_manager:customer-list')

    def get_success_url(self):
        messages.success(
            self.request, "Customer profile updated successfully.")
        return reverse_lazy('admin_manager:customer-detail', kwargs={'customer_id': self.object.id})


class CustomerDeleteAdminView(LoginRequiredMixin, AdminRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(CustomUser, id=kwargs['customer_id'])

        customer.is_active = False
        customer.save()

        messages.success(
            self.request,
            f'Customer "{customer.get_full_name() or customer.username}" removed successfully.'
        )

        return redirect('admin_manager:customer-list')


def filter_staff(request):
    query = request.GET.get('q', '')

    staffs = StaffProfile.objects.all()

    if query:
        staffs = staffs.filter(
            Q(user__username__icontains=query) |
            Q(employee_number__icontains=query)
        )

    data = list(
        staffs.values(
            'id',
            'employee_number',
            'user__username'
        )
    )

    return JsonResponse({'staff': data})


def notifications(request):
    admin = CustomUser.UserRoleChoices.ADMIN
    notifications = Notification.objects.filter(
        receiver=admin
    ).order_by('-timestamp')
    return render(request, 'admin_manager/notifications.html', {'notifications': notifications})


class NotificationView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Notification
    template_name = 'admin_manager/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        admin = CustomUser.UserRoleChoices.ADMIN
        return Notification.objects.filter(
            receiver__role=admin
        ).order_by('-timestamp')


class AppointmentNotificationView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Notification
    template_name = 'admin_manager/appointment-notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        admin = CustomUser.UserRoleChoices.ADMIN
        return Notification.objects.filter(
            receiver__role=admin, notification_type=Notification.NotificationTypes.APPOINTMENT
        ).order_by('-timestamp')


def admin_cancel_appointment(request, appointment_id):
    if not request.user.is_authenticated:
        return redirect('users:login')

    if request.user.role != CustomUser.UserRoleChoices.ADMIN:
        messages.error(request, "Sorry you're not allowed here.")
        return redirect('core:home')

    appointment = get_object_or_404(CustomerAppointment, id=appointment_id)
    admin_approval = get_object_or_404(
        AdminAppointmentApproval,
        customer_appointment=appointment
    )

    # if admin_approval.status in [
    #     AdminAppointmentApproval.StatusChoices.PENDING.value,
    #     AdminAppointmentApproval.StatusChoices.APPROVED.value
    # ]:
    if admin_approval.status == AdminAppointmentApproval.StatusChoices.APPROVED.value or admin_approval.status == AdminAppointmentApproval.StatusChoices.PENDING.value:
        print(
            f'Current appointment status: {appointment.get_status_display()}')
        print(
            f'Current admin approval status: {admin_approval.get_status_display()}')
        print(
            f'Appointment ID: {appointment.id}, Admin Approval ID: {admin_approval.id}')
        print(f'Admin user: {request.user.username} (ID: {request.user.id})')
        print(
            f'Approved status Value: {AdminAppointmentApproval.StatusChoices.APPROVED.value}, Pending status: {AdminAppointmentApproval.StatusChoices.PENDING.value}')
        print(
            f'Approved status: {AdminAppointmentApproval.StatusChoices.APPROVED}, Pending status: {AdminAppointmentApproval.StatusChoices.PENDING}')
        print(
            f'admin_approval.status == APPROVED: {admin_approval.status == AdminAppointmentApproval.StatusChoices.APPROVED.value}')
        print(
            f'admin_approval.status == PENDING: {admin_approval.status == AdminAppointmentApproval.StatusChoices.PENDING.value}')
        admin_approval.cancellation_reason = (
            AdminAppointmentApproval.CANCELLED_REASON.ADMIN_CANCELLED
        )
        admin_approval.cancelled_by = request.user
        admin_approval.cancelled_at = timezone.now()
        admin_approval.status = AdminAppointmentApproval.StatusChoices.CANCELED
        admin_approval.save()

        appointment.status = CustomerAppointment.AppointmentStatusChoices.CANCELED
        appointment.save()

        # Notification.objects.create(
        #     receiver=appointment.user,
        #     sender=request.user,
        #     message=f'Your appointment for {appointment.service.name} on '
        #     f'{appointment.appointment_date} at {appointment.time_slot} '
        #     f'has been canceled by an administrator.',
        #     notification_type=Notification.NotificationTypes.CANCELED_APPOINTMENT,
        #     link=reverse('customer:appointment-list')
        # )

        notify(
            sender=request.user,
            receiver=appointment.user,
            message=f"Your appointment for {appointment.service.name} on {appointment.appointment_date} at {appointment.time_slot}  has been canceled by an administrator.",
            notification_type=Notification.NotificationTypes.CANCELED_APPOINTMENT,
            link=reverse('customer:appointment-list')
        )
        # send_notification(notification)

        messages.success(request, 'Appointment canceled successfully.')
    else:
        messages.error(
            request,
            f'Cannot cancel appointment. appointment status: {appointment.get_status_display()}'
        )

    return redirect('admin_manager:dashboard')


@superuser_required
def delete_all_notifications(request):
    notifications = Notification.objects.filter(receiver=request.user)
    notifications.delete()
    messages.success(request, 'All notifications deleted successfully.')
    return redirect('admin_manager:notifications')


# class DeleteAllNotificationsView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Notification
#     success_url = reverse_lazy('admin_manager:notifications')

#     def get_queryset(self):
#         return Notification.objects.filter(receiver=self.request.user)

#     def test_func(self):
#         return self.request.user.role == CustomUser.UserRoleChoices.ADMIN

#     def delete(self, request, *args, **kwargs):
#         messages.success(request, 'All notifications deleted successfully.')
#         return super().delete(request, *args, **kwargs)

@superuser_required
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
            return redirect('admin_manager:notifications')

        return HttpResponse('No notifications selected.')


def customer_reviews(request):
    reviews = Feedback.objects.all().order_by('-created_at')
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    # if 'rating_approve' in request.POST:

    #     review_id = request.POST.get('rating_approve')
    #     try:
    #         review = Feedback.objects.get(id=review_id)
    #         review.approved = not review.approved
    #         review.save()
    #         status = 'Approved' if review.approved else 'Unapproved'
    #         messages.success(request, f'Review has been: {status}')
    #     except Feedback.DoesNotExist:
    #         messages.error(request, 'Review is not found.')
    context = {
        'reviews': reviews,
        'avg_rating': avg_rating,
        'page_obj': page_obj,
        'mobile_reviews': page_obj
    }
    return render(request, 'admin_manager/reviews.html', context)


@require_http_methods(["POST"])
def update_approval(request, review_id):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        approved_status = data.get('approved', None)
        if isinstance(approved_status, str):
            approved_status = approved_status.lower() == 'true'
        # Get the review
        review = get_object_or_404(Feedback, id=review_id)

        # Update approval status
        review.approved = approved_status
        review.save()
        review.refresh_from_db()
        status = 'Approved' if review.approved else 'Unapproved'
        messages.success(request, f'Review has been: {status}')
        return JsonResponse({
            'status': 'success',
            'message': 'Review updated successfully',
            'approved': review.approved
        })

    except Feedback.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Review not found'
        }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


class DeleteReviewView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Feedback
    # pk_url_kwarg = 'review_id'
    success_url = reverse_lazy('admin_manager:reviews')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'The review is deleted successfully.')
        return response

    def get_success_url(self):
        return reverse('admin_manager:reviews')


def delete_review(request, review_id):
    review = get_object_or_404(Feedback, id=review_id)
    if review:
        review.delete()
        messages.success(request, 'Review deleted successfully.')
        return redirect('admin_manager:reviews')
    else:
        messages.error(request, 'An error Occured')


def system_backup_page(request):
    return render(request, 'admin_manager/system-backup.html')


@staff_member_required
def system_backup(request, format):

    models_to_backup = [
        Service,
        Feedback,
        CustomerAppointment,
    ]

    data = []

    for model in models_to_backup:

        queryset = model.objects.all()

        serialized_data = json.loads(
            serializers.serialize(
                'json',
                queryset
            )
        )

        data.extend(serialized_data)
    filename_base = (
        f'backup_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    )
    # =========================
    # JSON EXPORT
    # =========================
    if format == 'json':
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{filename_base}.json"'
        )

        return response

    # =========================
    # CSV EXPORT
    # =========================
    elif format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['model', 'id', 'field', 'value'])
        for item in data:
            model = item['model']
            pk = item['pk']
            fields = item['fields']
            for key, value in fields.items():
                writer.writerow([model, pk, key, value])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="{filename_base}.csv')
        response.write(output.getvalue())
        return response
    # =========================
    # PDF EXPORT
    # =========================
    elif format == 'pdf':
        response = HttpResponse(content_type='pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{filename_base}.pdf')
        response.write("PDF export placeholder - integrate reportlab later")
        return response
    return 'Invalid Format'


class AddTeamMemberView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = TeamMember
    template_name = 'admin_manager/add-team-member.html'
    form_class = TeamMemberForm
    success_url = reverse_lazy('admin_manager:team-list')

    def form_valid(self, form):
        member = form.save(commit=False)
        messages.success(self.request, f'Team Member {(member.name)} added successfully.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'An error occured added team member.')
        return super().form_invalid(form)

class TeamMemberView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = TeamMember
    template_name = 'admin_manager/team.html'
    context_object_name = 'team_members'

    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by('display_order')


class TeamMemberEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = 'admin_manager/edit-team-member.html'
    pk_url_kwarg = 'member_id'
    context_object_name = 'member'
    success_url = reverse_lazy('admin_manager:team-list')
    def form_valid(self, form):
        member = form.save(commit=False)
        messages.success(
            self.request, f'The profile for member {(member.name)} updated successfully.')
        return super().form_valid(form)


class TeamMemberDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = TeamMember
    pk_url_kwarg = 'member_id'

    def get_success_url(self):
        messages.success(
            self.request,
            f'The member {self.object.name} was deleted successfully.'
        )
        return reverse_lazy('admin_manager:team-list')


def delete_team_member(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)

    member_name = member.name
    member.delete()

    messages.success(
        request,
        f'The member {member_name} was deleted successfully.'
    )

    return redirect('admin_manager:team-list')
