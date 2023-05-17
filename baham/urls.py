from django.urls import path
from . import views


urlpatterns = [
    path('', views.view_home, name='home'),
    path('baham/vehicles', views.view_vehicles, name='vehicles'),
    path('baham/vehicles/create', views.create_vehicle, name='createvehicle'),
    path('baham/vehicles/save/', views.save_vehicle, name='savevehicle'),
    path('baham/aboutus', views.view_aboutus, name='aboutus'),
    path('vehicle/<int:model_id>/void/', views.vehicle_void, name='vehicle_soft_void'),
    path('vehicle/<int:model_id>/unvoid/', views.vehicle_unvoid, name='vehicle_undoSoftDelete_unvoid'),
]
