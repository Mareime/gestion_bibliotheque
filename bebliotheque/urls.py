from django.urls import path
from . import views

urlpatterns = [
path('', views.login, name='login'),
path('user_signup/', views.user_signup, name='user_signup'),
path('Emprinter/<int:id>/',views.Emprinter,name='Emprinter'),
path('aller_emprunter/<id>',views.aller_emprunter,name='aller_emprunter')
 ]