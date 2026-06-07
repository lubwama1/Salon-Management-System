
# Context processor to fetch customer appointment details for review
from customer.models import CustomerAppointment

try:
    def customer_appointment_review(request, approval_id):
        appointment = CustomerAppointment.objects.get(id=approval_id)
        if appointment:
            context = {
                'appointment_id': appointment
            }
        return context

except Exception as e:
    print(f"Error in context processor: {e}")