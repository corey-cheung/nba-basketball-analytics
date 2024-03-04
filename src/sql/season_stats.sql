SELECT
    *,
    season = (
        SELECT MAX(season) AS current_season
        FROM main_mart.fct_season_stats
    ) AS current_season
FROM main_mart.fct_season_stats
WHERE total_games != 0
;
