select fd_cons.*, dk_cons.toptier_dk, midtier_dk, lowtier_dk from
(select
a.player_id,
a.playernm_full,
a.pos,
sum(case when a.consrate = 2 then 1 else 0 end) as toptier_fd,
sum(case when a.consrate = 1 then 1 else 0 end) as midtier_fd,
sum(case when a.consrate = 0 then 1 else 0 end) as lowtier_fd
from 
	(select
	player_id,
	playernm_full,
	pos,
	case when fdp/fd_salary * 1000 >= 3 then 2
	when fdp/fd_salary * 1000 >= 1.5 then 1
	else 0
	end as consrate
	from `dfs_results_2014`
	where fdp <> 0 and pos <> 'D') a
group by 1,2,3) fd_cons

left join

(select
b.player_id,
b.playernm_full,
b.pos,
sum(case when b.consrate = 2 then 1 else 0 end) as toptier_dk,
sum(case when b.consrate = 1 then 1 else 0 end) as midtier_dk,
sum(case when b.consrate = 0 then 1 else 0 end) as lowtier_dk
from 
	(select
	player_id,
	playernm_full,
	pos,
	case when dkp/dk_salary * 1000 >= 3 then 2
	when dkp/dk_salary * 1000 >= 1.5 then 1
	else 0
	end as consrate
	from `dfs_results_2014`
	where dkp <> 0 and pos <> 'D') b
group by 1,2,3) dk_cons

on fd_cons.player_id = dk_cons.player_id
order by toptier_dk desc;