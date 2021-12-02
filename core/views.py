from django.contrib import auth
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import LoginForm, JoinForm
from django.contrib.auth import authenticate, login, logout  #login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

##############################

# Create your views here.
@login_required(login_url='/login/')
def home( request ):
    # "user1"+"-"+"user2"
    return render(request, 'core/home.html', {})


def user_login(request):
    print(f"User {request.user} logged in!")
    if (request.method == 'POST'):
        # use form provided in Forms.py
        login_form = LoginForm(request.POST)
        if(login_form.is_valid()):
            # Authenticate user 
            this_username = login_form.cleaned_data['username']
            this_password = login_form.cleaned_data['password']
            this_user = authenticate(
                request=request,
                username=this_username,
                password=this_password
            )

            # Check if user already exists in our DB
            if (this_user is not None):
                if (this_user.is_active):
                    login(request, this_user)
                    # messages.success(request, "Greetings, ".format(this_username))
                    return redirect(to="home")
                else:
                    return HttpResponse("Your account is not active")
            else:
                # invalid user-object, send message to "Log" file about potential problem.
                print("Someone tried to login and failed.")
                print("They had username: {} and password: {}".format(this_username, this_password))
                messages.info(request, "Sorry, Let's try that again...")
                return render(request, 'core/login.html', {"login_form": LoginForm})
    else:
        # Form was not Valid
        return render(request, 'core/login.html', {"login_form": LoginForm})
    # return render(request, 'core/login.html', {

    # })


def user_register(request):

    print(f"\n\nAttempting to register: {request.user}")
    if (request.method == 'POST'):
        join_form = JoinForm( request.POST )
        if (join_form.is_valid()):
            new_user = join_form.save() # Save, and get the current user
            
            new_user.set_password(new_user.password) # Encrypt Password, and save to DB 
            new_user.save()

            username = join_form.cleaned_data['username']
            if request is not None:
                # messages.success(request, "Account was created for {}".format(username))
                print(f"New User {request.user}, has just Registered!")
            
            return redirect("/")
        else:
            return render(request, 'core/register.html', { 
                'join_form' : join_form,
            })
    else:
        # Form invalid
        return render(request, 'core/register.html', {
            'join_form' : JoinForm(),
        })

@login_required(login_url='/login/')
def user_logout(request):
    print(f"User {request.user} logout!")
    logout( request )
    return redirect(to="/")
