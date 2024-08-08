from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from django.urls import path,reverse_lazy
from django.contrib.auth import views as auth_views

app_name='userapp'
urlpatterns = [
    path('', views.index, name='index'),
    
    path('loginuser', views.loginu, name='loginuser'),
    path('signupuser', views.signupu, name='signupuser'),
    path('mainpage', views.mainpage, name='mainpage'),
    path('profile/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('logout',views.signout,name='logout'),
    path('address', views.address, name='address'),
    path('addaddress',views.addaddress,name='addaddress'),
    path('editaddress',views.editaddress,name='editaddress'),
    path('editaddress/<int:address_id>/', views.editaddress, name='editaddress'),
    path('admin-dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('admin_profile/update_admin_profile', views.update_admin_profile, name='update_admin_profile'),
    path('admin-dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin_userview/', views.admin_userview, name='admin_userview'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-user-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    # passwordreset start
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='forgotpassword.html',
        email_template_name='registration/password_reset_email.html',
        success_url=reverse_lazy('userapp:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='forgotpassworddone.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
         success_url=reverse_lazy('userapp:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='forgotpasswordcomplete.html'
    ), name='password_reset_complete'),
    #passwordresent end
    path('accounts/', include('allauth.urls')),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('admin_productadd/', views.admin_productadd, name='admin_productadd'),
    path('admin_viewproduct/', views.admin_viewproduct, name='admin_viewproduct'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin_editproduct/<int:product_id>/', views.admin_editproduct, name='admin_editproduct'),
    path('admin_addcomponent/', views.admin_addcomponent, name='admin_addcomponent'),
    path('admin_viewcomponent/', views.admin_viewcomponent, name='admin_viewcomponent'),
    path('admin_editcomponent/<int:component_id>/', views.admin_editcomponent, name='admin_editcomponent'),
    path('delete-component/<int:component_id>/', views.delete_component, name='delete_component'),
    path('search/', views.search_results, name='search_results'),
    path('pc_custom/', views.pc_custom, name='pc_custom'),
    path('profile', views.profile, name='profile'),
    path('address/', views.address, name='address'),
    path('get_components/', views.get_components, name='get_components'),
    path('keyboards/', views.keyboards_view, name='keyboards'),
    path('monitors/', views.monitors_view, name='monitors'),
    path('update_admin_profile/', views.update_admin_profile, name='update_admin_profile'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)