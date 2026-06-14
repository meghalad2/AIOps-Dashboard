import { useState } from 'react'
import axios from 'axios'

export default function RemediationTrigger({ services }) {
  const [deployment, setDeployment] = useState('')
  const [namespace, setNamespace] = useState('production')
  const [action, setAction] = useState('restart')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFire = async () => {
    if (!deployment) return
    setLoading(true)
    setResult(null)
    try {
      const r = await axios.post('/api/remediate', { action, deployment, namespace })
      setResult(r.data)
    } catch (e) {
      setResult({ status: 'failure', error: e.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel remediation-trigger">
      <h2>Manual Remediation Override</h2>
      <div className="trigger-form">
        <div className="form-group">
          <input
            type="text"
            className="input-styled"
            placeholder="Deployment name (e.g. payment-service)"
            value={deployment}
            onChange={e => setDeployment(e.target.value)}
          />
        </div>
        <div className="form-row">
          <select className="select-styled" value={namespace} onChange={e => setNamespace(e.target.value)}>
            <option>production</option>
            <option>staging</option>
          </select>
          <select className="select-styled" value={action} onChange={e => setAction(e.target.value)}>
            <option value="restart">Restart</option>
            <option value="scale">Scale</option>
            <option value="rollback">Rollback</option>
          </select>
        </div>
        <button 
          className="btn-trigger" 
          onClick={handleFire} 
          disabled={loading || !deployment}
        >
          {loading ? (
            <div className="btn-content">
              <span className="spinner-mini"></span> Executing Command...
            </div>
          ) : 'Run Manual Override'}
        </button>
      </div>
      {result && (
        <div className={`trigger-result ${result.status}`}>
          <div className="result-header">
            <span className="status-title">
              {result.status === 'success' ? 'Command Executed Successfully' : 'Command Execution Failed'}
            </span>
          </div>
          {result.stdout && <pre className="console-log">{result.stdout}</pre>}
          {result.error && <pre className="console-log error">{result.error}</pre>}
        </div>
      )}
    </div>
  )
}
