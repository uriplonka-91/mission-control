import { useState, useEffect } from 'react'
import TaskManager from '../components/TaskManager'
import Dashboard from '../components/Dashboard'

export default function Home() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    // Load tasks from localStorage
    const saved = localStorage.getItem('tasks')
    if (saved) setTasks(JSON.parse(saved))
  }, [])

  const saveTasks = (newTasks) => {
    setTasks(newTasks)
    localStorage.setItem('tasks', JSON.stringify(newTasks))
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

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-white">Mission Control</h1>
          <p className="text-slate-400">Your command center</p>
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
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {currentPage === 'dashboard' && <Dashboard tasks={tasks} />}
        {currentPage === 'tasks' && (
          <TaskManager
            tasks={tasks}
            onAddTask={addTask}
            onToggleTask={toggleTask}
            onDeleteTask={deleteTask}
          />
        )}
      </main>
    </div>
  )
}
