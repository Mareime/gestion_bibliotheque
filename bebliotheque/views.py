from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from .models import User,Book
from django.contrib.auth.hashers import check_password
# Create your views here.
def login(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                return redirect('success')  # Redirect to a success page or dashboard
            else:
                books = Book.objects.all().values()
                template = loader.get_template('s.html')
                return HttpResponse(template.render({'books': books}, request))
                # return render(request, 's.html')
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email or password'})

    return render(request, "login.html")
def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, "user_signup.html", {'error': 'Passwords do not match'})

        if User.objects.filter(email=email).exists():
            return render(request, "user_signup.html", {'error': 'Email already exists'})

        
        user = User(username=username, email=email, password=password)
        user.save()

        return redirect('login')

    return render(request, "user_signup.html")
