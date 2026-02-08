import { Task, Priority } from "@/types";

interface TaskItemProps {
  task: Task;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

const priorityColors: Record<Priority, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-green-100 text-green-700 border-green-200",
};

const priorityLabels: Record<Priority, string> = {
  high: "High",
  medium: "Med",
  low: "Low",
};

function formatDueDate(dateStr: string | null): string | null {
  if (!dateStr) return null;

  const due = new Date(dateStr);
  const now = new Date();
  const diffMs = due.getTime() - now.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? "s" : ""}`;
  } else if (diffDays === 0) {
    return "Due today";
  } else if (diffDays === 1) {
    return "Due tomorrow";
  } else if (diffDays <= 7) {
    return `Due in ${diffDays} days`;
  } else {
    return `Due ${due.toLocaleDateString()}`;
  }
}

function getDueDateColor(dateStr: string | null): string {
  if (!dateStr) return "text-gray-500";

  const due = new Date(dateStr);
  const now = new Date();
  const diffMs = due.getTime() - now.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return "text-red-600";
  if (diffDays === 0) return "text-orange-600";
  if (diffDays <= 2) return "text-yellow-600";
  return "text-gray-500";
}

export function TaskItem({ task, onToggle, onEdit, onDelete }: TaskItemProps) {
  const dueDateText = formatDueDate(task.due_date);
  const dueDateColor = getDueDateColor(task.due_date);

  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-start gap-3">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={onToggle}
        className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        aria-label={`Mark "${task.title}" as ${
          task.completed ? "incomplete" : "complete"
        }`}
      />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3
            className={`font-medium ${
              task.completed ? "text-gray-400 line-through" : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>

          {/* Priority badge */}
          <span
            className={`text-xs px-2 py-0.5 rounded border ${priorityColors[task.priority]}`}
          >
            {priorityLabels[task.priority]}
          </span>

          {/* Recurring indicator */}
          {task.recurring && (
            <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700 border border-purple-200">
              {task.recurring}
            </span>
          )}
        </div>

        {task.description && (
          <p className="text-sm text-gray-500 mt-1 truncate">
            {task.description}
          </p>
        )}

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="flex gap-1 mt-2 flex-wrap">
            {task.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Due date and created date */}
        <div className="flex gap-3 mt-2 text-xs">
          {dueDateText && (
            <span className={dueDateColor}>{dueDateText}</span>
          )}
          <span className="text-gray-400">
            Created {new Date(task.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onEdit}
          className="text-gray-400 hover:text-gray-600"
          aria-label={`Edit task: ${task.title}`}
        >
          Edit
        </button>
        <button
          onClick={onDelete}
          className="text-red-400 hover:text-red-600"
          aria-label={`Delete task: ${task.title}`}
        >
          Delete
        </button>
      </div>
    </div>
  );
}
