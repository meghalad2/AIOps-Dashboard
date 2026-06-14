import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { format } from 'date-fns'

export default function MttrChart({ data }) {
  const formatted = data.map(d => ({
    ...d,
    time: format(new Date(d.fired_at), 'MM/dd HH:mm'),
    mttr_min: +(d.mttr_seconds / 60).toFixed(1),
  }))

  return (
    <div className="panel mttr-chart">
      <div className="panel-header">
        <h2>Remediation Speed (MTTR Trend)</h2>
        <span className="subtitle">Minutes to recovery (Last 30 incidents)</span>
      </div>
      
      {data.length === 0 ? (
        <div className="empty-chart">
          <p className="empty">No resolved incidents available for trend charting.</p>
        </div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={formatted} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
              <defs>
                <linearGradient id="colorMttr" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3ca6ff" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3ca6ff" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2e3a" vertical={false} />
              <XAxis dataKey="time" tick={{ fill: '#8e98b0', fontSize: 10 }} axisLine={{ stroke: '#2e3342' }} />
              <YAxis tick={{ fill: '#8e98b0', fontSize: 10 }} axisLine={{ stroke: '#2e3342' }} unit="m" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e222d', borderColor: '#2d3345', borderRadius: 8, color: '#fff' }}
                itemStyle={{ color: '#3ca6ff' }}
                labelStyle={{ color: '#8e98b0' }}
                formatter={(v) => [`${v}m`, 'Resolution Time']} 
              />
              <Area
                type="monotone"
                dataKey="mttr_min"
                stroke="#3ca6ff"
                fillOpacity={1}
                fill="url(#colorMttr)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
