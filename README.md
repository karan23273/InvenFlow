# Inventory Management System

## Overview

A prototype Inventory Management System (IMS) designed to manage and
track stock efficiently. It supports basic inventory operations and
serves as a foundation for implementing advanced features.

## Features

-   Data Entry: Add and update inventory items.
-   Data Display: View tables and stock records.
-   Database Integration: Uses SQLite (`todo.db`) for storage.
-   ER Diagram: Includes database design (`ER diagram.pdf`).
-   Flask-based Application (`app.py`).

## Project Structure

    __pycache__/           # Compiled Python files
    instance/              # Flask instance folder
    templates/             # HTML templates for UI
    Data_Entry             # Module for adding/updating data
    Data_Table             # Inventory table structure
    Data_TableShow         # Logic for displaying data
    SQL_Queries            # SQL statements for inventory management
    todo.db                # SQLite database
    app.py                 # Main Flask application
    tempCodeRunnerFile.py  # Temporary runner file
    README.md              # Project documentation
    ER diagram.pdf         # Database schema diagram

## Tech Stack

-   Backend: Python (Flask)
-   Database: SQLite
-   Frontend: HTML templates (Flask)

## How to Run

1.  Clone this repository:

    ``` bash
    git clone <repo-link>
    ```

2.  Install dependencies:

    ``` bash
    pip install flask
    ```

3.  Run the application:

    ``` bash
    python app.py
    ```

4.  Open your browser at:

        http://127.0.0.1:5000

## Current Status

This project is a **work-in-progress (WIP)**: - Core modules (data
entry, data display) are functional. - Advanced features (analytics,
restocking alerts) to be added.

## Future Enhancements

-   Inventory analytics dashboard.
-   User authentication and access control.
-   Barcode/QR code integration.

## License

This project is for educational purposes and is not yet
production-ready.
