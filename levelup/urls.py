from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from levelupapi.views import register_user, login_user
from levelupapi.views import GameTypeView, GameView, EventView, user_profile

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'games', GameView, 'game')
router.register(r'gametypes', GameTypeView, 'gametype')
router.register(r'events', EventView, 'event')

urlpatterns = [
    path('', include(router.urls)),
    path('profile', user_profile),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
]
