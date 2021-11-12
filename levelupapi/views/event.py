from django.core.exceptions import ValidationError
from django.db.models import fields, Count
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Event
from django.contrib.auth.models import User
from rest_framework.decorators import action
from levelupapi.models.game import Game
from levelupapi.models.gamer import Gamer
from django.db.models import Q



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
        gamer = Gamer.objects.get(user=request.auth.user)
        events = Event.objects.annotate(
            attendees_count=Count('attendees'),
            joined=Count(
            'attendees',
            filter=Q(attendees=gamer)
                )
            )

        game_id = self.request.query_params.get("game_id", None)
        # for event in events:
        #     event.joined = gamer in event.attendees.all()

        if game_id is not None:
            events = events.filter(game_id =game_id)

        serializer = EventSerializer(events, many=True, context={"request":request})
        return Response(serializer.data)
    
    @action(methods=['post', 'delete'], detail=True)
    def signup(self, request, pk=None):
        """Managing gamers signing up for events"""
        # Django uses the `Authorization` header to determine
        # which user is making the request to sign up
        gamer = Gamer.objects.get(user=request.auth.user)

        try:
            # Handle the case if the client specifies a game
            # that doesn't exist
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(
                {'message': 'Event does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # A gamer wants to sign up for an event
        if request.method == "POST":
            try:
                # Using the attendees field on the event makes it simple to add a gamer to the event
                # .add(gamer) will insert into the join table a new row the gamer_id and the event_id
                event.attendees.add(gamer)
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        # User wants to leave a previously joined event
        elif request.method == "DELETE":
            try:
                # The many to many relationship has a .remove method that removes the gamer from the attendees list
                # The method deletes the row in the join table that has the gamer_id and event_id
                event.attendees.remove(gamer)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})


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
    joined = serializers.BooleanField(required=False)
    attending_count = serializers.IntegerField(default=None)
    class Meta:
        model = Event
        fields = ("id", "game", "organizer", "description", "date","time", "attendees", "joined", "attending_count")
        depth = 2