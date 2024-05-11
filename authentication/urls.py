from operator import ge
from django.urls import path
from authentication.views import LoginView, UserDetail, Create_User, Upload_Profile, Add_Notice, NoticeView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/<str:username>/', UserDetail.as_view(), name='users'),
    path('create_user/', Create_User, name='create_user'),
    path('upload_profile/', Upload_Profile, name='upload_profile'),
    path('notice/', NoticeView.as_view(), name="notice"),
    path('add_notice/', Add_Notice, name='add_notice'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
