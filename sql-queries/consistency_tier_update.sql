delete from consistency_tiers;
insert into consistency_tiers (
player_id, playernm_full, pos, toptier_fd, midtier_fd, lowtier_fd, toptier_dk, midtier_dk, lowtier_dk)
select fd_cons.player_id, c.playernm_full, fd_cons.pos, fd_cons.toptier_fd, fd_cons.midtier_fd, fd_cons.lowtier_fd, dk_cons.toptier_dk, dk_cons.midtier_dk, dk_cons.lowtier_dk from
(select
a.player_id,
a.pos,
sum(case when a.consrate = 2 then 1 else 0 end) as toptier_fd,
sum(case when a.consrate = 1 then 1 else 0 end) as midtier_fd,
sum(case when a.consrate = 0 then 1 else 0 end) as lowtier_fd
from 
	(select
	player_id,
	playernm_full,
	pos,
	case when fdp/fd_salary * 1000 >= 1.7 then 2	-- 67%
	when fdp/fd_salary * 1000 >= 0.7 then 1 -- 33%
	else 0
	end as consrate
	from `v_rotoguru_historicals`
	where fdp <> 0 and pos <> 'D') a
group by 1,2) fd_cons

left join

(select
b.player_id,
b.pos,
sum(case when b.consrate = 2 then 1 else 0 end) as toptier_dk,
sum(case when b.consrate = 1 then 1 else 0 end) as midtier_dk,
sum(case when b.consrate = 0 then 1 else 0 end) as lowtier_dk
from 
	(select
	player_id,
	playernm_full,
	pos,
	case when dkp/dk_salary * 1000 >= 2.7 then 2 -- 67%
	when dkp/dk_salary * 1000 >= 0.95 then 1 -- 25%
	else 0
	end as consrate
	from `v_rotoguru_historicals`
	where dkp <> 0 and pos <> 'D') b
group by 1,2) dk_cons

on fd_cons.player_id = dk_cons.player_id
left join (select distinct player_id, playernm_full from v_rotoguru_historicals) c on fd_cons.player_id = c.player_id
order by toptier_dk desc