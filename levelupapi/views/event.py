from django.core.exceptions import ValidationError
from django.db.models import fields
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Event
from django.contrib.auth.models import User

from levelupapi.models.game import Game
from levelupapi.models.gamer import Gamer



class EventView(ViewSet):
    """Level up Events"""
    def create(self, request):
        """Handles Posting Operations"""
        gamer = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data["game_id"])
        try:
            event = Event.objects.create(
                game = game,
                organizer = gamer,
                description = request.data["description"],
                date = request.data["date"],
                time = request.data["time"]
            )
            serializer = EventSerializer(event, context={"request": request})
            return Response({"reason": "Event Posted"}, status= status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status= status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handles Put request from front end"""
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.game = Game.objects.get(pk=request.data["game_id"])
        event.organizer = gamer
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        event.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT) 

    def destroy(self, reuqest, pk=None):
        """Handles Deletes from the client"""
        try:
            event = Event.objects.get(pk=pk)
            event.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Get Single Event"""
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)



    def list(self, request):
        """Gets all Events, or filters by organizer"""
        events = Event.objects.all()
        game_id = self.request.query_params.get("game_id", None)
        if game_id is not None:
            events = events.filter(game_id =game_id)

        serializer = EventSerializer(events, many=True, context={"request":request})
        return Response(serializer.data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
class GamerSerializer(serializers.ModelSerializer):
    """JSON Serializer for gamers
    Only Getting first name and last name"""
    user = UserSerializer()
    class Meta:
        model = Gamer
        fields = ('id', 'user','bio')
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields =('title', 'maker', "number_of_players")
class EventSerializer(serializers.ModelSerializer):
    organizer = GamerSerializer()
    game = GameSerializer()
    class Meta:
        model = Event
        fields = ("id", "game", "organizer", "description", "date","time")
        depth = 2