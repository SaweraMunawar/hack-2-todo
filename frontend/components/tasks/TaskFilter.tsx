"use client";

import { Priority, TaskFilterParams } from "@/types";

interface TaskFilterProps {
  filters: TaskFilterParams;
  onFilterChange: (filters: Partial<TaskFilterParams>) => void;
}

const statusOptions = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
] as const;

const priorityOptions = [
  { value: "", label: "Any Priority" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
] as const;

const sortOptions = [
  { value: "", label: "Newest First" },
  { value: "due_date", label: "Due Date" },
  { value: "priority", label: "Priority" },
  { value: "title", label: "Title" },
] as const;

export function TaskFilter({ filters, onFilterChange }: TaskFilterProps) {
  return (
    <div className="space-y-3 mb-4">
      {/* Status filter buttons */}
      <div className="flex gap-2">
        {statusOptions.map((s) => (
          <button
            key={s.value}
            onClick={() => onFilterChange({ status: s.value })}
            className={`px-3 py-1 rounded text-sm ${
              (filters.status || "all") === s.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Advanced filters row */}
      <div className="flex flex-wrap gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search tasks..."
            value={filters.search || ""}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            className="w-full px-3 py-1.5 text-sm rounded border border-gray-300 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Priority filter */}
        <select
          value={filters.priority || ""}
          onChange={(e) =>
            onFilterChange({
              priority: (e.target.value as Priority) || undefined,
            })
          }
          className="px-3 py-1.5 text-sm rounded border border-gray-300 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {priorityOptions.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>

        {/* Sort */}
        <select
          value={filters.sort || ""}
          onChange={(e) =>
            onFilterChange({
              sort: (e.target.value as TaskFilterParams["sort"]) || undefined,
            })
          }
          className="px-3 py-1.5 text-sm rounded border border-gray-300 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {sortOptions.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        {/* Tags input */}
        <input
          type="text"
          placeholder="Filter by tags..."
          value={filters.tags || ""}
          onChange={(e) => onFilterChange({ tags: e.target.value })}
          className="px-3 py-1.5 text-sm rounded border border-gray-300 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 min-w-[150px]"
        />
      </div>
    </div>
  );
}
