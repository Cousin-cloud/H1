import React, { useMemo, useState } from 'react';
import { api, withAuth } from '../api/client';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, Legend
} from 'recharts';

type PlanRow = {
  month: string; plant_type: string; operation: string; division: string;
  required_man_hours: number; monthly_capacity: number; stretch_capacity: number; status: 'green'|'amber'|'red';
};

const COLORS = { green: '#22c55e', amber: '#f59e0b', red: '#ef4444' };

export const App = () => {
  const [token, setToken] = useState('');
  const [scenario, setScenario] = useState('confirmed');
  const [data, setData] = useState<PlanRow[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadPlanning = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/planning?scenario=${scenario}`, withAuth(token));
      setData(res.data);
    } finally { setLoading(false); }
  };

  const doPreview = async () => {
    if (!file) return;
    const form = new FormData(); form.append('file', file);
    const res = await api.post('/api/upload/preview', form, withAuth(token));
    setPreview(res.data);
  };

  const doConfirm = async () => {
    if (!file) return;
    const form = new FormData(); form.append('file', file);
    await api.post('/api/upload/confirm', form, withAuth(token));
    await loadPlanning();
  };

  const statusCount = useMemo(() => {
    const count = { green: 0, amber: 0, red: 0 };
    data.forEach(r => count[r.status]++);
    return Object.entries(count).map(([name, value]) => ({ name, value }));
  }, [data]);

  const byPlant = useMemo(() => {
    const map: Record<string, { demand: number; capacity: number }> = {};
    data.forEach(r => {
      if (!map[r.plant_type]) map[r.plant_type] = { demand: 0, capacity: 0 };
      map[r.plant_type].demand += Number(r.required_man_hours);
      map[r.plant_type].capacity += Number(r.monthly_capacity);
    });
    return Object.entries(map).map(([plant, v]) => ({ plant, ...v }));
  }, [data]);

  return <div className='wrap'>
    <header className='header'>
      <h1>Enterprise Production Capacity Planner</h1>
      <p>Joinery + Metal | 3-Shift Planning | Retail & Hospitality</p>
    </header>

    <section className='panel auth'>
      <input placeholder='Supabase JWT token' value={token} onChange={e=>setToken(e.target.value)} />
      <select value={scenario} onChange={e=>setScenario(e.target.value)}>
        <option value='confirmed'>Confirmed only</option>
        <option value='confirmed_probable'>Confirmed + Probable</option>
        <option value='all'>All demand</option>
      </select>
      <button onClick={loadPlanning}>{loading ? 'Loading...' : 'Run Scenario'}</button>
    </section>

    <section className='grid'>
      <div className='panel'>
        <h3>Demand Upload</h3>
        <input type='file' onChange={e=>setFile(e.target.files?.[0] || null)} />
        <div className='row'>
          <button onClick={doPreview}>Preview</button>
          <button onClick={doConfirm}>Confirm</button>
        </div>
        {preview && <div className='preview'>
          <p>Valid Rows: <b>{preview.valid_count}</b> | Error Rows: <b>{preview.error_count}</b></p>
          {preview.error_count > 0 && <p className='redTxt'>Some rows excluded. Review error reasons before commit.</p>}
        </div>}
      </div>

      <div className='panel'>
        <h3>Load Status Heatmap</h3>
        <ResponsiveContainer width='100%' height={220}>
          <PieChart><Pie data={statusCount} dataKey='value' nameKey='name' outerRadius={70}>
            {statusCount.map((s, i) => <Cell key={i} fill={COLORS[s.name as keyof typeof COLORS]} />)}
          </Pie><Legend /></PieChart>
        </ResponsiveContainer>
      </div>

      <div className='panel wide'>
        <h3>Demand vs Capacity by Plant</h3>
        <ResponsiveContainer width='100%' height={280}>
          <BarChart data={byPlant}><CartesianGrid strokeDasharray='3 3' /><XAxis dataKey='plant' /><YAxis /><Tooltip />
            <Bar dataKey='demand' fill='#ef4444' /><Bar dataKey='capacity' fill='#10b981' />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>

    <section className='panel'>
      <h3>Operation Drilldown</h3>
      <table>
        <thead><tr><th>Month</th><th>Plant</th><th>Operation</th><th>Division</th><th>Demand</th><th>Capacity</th><th>Stretch</th><th>Status</th></tr></thead>
        <tbody>{data.map((r,i)=><tr key={i}><td>{r.month}</td><td>{r.plant_type}</td><td>{r.operation}</td><td>{r.division}</td><td>{r.required_man_hours.toFixed(1)}</td><td>{r.monthly_capacity.toFixed(1)}</td><td>{r.stretch_capacity.toFixed(1)}</td><td><span className={`badge ${r.status}`}>{r.status.toUpperCase()}</span></td></tr>)}</tbody>
      </table>
    </section>
  </div>
}
