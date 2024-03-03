SELECT
    game_date AS game_date,
    home_team,
    home_team_score,
    visitor_team_score,
    visitor_team,
    season,
    status,
    home_team_win
FROM main_mart.fct_game
WHERE game_date = (
    SELECT MAX(game_date)
    FROM main_mart.fct_game
    WHERE status = 'Final'
);
