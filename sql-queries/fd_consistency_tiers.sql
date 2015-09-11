select
a.player_id,
a.playernm_full,
a.pos,
sum(case when a.consrate = 2 then 1 else 0 end) as toptier,
sum(case when a.consrate = 1 then 1 else 0 end) as midtier,
sum(case when a.consrate = 0 then 1 else 0 end) as lowtier
from 
(select
player_id,
playernm_full,
pos,
case when fdp/fd_salary * 1000 >= 4 then 2
when fdp/fd_salary * 1000 >= 2 then 1
else 0
end as consrate
from `dfs_results_2014`
where fdp <> 0) a
group by 1,2,3
order by toptier desc;