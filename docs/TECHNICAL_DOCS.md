# Student Manager - Technical Documentation

**Author**: Khaled (Lead Architect)
**Status**: Draft / Initial Specification

## Overview

This system is designed to manage student enrollments and administrative tasks using a Terminal User Interface (TUI). It leverages the `Textual` framework for a modern, responsive CLI experience.

## Architecture & Modules

### 1. Entry Point (`main.py`)

- Initializes the environment.
- Boots the primary application loop.

### 2. UI Layer (`src/ui.py`)

- **Framework**: Built on `Textual`.
- **Components**:
  - `MarkdownViewer`: Currently used for displaying documentation and static information.
  - **Planned Screens**:
    - `Salutation Screen`: Initial landing to choose between "Student" and "Admin" roles.
    - `Student Dashboard`: Username registration, subject selection, and progress monitoring.

### 3. Logic Layer (`src/enrollment.py`)

- _Status: Implementation Pending._
- Responsible for CRUD operations on student data and subject validation.

## Technical Specifications (Gasser's Notes)

### Data Validation

- **Username Unique Constraint**: Prevent duplicate registration in memory/storage.
- **Subject Constraints**:
  - Maximum 8 subjects per student.
  - No duplicate subject names allowed.
- **Progress Tracking**: Implementation of a progress bar to visualize subject load.

### Role-Based Access Control (RBAC)

- **Student**: Can register, add/edit/remove their own subjects.
- **Admin**: Full oversight, including the ability to add/manage quizzes within specific subjects.

### Error Handling

- Use explicit exception handling for input validation (duplicate entries, overflows).
- TUI-based alerts for user feedback.

## Roadmap

1. Implement the role-selection landing page.
2. Develop the `enrollment.py` backend logic with Pydantic for schema validation.
3. Integrate the quiz feature for Admin roles.
4. Implement the Database layer with SQLite.
