create table if not exists user_roles (
  user_id uuid primary key,
  role text not null check (role in ('admin','planner','viewer')),
  created_at timestamptz default now()
);
create table if not exists capacity_config (
  id bigserial primary key,
  plant_type text not null,
  operation text not null,
  shift int not null check (shift between 1 and 3),
  workers_per_shift int not null,
  hours_per_shift numeric(6,2) not null,
  working_days_per_month int not null,
  unique (plant_type, operation, shift)
);
create table if not exists upload_logs (
  id bigserial primary key,
  filename text not null,
  uploaded_by uuid,
  valid_count int not null,
  error_count int not null,
  created_at timestamptz default now()
);
create table if not exists demand_records (
  id bigserial primary key,
  upload_log_id bigint references upload_logs(id),
  division text not null,
  plant_type text not null,
  project_name text not null,
  client text not null,
  forecast_type text not null,
  operation text not null,
  required_man_hours numeric(10,2) not null,
  work_date date not null
);
create table if not exists upload_error_logs (
  id bigserial primary key,
  upload_log_id bigint references upload_logs(id),
  row_number int not null,
  reason text not null,
  raw_data jsonb not null,
  created_at timestamptz default now()
);
create index if not exists idx_demand_work_date on demand_records(work_date);
create index if not exists idx_demand_dims on demand_records(plant_type, operation, division, forecast_type);

alter table user_roles enable row level security;
alter table capacity_config enable row level security;
alter table upload_logs enable row level security;
alter table demand_records enable row level security;
alter table upload_error_logs enable row level security;

create policy user_roles_read on user_roles for select using (auth.uid() = user_id);
create policy capacity_read on capacity_config for select using (true);
create policy capacity_admin_write on capacity_config for all using (exists(select 1 from user_roles ur where ur.user_id=auth.uid() and ur.role='admin'));
create policy demand_read on demand_records for select using (true);
create policy demand_planner_write on demand_records for insert with check (exists(select 1 from user_roles ur where ur.user_id=auth.uid() and ur.role in ('admin','planner')));
create policy logs_read on upload_logs for select using (true);
create policy logs_write on upload_logs for insert with check (exists(select 1 from user_roles ur where ur.user_id=auth.uid() and ur.role in ('admin','planner')));
create policy error_read on upload_error_logs for select using (true);
create policy error_write on upload_error_logs for insert with check (exists(select 1 from user_roles ur where ur.user_id=auth.uid() and ur.role in ('admin','planner')));
