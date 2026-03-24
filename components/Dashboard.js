export default function Dashboard({ tasks = [], projects = [] }) {
  const completedCount = tasks.filter((t) => t.completed).length
  const pendingCount = tasks.filter((t) => !t.completed).length
  const totalCount = tasks.length
  const activeProjects = projects.filter((p) => p.status !== 'Deployed').length
  const deployedProjects = projects.filter((p) => p.status === 'Deployed').length

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Tasks Card */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-400 text-sm font-medium">Total Tasks</h3>
          <p className="text-4xl font-bold text-white mt-2">{totalCount}</p>
          <p className="text-slate-500 text-xs mt-2">Across all statuses</p>
        </div>

        {/* Pending Tasks Card */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-400 text-sm font-medium">Pending</h3>
          <p className="text-4xl font-bold text-yellow-400 mt-2">{pendingCount}</p>
          <p className="text-slate-500 text-xs mt-2">Need attention</p>
        </div>

        {/* Completed Tasks Card */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-400 text-sm font-medium">Completed</h3>
          <p className="text-4xl font-bold text-green-400 mt-2">{completedCount}</p>
          <p className="text-slate-500 text-xs mt-2">Tasks finished</p>
        </div>
      </div>

      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-white mb-2">Welcome, Uri</h2>
        <p className="text-blue-100">
          You're all set. Navigate to Tasks or Projects to start managing your work.
        </p>
      </div>

      {/* Projects Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-sm font-medium text-slate-400">Active Projects</h3>
          <p className="text-4xl font-bold text-blue-400 mt-2">{activeProjects}</p>
          <p className="text-slate-500 text-xs mt-2">In progress or under review</p>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-sm font-medium text-slate-400">Deployed</h3>
          <p className="text-4xl font-bold text-green-400 mt-2">{deployedProjects}</p>
          <p className="text-slate-500 text-xs mt-2">Projects live</p>
        </div>
      </div>

      {/* Recent Activity */}
      {tasks.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Tasks</h3>
          <div className="space-y-3">
            {tasks.slice(-5).reverse().map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between p-3 bg-slate-700 rounded"
              >
                <span className={task.completed ? 'line-through text-slate-500' : 'text-white'}>
                  {task.title}
                </span>
                <span className={`text-xs px-2 py-1 rounded ${
                  task.completed
                    ? 'bg-green-900 text-green-300'
                    : 'bg-yellow-900 text-yellow-300'
                }`}>
                  {task.completed ? 'Done' : 'Pending'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Projects Preview */}
      {projects.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Active Projects</h3>
          <div className="space-y-3">
            {projects
              .filter((p) => p.status !== 'Deployed')
              .slice(-3)
              .reverse()
              .map((project) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-3 bg-slate-700 rounded"
                >
                  <div>
                    <p className="text-white font-medium">{project.name}</p>
                    <p className="text-slate-400 text-xs">{project.status}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    project.priority === 'High'
                      ? 'bg-red-900 text-red-300'
                      : project.priority === 'Medium'
                      ? 'bg-yellow-900 text-yellow-300'
                      : 'bg-green-900 text-green-300'
                  }`}>
                    {project.priority}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
