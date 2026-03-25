import { useState } from 'react'

const DEFAULT_AGENTS = [
  {
    id: 1,
    name: 'Henry',
    role: 'Chief of Staff',
    specialization: 'Operations, Systems, Processes',
    status: 'Active',
    model: 'Haiku',
    createdAt: '2026-03-20',
  },
]

export default function AgentManager() {
  const [agents, setAgents] = useState(DEFAULT_AGENTS)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    specialization: '',
    status: 'Active',
    model: 'Haiku',
  })
  const [editingId, setEditingId] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (editingId) {
      setAgents(
        agents.map((a) =>
          a.id === editingId ? { ...a, ...formData } : a
        )
      )
      setEditingId(null)
    } else {
      const newAgent = {
        id: Date.now(),
        ...formData,
        createdAt: new Date().toISOString().split('T')[0],
      }
      setAgents([...agents, newAgent])
    }
    setFormData({
      name: '',
      role: '',
      specialization: '',
      status: 'Active',
      model: 'Haiku',
    })
    setShowForm(false)
  }

  const handleEdit = (agent) => {
    setFormData({
      name: agent.name,
      role: agent.role,
      specialization: agent.specialization,
      status: agent.status,
      model: agent.model,
    })
    setEditingId(agent.id)
    setShowForm(true)
  }

  const handleDelete = (id) => {
    if (id !== 1) { // Don't allow deleting Henry
      setAgents(agents.filter((a) => a.id !== id))
    }
  }

  const getStatusColor = (status) => {
    return status === 'Active' ? 'bg-green-900 text-green-300' : 'bg-gray-900 text-gray-300'
  }

  const getModelColor = (model) => {
    return model === 'Sonnet' ? 'bg-blue-900 text-blue-300' : 'bg-purple-900 text-purple-300'
  }

  return (
    <div className="space-y-6">
      {/* Add Agent Form */}
      {showForm && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4">
            {editingId ? 'Edit Agent' : 'Add New Agent'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Agent Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Alex"
                  required
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Role
                </label>
                <input
                  type="text"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  placeholder="e.g., Recruiting Agent"
                  required
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Specialization
              </label>
              <input
                type="text"
                value={formData.specialization}
                onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                placeholder="e.g., Hiring, Onboarding, Candidate Tracking"
                className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
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
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Model
                </label>
                <select
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:outline-none focus:border-blue-500"
                >
                  <option value="Haiku">Haiku (Faster, Cheaper)</option>
                  <option value="Sonnet">Sonnet (Smarter, Slower)</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition"
              >
                {editingId ? 'Update' : 'Add'} Agent
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setEditingId(null)
                  setFormData({
                    name: '',
                    role: '',
                    specialization: '',
                    status: 'Active',
                    model: 'Haiku',
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

      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition"
        >
          + Add Agent
        </button>
      )}

      {/* Agents List */}
      <div className="space-y-4">
        <div className="text-slate-400 text-sm">
          {agents.length} agent{agents.length !== 1 ? 's' : ''} in your team
        </div>
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition"
          >
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="text-xl font-bold text-white">{agent.name}</h3>
                <p className="text-slate-400 text-sm mt-1">{agent.role}</p>
                <p className="text-slate-500 text-xs mt-2">{agent.specialization}</p>
              </div>
              {agent.id !== 1 && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(agent)}
                    className="text-blue-400 hover:text-blue-300 text-sm font-medium transition"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(agent.id)}
                    className="text-red-400 hover:text-red-300 text-sm font-medium transition"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(agent.status)}`}>
                {agent.status}
              </span>
              <span className={`px-3 py-1 rounded text-sm font-medium ${getModelColor(agent.model)}`}>
                {agent.model}
              </span>
              <span className="text-slate-500 text-xs">
                Added: {agent.createdAt}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
