from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from levelupapi.models.event_gamer import EventGamer
from levelupapi.models.event import Event
from levelupapi.models.gamer import Gamer
from django.contrib.auth.models import User
from levelupapi.models.game import Game

@api_view(['GET'])
def user_profile(request):
    """Handle GET requests to profile resource

    Returns:
        Response -- JSON representation of user info and events
    """
    gamer = Gamer.objects.get(user=request.auth.user)
    
    # : Use the django orm to filter events if the gamer is attending the event
    # attending =
    print(gamer.attending.all()) 
    attending = gamer.attending.all()
    #  Use the orm to filter events if the gamer is hosting the event
    # hosting =
    hosting = gamer.event_set
    attending = EventSerializer(
        attending, many=True, context={'request': request})
    hosting = EventSerializer(
        hosting, many=True, context={'request': request})
    gamer = GamerSerializer(
        gamer, many=False, context={'request': request})

    # Manually construct the JSON structure you want in the response
    profile = {
        "gamer": gamer.data,
        "attending": attending.data,
        "hosting": hosting.data
    }

    return Response(profile)
class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games"""
    class Meta:
        model = Game
        fields = ('title',)
class EventSerializer(serializers.ModelSerializer):
    game = GameSerializer(many=False)
    class Meta:
        model = Event
        fields = ("id", "game", "description", "date","time")
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
class GamerSerializer(serializers.ModelSerializer):
    """JSON Serializer for gamers
    Only Getting first name and last name"""
    user = UserSerializer(many=False)
    class Meta:
        model = Gamer
        fields = ('id', 'user','bio')
