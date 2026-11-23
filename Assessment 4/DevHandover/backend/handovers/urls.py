from django.urls import path
from . import views
urlpatterns=[path('csrf/',views.csrf),path('login/',views.sign_in),path('logout/',views.sign_out),path('me/',views.me),path('users/',views.users),path('projects/',views.projects),path('projects/<int:pk>/',views.project_detail),path('projects/<int:pk>/items/<int:item_id>/evidence/',views.evidence),path('projects/<int:pk>/items/<int:item_id>/review/',views.review),path('projects/<int:pk>/accept/',views.accept)]
