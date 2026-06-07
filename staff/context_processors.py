
from staff.models import StaffProfile
from users.models import CustomUser

def staff_profiles(request):
    STAFF_ROLE = CustomUser.UserRoleChoices.STAFF

    if request.user.is_authenticated and request.user.role == STAFF_ROLE:
        try:
            staff_profile = StaffProfile.objects.get(user=request.user)
        except StaffProfile.DoesNotExist:
            staff_profile = None
        return {
            'staff_profile': staff_profile
        }
    return {
        'staff_profile': None
    }