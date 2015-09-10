create or replace view salary_stats as select
dk_salary,
count(*) as players,
sum(dkp) as points,
sum(dkp)/count(*) as avg_dkp
from `dfs_results_2014`
where dkp <> 0
group by dk_salary
order by dk_salary desc
;