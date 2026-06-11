import logging

from django.contrib.auth import authenticate, login
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.shortcuts import redirect, render
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from staff.models import StaffProfile
from admin_manager.models import AdminProfile
from django.contrib.auth.decorators import login_required


def register(request):
    try:
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Your account has been created successfully. You can now log in.')
                return redirect('account_login')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = UserRegistrationForm()
        context = {
            'form': form
        }
        return render(request, 'account/signup.html', context)
    except Exception as e:
        logging.error(f"Error during registration: {str(e)}")
        return HttpResponseServerError(f"Internal Server Error, Details: {str(e)}")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        CUSTOMER_ROLE = CustomUser.UserRoleChoices.CUSTOMER
        ADMIN_ROLE = CustomUser.UserRoleChoices.ADMIN
        STAFF_ROLE = CustomUser.UserRoleChoices.STAFF
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == CUSTOMER_ROLE:
                return redirect('core:home')

            if user.role == ADMIN_ROLE:
                return redirect('users:admin-confirmation')

            if user.role == STAFF_ROLE:
                return redirect('users:staff-confirmation')

        messages.error(request, "Invalid credentials")

    return render(request, 'account/login.html')


def user_logout(request):
    try:
        logout(request)
        return redirect('account_login')

    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
        return HttpResponseServerError(f"Internal Server Error, Details: {str(e)}")


@login_required(login_url='account_login')
def staff_register_confirmation(request):
    user = request.user
    STAFF_ROLE = CustomUser.UserRoleChoices.STAFF

    if user.role != STAFF_ROLE:
        return redirect('core:home')

    if request.method == 'POST':
        employee_number = request.POST.get('employee_number', '').strip()

        if not employee_number:
            messages.error(request, "Employee number is required.")
            return redirect('users:staff-confirmation')

        try:
            # Find by employee_number only (since it's unique)
            staff = StaffProfile.objects.get(employee_number=employee_number)
            print(f"Found staff: {staff.full_name} (ID: {staff.id})")

        except StaffProfile.DoesNotExist:
            print(f"No staff found with employee_number: '{employee_number}'")
            messages.error(request, f"Invalid employee number. Please check and try again.")
            return redirect('users:staff-confirmation')

        # Check if already linked to another user
        if staff.user and staff.user != user:
            messages.error(request, f"This employee number is already linked to another account.")
            return redirect('users:staff-confirmation')

        # Link staff to user
        staff.user = user
        staff.save()
        print(f"Staff {staff.full_name} linked to user {user.username}")

        # Mark verification
        user.is_staff_verified = True
        user.save()
        print(f"User {user.username} marked as staff verified")

        messages.success(request, f"Welcome {staff.full_name}! Staff verification successful.")
        return redirect('core:home')

    return render(request, 'users/staff-confirmation.html')

# @login_required(login_url='users:login')
# def staff_register_confirmation(request):
#     user = request.user
#     STAFF_ROLE = CustomUser.UserRoleChoices.STAFF
#     if user.role != STAFF_ROLE:
#         return redirect('core:home')

#     if request.method == 'POST':
#         employee_number = request.POST.get('employee_number')
#         staff_id = request.POST.get('staff_id')
#         print("Received employee number:", employee_number)
#         print("Received staff ID:", staff_id)
#         if not employee_number:
#             if not user.is_staff_verified:
#                 messages.error(request, "Please verify your staff status.")
#                 return redirect('users:staff-confirmation')
#             messages.error(request, "Employee number is required.")
#             return redirect('users:staff-confirmation')

#         # get staff record
#         try:
#             staff = StaffProfile.objects.get(id=staff_id, employee_number=employee_number)
#             print("Staff found:", staff)
#         except StaffProfile.DoesNotExist:
#             messages.error(request, "Invalid employee number.")
#             return redirect('users:staff-confirmation')
#         except Exception as e:
#             print("Error retrieving staff:", e)
#             messages.error(request, "An error occurred while verifying employee number.")
#             return redirect('users:staff-confirmation')

#         # prevent double linking
#         if staff.user and staff.user != user:
#             messages.error(request, "This employee number is already linked.")
#             return redirect('users:staff-confirmation')

#         # link staff to user

#         staff.user = user
#         print(f'Staff linked to user: {user} with employee number: {employee_number}')
#         print(f'True: {staff.user} == {user} {staff.user == user if staff.user else False}')
#         staff.save()

#         # mark verification
#         user.is_staff_verified = True
#         user.save()

#         messages.success(request, "Staff confirmed successfully!")
#         return redirect('core:home')

#     return render(request, 'users/staff-confirmation.html')


def admin_register_confirmation(request):
    user = request.user

    if user.role != CustomUser.UserRoleChoices.ADMIN:
        return redirect('core:home')

    if request.method == 'POST':
        employee_number = request.POST.get('employee_number')

        if not employee_number:
            messages.error(request, 'ADMIN employee NUMBER is required.')
            return redirect('users:admin-confirmation')

        try:
            admin = AdminProfile.objects.get(employee_number=employee_number)
        except AdminProfile.DoesNotExist:
            messages.error(request, 'Invalid Employee Number.')
            return redirect('users:admin-confirmation')

        admin.user = user
        admin.save()

        user.is_admin_verified = True
        user.employee_number = employee_number
        user.save()

        messages.success(
            request, 'Your ADMIN account has been confirmed Successfully!')
        return redirect('core:home')

    return render(request, 'users/admin-confirmation.html')
