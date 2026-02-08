# Phase V: Acceptance Criteria

## Part A: Advanced Features

### AC-1: Priority Feature
- [ ] Tasks support priority levels (high, medium, low)
- [ ] Default priority is "medium"
- [ ] Priority displayed with visual indicator in UI
- [ ] Can set priority via chat: "Set task X to high priority"
- [ ] Can filter tasks by priority

### AC-2: Tags Feature
- [ ] Tasks support multiple tags (array of strings)
- [ ] Can add tags via API and chat
- [ ] Can remove tags via API and chat
- [ ] Can filter tasks by one or more tags
- [ ] Tags displayed as badges in UI

### AC-3: Search Feature
- [ ] Search endpoint filters by keyword in title
- [ ] Search via chat: "Find tasks about groceries"
- [ ] Search is case-insensitive
- [ ] Empty search returns all tasks

### AC-4: Filter and Sort
- [ ] Filter by status: pending, completed, all
- [ ] Filter by priority: high, medium, low
- [ ] Filter by tags (single or multiple)
- [ ] Sort by: due_date, priority, title, created_at
- [ ] Sort order: ascending or descending
- [ ] Combined filters work correctly

### AC-5: Due Dates
- [ ] Tasks can have due date with time
- [ ] Date/time picker in frontend
- [ ] Can set due date via chat: "Set due date to tomorrow at 3pm"
- [ ] Tasks sortable by due date
- [ ] Overdue tasks visually highlighted

### AC-6: Recurring Tasks
- [ ] Can create recurring tasks (daily, weekly, monthly)
- [ ] Completing recurring task creates next occurrence
- [ ] Next occurrence has correct due date
- [ ] Recurring pattern displayed in UI
- [ ] Can cancel recurring via chat

### AC-7: Reminders
- [ ] Reminder events published when due date approaches
- [ ] Default reminder: 1 hour before due date
- [ ] Browser notifications work (with permission)
- [ ] Reminders stop after task completed

## Part B: Kafka Integration

### AC-8: Kafka Topics
- [ ] task-events topic receives all CRUD operations
- [ ] reminders topic receives due date reminder events
- [ ] task-updates topic receives real-time updates
- [ ] Events have correct schema (event_id, timestamp, etc.)

### AC-9: Event Publishing
- [ ] Task create publishes "created" event
- [ ] Task update publishes "updated" event
- [ ] Task complete publishes "completed" event
- [ ] Task delete publishes "deleted" event
- [ ] Events include full task data

### AC-10: Microservices
- [ ] Recurring Task Service creates next occurrences
- [ ] Audit Service logs all events
- [ ] Notification Service sends browser notifications
- [ ] Services handle failures gracefully

## Part C: Dapr Integration

### AC-11: Pub/Sub
- [ ] Events published via Dapr HTTP API
- [ ] No direct Kafka client code in main app
- [ ] Subscriptions configured declaratively
- [ ] Multiple services can subscribe to same topic

### AC-12: State Management
- [ ] Conversation state stored via Dapr
- [ ] State survives pod restarts
- [ ] State can be retrieved by key
- [ ] Old state can be deleted

### AC-13: Service Invocation
- [ ] Services discover each other via app-id
- [ ] Built-in retries on failures
- [ ] No hardcoded service URLs

### AC-14: Bindings
- [ ] Cron binding triggers reminder checks
- [ ] Schedule configurable (e.g., every 5 minutes)
- [ ] Binding calls specified endpoint

### AC-15: Secrets
- [ ] API keys accessed via Dapr secrets API
- [ ] Secrets stored in Kubernetes secrets
- [ ] No secrets in application code or config

## Part D: Cloud Deployment

### AC-16: CI/CD Pipeline
- [ ] GitHub Actions workflow defined
- [ ] Builds trigger on push to main
- [ ] Docker images built and pushed
- [ ] Helm charts deployed to cluster
- [ ] Rollback possible on failure

### AC-17: Cloud Kubernetes
- [ ] Application deploys to DOKS/GKE/AKS
- [ ] All pods reach Running state
- [ ] Services accessible via LoadBalancer
- [ ] Horizontal Pod Autoscaler configured

### AC-18: Production Configuration
- [ ] Multiple replicas for high availability
- [ ] Resource limits appropriate for cloud
- [ ] Health checks pass
- [ ] Logs accessible via kubectl

### AC-19: Monitoring
- [ ] Pod metrics available (CPU, memory)
- [ ] Application logs viewable
- [ ] Health endpoints monitored
- [ ] Alerts configured for failures

## Part E: Documentation

### AC-20: Documentation
- [ ] README with cloud deployment instructions
- [ ] Environment variables documented
- [ ] Architecture diagrams included
- [ ] Dapr component configuration documented
- [ ] Kafka setup documented
- [ ] CI/CD pipeline documented

## Test Scenarios

### TS-1: Advanced Features Happy Path

1. Create task with high priority and tags
2. Set due date for tomorrow
3. Verify task appears with priority badge and tags
4. Search for task by keyword
5. Filter by priority and tags
6. Complete task
7. If recurring, verify next occurrence created

### TS-2: Kafka Event Flow

1. Create a task
2. Verify "created" event in task-events topic
3. Complete the task
4. Verify "completed" event published
5. If recurring, verify next task created by service

### TS-3: Reminder Flow

1. Create task with due date 10 minutes from now
2. Wait for cron binding to trigger
3. Verify reminder event published
4. Verify browser notification received
5. Complete task
6. Verify no more reminders

### TS-4: Dapr Integration

1. Publish event via Dapr pub/sub
2. Verify consumers receive event
3. Save state via Dapr state API
4. Retrieve state and verify
5. Invoke service via Dapr
6. Access secret via Dapr

### TS-5: Cloud Deployment

1. Push code to main branch
2. Verify CI/CD pipeline runs
3. Verify images pushed to registry
4. Verify Helm deployment succeeds
5. Access application via LoadBalancer
6. Verify full functionality

### TS-6: Resilience

1. Deploy to cloud with 2 replicas
2. Kill one backend pod
3. Verify application still works
4. Verify pod auto-recovers
5. Generate load
6. Verify HPA scales pods

## Verification Commands

```bash
# Check Kafka topics (local)
docker exec redpanda rpk topic list
docker exec redpanda rpk topic consume task-events

# Check Dapr status
dapr status -k
kubectl get pods -n dapr-system

# Check Dapr components
dapr components -k

# View Dapr dashboard
dapr dashboard

# Check cloud deployment
kubectl get pods -n production
kubectl get svc -n production
kubectl logs -l app=todo-backend -n production

# Check HPA
kubectl get hpa -n production

# Test health endpoint
curl https://your-app.cloud/api/v1/health
```
