  SELECT
                    a.*,
                    c.first_name ||" "||c.last_name as full_name,
                    
                    b.id
                FROM levelupapi_game as a
                JOIN levelupapi_gamer as b
                ON b.id = a.gamer_id
                JOIN auth_user as c
                ON c.id = b.user_id