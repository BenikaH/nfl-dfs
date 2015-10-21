SELECT opp, 
sum(wr_per_wk) as wrpts, 
sum(rb_per_wk) as rbpts, 
sum(te_per_wk) as tepts

FROM

	(SELECT
		-- break out into columns by position
	opp, 
	pos, 
	case when pos = 'WR' then (dkp/weeks) else 0 end as wr_per_wk, 
	case when pos = 'RB' then (dkp/weeks) else 0 end as rb_per_wk, 
	case when pos = 'TE' then (dkp/weeks) else 0 end as te_per_wk 
	from 

		(SELECT 
			-- join to position here
		opp,
		pos,
		sum(dkp) as dkp,
		count(distinct yearweek) as weeks
		from
		(SELECT
			year, 
			week, 
			yearweek, 
			opp,
			pos,
			sum(dkp) as dkp
			FROM nfl_gamecenter 
			group by 1,2,3,4,5) a

				WHERE (
	
					SELECT count(*) 
					FROM (
						SELECT 
						year, 
						week, 
						yearweek, 
						opp,
						pos, 
						sum(pass_yds) as passing,
						sum(dkp) as dkp
						FROM nfl_gamecenter 
						GROUP BY 1,2,3,4,5) b
	
					WHERE a.yearweek <= b.yearweek and b.opp = a.opp and b.pos = a.pos) <= 6
			
				and pos in ('WR', 'RB', 'TE') GROUP BY 1, 2) f
	
	) g 

GROUP BY 1 ORDER BY 2 DESC