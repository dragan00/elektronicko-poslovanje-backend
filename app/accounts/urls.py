from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('accounts', views.AccountViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterApiView.as_view()),
    path('update_account/<pk>/', views.UpdateAccountApiView.as_view()),
    path('remove_account/', views.RemoveAccountApiView.as_view()),
    path('auth/', views.CustomAuthToken.as_view()),
    path('logout/', views.Logout.as_view()),
    path('change_password/<int:pk>/', views.ChangePasswordView.as_view()),
    path('getuser/', views.GetUserApiView.as_view(), name='getUserByToken'),
    path('panes/', views.PanesApiView.as_view(), name='panes'),
    path('avatar/', views.AvatarApiView.as_view(), name='avatar'),
]
