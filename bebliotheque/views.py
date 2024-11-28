import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from .models import User,Book,Borrowing
from django.contrib.auth.hashers import check_password
from django.utils import timezone,dateformat
# Create your views here.
def login(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')
       
        try:
            user = User.objects.get(email=email)
            request.session['id_user']=user.id
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


def aller_emprunter(request, id):
    book = get_object_or_404(Book, id=id)
    # user = User.objects.get()
    return render(request, "Emprinter.html", {'book': book})
    # return HttpResponse(template.render({'books':books}))


def Emprinter(request, id):
    books = Book.objects.get(id=id)
    user = User.objects.get(id=request.session['id_user'])
    if request.method == 'POST':
        return_date=request.POST.get('return_date')
        # return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()
        book_id = books.id
        user_id = request.session['id_user']
        date_bowring = timezone.now().date()
        copies = books.copies_available
        if copies > 0:
            books.copies_available=copies-1
            bowring = Borrowing(
            date_bowring=date_bowring,
            return_date=return_date,
            book=books,
            user=user 
                )

            bowring.save()
            books.save()
        return HttpResponse(f"Requête POST reçue avec succès: {return_date},{book_id},{date_bowring},{copies}")
