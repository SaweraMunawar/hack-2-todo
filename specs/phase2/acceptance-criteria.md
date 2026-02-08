# Phase II Acceptance Criteria

## Document Information
- **Phase**: II - Todo Full-Stack Web Application
- **Version**: 2.0.0

---

## 1. Authentication Acceptance Criteria (Better Auth)

### AC-1: User Registration

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-1.1 | Register with valid email and password | Account created, session established, redirected to /tasks |
| AC-1.2 | Register with existing email | Error message displayed |
| AC-1.3 | Register with invalid email format | Validation error displayed |
| AC-1.4 | Register with password < 8 chars | Error: "Password must be at least 8 characters" |
| AC-1.5 | Register with mismatched password confirmation | Error: "Passwords do not match" |

### AC-2: User Login

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-2.1 | Login with valid credentials | Session established, redirected to /tasks |
| AC-2.2 | Login with wrong password | Error: "Invalid email or password" |
| AC-2.3 | Login with non-existent email | Error: "Invalid email or password" |
| AC-2.4 | Login with empty email | Validation error displayed |
| AC-2.5 | Login with empty password | Validation error displayed |

### AC-3: User Logout

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-3.1 | Click logout button | Session ended, redirected to /login |
| AC-3.2 | Access /tasks after logout | Redirected to /login |

### AC-4: Session Management

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-4.1 | Access /tasks with valid session | Page loads, tasks displayed |
| AC-4.2 | Access /tasks without session | Redirected to /login |
| AC-4.3 | Access /login while authenticated | Redirected to /tasks |
| AC-4.4 | Access /register while authenticated | Redirected to /tasks |
| AC-4.5 | Refresh page while authenticated | Session persists, stay on page |

### AC-5: JWT Token

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-5.1 | Get JWT token from Better Auth | Valid JWT returned |
| AC-5.2 | JWT contains user ID in sub claim | User ID present in payload |
| AC-5.3 | FastAPI validates JWT via JWKS | 200 OK for valid token |
| AC-5.4 | FastAPI rejects invalid JWT | 401 Unauthorized |
| AC-5.5 | FastAPI rejects expired JWT | 401 "Token has expired" |

---

## 2. Task CRUD Acceptance Criteria

### AC-6: Create Task

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-6.1 | Create task with title only | Task created with empty description |
| AC-6.2 | Create task with title and description | Task created with both fields |
| AC-6.3 | Create task with empty title | Error: "Title cannot be empty" |
| AC-6.4 | Create task with title > 200 chars | Error: "Title must be 200 characters or less" |
| AC-6.5 | Create task with description > 1000 chars | Error: "Description must be 1000 characters or less" |
| AC-6.6 | New task appears in list immediately | UI updates to show new task |
| AC-6.7 | New task has completed = false | Default uncompleted status |

### AC-7: Read/List Tasks

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-7.1 | View tasks when none exist | "No tasks yet" message displayed |
| AC-7.2 | View tasks when tasks exist | All user's tasks displayed |
| AC-7.3 | Tasks ordered by newest first | Most recent task at top |
| AC-7.4 | Task shows title | Title visible |
| AC-7.5 | Task shows description (or empty) | Description visible or empty |
| AC-7.6 | Task shows completion status | Checkbox checked/unchecked |
| AC-7.7 | Task shows created date | Formatted date visible |
| AC-7.8 | Filter by "All" | All tasks shown |
| AC-7.9 | Filter by "Active" | Only incomplete tasks shown |
| AC-7.10 | Filter by "Completed" | Only completed tasks shown |

### AC-8: Update Task

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-8.1 | Click edit button | Edit form/modal opens with current values |
| AC-8.2 | Update title only | Title changes, description unchanged |
| AC-8.3 | Update description only | Description changes, title unchanged |
| AC-8.4 | Update both fields | Both fields change |
| AC-8.5 | Update with empty title | Error: "Title cannot be empty" |
| AC-8.6 | Cancel edit | No changes saved |
| AC-8.7 | Updated task shows new values | UI reflects changes |
| AC-8.8 | updated_at field is set | Timestamp recorded |

### AC-9: Delete Task

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-9.1 | Click delete button | Confirmation dialog appears |
| AC-9.2 | Confirm delete | Task removed from list |
| AC-9.3 | Cancel delete | Task remains in list |
| AC-9.4 | Deleted task no longer appears | UI updated immediately |
| AC-9.5 | Refresh page after delete | Task still gone |

### AC-10: Toggle Completion

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-10.1 | Toggle incomplete task | Checkbox checked, status = completed |
| AC-10.2 | Toggle complete task | Checkbox unchecked, status = incomplete |
| AC-10.3 | Completed task title strikethrough | Visual indication of completion |
| AC-10.4 | Toggle updates updated_at | Timestamp recorded |
| AC-10.5 | Toggle reflects in filter | Task moves between Active/Completed |

---

## 3. Data Isolation Acceptance Criteria

### AC-11: User Data Isolation

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-11.1 | User A cannot see User B's tasks | Only own tasks in list |
| AC-11.2 | User A cannot update User B's task (API) | 404 Not Found response |
| AC-11.3 | User A cannot delete User B's task (API) | 404 Not Found response |
| AC-11.4 | User A cannot toggle User B's task (API) | 404 Not Found response |
| AC-11.5 | User A guesses User B's task UUID (API) | 404 Not Found response |
| AC-11.6 | New user sees empty task list | Fresh account, no tasks |

---

## 4. UI/UX Acceptance Criteria

### AC-12: Responsive Design

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-12.1 | App usable on mobile (375px) | All features accessible |
| AC-12.2 | App usable on tablet (768px) | Proper layout |
| AC-12.3 | App usable on desktop (1280px) | Centered, readable width |

### AC-13: Loading States

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-13.1 | Page load shows loading state | Spinner or loading text |
| AC-13.2 | Form submit shows loading | Button disabled + indicator |
| AC-13.3 | Task toggle is responsive | Immediate visual feedback |

### AC-14: Error Handling

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-14.1 | Network error displays message | User-friendly error |
| AC-14.2 | Server error displays message | User-friendly error |
| AC-14.3 | Validation errors show inline | Field-level error messages |
| AC-14.4 | Errors are dismissable | Can close/clear errors |

### AC-15: Accessibility

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-15.1 | All inputs have labels | Screen reader accessible |
| AC-15.2 | Keyboard navigation works | Tab through all elements |
| AC-15.3 | Focus visible on all elements | Clear focus indicators |
| AC-15.4 | Buttons have accessible names | ARIA labels present |

---

## 5. Security Acceptance Criteria

### AC-16: Authentication Security

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-16.1 | Passwords never sent in plaintext | HTTPS in production |
| AC-16.2 | Passwords hashed in database | Better Auth handles hashing |
| AC-16.3 | JWT validated via JWKS | Public key verification |
| AC-16.4 | Invalid JWT rejected | 401 response |
| AC-16.5 | Session cookies HttpOnly | Not accessible via JS |

### AC-17: API Security

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-17.1 | All task endpoints require auth | 401 without token |
| AC-17.2 | SQL injection prevented | SQLModel parameterization |
| AC-17.3 | XSS prevented in task display | React escapes HTML |
| AC-17.4 | CORS properly configured | Only allowed origins |

---

## 6. Database Acceptance Criteria

### AC-18: Data Persistence

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-18.1 | Created task persists after refresh | Still in database |
| AC-18.2 | Updated task persists after refresh | Changes preserved |
| AC-18.3 | Deleted task gone after refresh | Not in database |
| AC-18.4 | User persists after logout/login | Same account, same data |

### AC-19: Data Integrity

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-19.1 | Task requires user_id | NOT NULL enforced |
| AC-19.2 | User email unique | Duplicate email rejected |
| AC-19.3 | UUID primary keys | No sequential IDs exposed |
| AC-19.4 | Timestamps in UTC | Consistent timezone |

---

## 7. API Acceptance Criteria

### AC-20: REST Compliance

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-20.1 | GET /tasks returns 200 | OK with task array |
| AC-20.2 | POST /tasks returns 201 | Created with task |
| AC-20.3 | PATCH /tasks/:id returns 200 | OK with updated task |
| AC-20.4 | DELETE /tasks/:id returns 204 | No content |
| AC-20.5 | POST /tasks/:id/toggle returns 200 | OK with toggled task |
| AC-20.6 | GET /health returns 200 | Health status |

### AC-21: Error Responses

| ID | Criterion | Expected Result |
|----|-----------|-----------------|
| AC-21.1 | 401 for missing auth | Unauthorized |
| AC-21.2 | 404 for missing resource | Not Found |
| AC-21.3 | 422 for validation errors | Unprocessable Entity |

---

## 8. Test Scenarios

### TS-1: Happy Path - New User

```
1. Navigate to /register
2. Enter valid email, password, and confirmation
3. Click Create Account
4. Verify redirected to /tasks
5. Verify empty task list shown
6. Add a new task with title "Test Task"
7. Verify task appears in list
8. Toggle task to complete
9. Verify checkbox checked
10. Click logout
11. Verify redirected to /login
```

### TS-2: Happy Path - Returning User

```
1. Navigate to /login
2. Enter credentials
3. Click Sign In
4. Verify previous tasks visible
5. Edit a task title
6. Verify changes saved
7. Delete a task
8. Verify task removed
```

### TS-3: Data Isolation Test

```
1. Register User A
2. Create 3 tasks as User A
3. Logout
4. Register User B
5. Verify User B sees empty list
6. Create 2 tasks as User B
7. Verify User B sees only 2 tasks
8. Logout
9. Login as User A
10. Verify User A still sees only 3 tasks
```

### TS-4: JWT Validation Test

```
1. Login with valid credentials
2. Capture JWT from authClient.token()
3. Make API request with valid JWT
4. Verify 200 OK response
5. Make API request with invalid JWT
6. Verify 401 response
```

---

## 9. Verification Checklist

### Pre-Deployment

- [ ] All AC-1 through AC-21 pass
- [ ] No console errors in browser
- [ ] No unhandled promise rejections
- [ ] API returns proper status codes
- [ ] Database schema created
- [ ] Better Auth tables migrated
- [ ] Environment variables configured

### Production Verification

- [ ] HTTPS working
- [ ] CORS allowing frontend origin
- [ ] Database connection stable
- [ ] Better Auth functioning
- [ ] JWT issuance working
- [ ] JWKS endpoint accessible
- [ ] Registration works
- [ ] Login works
- [ ] Task CRUD works
- [ ] Logout works
