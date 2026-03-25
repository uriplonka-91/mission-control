import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'

export default function ProtectedLayout({ children }) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const authenticated = localStorage.getItem('authenticated')
    if (!authenticated && router.pathname !== '/login') {
      router.push('/login')
    } else {
      setIsAuthenticated(!!authenticated)
      setIsLoading(false)
    }
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated && router.pathname !== '/login') {
    return null
  }

  return children
}
