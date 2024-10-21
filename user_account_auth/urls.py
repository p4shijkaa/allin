from django.urls import path

from user_account_auth.views import UserRegistrationView, UserLoginView, UserLogoutView, \
    PasswordResetView, PasswordResetConfirmView, UserDeleteView, UserDetailsView, GoogleLoginView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('delete-user/', UserDeleteView.as_view(), name='delete_user'),
    path('user-details/', UserDetailsView.as_view(), name='user_details'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
]
