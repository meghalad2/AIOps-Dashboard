import { formatDistanceToNow } from 'date-fns'

const SEVERITY_COLOR = { critical: '#ff5353', warning: '#ffaa3b', info: '#3ca6ff' }
const STATUS_COLOR   = { firing: '#ff5353', resolved: '#52d677', failed: '#e0833a' }

export default function IncidentFeed({ incidents, onSelect, selected }) {
  return (
    <div className="panel incident-feed">
      <div className="panel-header">
        <h2>Active & Historical Incidents</h2>
        <span className="badge-total">{incidents.length} logs</span>
      </div>
      <div className="feed-list">
        {incidents.length === 0 && (
          <div className="empty-state">
            <p className="empty">No incidents reported yet. Trigger a webhook alert to begin.</p>
          </div>
        )}
        {incidents.map(i => {
          const isSelected = selected?.id === i.id;
          return (
            <div
              key={i.id}
              className={`feed-item ${isSelected ? 'active' : ''} ${i.status}`}
              onClick={() => onSelect(i)}
            >
              <div className="feed-item-top">
                <span className="alert-name">{i.alert_name}</span>
                <span className="feed-sev" style={{ color: SEVERITY_COLOR[i.severity] }}>
                  {i.severity}
                </span>
              </div>
              <div className="feed-item-mid">
                <span className="pod-name">{i.pod}</span>
                <span className="ns-badge">{i.namespace}</span>
              </div>
              <div className="feed-item-bot">
                <span className="status-indicator" style={{ backgroundColor: STATUS_COLOR[i.status] }} />
                <span className="status-text" style={{ color: STATUS_COLOR[i.status] }}>
                  {i.status}
                </span>
                {i.mttr_seconds ? (
                  <span className="mttr">MTTR: {Math.round(i.mttr_seconds)}s</span>
                ) : null}
                <span className="time">
                  {formatDistanceToNow(new Date(i.fired_at), { addSuffix: true })}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}
