# Phase I User Interface Specification

## Document Information
- **Phase**: I - Todo In-Memory Python Console App
- **Version**: 1.0.0

---

## 1. Main Menu

### Layout
```
╔══════════════════════════════════════╗
║         TODO APP - Phase I           ║
╠══════════════════════════════════════╣
║                                      ║
║   1. Add Task                        ║
║   2. View Tasks                      ║
║   3. Update Task                     ║
║   4. Delete Task                     ║
║   5. Mark Complete                   ║
║   0. Exit                            ║
║                                      ║
╚══════════════════════════════════════╝

Enter your choice: _
```

### Menu Options
| Key | Label | Description |
|-----|-------|-------------|
| 1 | Add Task | Create a new task |
| 2 | View Tasks | Display all tasks |
| 3 | Update Task | Edit existing task |
| 4 | Delete Task | Remove a task |
| 5 | Mark Complete | Toggle completion status |
| 0 | Exit | Quit the application |

### Input Handling
- Accept single digit (0-5)
- Ignore leading/trailing whitespace
- Invalid input → show error, redisplay menu

---

## 2. Message Formatting

### Success Messages
```
✓ [message]
```
- Green color if terminal supports it
- Prefix: `✓` or `[OK]`

### Error Messages
```
✗ Error: [message]
```
- Red color if terminal supports it
- Prefix: `✗ Error:` or `[ERROR]`

### Info Messages
```
ℹ [message]
```
- Blue/cyan color if terminal supports it
- Prefix: `ℹ` or `[INFO]`

### Warning Messages
```
⚠ [message]
```
- Yellow color if terminal supports it
- Prefix: `⚠` or `[WARNING]`

---

## 3. Section Headers

### Format
```
=== Section Title ===
```

### Usage
- Each feature starts with a section header
- Provides context for the current operation

---

## 4. Prompt Formatting

### Standard Input Prompt
```
Enter [field name]: _
```

### Optional Field Prompt
```
Enter [field name] (optional, press Enter to skip): _
```

### Confirmation Prompt
```
[Question]? (y/N): _
```
- Capital letter indicates default
- `(y/N)` → default No
- `(Y/n)` → default Yes

### Keep Current Value Prompt
```
Enter new [field name] (press Enter to keep current): _
```

---

## 5. Task Display Formats

### Brief List (for selection)
```
  #1: Buy groceries [pending]
  #2: Call dentist [completed]
  #3: Finish report [pending]
```

### Full Detail
```
[ ] #1: Buy groceries
    Get milk, eggs, and bread from the store...
    Created: 2024-01-15 10:30
```

### Single Task Detail (for confirmation)
```
  #1: Buy groceries
  Description: Get milk, eggs, and bread from the store
  Status: Pending
  Created: 2024-01-15 10:30
```

---

## 6. Visual Elements

### Separators
```
───────────────────────────────
```
- Used before summary lines
- Used to separate sections

### Box Drawing Characters
| Character | Name | Usage |
|-----------|------|-------|
| `╔` | Top-left | Menu corners |
| `╗` | Top-right | Menu corners |
| `╚` | Bottom-left | Menu corners |
| `╝` | Bottom-right | Menu corners |
| `═` | Horizontal | Menu borders |
| `║` | Vertical | Menu sides |
| `╠` | Left-T | Menu separator |
| `╣` | Right-T | Menu separator |

### Status Indicators
| Indicator | Meaning |
|-----------|---------|
| `[ ]` | Pending/incomplete |
| `[x]` | Completed |

### Icons (Unicode)
| Icon | Meaning |
|------|---------|
| `✓` | Success |
| `✗` | Error |
| `ℹ` | Information |
| `⚠` | Warning |

---

## 7. Color Scheme (Optional)

If terminal supports ANSI colors:

| Element | Color Code |
|---------|------------|
| Success | Green `\033[92m` |
| Error | Red `\033[91m` |
| Info | Cyan `\033[96m` |
| Warning | Yellow `\033[93m` |
| Header | Bold `\033[1m` |
| Reset | `\033[0m` |

### Fallback
- Detect if colors are supported
- Use plain text if not supported
- Never fail due to color issues

---

## 8. Screen Flow

### Application Start
```
1. Clear screen (optional)
2. Display welcome message
3. Display main menu
4. Wait for input
```

### After Each Action
```
1. Display result message
2. Pause briefly (or wait for Enter)
3. Redisplay main menu
```

### Application Exit
```
1. Display goodbye message
2. Exit cleanly
```

---

## 9. Keyboard Handling

### Supported Keys
| Key | Context | Behavior |
|-----|---------|----------|
| Enter | Prompts | Submit input |
| Ctrl+C | Anywhere | Exit gracefully |
| Ctrl+D | Anywhere | Exit gracefully |

### Ctrl+C Handling
- Never show ugly stack trace
- Show clean exit message
- Save state if applicable (not in Phase I)

---

## 10. Accessibility

### Requirements
- No reliance on color alone
- Text-based status indicators
- Clear, readable formatting
- Consistent navigation

### Screen Reader Friendly
- Linear content flow
- Descriptive prompts
- No purely decorative elements that confuse
