export default function ReasoningTrace({ incident }) {
  if (!incident) return (
    <div className="panel reasoning-trace empty-state-panel">
      <h2>AI Reasoning Trace</h2>
      <div className="empty-prompt">
        <div className="glow-icon">🤖</div>
        <p>Select an incident from the feed to view the AI SRE agent's diagnostic pipeline, root cause analysis, and chosen remediation path.</p>
      </div>
    </div>
  )

  return (
    <div className="panel reasoning-trace">
      <h2>AI Reasoning Trace</h2>
      
      <div className="trace-section">
        <label>Selected Target</label>
        <div className="target-summary">
          <span className="summary-val font-code">{incident.pod}</span>
          <span className="summary-sep">·</span>
          <span className="summary-val">{incident.namespace}</span>
        </div>
      </div>

      {incident.llm_output ? (
        <>
          <div className="trace-section">
            <label>AI Diagnostic Analysis</label>
            <pre className="trace-pre scrollbar-styled">{incident.llm_output}</pre>
          </div>
          <div className="trace-section">
            <label>Suggested Remediation</label>
            <code className="trace-cmd">{incident.remediation_command}</code>
          </div>
          <div className="trace-section">
            <label>Auto-Healing Action Outcome</label>
            <div className={`outcome-container ${incident.remediation_result || 'pending'}`}>
              <span className={`outcome-badge ${incident.remediation_result}`}>
                {incident.remediation_result ? incident.remediation_result.toUpperCase() : 'PENDING ANALYSIS'}
              </span>
            </div>
          </div>
        </>
      ) : (
        <div className="trace-section pending-flow">
          <div className="spinner-loader"></div>
          <p className="pending-text">Waiting for the AI reasoning agent to execute diagnosis...</p>
        </div>
      )}
    </div>
  )
}
