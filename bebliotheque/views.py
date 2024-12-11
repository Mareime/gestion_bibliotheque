import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import User, Book, Borrowing, Admin

# Connexion de l'utilisateur
def login(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')
       
        try:
            user = User.objects.get(email=email, password=password)
            if user:
                request.session["id_user"] = user.id
                books = Book.objects.all().values()
                return render(request, 's.html', {'books': books})

        except User.DoesNotExist:
            pass
        
        try:
            admin = Admin.objects.get(email=email, password=password)
            if admin:
                 request.session["id_admin"] = admin.id
                 users = User.objects.count()
                 total_books = Book.objects.count()
                 available_books = Book.objects.filter(copies_available__gt=0).count()
                 borrowings = Borrowing.objects.filter(returned=False).count()

                 return render(request, "admin/Dashbord.html", {
                'users': users,
                'total_books': total_books,
                'available_books': available_books,
                'borrowings': borrowings,
                    })
                
        except Admin.DoesNotExist:
            pass
        
        return render(request, "login.html", {"error": "Nom d'utilisateur ou mot de passe invalide"})
    
    return render(request, "login.html")


def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, "user_signup.html", {'error': 'Les mots de passe ne correspondent pas'})

        if User.objects.filter(email=email).exists():
            return render(request, "user_signup.html", {'error': 'Email déjà existant'})

        user = User(username=username, email=email, password=password)
        user.save()
        return redirect('login')

    return render(request, "user_signup.html")

def aller_emprunter(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, "Emprinter.html", {'book': book})


def Emprinter(request, id):
    if not request.session.get('id_user'):
        return redirect('login')  
    
    book = get_object_or_404(Book, id=id)
    user = get_object_or_404(User, id=request.session.get('id_user'))

    if request.method == 'POST':
        return_date_str = request.POST.get('return_date')

        
        try:
            return_date = datetime.datetime.strptime(return_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return HttpResponse("Date de retour invalide. Format attendu : AAAA-MM-JJ.", status=400)

        if return_date < timezone.now().date():
            return HttpResponse("La date de retour ne peut pas être antérieure à la date actuelle.", status=400)

        if book.copies_available <= 0:
            return HttpResponse("Desole, il n'y a plus de copies disponibles.", status=400)

        # Vérifier si l'utilisateur a déjà emprunté ce livre
        if Borrowing.objects.filter(user=user, book=book, returned=False).exists():
            return HttpResponse("Vous avez deja emprunté ce livre.", status=400)

        # Réduire les copies disponibles et enregistrer l'emprunt
        book.copies_available -= 1
        book.save()

        borrowing = Borrowing(
            borrow_date=timezone.now(),
            return_date=return_date,
            book=book,
            user=user
        )
        borrowing.save()

        # Rediriger après l'emprunt
        return redirect('s')  # Redirige vers la page appropriée

    return HttpResponse("Méthode non autorisée.", status=405)

# Tableau de bord de l'admin
def Dashbord(request):
    users = User.objects.count()
    total_books = Book.objects.count()
    available_books = Book.objects.filter(copies_available__gt=0).count()
    borrowings = Borrowing.objects.filter(returned=False).count()

    return render(request, "admin/Dashbord.html", {
        'users': users,
        'total_books': total_books,
        'available_books': available_books,
        'borrowings': borrowings,
    })

# Afficher les livres empruntés par un utilisateur
def User_books(request):
    borrowing = Borrowing.objects.filter(user_id=request.session.get('id_user'))
    return render(request, "profile.html", {'borrowing': borrowing})

# @never_cache
def return_book(request, id):
    borrowing = get_object_or_404(Borrowing, id=id)

    if borrowing.user.id != request.session.get('id_user'):
        return HttpResponse("Accès non autorisé", status=403)

    if borrowing.returned:
        return HttpResponse("Ce livre a déjà été retourné.", status=400)

    # Marquer le livre comme retourné et restaurer les copies disponibles
    borrowing.returned = True
    borrowing.save()

    book = borrowing.book
    book.copies_available += 1
    book.save()

    # Rediriger après le retour
    return redirect('profile')  

# Page d'accueil utilisateur
def home_user(request):
    books = Book.objects.all().values()
    return render(request, 's.html', {'books': books})


def AdminBooks(request):
    if request.method == "GET":
        books = Book.objects.all()
        return render(request, 'admin/livre.html', {'books': books})
    elif request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        copies_available = request.POST.get('copies_available')
        genre = request.POST.get('genre')
        publication_date = request.POST.get('publication_date')
        book = Book(title=title, author=author, copies_available=copies_available, publication_year=publication_date,genre=genre)
        book.save()
        return redirect('adminlivres')
    

def deletelivre(request,id):
    if request.method == "GET":
        book = get_object_or_404(Book, id=id)
        book.delete()
        return redirect('adminlivres')
    elif request.method == "POST":
        # Récupérer le livre à mettre à jour
        book = get_object_or_404(Book, id=id)

        # Récupérer les données du formulaire
        title = request.POST.get('title')
        author = request.POST.get('author')
        copies_available = request.POST.get('copies_available')
        genre = request.POST.get('genre')
        publication_date = request.POST.get('publication_date')

        # Valider et mettre à jour les champs
        if title:
            book.title = title
        if author:
            book.author = author
        if copies_available:
            book.copies_available = copies_available
        if genre:
            book.genre = genre
        if publication_date:
            book.publication_year = publication_date

        # Sauvegarder les modifications
        book.save()

        # Rediriger vers la page d'administration
        return redirect('adminlivres')


    
    


        