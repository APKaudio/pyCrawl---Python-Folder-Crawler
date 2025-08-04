# crawl.py
#
# This script recursively traverses the directory it is run from,
# listing all files and subdirectories in a Tkinter GUI window.
# For any Python (.py) files encountered, it will also parse the
# file to extract and display the names of all defined functions
# and classes. All output is also saved to a 'Crawl.log' file.
# It now also generates a 'MAP.txt' file with a tree-like structure
# of the discovered files and functions, with each line commented out.
#
# Author: Gemini (for Anthony Peter Kuzub)
# Version: 20250803.1139.3 # Updated version for MAP.txt tree and Open buttons

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import os
import ast # Module to parse Python code into an Abstract Syntax Tree
import inspect # For getting current function name for logging (optional, but good practice)
import threading
import datetime # For timestamping the log file
import subprocess # For opening files

# --- Logging and Console Output Functions (Simplified for standalone script) ---
def debug_log(message, **kwargs):
    """A simplified debug logging function."""
    pass # Suppress debug logs for cleaner console output in this standalone script

def console_log(message):
    """A simplified console output function for the GUI."""
    pass # Suppress direct console prints, will use GUI text widget


class FolderCrawlerApp:
    """
    Function Description:
    A Tkinter application that crawls a specified directory (defaulting to the
    script's directory) and displays its contents. It identifies Python files
    and lists their functions and classes. All output is also written to 'Crawl.log'.
    It now also generates a 'MAP.txt' file with a tree-like structure
    of the discovered files and functions, with each line commented out.

    Inputs:
        root (tk.Tk): The root Tkinter window.

    Process:
        1. Initializes the main application window and widgets.
        2. Sets up a scrolled text area for displaying results.
        3. Provides buttons to start the crawling process and open log/map files.
        4. Opens a log file ('Crawl.log') and a map file ('MAP.txt') for writing.
        5. Implements the `_crawl_directory` method to recursively scan folders,
           ignoring '__pycache__' directories and those starting with a dot.
        6. Implements the `_analyze_python_file` method to parse Python files
           and extract function and class definitions using the `ast` module,
           ignoring '__init__.py' files.
        7. Displays all collected information in the scrolled text area and writes to log file.
        8. Generates a tree-like map in 'MAP.txt' with commented lines and
           nested function/class representation.

    Outputs:
        A Tkinter GUI application, a 'Crawl.log' file, and a 'MAP.txt' file.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Folder and Python File Analyzer - crawl.py")
        self.root.geometry("800x600")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.current_file = os.path.basename(__file__)
        self.current_version = "20250803.1139.3" # Updated version

        self.log_file = None # Initialize log file handle
        self.map_file = None # Initialize map file handle

        # --- UI Elements ---
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1) # Makes the entry field stretch

        ttk.Label(control_frame, text="Directory to crawl:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.directory_path_var = tk.StringVar(value=os.getcwd()) # Default to current working directory
        self.directory_entry = ttk.Entry(control_frame, textvariable=self.directory_path_var, width=60)
        self.directory_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.browse_button = ttk.Button(control_frame, text="Browse...", command=self._browse_directory)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        self.crawl_button = ttk.Button(control_frame, text="Start Crawl", command=self._start_crawl)
        self.crawl_button.grid(row=0, column=3, padx=5, pady=5)

        self.open_log_button = ttk.Button(control_frame, text="Open Log", command=self._open_log_file)
        self.open_log_button.grid(row=0, column=4, padx=5, pady=5)

        self.open_map_button = ttk.Button(control_frame, text="Open Map", command=self._open_map_file)
        self.open_map_button.grid(row=0, column=5, padx=5, pady=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=25,
                                                   font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4",
                                                   insertbackground="#d4d4d4")
        self.text_area.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.text_area.tag_configure("dir", foreground="#6a9955") # Green for directories
        self.text_area.tag_configure("file", foreground="#569cd6") # Blue for files
        self.text_area.tag_configure("python_file", foreground="#cc7832") # Orange for Python files
        self.text_area.tag_configure("function", foreground="#ffc66d") # Yellow for functions
        self.text_area.tag_configure("class", foreground="#da70d6") # Purple for classes
        self.text_area.tag_configure("header", foreground="#9cdcfe", font=("Consolas", 12, "bold")) # Light blue for headers

        # Ensure log and map files are closed on window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """
        Function Description:
        Handles the window closing event, ensuring the log and map files are properly closed.

        Inputs:
            None.

        Process:
            1. Closes the log file if it's open.
            2. Closes the map file if it's open.
            3. Destroys the Tkinter root window.

        Outputs:
            None. Cleans up resources.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Closing application. Version: {self.current_version}. Goodbye!",
                    file=self.current_file, version=self.current_version, function=current_function)
        if self.log_file:
            self.log_file.close()
            debug_log(f"Crawl.log closed. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
        if self.map_file:
            self.map_file.close()
            debug_log(f"MAP.txt closed. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
        self.root.destroy()

    def _browse_directory(self):
        """
        Function Description:
        Opens a directory selection dialog and updates the directory path variable.

        Inputs:
            None.

        Process:
            1. Opens a dialog to select a directory.
            2. If a directory is selected, updates `self.directory_path_var`.

        Outputs:
            None. Updates the GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Browsing for directory. Version: {self.current_version}.",
                    file=self.current_file, version=self.current_version, function=current_function)

        selected_directory = filedialog.askdirectory(initialdir=self.directory_path_var.get())
        if selected_directory:
            self.directory_path_var.set(selected_directory)
            debug_log(f"Selected directory: {selected_directory}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)

    def _start_crawl(self):
        """
        Function Description:
        Initiates the crawling process in a separate thread to keep the GUI responsive.
        Opens both 'Crawl.log' and 'MAP.txt' files.

        Inputs:
            None.

        Process:
            1. Clears the text area.
            2. Opens the 'Crawl.log' file.
            3. Opens the 'MAP.txt' file and writes its initial header.
            4. Disables the crawl button.
            5. Starts a new thread to run `_crawl_directory_thread`.

        Outputs:
            None. Manages the crawling process.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting crawl. Version: {self.current_version}. Let's explore!",
                    file=self.current_file, version=self.current_version, function=current_function)

        self.text_area.delete(1.0, tk.END) # Clear previous output

        # Open the log file
        try:
            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Crawl.log")
            self.log_file = open(log_file_path, "w", encoding="utf-8")
            self._append_to_text_area(f"--- Crawl Log Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n", "header")
            self.log_file.write(f"--- Crawl Log Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
            debug_log(f"Crawl.log opened at {log_file_path}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
        except Exception as e:
            self._append_to_text_area(f"Error opening Crawl.log: {e}\n", "header")
            debug_log(f"Error opening Crawl.log: {e}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
            self.log_file = None # Ensure log_file is None if opening fails

        # Open the MAP.txt file and write its header
        try:
            map_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MAP.txt")
            self.map_file = open(map_file_path, "w", encoding="utf-8")
            map_header = """# Program Map:
# This section outlines the directory and file structure of the OPEN-AIR RF Spectrum Analyzer Controller application,
# providing a brief explanation for each component.
#
"""
            self.map_file.write(map_header)
            debug_log(f"MAP.txt opened at {map_file_path}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
        except Exception as e:
            self._append_to_text_area(f"Error opening MAP.txt: {e}\n", "header")
            debug_log(f"Error opening MAP.txt: {e}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
            self.map_file = None # Ensure map_file is None if opening fails

        self.crawl_button.config(state=tk.DISABLED)

        # Run the crawl in a separate thread to prevent GUI from freezing
        threading.Thread(target=self._crawl_directory_thread, daemon=True).start()

    def _crawl_directory_thread(self):
        """
        Function Description:
        Worker function for `_start_crawl`. Performs the actual directory traversal
        and Python file analysis. Updates the GUI on the main thread and writes to log file.
        Also builds the tree structure for MAP.txt.

        Inputs:
            None.

        Process:
            1. Gets the target directory.
            2. Iterates through directories and files using `os.walk`.
            3. **Ignores `__pycache__` directories and those starting with a dot.**
            4. For each item, appends its path to the text area and writes to log.
            5. For MAP.txt, constructs a tree-like structure with `├──` and `└──` prefixes,
               and prefixes each line with `# `.
            6. If it's a Python file (and not `__init__.py`), calls `_analyze_python_file` and
               appends its findings to both.
            7. Re-enables the crawl button on completion.
            8. Closes the log and map files.

        Outputs:
            None. Updates the GUI and creates/updates 'Crawl.log' and 'MAP.txt'.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running crawl thread. Version: {self.current_version}. Digging deep!",
                    file=self.current_file, version=self.current_version, function=current_function)

        target_directory = self.directory_path_var.get()
        if not os.path.isdir(target_directory):
            self._append_to_text_area(f"Error: '{target_directory}' is not a valid directory.", "header")
            self.root.after(0, lambda: self.crawl_button.config(state=tk.NORMAL))
            if self.log_file:
                self.log_file.write(f"Error: '{target_directory}' is not a valid directory.\n")
                self.log_file.close()
                self.log_file = None
            if self.map_file:
                self.map_file.write(f"Error: '{target_directory}' is not a valid directory.\n")
                self.map_file.close()
                self.map_file = None
            return

        self._append_to_text_area(f"Crawling directory: {target_directory}\n", "header")
        if self.log_file:
            self.log_file.write(f"Crawling directory: {target_directory}\n\n")

        map_output_lines = []

        try:
            # Simulate the root directory (e.g., OPEN-AIR/)
            root_dir_name = os.path.basename(target_directory)
            map_output_lines.append(f"# └── {root_dir_name}/\n")

            for root, dirs, files in os.walk(target_directory):
                # Ignore __pycache__ folders and folders starting with a dot
                dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]

                relative_root = os.path.relpath(root, target_directory)
                if relative_root == ".":
                    # This is the base directory, already handled above
                    current_indent_level = 0
                else:
                    current_indent_level = relative_root.count(os.sep) + 1 # +1 for the initial root dir

                # Display current directory in GUI log
                if relative_root != ".": # Avoid re-logging the base directory
                    display_root = relative_root + os.sep
                    self._append_to_text_area(f"\nDirectory: {display_root}", "dir")
                    if self.log_file:
                        self.log_file.write(f"\nDirectory: {display_root}\n")

                all_items = sorted(dirs) + sorted(files)
                for i, item in enumerate(all_items):
                    is_last_item_in_current_level = (i == len(all_items) - 1)
                    prefix = "└── " if is_last_item_in_current_level else "├── "
                    indent_str = "    " * current_indent_level

                    if item in dirs:
                        map_output_lines.append(f"#{indent_str}{prefix}{item}/\n")
                        # Display subdirectories in GUI log
                        self._append_to_text_area(f"  {indent_str}{prefix}{item}", "dir")
                        if self.log_file:
                            self.log_file.write(f"  {indent_str}{prefix}{item}\n")
                    elif item in files:
                        file_path = os.path.join(root, item)
                        map_output_lines.append(f"#{indent_str}{prefix}{item}\n")
                        # Display files in GUI log
                        self._append_to_text_area(f"  {indent_str}{prefix}{item}", "file")
                        if self.log_file:
                            self.log_file.write(f"  {indent_str}{prefix}{item}\n")

                        if item.lower().endswith(".py") and item.lower() != "__init__.py":
                            # Analyze Python file and get its functions/classes for MAP.txt
                            py_analysis_lines = self._analyze_python_file(file_path, current_indent_level + 1)
                            for line in py_analysis_lines:
                                map_output_lines.append(line + "\n")
                        elif item.lower() == "__init__.py":
                            # Log that __init__.py is being ignored
                            ignore_message = f"    [INFO] Ignoring __init__.py: {item}"
                            self._append_to_text_area(ignore_message, "file")
                            if self.log_file:
                                self.log_file.write(ignore_message + "\n")


        except Exception as e:
            error_message = f"\nAn error occurred during crawling: {e}"
            self._append_to_text_area(error_message, "header")
            if self.log_file:
                self.log_file.write(error_message + "\n")
            if self.map_file:
                self.map_file.write(error_message + "\n")
            debug_log(f"Error during crawl: {e}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
        finally:
            final_message = f"\n--- Crawl complete for {target_directory}. ---"
            self._append_to_text_area(final_message, "header")
            if self.log_file:
                self.log_file.write(final_message + "\n")
                self.log_file.close()
                self.log_file = None # Reset file handle after closing

            # Write all collected map lines to MAP.txt
            if self.map_file:
                for line in map_output_lines:
                    self.map_file.write(line)
                self.map_file.close()
                self.map_file = None # Reset file handle after closing
            self.root.after(0, lambda: self.crawl_button.config(state=tk.NORMAL))
            debug_log(f"Crawl finished. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)


    def _analyze_python_file(self, file_path, indent_level):
        """
        Function Description:
        Parses a Python file and extracts function and class definitions.
        Returns a list of formatted strings for MAP.txt and also updates the GUI log.

        Inputs:
            file_path (str): The full path to the Python file.
            indent_level (int): The current indentation level for the MAP.txt output.

        Process:
            1. Reads the content of the Python file.
            2. Uses `ast.parse` to build an Abstract Syntax Tree.
            3. Iterates through the AST nodes to find `FunctionDef` and `ClassDef` nodes.
            4. Returns formatted strings for found functions and classes, prefixed with `# `.
            5. Handles potential `SyntaxError` for invalid Python files.

        Outputs:
            list[str]: A list of formatted strings for MAP.txt.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Analyzing Python file: {file_path}. Version: {self.current_version}. Parsing!",
                    file=self.current_file, version=self.current_version, function=current_function)

        analysis_lines = []
        indent_str = "    " * indent_level # Indentation for the file itself

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            functions_found = []
            classes_found = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions_found.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes_found.append(node.name)

            if functions_found or classes_found:
                # Add to GUI log
                self._append_to_text_area(f"    [PY] Analysis for {os.path.basename(file_path)}:", "python_file")
                if self.log_file:
                    self.log_file.write(f"    [PY] Analysis for {os.path.basename(file_path)}:\n")

                # The inner items (functions/classes) need to be indented relative to the file's indentation
                # and also have the `|   ->` prefix.
                # The `indent_str` here is already for the file's level.
                # So, for functions/classes within the file, we add an additional "    " for visual nesting,
                # and then the `|   ->` part.
                inner_item_indent_prefix = indent_str + "    |   " # This creates the desired visual alignment

                if classes_found:
                    class_line_gui = f"      Classes: {', '.join(sorted(classes_found))}"
                    self._append_to_text_area(class_line_gui, "class")
                    if self.log_file:
                        self.log_file.write(class_line_gui + "\n")
                    for cls_name in sorted(classes_found):
                        analysis_lines.append(f"#{inner_item_indent_prefix}-> Class: {cls_name}")

                if functions_found:
                    function_line_gui = f"      Functions: {', '.join(sorted(functions_found))}"
                    self._append_to_text_area(function_line_gui, "function")
                    if self.log_file:
                        self.log_file.write(function_line_gui + "\n")
                    for func_name in sorted(functions_found):
                        analysis_lines.append(f"#{inner_item_indent_prefix}-> Function: {func_name}")
            else:
                no_defs_line = f"    [PY] No functions or classes found in {os.path.basename(file_path)}"
                self._append_to_text_area(no_defs_line, "python_file")
                if self.log_file:
                    self.log_file.write(no_defs_line + "\n")
                # If no definitions, still add a commented line to MAP.txt
                analysis_lines.append(f"#{indent_str}    - No functions or classes found.")

        except SyntaxError as e:
            syntax_error_line = f"    [PY] Syntax Error in {os.path.basename(file_path)}: {e}"
            self._append_to_text_area(syntax_error_line, "python_file")
            if self.log_file:
                self.log_file.write(syntax_error_line + "\n")
            analysis_lines.append(f"#{indent_str}    - Syntax Error: {e}")
            debug_log(f"Syntax Error in {file_path}: {e}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_version, function=current_function)
        except Exception as e:
            general_error_line = f"    [PY] Error analyzing {os.path.basename(file_path)}: {e}"
            self._append_to_text_area(general_error_line, "python_file")
            if self.log_file:
                self.log_file.write(general_error_line + "\n")
            analysis_lines.append(f"#{indent_str}    - Error analyzing: {e}")
            debug_log(f"Error analyzing {file_path}: {e}. Version: {self.current_version}.",
                        file=self.current_file, version=self.current_file, function=current_function)
        return analysis_lines

    def _append_to_text_area(self, text, tag=None):
        """
        Function Description:
        Appends text to the scrolled text area, ensuring the update happens on the main thread.
        Also writes the text to the log file if it's open.

        Inputs:
            text (str): The text to append.
            tag (str, optional): A tag for text styling. Defaults to None.

        Process:
            1. Inserts the text into the `text_area` widget.
            2. Applies the specified tag if provided.
            3. Scrolls to the end to show new content.
            4. Writes the text to `self.log_file` if it's not None.

        Outputs:
            None. Updates the GUI and writes to log file.
        """
        self.root.after(0, lambda: self.text_area.insert(tk.END, text + "\n", tag))
        self.root.after(0, lambda: self.text_area.see(tk.END))

        # Write to log file
        if self.log_file:
            try:
                self.log_file.write(text + "\n")
            except Exception as e:
                # This error handling is for the log file writing itself
                debug_log(f"Error writing to Crawl.log: {e}. Version: {self.current_version}.",
                            file=self.current_file, version=self.current_version, function=inspect.currentframe().f_code.co_name)

    def _open_file(self, file_path, file_description):
        """
        Function Description:
        Opens a specified file using the default system application.

        Inputs:
            file_path (str): The full path to the file to open.
            file_description (str): A description of the file (e.g., "log file").

        Process:
            1. Checks if the file exists.
            2. Uses platform-specific commands to open the file.
            3. Provides feedback in the GUI if the file cannot be opened.

        Outputs:
            None. Opens a file or displays an error.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting to open {file_description}: {file_path}. Version: {self.current_version}.",
                    file=self.current_file, version=self.current_version, function=current_function)

        if not os.path.exists(file_path):
            message = f"Error: {file_description} not found at {file_path}"
            self._append_to_text_area(message, "header")
            debug_log(message, file=self.current_file, version=self.current_version, function=current_function)
            return

        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.uname().sysname == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', file_path], check=True)
            self._append_to_text_area(f"Opened {file_description}: {file_path}", "header")
        except FileNotFoundError:
            message = f"Error: Could not find application to open {file_description}."
            self._append_to_text_area(message, "header")
            debug_log(message, file=self.current_file, version=self.current_version, function=current_function)
        except Exception as e:
            message = f"Error opening {file_description}: {e}"
            self._append_to_text_area(message, "header")
            debug_log(message, file=self.current_file, version=self.current_version, function=current_function)

    def _open_log_file(self):
        """
        Function Description:
        Command for the "Open Log" button. Opens the Crawl.log file.
        """
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Crawl.log")
        self._open_file(log_file_path, "Crawl Log")

    def _open_map_file(self):
        """
        Function Description:
        Command for the "Open Map" button. Opens the MAP.txt file.
        """
        map_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MAP.txt")
        self._open_file(map_file_path, "Program Map")


if __name__ == "__main__":
    root = tk.Tk()
    app = FolderCrawlerApp(root)
    root.mainloop()
