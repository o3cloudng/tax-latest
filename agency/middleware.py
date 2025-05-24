
class AgencyAreaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        def check_is_tax_admin(request, user):
            passes_email = request.user.is_tax_admin
            
            return all([
                passes_email,
                # is_pro,
                # has_money,
            ])


        # print("USER MIDDLEWARE: ", request.user.is_admin)
        # print("USER - TAX ADMIN: ", request.user.is_tax_admin)
        # Code to be executed for each request/response after
        # the view is called.

        return response