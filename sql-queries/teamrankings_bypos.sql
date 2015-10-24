SET @weeks = 5;
SET @curweek = 7;

SELECT
of.team as team,
of.qbvar + de.qbvar as qbrank,
of.wrvar + de.wrvar as wrrank,
of.rbvar + de.rbvar as rbrank,
of.tevar + de.tevar as terank
FROM
(
SELECT team, 
sum(qb_per_wk) - sum(qbavgpts) as qbvar, 
sum(wr_per_wk) - sum(wravgpts) as wrvar, 
sum(rb_per_wk) - sum(rbavgpts) as rbvar, 
sum(te_per_wk) - sum(teavgpts) as tevar
FROM
	(SELECT
		-- break out into columns by position
	f.team, 
	f.pos, 
	case when f.pos = 'QB' then (f.dkp/f.weeks) else 0 end as qb_per_wk,
	case when f.pos = 'QB' then avg.pts_wk else 0 end as qbavgpts, 
	case when f.pos = 'WR' then (f.dkp/f.weeks) else 0 end as wr_per_wk,
	case when f.pos = 'WR' then avg.pts_wk else 0 end as wravgpts, 
	case when f.pos = 'RB' then (f.dkp/f.weeks) else 0 end as rb_per_wk,
	case when f.pos = 'RB' then avg.pts_wk else 0 end as rbavgpts,  
	case when f.pos = 'TE' then (f.dkp/f.weeks) else 0 end as te_per_wk,
	case when f.pos = 'TE' then avg.pts_wk else 0 end as teavgpts 
	from 
		(SELECT 
			-- join to position here
		team,
		pos,
		sum(dkp) as dkp,
		count(distinct yearweek) as weeks
		from
		(SELECT
			year, 
			week, 
			yearweek, 
			team,
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
						team,
						pos, 
						sum(pass_yds) as passing,
						sum(dkp) as dkp
						FROM nfl_gamecenter 
						GROUP BY 1,2,3,4,5) b
					WHERE a.yearweek <= b.yearweek and b.team = a.team and b.pos = a.pos) <= @weeks
					and pos in ('QB', 'WR', 'RB', 'TE') GROUP BY 1, 2) f
				-- #####join start
				LEFT JOIN (
				SELECT
				pos,
				sum(dkp),
				sum(weeks),
				sum(dkp)/sum(weeks) as pts_wk
				FROM (
				SELECT 
				team,
				pos,
				sum(dkp) as dkp,
				count(distinct yearweek) as weeks
				FROM
				(SELECT
					year, 
					week, 
					yearweek, 
					team,
					pos,
					sum(dkp) as dkp
					FROM nfl_gamecenter 
					GROUP BY 1,2,3,4,5) a
						WHERE (
							SELECT count(*) 
							FROM (
								SELECT 
								year, 
								week, 
								yearweek, 
								team,
								pos, 
								sum(pass_yds) as passing,
								sum(dkp) as dkp
								FROM nfl_gamecenter 
								GROUP BY 1,2,3,4,5) b
							WHERE a.yearweek <= b.yearweek and b.team = a.team and b.pos = a.pos) <= @weeks
						and pos in ('QB', 'WR', 'RB', 'TE') GROUP BY 1, 2) f GROUP BY 1) avg ON avg.pos = f.pos
				-- #####join end
	) g 
GROUP BY 1 ORDER BY 2 DESC) of
LEFT JOIN
(
SELECT g.opp,
sc.team, 
sum(qb_per_wk) - sum(qbavgpts) as qbvar, 
sum(wr_per_wk) - sum(wravgpts) as wrvar, 
sum(rb_per_wk) - sum(rbavgpts) as rbvar, 
sum(te_per_wk) - sum(teavgpts) as tevar
FROM
	(SELECT
		-- break out into columns by position
	f.opp, 
	f.pos, 
	case when f.pos = 'QB' then (f.dkp/f.weeks) else 0 end as qb_per_wk,
	case when f.pos = 'QB' then avg.pts_wk else 0 end as qbavgpts, 
	case when f.pos = 'WR' then (f.dkp/f.weeks) else 0 end as wr_per_wk,
	case when f.pos = 'WR' then avg.pts_wk else 0 end as wravgpts, 
	case when f.pos = 'RB' then (f.dkp/f.weeks) else 0 end as rb_per_wk,
	case when f.pos = 'RB' then avg.pts_wk else 0 end as rbavgpts,  
	case when f.pos = 'TE' then (f.dkp/f.weeks) else 0 end as te_per_wk,
	case when f.pos = 'TE' then avg.pts_wk else 0 end as teavgpts 
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
					WHERE a.yearweek <= b.yearweek and b.opp = a.opp and b.pos = a.pos) <= @weeks
				and pos in ('QB', 'WR', 'RB', 'TE') GROUP BY 1, 2) f
				-- #####join start
				LEFT JOIN (
				SELECT
				pos,
				sum(dkp),
				sum(weeks),
				sum(dkp)/sum(weeks) as pts_wk
				FROM (
				SELECT 
				opp,
				pos,
				sum(dkp) as dkp,
				count(distinct yearweek) as weeks
				FROM
				(SELECT
					year, 
					week, 
					yearweek, 
					opp,
					pos,
					sum(dkp) as dkp
					FROM nfl_gamecenter 
					GROUP BY 1,2,3,4,5) a
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
							WHERE a.yearweek <= b.yearweek and b.opp = a.opp and b.pos = a.pos) <= @weeks
						and pos in ('QB', 'WR', 'RB', 'TE') GROUP BY 1, 2) f GROUP BY 1) avg ON avg.pos = f.pos
				-- #####join end
	) g 
	LEFT JOIN
	(
	SELECT a.cbs_team as team, t.cbs_team as opp
	FROM
		(
		SELECT DISTINCT n.team, t.cbs_team, n.opp FROM numberfire_wkly_proj n
		LEFT JOIN
		team_map t on n.team = t.nf_team
		 WHERE week = @curweek) a
	LEFT JOIN
	team_map t on a.opp = t.nf_team) sc on g.opp = sc.opp
GROUP BY 1 ORDER BY 2 DESC) de on of.team = de.team;