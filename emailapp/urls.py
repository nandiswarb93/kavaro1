
from django.urls import path
from . import views
from landing import views as landing_views

urlpatterns = [
    # Home / Subscribe page
    path("", landing_views.home, name="home"),
    path('', views.subscribe_page, name='subscribe_page'),
    path('subscribe/', views.subscribe_page, name="subscribe"),

    # Save email form submission
    path('save-email/', views.save_email, name="save_email"),
    

    # Unsubscribe confirmation + action
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name="unsubscribe"),
]
