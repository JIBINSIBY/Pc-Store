from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from django.urls import path,reverse_lazy
from django.contrib.auth import views as auth_views
from .views import search_suggestions
from .views import create_order
from django.views.decorators.csrf import csrf_exempt  # Only if needed

app_name='userapp'
print("Loading userapp URLs")

urlpatterns = [
    # ... other url patterns ...
    path('cancel-custom-order/<int:order_id>/', views.cancel_custom_order, name='cancel_custom_order'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    # ... other URL patterns ...
    path('build-orders/', views.build_order_view, name='build_orders'),
    path('orders/', views.order_view, name='orders'),
    path('check-stock-availability/', views.check_stock_availability, name='check_stock_availability'),
    path('place-custom-order/', views.place_custom_order, name='place_custom_order'),
    path('razorpay-callback/', views.razorpay_callback, name='razorpay_callback'),
    path('update-build-status/<int:build_id>/', views.update_build_status, name='update_build_status'),
    path('check-stock-availability/', views.check_stock_availability, name='check_stock_availability'),
    # ... other URL patterns ...
    path('check-stock-availability/', views.check_stock_availability, name='check_stock_availability'),
    path('payment-success-custom-pc/', views.payment_success_custom_pc, name='payment_success_custom_pc'),
    # ... other URL patterns ...
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    # ... other url patterns ...
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    # ... other url patterns ...
    path('create-custom-order/', views.create_custom_order, name='create_custom_order'),
    # ... other URL patterns ...
    path('remove-build/<int:build_id>/', views.remove_build, name='remove_build'),
    path('mark-messages-read/', views.mark_messages_read, name='mark_messages_read'),
    path('create-order/', create_order, name='create_order'),  # Ensure this line is present
    # ... other URL patterns ...
    path('checkoutcustom/<int:build_id>/', views.checkoutcustom, name='checkoutcustom'),
    path('messageforbuild/', views.messageforbuild, name='messageforbuild'),
    path('accept-recommendations/', views.accept_recommendations, name='accept_recommendations'),
    path('user-send-message-to-staff/', views.user_send_message_to_staff, name='user_send_message_to_staff'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-recommendations/<int:build_id>/', views.get_recommendations, name='get_recommendations'),
    # ... other url patterns ...
    path('messageforbuild/', views.messageforbuild, name='messageforbuild'),
    path('get-recommendations/<int:build_id>/', views.get_recommendations, name='get_recommendations'),
    path('admin_editproduct/<int:product_id>/', views.admin_editproduct, name='admin_editproduct'),
    path('send-message/<int:build_id>/', views.send_message, name='send_message'),
    # ... other url patterns ...
    # ... other url patterns ...
    path('admin_editcomponent/<int:component_id>/', views.admin_editcomponent, name='admin_editcomponent'),
    # ... other url patterns ...
    # ... other URL patterns ...
    path('delete-component/<int:component_id>/', views.delete_component, name='delete_component'),

    path('staff/build-requests/', views.staff_build_requests, name='staff_build_requests'),
    path('staff/build-request/<int:build_id>/', views.build_request_details, name='build_request_details'),
    path('update-build-status/<int:build_id>/', views.update_build_status, name='update_build_status'),
    # ... other URL patterns ...
    path('change-user-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    # ... other URL patterns ...
    # ... other URL patterns ...
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    # ... other URL patterns ...
    path('product/<int:product_id>/add_rating/', views.add_rating, name='add_rating'),
    # ... other URL patterns ...
    # ... other URL patterns ...
    path('<str:category>/<int:product_id>/', views.single_product, name='single_product'),
    path('add_rating/<int:product_id>/', views.add_rating, name='add_rating'),  # Removed this line
    # ... other URL patterns ...
    path('keyboard/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'keyboards'}),
    path('monitors/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'monitors'}),
    path('mouses/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'mouses'}),
    path('assembledcpus/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'assembledcpus'}),
    path('accessories/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'accessories'}),
    path('product/<int:product_id>/add_rating/', views.add_rating, name='add_rating'),  # Kept this line
    path('', views.index, name='index'),
    
    path('loginuser/', views.loginu, name='loginu'),
    path('signupuser', views.signupu, name='signupuser'),
    path('mainpage', views.mainpage, name='mainpage'),
    path('profile/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('logout/',views.logout_view,name='logout'),
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
    path('admin_viewproduct/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin_editproduct/<int:product_id>/', views.admin_editproduct, name='admin_editproduct'),
    path('admin_addcomponent/', views.admin_addcomponent, name='admin_addcomponent'),
    path('admin_viewcomponent/', views.admin_viewcomponent, name='admin_viewcomponent'),
    path('admin_editcomponent/<int:component_id>/', views.admin_editcomponent, name='admin_editcomponent'),
    path('delete-component/<int:component_id>/', views.delete_component, name='delete_component'),
    path('search/', views.search_results, name='search_results'),
    path('pc_custom/', views.pc_custom, name='pc_custom'),
    path('get_components/', views.get_components, name='get_components'),
    path('profile', views.profile, name='profile'),
    path('address/', views.address, name='address'),
    path('keyboards/', views.keyboards_view, name='keyboards'),
    path('monitors/', views.monitors_view, name='monitors'),
    path('mouses/', views.mouses_view, name='mouses'),
    path('assembledcpus/', views.assembledcpus_view, name='assembledcpus'),
    path('accessories/', views.accessories_view, name='accessories'),
    path('update_admin_profile/', views.update_admin_profile, name='update_admin_profile'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('keyboards/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'keyboards'}),
    path('monitors/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'monitors'}),
    path('mouses/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'mouses'}),
    path('assembledcpus/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'assembledcpus'}),
    path('accessories/<int:product_id>/', views.single_product, name='single_product', kwargs={'category': 'accessories'}),
    path('cart/', views.cart_view, name='cart_view'),
    path('login/', views.loginu, name='login'),
    path('remove-main-image/', views.remove_main_image, name='remove_main_image'),
    path('remove-additional-image/<int:image_id>/', views.remove_additional_image, name='remove_additional_image'),
    path('search-suggestions/', search_suggestions, name='search_suggestions'),
    path('<str:category>/<int:product_id>/', views.single_product, name='single_product'),
    path('delete-component/<int:component_id>/', views.delete_component, name='delete_component'),
    path('check-session/', views.check_session, name='check_session'),
    path('product/<int:product_id>/add_rating/', views.add_rating, name='add_rating'),
    path('keyboard/<int:product_id>/', views.single_product, name='single_product'),
    path('add_rating/<int:product_id>/', views.add_rating, name='add_rating'),  # Removed this line
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),  # Added this line
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),  # Added this line
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),  # Added this line
    path('checkout/', views.checkout, name='checkout'),
    path('add-address/', views.add_address, name='add_address'),
    path('logout-and-redirect/', views.logout_and_redirect, name='logout_and_redirect'),
    path('upi-payment/', views.upi_payment, name='upi_payment'),
    path('card-payment/', views.card_payment, name='card_payment'),
    path('cod-confirmation/', views.cod_confirmation, name='cod_confirmation'),
    path('check-compatibility/', views.check_compatibility, name='check_compatibility'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('yourbuild/', views.yourbuild, name='yourbuild'),
    path('api/build-components/<int:build_id>/', views.build_components, name='build_components'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('component-details-by-name/<str:component_name>/', views.component_details_by_name, name='component_details_by_name'),
    path('component-category/<str:component_name>/', views.get_component_category, name='get_component_category'),
    re_path(r'^recommended-components/(?P<category>.+)/$', views.get_recommended_components, name='get_recommended_components'),
    path('add-recommended-component/', views.add_recommended_component, name='add_recommended_component'),
    path('admin/edit-product/<int:product_id>/', views.admin_editproduct, name='admin_editproduct'),
    path('admin/edit-component/<int:component_id>/', views.admin_editcomponent, name='admin_editcomponent'),
    path('create-custom-order/', views.create_custom_order, name='create_custom_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-success-custom-pc/', views.payment_success_custom_pc, name='payment_success_custom_pc'),
    path('place-custom-order/', views.place_custom_order, name='place_custom_order'),
    path('razorpay-callback/', views.razorpay_callback, name='razorpay_callback'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('ordered-build/', views.ordered_build, name='ordered_build'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('build-order/<int:order_id>/', views.build_order_view, name='build_order'),
   # ... other URL patterns ...
    path('cancel-custom-order/<int:order_id>/', views.cancel_custom_order, name='cancel_custom_order'),
    path('ml/', views.ml_implement, name='ml_implement'),
    path('predict_component/', views.predict_component, name='predict_component'),
    path('delivery-dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery_profile/', views.delivery_profile, name='delivery_profile'),
    path('delivery_profile/update_delivery_profile', views.update_delivery_profile, name='update_delivery_profile'),
    path('delivery_assigned/', views.delivery_assigned, name='delivery_assigned'),
    path('delivery_completed/', views.delivery_completed, name='delivery_completed'),
    path('delivery_cancelled/', views.delivery_cancelled, name='delivery_cancelled'),
    path('update-delivery-profile/', views.update_delivery_profile, name='update_delivery_profile'),
    path('assign-delivery-boy/<int:order_id>/', views.assign_delivery_boy, name='assign_delivery_boy'),
     path('userapp/assign-delivery-boy/<int:order_id>/', views.assign_delivery_boy, name='assign_delivery_boy'),
    path('delivery/update-status/<int:delivery_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('delivery/send-otp/<int:delivery_id>/', views.send_delivery_otp, name='send_delivery_otp'),
    path('delivery/verify-otp/<int:delivery_id>/', views.verify_delivery_otp, name='verify_delivery_otp'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('get-cart-total/', views.get_cart_total, name='get_cart_total'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

