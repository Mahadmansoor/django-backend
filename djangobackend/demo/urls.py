from django.urls import path
from .views import login, list_files, list_folders, download_folder,edit, delete, create, upload_folder, logout, create_fold, get_users, get_folders, assign_folder_access
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', list_folders, name='folders'),
    path('dashboard/files', list_files, name='files'),
    path('download-folder/', download_folder, name='download-folder'),
    path('edit/', edit, name='edit'),
    path('delete/', delete, name='delete'),
    path('upload-file/', create, name='create'),
    path('upload-folder/', upload_folder, name='upload-folder'),
    path('create-folder/', create_fold, name='create-folder'),
    path('get-users/',get_users, name='get-users'),
    path('get-folders/', get_folders, name='get-folders'),
    path('assign-folder-access/', assign_folder_access, name='assign-folder-access')
]
