# 🎓 Student Manager (CLI + TUI)

Student Manager is a small, local terminal app for managing students, courses, and enrollments. It offers a basic CLI flow and an optional TUI powered by Textual.

Built for simplicity, security, and performance using Python and SQLite.

---

## ✨ Features

- **Student registration** with unique custom ID  
- **Course management** (admin-only)  
- **Enrollment control**:  
  - Max **8 courses per student**  
  - Max **3 enrollment changes allowed**  
- **SQLite persistence** – all data stored locally in `student_manager.db`  
- **Dual interface**:  
  - Classic **CLI** for quick tasks  
  - Modern **TUI** (powered by [Textual](https://textual.textualize.io/)) for rich interaction  
- **Admin access** via strong password (12+ chars, with uppercase, lowercase, digit, and symbol)  
- **Optimized performance** – handles 100k+ records efficiently  

---

## 📁 Project Structure

```
Student-manager-very-creative-/
├── src/
│   ├── __init__.py
│   │
│   ├── domain/                     # Pure business logic (no dependencies)
│   │   ├── __init__.py
│   │   ├── models.py               # Student, Course, Enrollment, User
│   │   └── interfaces.py           # Abstract repos 
│   │
│   ├── use_cases/                  # Application logic
│   │   ├── __init__.py
│   │   └── enrollment_manager.py   
│   │
│   ├── infrastructure/             # Technical details (DB, file I/O...)
│   │   ├── __init__.py
│   │   ├── database.py             # UniversityDB (SQLite optimized)
│   │   ├── repositories.py         # Concrete repo impls 
│   │   └── utils.py                # is_admin_string_hard, clear_screen
│   │
│   └── presentation/               # User interaction layer
│       ├── __init__.py
│       ├── app.py                  # Main app logic (CLI + TUI router)
│       └── interface.py            # CLI prompts & TUI components 
│
├── tests/
│   └── performance_test.py
│
├── main.py                         # Entry point
├── pyproject.toml                  # For pip install -e .
└── README.md
```

---

## ⚙️ Requirements

- **Python 3.12+**
- Standard library only (no external deps for CLI)
- **Textual** (only required for TUI mode)

---

## 📦 Install

```bash
# Create virtual environment
python -m venv env

# Activate it
# Linux/macOS:
source env/bin/activate
# Windows:
env\Scripts\activate

# Install in development mode (includes Textual for TUI)
pip install -e .
```

> 💡 The `-e` flag installs your project in "editable" mode, so changes to code take effect immediately.

---

## ▶️ Run

### CLI Mode (default)
```bash
python main.py
```

### TUI Mode
```bash
python main.py --tui
```

### Admin Mode (CLI)
Launch directly into admin mode by providing a **strong admin password** as the first argument:
```bash
python main.py "MySecure#Admin123"
```
> 🔒 Password must be ≥12 characters and include uppercase, lowercase, digit, and symbol.

### Admin Mode (TUI)
Launch directly into admin mode by providing a **strong admin password** as the first argument:
```bash
python main.py --tui "MySecure#Admin123"
```

---

## 🗃️ Database

- Default database file: `student_manager.db` (created automatically in project root)
- Fully self-contained — no server needed
- Safe for single-user local use

---

## 🧪 Performance Benchmark

Test scalability with the built-in benchmark:

```bash
# Test with 100,000 students and 10 courses
python tests/performance_test.py 100000 10

# Test with default values (100k users, 10 courses)
python tests/performance_test.py
```

---

## 📜 License

MIT License — free to use, modify, and distribute.

