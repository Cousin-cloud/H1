import React, { useState } from 'react';
import { api, withAuth } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const App = () => {
  const [token, setToken] = useState('');
  const [scenario, setScenario] = useState('confirmed');
  const [data, setData] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);

  const loadPlanning = async () => {
    const res = await api.get(`/api/planning?scenario=${scenario}`, withAuth(token));
    setData(res.data);
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

  return <div className='wrap'>
    <h1>Production Capacity Planner</h1>
    <input placeholder='Supabase JWT' value={token} onChange={e=>setToken(e.target.value)} />
    <div className='card'>
      <h3>Upload Demand</h3>
      <input type='file' onChange={e=>setFile(e.target.files?.[0] || null)} />
      <button onClick={doPreview}>Preview</button><button onClick={doConfirm}>Confirm Upload</button>
      {preview && <pre>{JSON.stringify(preview, null, 2)}</pre>}
    </div>
    <div className='card'>
      <select value={scenario} onChange={e=>setScenario(e.target.value)}>
        <option value='confirmed'>Confirmed only</option>
        <option value='confirmed_probable'>Confirmed + Probable</option>
        <option value='all'>All demand</option>
      </select>
      <button onClick={loadPlanning}>Run Planning</button>
      <ResponsiveContainer width='100%' height={360}><BarChart data={data}><XAxis dataKey='operation' /><YAxis /><Tooltip />
        <Bar dataKey='required_man_hours' fill='#d9534f' /><Bar dataKey='monthly_capacity' fill='#5cb85c' />
      </BarChart></ResponsiveContainer>
      <table><thead><tr><th>Month</th><th>Plant</th><th>Operation</th><th>Division</th><th>Status</th></tr></thead>
      <tbody>{data.map((r,i)=><tr key={i}><td>{r.month}</td><td>{r.plant_type}</td><td>{r.operation}</td><td>{r.division}</td><td className={r.status}>{r.status}</td></tr>)}</tbody></table>
    </div>
  </div>
}
