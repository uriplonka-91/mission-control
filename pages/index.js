import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import TaskManager from '../components/TaskManager'
import ProjectManager from '../components/ProjectManager'
import AgentManager from '../components/AgentManager'
import Dashboard from '../components/Dashboard'
import EmailManager from '../components/EmailManager'
import CalendarManager from '../components/CalendarManager'

export default function Home() {
  const router = useRouter()
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [tasks, setTasks] = useState([])
  const [projects, setProjects] = useState([])
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const authenticated = localStorage.getItem('authenticated')
    if (!authenticated) {
      router.push('/login')
    } else {
      setIsAuthenticated(true)
    }
  }, [router])

  useEffect(() => {
    // Load tasks from localStorage
    const savedTasks = localStorage.getItem('tasks')
    if (savedTasks) setTasks(JSON.parse(savedTasks))
    
    // Load projects from localStorage
    const savedProjects = localStorage.getItem('projects')
    if (savedProjects) setProjects(JSON.parse(savedProjects))
  }, [])

  const saveTasks = (newTasks) => {
    setTasks(newTasks)
    localStorage.setItem('tasks', JSON.stringify(newTasks))
  }

  const saveProjects = (newProjects) => {
    setProjects(newProjects)
    localStorage.setItem('projects', JSON.stringify(newProjects))
  }

  const addTask = (title) => {
    const newTask = {
      id: Date.now(),
      title,
      completed: false,
      createdAt: new Date().toISOString(),
    }
    saveTasks([...tasks, newTask])
  }

  const toggleTask = (id) => {
    saveTasks(
      tasks.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const deleteTask = (id) => {
    saveTasks(tasks.filter((t) => t.id !== id))
  }

  const addProject = (data) => {
    const newProject = {
      id: Date.now(),
      ...data,
      createdAt: new Date().toISOString(),
    }
    saveProjects([...projects, newProject])
  }

  const updateProject = (id, data) => {
    saveProjects(
      projects.map((p) => (p.id === id ? { ...p, ...data } : p))
    )
  }

  const deleteProject = (id) => {
    saveProjects(projects.filter((p) => p.id !== id))
  }

  const handleLogout = () => {
    localStorage.removeItem('authenticated')
    router.push('/login')
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">Mission Control</h1>
            <p className="text-slate-400">Your command center</p>
          </div>
          <button
            onClick={handleLogout}
            className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded font-medium transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-6">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={`py-4 px-2 border-b-2 font-medium transition ${
                currentPage === 'dashboard'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentPage('tasks')}
              className={`py-4 px-2 border-b-2 font-medium transition ${
                currentPage === 'tasks'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Tasks
            </button>
            <button
              onClick={() => setCurrentPage('projects')}
              className={`py-4 px-2 border-b-2 font-medium transition ${
                currentPage === 'projects'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Projects
            </button>
            <button
              onClick={() => setCurrentPage('agents')}
              className={`py-4 px-2 border-b-2 font-medium transition ${
                currentPage === 'agents'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Agents
            </button>
            <button
              onClick={() => setCurrentPage('email')}
              className={`py-4 px-2 border-b-2 font-medium transition ${
                currentPage === 'email'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Email
            </button>
            <button
              onClick={() => setCurrentPage('calendar')}
              className={`py-4 px-2 border-b-2 font-medium transition ${
                currentPage === 'calendar'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Calendar
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {currentPage === 'dashboard' && <Dashboard tasks={tasks} projects={projects} />}
        {currentPage === 'tasks' && (
          <TaskManager
            tasks={tasks}
            onAddTask={addTask}
            onToggleTask={toggleTask}
            onDeleteTask={deleteTask}
          />
        )}
        {currentPage === 'projects' && (
          <ProjectManager
            projects={projects}
            onAddProject={addProject}
            onUpdateProject={updateProject}
            onDeleteProject={deleteProject}
          />
        )}
        {currentPage === 'agents' && <AgentManager />}
        {currentPage === 'email' && <EmailManager />}
        {currentPage === 'calendar' && <CalendarManager />}
      </main>
    </div>
  )
}
