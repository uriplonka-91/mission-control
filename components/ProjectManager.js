import { useState } from 'react'

const STATUSES = ['Not Started', 'In Progress', 'Review', 'Deployed']
const PRIORITIES = ['Low', 'Medium', 'High']

export default function ProjectManager({ projects, onAddProject, onUpdateProject, onDeleteProject }) {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'Not Started',
    priority: 'Medium',
    onedrive_link: '',
  })
  const [editingId, setEditingId] = useState(null)
  const [filter, setFilter] = useState('all')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (editingId) {
      onUpdateProject(editingId, formData)
      setEditingId(null)
    } else {
      onAddProject(formData)
    }
    setFormData({
      name: '',
      description: '',
      status: 'Not Started',
      priority: 'Medium',
      onedrive_link: '',
    })
    setShowForm(false)
  }

  const handleEdit = (project) => {
    setFormData({
      name: project.name,
      description: project.description,
      status: project.status,
      priority: project.priority,
      onedrive_link: project.onedrive_link,
    })
    setEditingId(project.id)
    setShowForm(true)
  }

  const filteredProjects = projects.filter((p) => {
    if (filter === 'active') return p.status !== 'Deployed'
    if (filter === 'deployed') return p.status === 'Deployed'
    return true
  })

  const getPriorityColor = (priority) => {
    if (priority === 'High') return 'bg-red-900 text-red-300'
    if (priority === 'Medium') return 'bg-yellow-900 text-yellow-300'
    return 'bg-green-900 text-green-300'
  }

  const getStatusColor = (status) => {
    if (status === 'Deployed') return 'bg-green-600'
    if (status === 'Review') return 'bg-blue-600'
    if (status === 'In Progress') return 'bg-yellow-600'
    return 'bg-gray-600'
  }

  return (
    <div className="space-y-6">
      {/* Add/Edit Project Form */}
      {showForm && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4">
            {editingId ? 'Edit Project' : 'New Project'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Project Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Scheduling Process Optimization"
                required
                className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="What is this project about?"
                className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500 h-24"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Priority
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                OneDrive Link (Optional)
              </label>
              <input
                type="url"
                value={formData.onedrive_link}
                onChange={(e) => setFormData({ ...formData, onedrive_link: e.target.value })}
                placeholder="https://..."
                className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition"
              >
                {editingId ? 'Update' : 'Create'} Project
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setEditingId(null)
                  setFormData({
                    name: '',
                    description: '',
                    status: 'Not Started',
                    priority: 'Medium',
                    onedrive_link: '',
                  })
                }}
                className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-2 rounded font-medium transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* New Project Button */}
      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition"
        >
          + New Project
        </button>
      )}

      {/* Filter Buttons */}
      <div className="flex gap-2">
        {['all', 'active', 'deployed'].map((f) => (
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

      {/* Projects List */}
      <div className="space-y-4">
        {filteredProjects.length === 0 ? (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
            <p className="text-slate-400">
              No {filter !== 'all' ? filter : ''} projects yet. Create one to get started!
            </p>
          </div>
        ) : (
          filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="text-xl font-bold text-white">{project.name}</h3>
                  <p className="text-slate-400 text-sm mt-1">{project.description}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(project)}
                    className="text-blue-400 hover:text-blue-300 text-sm font-medium transition"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDeleteProject(project.id)}
                    className="text-red-400 hover:text-red-300 text-sm font-medium transition"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-3 py-1 rounded text-sm font-medium text-white ${getStatusColor(project.status)}`}>
                  {project.status}
                </span>
                <span className={`px-3 py-1 rounded text-sm font-medium ${getPriorityColor(project.priority)}`}>
                  {project.priority} Priority
                </span>
                {project.onedrive_link && (
                  <a
                    href={project.onedrive_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm font-medium transition"
                  >
                    📄 View Document
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
