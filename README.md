# `crawl.py`: Project Structure & Function Mapper for LLMs

## Overview

As projects scale, understanding their internal organization, the relationship between files and functions, and managing dependencies becomes increasingly complex. `crawl.py` is a specialized Python script designed to address this challenge by **intelligently mapping the structure of a project's codebase**.

It recursively traverses a specified directory, identifies Python files, and **extracts all defined functions and classes**. The output is presented in a user-friendly Tkinter GUI, saved to a detailed `Crawl.log` file, and most importantly, generated into a **`MAP.txt` file structured as a tree-like representation with each line commented out.**

---

## Why is `MAP.txt` invaluable for LLMs?

The `MAP.txt` file serves as a crucial input for Large Language Models (LLMs) like myself. Before an LLM is tasked with analyzing code fragments, understanding the overall project, or even generating new code, it can be **fed this `MAP.txt` file**. This provides the LLM with:

* **Holistic Project Understanding**: A clear, commented overview of the entire project's directory and file hierarchy.

* **Function-to-File Relationship**: Explicit knowledge of which functions and classes reside within which files, allowing the LLM to easily relate code snippets to their definitions.

* **Dependency Insights (Implicit)**: By understanding the structure, an LLM can infer potential dependencies and relationships between different modules and components, aiding in identifying or avoiding circular dependencies and promoting good architectural practices.

* **Contextual Awareness**: Enhances the LLM's ability to reason about code, debug issues, or suggest improvements by providing necessary context about the codebase's organization.

Essentially, `MAP.txt` acts as a concise, structured "project guide" that an LLM can quickly process to build a comprehensive mental model of the software, significantly improving its performance on code-related tasks.

---

## Features

* **Recursive Directory Traversal**: Scans all subdirectories from a chosen root.

* **Python File Analysis**: Parses `.py` files to identify functions and classes using Python's `ast` module.

* **Intuitive GUI**: A Tkinter-based interface displays the crawl results in real-time.

* **Detailed Logging**: Generates `Crawl.log` with a comprehensive record of the scan.

* **LLM-Ready `MAP.txt`**: Creates a commented, tree-structured `MAP.txt` file, explicitly designed for easy ingestion and understanding by LLMs.

* **Intelligent Filtering**: Automatically ignores `__pycache__` directories, dot-prefixed directories (e.g., `.git`), and `__init__.py` files to focus on relevant code.

* **File Opening Utility**: Buttons to quickly open the generated `Crawl.log` and `MAP.txt` files with your system's default viewer.

---

## How to Use

1.  **Run the script**:

    ```bash
    python crawl.py

    ```

2.  **Select Directory**: The GUI will open, defaulting to the directory where `crawl.py` is located. You can use the "Browse..." button to select a different project directory.

3.  **Start Crawl**: Click the "Start Crawl" button. The GUI will populate with the discovered structure, and `Crawl.log` and `MAP.txt` files will be generated in the same directory as `crawl.py`.

4.  **View Output**: Use the "Open Log" and "Open Map" buttons to view the generated files.

---

## `MAP.txt` Example Structure

```
# Program Map:
# This section outlines the directory and file structure of the OPEN-AIR RF Spectrum Analyzer Controller application,
# providing a brief explanation for each component.
#
# └── YourProjectRoot/
#     ├── module_a/
#     |   ├── script_x.py
#     |   |   -> Class: MyClass
#     |   |   -> Function: process_data
#     |   |   -> Function: validate_input
#     |   ├── util.py
#     |   |   -> Function: helper_function
#     |   |   -> Function: another_utility
#     ├── data/
#     |   └── raw_data.csv
#     └── main.py
#         -> Class: MainApplication
#         -> Function: initialize_app
#         -> Function: run_program

```
