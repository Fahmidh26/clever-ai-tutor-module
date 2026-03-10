import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003'

function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [experts, setExperts] = useState([])
  const [expertsError, setExpertsError] = useState('')
  const [chatPrompt, setChatPrompt] = useState('Explain Newton second law with a real-world example.')
  const [chatResult, setChatResult] = useState('')
  const [chatError, setChatError] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  const callbackPath = useMemo(() => window.location.pathname, [])

  const loadSession = async () => {
    try {
      setError('')
      const response = await fetch(`${API_BASE_URL}/api/me`, {
        credentials: 'include',
      })

      if (response.status === 401) {
        setSession(null)
        return
      }

      if (!response.ok) {
        throw new Error(`Session check failed (${response.status})`)
      }

      const data = await response.json()
      setSession(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error while loading session')
    } finally {
      setLoading(false)
    }
  }

  const loadExperts = async () => {
    try {
      setExpertsError('')
      const response = await fetch(
        `${API_BASE_URL}/api/main-site/api/experts?domain=expert-chat`,
        { credentials: 'include' }
      )

      if (!response.ok) {
        throw new Error(`Experts request failed (${response.status})`)
      }

      const data = await response.json()
      const list = Array.isArray(data?.experts) ? data.experts : Array.isArray(data) ? data : []
      setExperts(list)
    } catch (err) {
      setExpertsError(err instanceof Error ? err.message : 'Could not fetch experts')
      setExperts([])
    }
  }

  useEffect(() => {
    if (callbackPath === '/auth/callback') {
      window.history.replaceState({}, '', '/')
    }
    loadSession()
  }, [callbackPath])

  useEffect(() => {
    if (session?.access_token) {
      loadExperts()
    }
  }, [session])

  const startLogin = () => {
    window.location.href = `${API_BASE_URL}/oauth/login`
  }

  const logout = async () => {
    await fetch(`${API_BASE_URL}/api/logout`, {
      method: 'POST',
      credentials: 'include',
    })
    setSession(null)
    setExperts([])
    setChatResult('')
    setChatError('')
  }

  const sendDemoChat = async () => {
    if (!chatPrompt.trim()) {
      return
    }
    setChatLoading(true)
    setChatError('')

    try {
      const expertId = experts[0]?.id ?? null
      const response = await fetch(`${API_BASE_URL}/api/main-site/api/expert-chat`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          message: chatPrompt.trim(),
          expert_id: expertId,
          domain: 'expert-chat',
          conversation: [],
        }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data?.message || data?.error || `Chat request failed (${response.status})`)
      }
      setChatResult(data?.response || data?.message || JSON.stringify(data))
    } catch (err) {
      setChatError(err instanceof Error ? err.message : 'Chat request failed')
      setChatResult('')
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>Clever AI Tutor</h1>
          <p>React + FastAPI with shared main-site authentication.</p>
        </div>
        <div className="actions">
          {session ? (
            <button onClick={logout}>Logout</button>
          ) : (
            <button onClick={startLogin}>Login with Main Site</button>
          )}
        </div>
      </header>

      <section className="card">
        <h2>Session</h2>
        {loading ? <p>Loading session...</p> : null}
        {error ? <p className="error">Error: {error}</p> : null}
        {!loading && !session ? <p>Not logged in.</p> : null}
        {session?.user ? (
          <pre>{JSON.stringify({ user: session.user }, null, 2)}</pre>
        ) : null}
      </section>

      <section className="card">
        <h2>Main Site Experts API (via backend proxy)</h2>
        {!session ? <p>Login first to fetch experts.</p> : null}
        {expertsError ? <p className="error">Error: {expertsError}</p> : null}
        {session && !expertsError ? <p>Loaded experts: {experts.length}</p> : null}
        {experts.length > 0 ? (
          <ul>
            {experts.slice(0, 5).map((expert) => (
              <li key={expert.id ?? expert.name}>
                {expert.name || expert.expert_name || 'Unnamed expert'}
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      <section className="card">
        <h2>Demo Expert Chat</h2>
        <textarea
          value={chatPrompt}
          onChange={(event) => setChatPrompt(event.target.value)}
          rows={3}
          placeholder="Ask a question..."
          disabled={!session || chatLoading}
        />
        <button onClick={sendDemoChat} disabled={!session || chatLoading || !chatPrompt.trim()}>
          {chatLoading ? 'Sending...' : 'Send Prompt'}
        </button>
        {chatError ? <p className="error">Error: {chatError}</p> : null}
        {chatResult ? <pre>{chatResult}</pre> : null}
      </section>
    </main>
  )
}

export default App
