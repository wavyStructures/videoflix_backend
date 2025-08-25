from django.urls import path
from .views import (
    RegisterView, 
    LoginView, LogoutView, 
    ActivateView, 
    # RefreshTokenView, PasswordResetView, PasswordConfirmView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path(
        'activate/<str:uidb64>/<str:token>/',
        ActivateView.as_view(),
        name='activate'
    ),
    # path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    # path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    # path(
    #     'password_confirm/<str:uidb64>/<str:token>/',
    #     PasswordConfirmView.as_view(),
    #     name='password_confirm'
    # ),
]