WITH last_10 AS (

    SELECT
        team.team_name_abbreviation AS team_name,
        last_10_games.game_date,
        last_10_games.home_team,
        last_10_games.home_team_score,
        last_10_games.visitor_team,
        last_10_games.visitor_team_score,
        last_10_games.home_team_win
    FROM main_mart.dim_team AS team
    JOIN ( -- correlated subquery to loop through all teams and get latest 10
        SELECT
            game_date,
            home_team,
            home_team_score,
            visitor_team,
            visitor_team_score,
            home_team_win
        FROM main_mart.fct_game AS game
        WHERE team.team_name_abbreviation = game.home_team OR team.team_name_abbreviation = game.visitor_team
        ORDER BY game_date DESC
        LIMIT 10
    ) AS last_10_games ON TRUE
    WHERE team.conference IS NOT NULL
),

wins AS (

    SELECT
        team_name,
        SUM(
            CASE WHEN team_name = (
                CASE WHEN home_team_win THEN home_team ELSE visitor_team END
            ) THEN 1 ELSE 0 END
        ) AS total_wins_last_10
    FROM last_10
    GROUP BY team_name
)

SELECT *
FROM last_10
LEFT JOIN wins USING(team_name)
ORDER BY team_name
;
