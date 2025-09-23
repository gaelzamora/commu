from django.urls import path
from .views import *
from .views_media import *

urlpatterns = [
    # registro en 3 pasos
    path("auth/register/start/", RegisterStartView.as_view()),
    path("auth/register/verify/", RegisterVerifyView.as_view()),
    path("auth/register/complete/", RegisterCompleteView.as_view()),

    # auth existente
    path("auth/login/",    LoginView.as_view()),
    path("auth/refresh/",  RefreshView.as_view()),
    path("auth/logout/",   LogoutView.as_view()),

    # perfil
    path("users/me/",      MeView.as_view()),

    # media
    path("media/avatar/presign/", PresignAvatarView.as_view()),
    path("media/avatar/confirm/", ConfirmAvatarView.as_view()),
    path("media/avatar/url/",     AvatarUrlView.as_view()),

]
