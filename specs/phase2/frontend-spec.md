# Phase II Frontend Specification

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.0.0
- **Framework**: Next.js 14+ (App Router) + Better Auth

---

## 1. Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Next.js 14+ |
| Router | App Router |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Authentication | Better Auth + JWT plugin |
| State | React Context + useState |
| HTTP | fetch API |
| Package Manager | pnpm |

---

## 2. Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Home → redirect
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts    # Better Auth handler
│   │   ├── login/
│   │   │   └── page.tsx            # Login page
│   │   ├── register/
│   │   │   └── page.tsx            # Registration page
│   │   └── tasks/
│   │       └── page.tsx            # Task list (protected)
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskFilter.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Container.tsx
│   ├── lib/
│   │   ├── auth.ts                 # Better Auth server config
│   │   ├── auth-client.ts          # Better Auth client
│   │   └── api.ts                  # Task API client
│   └── types/
│       └── index.ts                # TypeScript types
├── public/
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

---

## 3. Better Auth Setup

### 3.1 Server Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },

  plugins: [
    jwt({
      jwks: {
        keyPairConfig: {
          alg: "RS256",
        },
      },
    }),
  ],
});

export type Session = typeof auth.$Infer.Session;
```

### 3.2 API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### 3.3 Client Configuration

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [jwtClient()],
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

---

## 4. Routes

### 4.1 Route Configuration

| Route | Component | Auth Required | Description |
|-------|-----------|---------------|-------------|
| `/` | Home | No | Redirect to /tasks or /login |
| `/login` | LoginPage | No (redirect if auth) | User login |
| `/register` | RegisterPage | No (redirect if auth) | User registration |
| `/tasks` | TasksPage | Yes | Task management |

### 4.2 Home Page Redirect

```typescript
// app/page.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function HomePage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (session) {
    redirect("/tasks");
  } else {
    redirect("/login");
  }
}
```

### 4.3 Protected Route Pattern

```typescript
// app/tasks/page.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { TaskList } from "@/components/tasks/TaskList";

export default async function TasksPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return <TaskList />;
}
```

---

## 5. Components

### 5.1 Layout Components

#### Root Layout

```typescript
// app/layout.tsx
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
      </body>
    </html>
  );
}
```

#### Header

```typescript
// components/layout/Header.tsx
"use client";

import { useSession, signOut } from "@/lib/auth-client";
import Link from "next/link";

export function Header() {
  const { data: session, isPending } = useSession();

  return (
    <header className="bg-white shadow">
      <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-gray-900">
          Todo App
        </Link>

        <div className="flex items-center gap-4">
          {isPending ? (
            <span className="text-gray-500">Loading...</span>
          ) : session ? (
            <>
              <span className="text-gray-600">{session.user.email}</span>
              <button
                onClick={() => signOut()}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
```

### 5.2 Auth Components

#### LoginForm

```typescript
// components/auth/LoginForm.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signIn } from "@/lib/auth-client";
import Link from "next/link";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await signIn.email({
        email,
        password,
      });

      if (result.error) {
        setError(result.error.message || "Invalid email or password");
      } else {
        router.push("/tasks");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded">{error}</div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? "Signing in..." : "Sign In"}
      </button>

      <p className="text-center text-sm text-gray-600">
        Don't have an account?{" "}
        <Link href="/register" className="text-blue-600 hover:underline">
          Register
        </Link>
      </p>
    </form>
  );
}
```

#### RegisterForm

```typescript
// components/auth/RegisterForm.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signUp } from "@/lib/auth-client";
import Link from "next/link";

export function RegisterForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setIsLoading(true);

    try {
      const result = await signUp.email({
        email,
        password,
        name,
      });

      if (result.error) {
        setError(result.error.message || "Registration failed");
      } else {
        router.push("/tasks");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded">{error}</div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Name
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? "Creating account..." : "Create Account"}
      </button>

      <p className="text-center text-sm text-gray-600">
        Already have an account?{" "}
        <Link href="/login" className="text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
```

### 5.3 Task Components

#### TaskList

```typescript
// components/tasks/TaskList.tsx
"use client";

import { useState, useEffect } from "react";
import { getTasks, toggleTask, deleteTask } from "@/lib/api";
import { Task } from "@/types";
import { TaskItem } from "./TaskItem";
import { TaskForm } from "./TaskForm";
import { TaskFilter } from "./TaskFilter";

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [isCreating, setIsCreating] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const completed = filter === "all" ? undefined : filter === "completed";
      const response = await getTasks({ completed });
      setTasks(response.tasks);
    } catch (err) {
      setError("Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const handleToggle = async (id: string) => {
    try {
      const updated = await toggleTask(id);
      setTasks(tasks.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      setError("Failed to update task");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
      await deleteTask(id);
      setTasks(tasks.filter((t) => t.id !== id));
    } catch (err) {
      setError("Failed to delete task");
    }
  };

  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Task
        </button>
      </div>

      <TaskFilter filter={filter} onFilterChange={setFilter} />

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
      )}

      {isLoading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No tasks yet. Add one to get started!
        </div>
      ) : (
        <>
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

          <div className="mt-4 text-sm text-gray-500">
            {tasks.length} tasks, {completedCount} completed
          </div>
        </>
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
```

#### TaskItem

```typescript
// components/tasks/TaskItem.tsx
import { Task } from "@/types";

interface TaskItemProps {
  task: Task;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

export function TaskItem({ task, onToggle, onEdit, onDelete }: TaskItemProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-start gap-3">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={onToggle}
        className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        aria-label={`Mark "${task.title}" as ${task.completed ? "incomplete" : "complete"}`}
      />

      <div className="flex-1 min-w-0">
        <h3
          className={`font-medium ${
            task.completed ? "text-gray-400 line-through" : "text-gray-900"
          }`}
        >
          {task.title}
        </h3>
        {task.description && (
          <p className="text-sm text-gray-500 mt-1 truncate">
            {task.description}
          </p>
        )}
        <p className="text-xs text-gray-400 mt-1">
          {new Date(task.created_at).toLocaleDateString()}
        </p>
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
```

#### TaskForm

```typescript
// components/tasks/TaskForm.tsx
"use client";

import { useState } from "react";
import { createTask, updateTask } from "@/lib/api";
import { Task } from "@/types";

interface TaskFormProps {
  task?: Task | null;
  onClose: () => void;
  onSaved: () => void;
}

export function TaskForm({ task, onClose, onSaved }: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const isEditing = !!task;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setIsLoading(true);

    try {
      if (isEditing) {
        await updateTask(task.id, { title, description });
      } else {
        await createTask({ title, description });
      }
      onSaved();
      onClose();
    } catch (err) {
      setError("Failed to save task");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 className="text-xl font-bold mb-4">
          {isEditing ? "Edit Task" : "New Task"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded">{error}</div>
          )}

          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Title *
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={200}
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={1000}
              rows={3}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? "Saving..." : isEditing ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

#### TaskFilter

```typescript
// components/tasks/TaskFilter.tsx
interface TaskFilterProps {
  filter: "all" | "active" | "completed";
  onFilterChange: (filter: "all" | "active" | "completed") => void;
}

export function TaskFilter({ filter, onFilterChange }: TaskFilterProps) {
  const filters: Array<"all" | "active" | "completed"> = [
    "all",
    "active",
    "completed",
  ];

  return (
    <div className="flex gap-2 mb-4">
      {filters.map((f) => (
        <button
          key={f}
          onClick={() => onFilterChange(f)}
          className={`px-3 py-1 rounded text-sm ${
            filter === f
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          {f.charAt(0).toUpperCase() + f.slice(1)}
        </button>
      ))}
    </div>
  );
}
```

---

## 6. API Client

```typescript
// lib/api.ts
import { authClient } from "./auth-client";
import { Task, TaskCreate, TaskUpdate, TaskListResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const { token } = await authClient.token();

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Request failed");
  }

  return response;
}

export async function getTasks(params?: {
  completed?: boolean;
  limit?: number;
  offset?: number;
}): Promise<TaskListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.completed !== undefined) {
    searchParams.set("completed", String(params.completed));
  }
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));

  const query = searchParams.toString();
  const response = await fetchWithAuth(`/tasks${query ? `?${query}` : ""}`);
  return response.json();
}

export async function createTask(data: TaskCreate): Promise<Task> {
  const response = await fetchWithAuth("/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function updateTask(id: string, data: TaskUpdate): Promise<Task> {
  const response = await fetchWithAuth(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function deleteTask(id: string): Promise<void> {
  await fetchWithAuth(`/tasks/${id}`, { method: "DELETE" });
}

export async function toggleTask(id: string): Promise<Task> {
  const response = await fetchWithAuth(`/tasks/${id}/toggle`, {
    method: "POST",
  });
  return response.json();
}
```

---

## 7. TypeScript Types

```typescript
// types/index.ts
export interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}
```

---

## 8. Environment Variables

```bash
# .env.example

# Database for Better Auth
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Better Auth secret (min 32 chars)
BETTER_AUTH_SECRET=<generated-secret>

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000

# FastAPI backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 9. Styling (Tailwind)

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
};

export default config;
```

---

## 10. Page Layouts

### 10.1 Login Page

```
┌────────────────────────────────────┐
│            Todo App                 │
├────────────────────────────────────┤
│                                    │
│         ┌──────────────────┐       │
│         │   Sign In        │       │
│         │                  │       │
│         │  Email: [______] │       │
│         │  Pass:  [______] │       │
│         │                  │       │
│         │  [  Sign In  ]   │       │
│         │                  │       │
│         │  Don't have an   │       │
│         │  account?        │       │
│         │  Register        │       │
│         └──────────────────┘       │
│                                    │
└────────────────────────────────────┘
```

### 10.2 Tasks Page

```
┌────────────────────────────────────┐
│  Todo App       user@x.com [Logout]│
├────────────────────────────────────┤
│                                    │
│  My Tasks                [+ Add]   │
│                                    │
│  [All] [Active] [Completed]        │
│                                    │
│  ┌────────────────────────────┐    │
│  │ [x] Task title     [Edit]  │    │
│  │     Description... [Delete]│    │
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │ [ ] Another task   [Edit]  │    │
│  │     More text...   [Delete]│    │
│  └────────────────────────────┘    │
│                                    │
│  2 tasks, 1 completed              │
│                                    │
└────────────────────────────────────┘
```
