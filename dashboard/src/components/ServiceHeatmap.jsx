function scoreColor(score) {
  if (score >= 85) return '#52d677' // Green
  if (score >= 60) return '#ffaa3b' // Orange
  return '#ff5353' // Red
}

export default function ServiceHeatmap({ services }) {
  return (
    <div className="panel service-heatmap">
      <div className="panel-header">
        <h2>Service Infrastructure Health</h2>
        <span className="subtitle">Real-time autonomic health scores</span>
      </div>
      {services.length === 0 ? (
        <p className="empty">No services tracked. Trigger alert webhooks to discover services.</p>
      ) : (
        <div className="heatmap-grid">
          {services.map(s => {
            const color = scoreColor(s.health_score);
            return (
              <div 
                key={s.service} 
                className="heatmap-cell"
                style={{ borderLeft: `4px solid ${color}` }}
              >
                <div className="cell-top">
                  <div className="cell-name">{s.service}</div>
                  <div className="cell-score" style={{ color: color }}>
                    {s.health_score}
                  </div>
                </div>
                <div className="cell-details">
                  <div className="cell-metric">
                    <span className="metric-label">7d Logs:</span>
                    <span className="metric-val">{s.incident_count_7d}</span>
                  </div>
                  {s.avg_mttr_seconds ? (
                    <div className="cell-metric">
                      <span className="metric-label">Avg MTTR:</span>
                      <span className="metric-val">{Math.round(s.avg_mttr_seconds)}s</span>
                    </div>
                  ) : null}
                  <div className="cell-metric status-wrapper">
                    <span className="metric-label">Status:</span>
                    <span className="metric-status-val" style={{ color: color }}>
                      {s.health_score >= 85 ? 'HEALTHY' : s.health_score >= 60 ? 'DEGRADED' : 'CRITICAL'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  )
}
