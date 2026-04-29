-- sample users (replace UUIDs with real auth users in your environment)
insert into user_roles(user_id, role) values
('11111111-1111-1111-1111-111111111111','admin'),
('22222222-2222-2222-2222-222222222222','planner'),
('33333333-3333-3333-3333-333333333333','viewer')
on conflict (user_id) do nothing;

insert into capacity_config(plant_type,operation,shift,workers_per_shift,hours_per_shift,working_days_per_month) values
('Joinery','Milling',1,8,8,22),('Joinery','Milling',2,8,8,22),('Joinery','Assembly',1,10,8,22),('Joinery','Assembly',2,10,8,22),
('Joinery','Polishing',1,6,8,22),('Joinery','Upholstery',1,5,8,22),('Metal','Metal Fabrication',1,12,8,22),('Metal','Metal Fabrication',2,12,8,22),('Metal','Assembly',1,7,8,22)
on conflict do nothing;

insert into upload_logs(id, filename, uploaded_by, valid_count, error_count) values
(1001,'demand_sample_may.csv','22222222-2222-2222-2222-222222222222',40,2)
on conflict (id) do nothing;

insert into demand_records(upload_log_id, division, plant_type, project_name, client, forecast_type, operation, required_man_hours, work_date) values
(1001,'Retail','Joinery','Store Fitout A','BrandX','Confirmed','Milling',24,'2026-05-01'),
(1001,'Retail','Joinery','Store Fitout A','BrandX','Confirmed','Milling',24,'2026-05-02'),
(1001,'Hospitality','Metal','Hotel Lobby','HotelCo','Probable','Metal Fabrication',18,'2026-05-03'),
(1001,'Hospitality','Metal','Hotel Lobby','HotelCo','Probable','Metal Fabrication',18,'2026-05-04');

insert into upload_error_logs(upload_log_id,row_number,reason,raw_data) values
(1001,5,'end date before start date','{"Project Name":"Invalid Date","Production Start Date":"2026-06-15","Production End Date":"2026-06-01"}'::jsonb),
(1001,9,'Unknown string format','{"Project Name":"Bad Date","Production Start Date":"not-a-date","Production End Date":"2026-06-10"}'::jsonb);
