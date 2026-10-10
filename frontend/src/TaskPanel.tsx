export type Task = {
  id: number
  title: string
  status: "todo" | "in_progress" | "done"
}

const STATUS_ICON = { todo: "☐", in_progress: "⏳", done: "☑" }

type TaskPanelProps = {
  tasks: Task[]
}

export function TaskPanel({ tasks }: TaskPanelProps) {
  return (
    <aside className="tasks">
      <h2>Tasks</h2>
      {tasks.length === 0 ? (
        <p>No tasks yet.</p>
      ) : (
        <ul>
          {tasks.map((task) => (
            <li key={task.id} className={task.status}>
              {STATUS_ICON[task.status]} {task.title}             
            </li>
          ))}
        </ul>
      )}
    </aside>
  )
}