from django.urls import path
from .views import UserGameList, UserEventView

urlpatterns = [
    path('reports/usergames', UserGameList.as_view()),
    path('reports/usereventlist', UserEventView.as_view())
]
