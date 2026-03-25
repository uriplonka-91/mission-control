import { useState } from 'react'
import { useRouter } from 'next/router'

export default function Login() {
  const router = useRouter()
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleLogin = (e) => {
    e.preventDefault()
    // Simple password check - in production, use proper auth
    if (password === 'mission2024') {
      localStorage.setItem('authenticated', 'true')
      router.push('/')
    } else {
      setError('Incorrect password')
      setPassword('')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8">
          <h1 className="text-3xl font-bold text-white mb-2">Mission Control</h1>
          <p className="text-slate-400 mb-6">Secure Access</p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  setError('')
                }}
                placeholder="Enter password"
                className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
                autoFocus
              />
            </div>

            {error && (
              <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded transition"
            >
              Sign In
            </button>
          </form>

          <p className="text-slate-500 text-xs text-center mt-6">
            Default password: mission2024 (change in settings)
          </p>
        </div>
      </div>
    </div>
  )
}
