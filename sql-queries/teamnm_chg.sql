select a.cbs_team as team, t.cbs_team as opp

from

(
select distinct n.team, t.cbs_team, n.opp from numberfire_wkly_proj n
left join
team_map t on n.team = t.nf_team

 where week = 7) a
 
left join

team_map t on a.opp = t.nf_team;