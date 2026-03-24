import { useState } from 'react'

export default function TaskManager({ tasks, onAddTask, onToggleTask, onDeleteTask }) {
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [filter, setFilter] = useState('all')

  const handleAddTask = (e) => {
    e.preventDefault()
    if (newTaskTitle.trim()) {
      onAddTask(newTaskTitle)
      setNewTaskTitle('')
    }
  }

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'completed') return task.completed
    if (filter === 'pending') return !task.completed
    return true
  })

  return (
    <div className="space-y-6">
      {/* Add Task Form */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-4">Add New Task</h2>
        <form onSubmit={handleAddTask} className="flex gap-2">
          <input
            type="text"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            placeholder="Enter task title..."
            className="flex-1 bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition"
          >
            Add Task
          </button>
        </form>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2">
        {['all', 'pending', 'completed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded font-medium transition capitalize ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:text-slate-300 border border-slate-700'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">
          {filter === 'all' && 'All Tasks'}
          {filter === 'pending' && 'Pending Tasks'}
          {filter === 'completed' && 'Completed Tasks'}
        </h2>

        {filteredTasks.length === 0 ? (
          <p className="text-slate-400 text-center py-8">
            No {filter !== 'all' ? filter : ''} tasks yet. Create one to get started!
          </p>
        ) : (
          <div className="space-y-2">
            {filteredTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between p-4 bg-slate-700 rounded hover:bg-slate-600 transition"
              >
                <div className="flex items-center gap-3 flex-1">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => onToggleTask(task.id)}
                    className="w-5 h-5 accent-blue-600 cursor-pointer"
                  />
                  <span
                    className={`${
                      task.completed
                        ? 'line-through text-slate-500'
                        : 'text-white'
                    }`}
                  >
                    {task.title}
                  </span>
                </div>
                <button
                  onClick={() => onDeleteTask(task.id)}
                  className="text-red-400 hover:text-red-300 text-sm font-medium transition"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
