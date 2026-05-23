from django.urls import path

from apps.users.views import LoginView, MeView, RegisterView, UserListView, UserRoleUpdateView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("usuarios/", UserListView.as_view(), name="usuarios"),
    path("usuarios/<int:pk>/rol/", UserRoleUpdateView.as_view(), name="usuario-rol"),
]
