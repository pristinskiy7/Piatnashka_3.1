# players/cloud_sync.py

# Твоя персональная строка подключения с паролем
CONNECTION_STRING = "mongodb+srv://pristinskiy7_db_user:6VqyOpCLpYisKRwL@cluster0.vuq8m7h.mongodb.net/puzzle_game?retryWrites=true&w=majority&appName=Cluster0"

def sync_data():
    try:
        from pymongo import MongoClient
        import datetime
        from players.team_manager import get_team_id, _load_team_full_data
        from players.manager import _load_players_data

        client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=5000)
        db = client['puzzle_game']
        collection = db['teams_leaderboard']

        t_id = get_team_id()
        local_team = _load_team_full_data()
        local_players_data = _load_players_data()

        if not t_id: return None

        # Собираем список лучших результатов игроков этой команды
        players_ranking_data = []
        for p in local_players_data.get('players', []):
            best = p.get('best_game')
            if best:
                players_ranking_data.append({
                    "player_name": p["name"],
                    "best_xp": best.get("xp", 0),
                    "board": best.get("size", "4x4"),
                    "team_name": local_team["team_name"]
                })

        my_team_payload = {
            "team_id": t_id,
            "team_name": local_team["team_name"],
            "last_sync": datetime.datetime.now().isoformat(timespec='seconds'),
            "total_xp": sum(p.get('total', {}).get('xp', 0) for p in local_players_data.get('players', [])),
            "players_count": len(local_players_data.get('players', [])),
            "best_players": players_ranking_data  # Добавляем список достижений
        }

        collection.replace_one({"team_id": t_id}, my_team_payload, upsert=True)

        # 1. Получаем Топ-10 Команд
        top_teams = list(collection.find().sort("total_xp", -1).limit(10))

        # 2. Получаем Топ-50 Игроков (вытягиваем из всех команд и сортируем вручную)
        all_teams = list(collection.find())
        all_players = []
        for team in all_teams:
            for p in team.get("best_players", []):
                all_players.append(p)

        # Сортируем всех игроков по best_xp
        top_players = sorted(all_players, key=lambda x: x['best_xp'], reverse=True)[:50]

        return {"teams": top_teams, "players": top_players}

    except Exception as e:
        print(f"ЛОГ ОШИБКИ ОБЛАКА: {e}")
        return None