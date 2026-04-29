insert into capacity_config(plant_type,operation,shift,workers_per_shift,hours_per_shift,working_days_per_month) values
('Joinery','Milling',1,8,8,22),('Joinery','Milling',2,8,8,22),('Joinery','Assembly',1,10,8,22),
('Joinery','Polishing',1,6,8,22),('Joinery','Upholstery',1,5,8,22),('Metal','Metal Fabrication',1,12,8,22),('Metal','Metal Fabrication',2,12,8,22)
on conflict do nothing;
