from django.conf.urls import url
from base.user_views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # User CRUD APIs
    url(r'^login$', UserLoginView.as_view(), name='login'),
    url(r'^signup$', UserCreateView.as_view(), name='register'),
    url(r'^logout$', UserLogoutView.as_view(), name='logout'),
    url(r'^user/get/(?P<id>[\w-]+)$', UserGetView.as_view(), name='get_user'),
    url(r'^user/update/(?P<id>[\w-]+)$', UserUpdateView.as_view(), name='update_user'),
    url(r'^user/delete/(?P<id>[\w-]+)$', UserDeleteView.as_view(), name = 'delete_user'),
    url(r'^user/list', UserList.as_view(), name = 'user_list'),
    url(r'^change_password', ChangePasswordView.as_view(), name='change_password'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)