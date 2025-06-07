from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from account.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.utils import send_email_function
from agency.models import Agency
from core import settings 
from django.urls import reverse_lazy

# @login_required
def userlogin_old(request):
    pass  # add to imports

def userlogin(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    form = LoginForm()
    message = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                if user.is_disabled:
                    messages.success(request, "You are not allowed, please, contact the admin.")
                    logout(request)
                    return redirect("login")
                if user.is_tax_admin:
                    messages.success(request, f"Welcome {user.company_name}.")
                    return redirect("agency_dashboard")

                
                message = f'Hello {user.email}! You have been logged in'
                messages.success(request, "You have successfully logged in.")
                return redirect("dashboard")
            else:
                messages.error(request, "Login failed!.")
                message = 'Login failed!'

            
    return render(request, 'tax-payers/login.html', context={'form': form, 'message': message})
    # context = {
    #     form: form
    # }
    # return render(request, 'login.html', context)


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            message = f'Hello {user.email}! You have been logged in'
            messages.success(request, message)
            return redirect("setup_profile")
        else:
            message = form.errors
            # print(f'{form.error_messages}')
            messages.error(request, message)
    else:
        form = SignupForm()
    context = {
        form: form
    }
    return render(request, 'tax-payers/signup.html',{"form": form})


def logout_user(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    user = User.objects.get(id = request.user.id)
    if user.is_profile_complete:
        context = {
            "is_profile_complete" : True
        }
    context = {
         "is_profile_complete" : False
    }
    return render(request, 'tax-payers/dashboard.html', context)

@login_required
def setup_profile(request):
    user = User.objects.get(pk=request.user.id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # print("PROFILE: ", form)
            profile = form.save(commit=False)
            profile.email = request.user.email
            profile.is_profile_complete = True
            profile.save()

            # EMAIL TO NEW COMPANY 
            agency = Agency.objects.first()
            # Send email to new user company
            # mail_subject = "Welcome to Lasimra e-Collection System!"
            mail_subject = f"New Company Registration Alert - {profile.company_name}"
            to_email = profile.email
            # print("URL: ", settings.URL)
            html_content = render_to_string("Emails/tax_payer/new_company_reg.html", {
                "company_name":profile.company_name,
                "agency_email":agency.agency_email,
                "agency_phone":agency.phone_number,
                "login":settings.LOGIN_REDIRECT_URL,
                })
            text_content = strip_tags(html_content)
            send_email_function(html_content, text_content, to_email, mail_subject)
            # EMAIL TO ADMIN OF NEW COMAPNY
            to_email = agency.agency_email
            
            html_content = render_to_string("Emails/admin/new_company_reg.html", {
                "company_name":profile.company_name,
                "reg_date":profile.created_at,
                "company_email":profile.email,
                "company_phone":profile.phone_number,
                "agency_email":agency.agency_email,
                "agency_phone":agency.phone_number,
                "login":settings.URL,
                })
            text_content = strip_tags(html_content)
            send_email_function(html_content, text_content, to_email, mail_subject)


            messages.success(request, "Profile completed successfully")
            return redirect("dashboard")
        else:
            messages.error(request, "Please, fill the profile correctly.")
            return redirect(reverse_lazy('setup_profile'))
        
    form = UserProfileForm(instance=user)
            
    context = {
        'form':form,
        'user':user,
    }
    return render(request, 'tax-payers/settings.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        # old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        user = User.objects.get(pk=request.user.id)
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully.")
        else:
            messages.error(request, "You cannot perform this action.")


    context = {}
    return render(request, 'tax-payers/user_mngt/change_password.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")

        if not User.objects.filter(email = email).exists():
            messages.error(request, "Email does not exist.")
            return redirect('forgot_password')
        else:
            user = User.objects.get(email = email)
            # Generate random password & update password <new_password>
            # user.set_password("new_password")
            # Send <new_password> in email to user

            messages.success(request, f"Please, check your email: {user.email} for further instructions.")

    context = {}
    return render(request, 'tax-payers/user_mngt/forgot_password.html', context)