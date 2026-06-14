import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import IncidentFeed from './components/IncidentFeed'
import ReasoningTrace from './components/ReasoningTrace'
import MttrChart from './components/MttrChart'
import ServiceHeatmap from './components/ServiceHeatmap'
import RemediationTrigger from './components/RemediationTrigger'
import { useWebSocket } from './hooks/useWebSocket'
import './App.css'

export default function App() {
  const [incidents, setIncidents] = useState([])
  const [services, setServices] = useState([])
  const [mttrSeries, setMttrSeries] = useState([])
  const [selectedIncident, setSelectedIncident] = useState(null)

  // Load initial data from REST API
  useEffect(() => {
    axios.get('/api/incidents').then(r => {
      setIncidents(r.data)
      if (r.data.length > 0) {
        setSelectedIncident(r.data[0]) // Select the latest incident by default
      }
    })
    axios.get('/api/services').then(r => setServices(r.data))
    axios.get('/api/stats/mttr').then(r => setMttrSeries(r.data))
  }, [])

  // Handle live WebSocket events
  const handleEvent = useCallback((event) => {
    if (event.type === 'incident_fired') {
      const newInc = {
        id: event.incident_id,
        alert_name: event.alert_name,
        severity: event.severity,
        namespace: event.namespace,
        pod: event.pod,
        service: event.service,
        status: 'firing',
        fired_at: event.fired_at,
      }
      setIncidents(prev => [newInc, ...prev])
      setSelectedIncident(newInc)
    }

    if (event.type === 'llm_reasoning') {
      setIncidents(prev =>
        prev.map(i =>
          i.id === event.incident_id
            ? { ...i, llm_output: event.llm_output, remediation_command: event.remediation_command }
            : i
        )
      )
      setSelectedIncident(prev => 
        prev && prev.id === event.incident_id
          ? { ...prev, llm_output: event.llm_output, remediation_command: event.remediation_command }
          : prev
      )
    }

    if (event.type === 'remediation_result') {
      const updatedStatus = event.result === 'success' ? 'resolved' : 'failed'
      setIncidents(prev =>
        prev.map(i =>
          i.id === event.incident_id
            ? { ...i, status: updatedStatus, resolved_at: event.resolved_at, remediation_result: event.result }
            : i
        )
      )
      setSelectedIncident(prev =>
        prev && prev.id === event.incident_id
          ? { ...prev, status: updatedStatus, resolved_at: event.resolved_at, remediation_result: event.result }
          : prev
      )
      // Refresh MTTR series and services after a resolution
      axios.get('/api/stats/mttr').then(r => setMttrSeries(r.data))
      axios.get('/api/services').then(r => setServices(r.data))
    }

    if (event.type === 'service_health_updated') {
      setServices(prev =>
        prev.map(s =>
          s.service === event.service
            ? { ...s, health_score: event.health_score,
                incident_count_7d: event.incident_count_7d,
                last_remediation_result: event.last_result }
            : s
        )
      )
    }
  }, [])

  // Use relative ws path based on current host via proxy config
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
  const connected = useWebSocket(wsUrl, handleEvent)

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <div className="pulsing-logo"></div>
          <h1>AEGIS AIOps Control Plane</h1>
        </div>
        <div className="header-right">
          <span className={`ws-status ${connected ? 'connected' : 'disconnected'}`}>
            <span className="dot"></span>
            {connected ? 'LIVE CONNECTION' : 'RECONNECTING…'}
          </span>
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="grid-top">
          <ServiceHeatmap services={services} />
          <MttrChart data={mttrSeries} />
        </div>

        <div className="grid-bottom">
          <div className="left-panel">
            <IncidentFeed
              incidents={incidents}
              onSelect={setSelectedIncident}
              selected={selectedIncident}
            />
          </div>
          <div className="right-panel">
            <ReasoningTrace incident={selectedIncident} />
            <RemediationTrigger services={services} />
          </div>
        </div>
      </div>
    </div>
  )
}
