"""Module for generating games by user report"""
from django.shortcuts import render
from django.db import connection
from django.views import View

from levelupreports.views.helpers import dict_fetch_all


class UserEventView(View):
    def get(self, request):
        with connection.cursor() as db_cursor:
            db_cursor.execute("""
            SELECT
                a.*,
                d.first_name ||" "|| d.last_name as full_name,
                e.title as game_name,
                c.id as gamer_id
            FROM levelupapi_event as a
            JOIN levelupapi_eventgamer as b
                ON b.event_id = a.id
            JOIN levelupapi_gamer as c
                ON c.id = b.gamer_id
            JOIN auth_user as d
                ON d.id = c.user_id
            JOIN levelupapi_game as e
                ON e.id = a.game_id
            """)

            dataset = dict_fetch_all(db_cursor)

            events_by_user = []

            for row in dataset:
                event = {
                    'id': row['id'],
                    'date': row['date'],
                    'time': row['time'],
                    'game_name': row['game_name']
                }

                user_dict = next(
                        (
                            user_event for user_event in events_by_user
                            if user_event['gamer_id'] == row['gamer_id']
                        ),
                        None
                    )
                
                if user_dict is not None:
                    # If the user_dict is already in the games_by_user list, append the game to the games list
                    user_dict['events'].append(event)
                else:
                    # If the user is not on the games_by_user list, create and add the user to the list
                    events_by_user.append({
                        "gamer_id": row['gamer_id'],
                        "full_name": row['full_name'],
                        "events": [event]
                    })
            template = 'users/events_list_gamer.html'
            context = {
                "user_events": events_by_user
            }
            return render(request, template, context)