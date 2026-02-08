"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { getTasks, toggleTask, deleteTask } from "@/lib/api";
import { Task, TaskFilterParams } from "@/types";
import { TaskItem } from "./TaskItem";
import { TaskForm } from "./TaskForm";
import { TaskFilter } from "./TaskFilter";

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [completedCount, setCompletedCount] = useState(0);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TaskFilterParams>({
    status: "all",
  });
  const [isCreating, setIsCreating] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Debounce search to avoid too many API calls
  const [debouncedSearch, setDebouncedSearch] = useState(filters.search);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(filters.search);
    }, 300);
    return () => clearTimeout(timer);
  }, [filters.search]);

  const apiFilters = useMemo(
    () => ({
      ...filters,
      search: debouncedSearch,
    }),
    [filters, debouncedSearch]
  );

  const loadTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await getTasks(apiFilters);
      setTasks(response.tasks);
      setTotal(response.total);
      setPendingCount(response.pending_count);
      setCompletedCount(response.completed_count);
    } catch {
      setError("Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  }, [apiFilters]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleFilterChange = (newFilters: Partial<TaskFilterParams>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleToggle = async (id: string) => {
    try {
      const updated = await toggleTask(id);
      setTasks(tasks.map((t) => (t.id === id ? updated : t)));
      // Reload to get accurate counts
      loadTasks();
    } catch {
      setError("Failed to update task");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
      await deleteTask(id);
      setTasks(tasks.filter((t) => t.id !== id));
      // Reload to get accurate counts
      loadTasks();
    } catch {
      setError("Failed to delete task");
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
          <p className="text-sm text-gray-500 mt-1">
            {total} total &bull; {pendingCount} pending &bull; {completedCount}{" "}
            completed
          </p>
        </div>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Task
        </button>
      </div>

      <TaskFilter filters={filters} onFilterChange={handleFilterChange} />

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-800 hover:text-red-900"
          >
            Dismiss
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {filters.search || filters.priority || filters.tags
            ? "No tasks match your filters."
            : "No tasks yet. Add one to get started!"}
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={() => handleToggle(task.id)}
              onEdit={() => setEditingTask(task)}
              onDelete={() => handleDelete(task.id)}
            />
          ))}
        </div>
      )}

      {(isCreating || editingTask) && (
        <TaskForm
          task={editingTask}
          onClose={() => {
            setIsCreating(false);
            setEditingTask(null);
          }}
          onSaved={loadTasks}
        />
      )}
    </div>
  );
}
