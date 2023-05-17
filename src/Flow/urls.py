"""
URL configuration for Flow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView
from manager import views as manager_views
from authentication import views as auth_views
from authentication.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url=reverse_lazy('login')), name='login'),
    path('login/', CustomLoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('register/', auth_views.register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('setup/', manager_views.setup, name='setup'),
    path('setup/next_week/<int:next_week>/', manager_views.setup, name='setup_next_week'),
    path('calendar/', manager_views.calendar, name='calendar'),
    path('calendar/<int:next_week>/', manager_views.calendar, name='calendar_next_week'),
    path('account/', manager_views.account, name='account'),
    path('requests/', manager_views.requests, name='requests'),
    path('requests/approve/<int:request_id>/', manager_views.handle_request, name='handle_request'),
    path('requests/reject/<int:request_id>/', manager_views.handle_request, name='handle_request'),
    path('requests_status/', manager_views.requests_status, name='requests_status'),
]
