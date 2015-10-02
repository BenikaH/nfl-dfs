SET @weeknum = 4;

SELECT
nf.week,
nf.team,
p.gamedate,
concat(nf.playernm_first, " ", nf.playernm_last) as playernm_full,
nf.pos,
nf.team,
nf.opp,
nf.dk_salary,
dks.week_chg,
nf.fd_salary,
fds.week_chg,
nf.opp_rank,
nf.ovr_rank,
nf.pos_rank,
nf.dkp as nf_dkp,
nf.fdp as nf_fdp,
rw.dkp as rw_dkp,
rw.fdp as rw_fdp,
rg.dkp as rg_dkp,
rg.fdp as rg_fdp,
fp.dkp as fp_dkp,
fp.fdp as fp_fdp,
fs.dkp as fs_dkp,
fs.fdp as fs_fdp,
e.dkp as e_dkp,
e.fdp as e_fdp,
c.dkp as c_dkp,
c.fdp as c_fdp,
p.spread,
p.total,
p.teamtotal,
p.spread_chg,
p.teamtotal_chg,
vdk.avg_dkp,
vfd.avg_fdp,
cons.toptier_dk,
cons.midtier_dk,
cons.lowtier_dk,
cons.toptier_fd,
cons.midtier_fd,
cons.lowtier_fd

FROM
numberfire_wkly_proj nf
LEFT JOIN player_map map on nf.player_id = map.numberfire_id
LEFT JOIN (select distinct player_id, week, dkp, fdp from rotowire_wkly_proj) rw on rw.player_id = map.rotowire_id and rw.week = @weeknum
LEFT JOIN rotogrinders_wkly_proj rg on rg.player_id = map.rotogrinders_id and rg.week = @weeknum
LEFT JOIN fantasypros_wkly_proj fp on fp.player_id = map.fantasypros_id and fp.week = @weeknum
LEFT JOIN foxsports_wkly_proj fs on fs.player_id = map.foxsports_id and fs.week = @weeknum
LEFT JOIN espn_wkly_proj e on e.player_id = map.espn_id and e.week = @weeknum
LEFT JOIN cbssports_wkly_proj c on c.player_id = map.cbssports_id and c.week = @weeknum
LEFT JOIN team_map tm on nf.team = tm.nf_team
-- LEFT JOIN rotogrinders_odds rgo on rgo.team = tm.rg_team and rgo.week = 2
LEFT JOIN pinnacle_odds p on p.team = tm.pinnacle_team and p.week = @weeknum
LEFT JOIN weekly_salaries_dk dks on dks.player_id = nf.player_id
LEFT JOIN weekly_salaries_fd fds on fds.player_id = nf.player_id
LEFT JOIN (select dk_salary, sum(points)/sum(players) as avg_dkp from v_dk_salary_stats group by 1) vdk on vdk.dk_salary = nf.dk_salary
LEFT JOIN (select fd_salary, sum(points)/sum(players) as avg_fdp from v_fd_salary_stats group by 1) vfd on vfd.fd_salary = nf.fd_salary
LEFT JOIN (select distinct player_id from v_rotoguru_historicals) guru on guru.player_id= map.rotoguru_id
LEFT JOIN (select distinct player_id, toptier_dk, midtier_dk, lowtier_dk, toptier_fd, midtier_fd, lowtier_fd from consistency_tiers) cons on cons.player_id = guru.player_id

WHERE nf.week = @weeknum
ORDER BY nf.dk_salary DESC;