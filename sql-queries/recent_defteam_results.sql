select
f.opp,
sum(f.passover) as poorpass_def,
sum(f.rushover) as poorrush_def

FROM
-- Finds max last 6 games
(
SELECT 
a.year, 
a.week, 
a.yearweek, 
a.opp, 
a.passing, 
case when a.passing >= 250 then 1 else 0 end as passover, -- 250 is average over last year +
case when g.rushing >= 110 then 1 else 0 end as rushover -- 110 is average over last year +

	FROM
	(SELECT
	year, 
	week, 
	yearweek, 
	opp, 
	sum(pass_yds) as passing 
	FROM nfl_gamecenter 
	group by 1,2,3,4) a
	
		LEFT JOIN
		(SELECT
			year,
			week,
			yearweek,
			opp,
			sum(rush_yds) as rushing
			FROM nfl_gamecenter
			group by 1,2,3,4) g ON a.yearweek = g.yearweek and a.opp = g.opp

		WHERE (
	
			SELECT count(*) 
			FROM (
				SELECT 
				year, 
				week, 
				yearweek, 
				opp, 
				sum(pass_yds) as passing 
				FROM nfl_gamecenter 
				group by 1,2,3,4) b
	
			WHERE a.yearweek <= b.yearweek and b.opp = a.opp

		) <= 6
		
order by opp asc, yearweek asc) f

group by 1
order by poorpass_def desc