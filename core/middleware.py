from account.models import User
from django.db.models import Q

class CheckProfileMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # is_complete = User.objects.filter(Q(company_name="Olumide AI Engineering")).exists()
        if request.user:
            is_not_complete = User.objects.filter(Q(email=request.user) & (Q(company_name="") \
                | Q(phone_number="") | Q(rc_number="") | Q(country="")\
                    | Q(address=""))).exists()
            request.is_not_complete = is_not_complete
            # print("IS COMPLETE: ", request.is_complete)
            response = self.get_response(request)
        else:
            request.is_not_complete = True
            response = self.get_response(request)

        return response
