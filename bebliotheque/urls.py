from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('user_signup/', views.user_signup, name='user_signup'),
    # path('logout/', views.deconnexion, name='deconnexion'),
    path('Emprinter/<int:id>/', views.Emprinter, name='Emprinter'),
    path('aller_emprunter/<int:id>/', views.aller_emprunter, name='aller_emprunter'),
    path('user/', views.home_user, name='s'),
    path('profile/', views.User_books, name='profile'),
    path('return_book/<int:id>/', views.return_book, name='return_book'),  # Correction ici
    path('admin/Dashbord/', views.Dashbord, name='Dashbord'),
]
