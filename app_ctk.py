import sys
import os
import subprocess
import threading
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from pathlib import Path


# Set appearance mode and VS Code color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# VS Code Color Scheme
VSCODE_COLORS = {
    'bg_dark': '#1e1e1e',           # Editor background
    'bg_darker': '#252526',         # Sidebar background
    'bg_darkest': '#181818',        # Activity bar
    'accent_blue': '#007acc',       # VS Code blue
    'accent_hover': '#094771',      # Hover blue
    'text_primary': '#cccccc',      # Main text
    'text_secondary': '#858585',    # Secondary text
    'border': '#2d2d30',            # Borders
    'selection': '#264f78',         # Selection
    'success': '#4ec9b0',           # Success green
    'error': '#f48771',             # Error red
    'warning': '#ce9178',           # Warning orange
}


class SyntaxHighlighter:
    """Syntax highlighter for text widget"""
    
    def __init__(self, text_widget, language='python'):
        self.text_widget = text_widget
        self.language = language.lower()
        self.configure_tags()
        
    def configure_tags(self):
        """Configure text tags for syntax highlighting"""
        self.text_widget.tag_config("keyword", foreground="#569cd6", font=("Consolas", 11, "bold"))
        self.text_widget.tag_config("string", foreground="#ce9178")
        self.text_widget.tag_config("comment", foreground="#6a9955")
        self.text_widget.tag_config("number", foreground="#b5cea8")
        self.text_widget.tag_config("function", foreground="#dcdcaa")
        self.text_widget.tag_config("class", foreground="#4ec9b0", font=("Consolas", 11, "bold"))
        
    def set_language(self, language):
        """Change highlighting language"""
        self.language = language.lower()
        
    def get_keywords(self):
        """Get keywords for current language"""
        keywords_dict = {
            'python': ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 
                      'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
                      'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
                      'try', 'while', 'with', 'yield', 'self', 'print'],
            'javascript': ['abstract', 'await', 'boolean', 'break', 'case', 'catch', 'class', 'const', 
                          'continue', 'debugger', 'default', 'delete', 'do', 'else', 'enum', 'export', 
                          'extends', 'false', 'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof',
                          'let', 'new', 'null', 'return', 'static', 'super', 'switch', 'this', 'throw', 
                          'true', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'async', 'console'],
            'java': ['abstract', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
                    'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 
                    'float', 'for', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long',
                    'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 
                    'super', 'switch', 'this', 'throw', 'throws', 'try', 'void', 'while'],
            'cpp': ['auto', 'bool', 'break', 'case', 'catch', 'char', 'class', 'const', 'continue', 
                   'default', 'delete', 'do', 'double', 'else', 'enum', 'explicit', 'extern', 'false', 
                   'float', 'for', 'friend', 'if', 'inline', 'int', 'long', 'namespace', 'new', 'nullptr',
                   'operator', 'private', 'protected', 'public', 'return', 'short', 'signed', 'sizeof',
                   'static', 'struct', 'switch', 'template', 'this', 'throw', 'true', 'try', 'typedef',
                   'using', 'virtual', 'void', 'while'],
            'c': ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else',
                 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 
                 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 
                 'unsigned', 'void', 'volatile', 'while'],
        }
        return keywords_dict.get(self.language, keywords_dict['python'])
    
    def highlight(self, event=None):
        """Apply syntax highlighting to the text"""
        # Remove all existing tags
        for tag in ["keyword", "string", "comment", "number", "function", "class"]:
            self.text_widget.tag_remove(tag, "1.0", "end")
        
        content = self.text_widget.get("1.0", "end-1c")
        
        # Highlight keywords
        keywords = self.get_keywords()
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, content):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.text_widget.tag_add("keyword", start_idx, end_idx)
        
        # Highlight strings
        for match in re.finditer(r'"[^"\\]*(\\.[^"\\]*)*"', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text_widget.tag_add("string", start_idx, end_idx)
            
        for match in re.finditer(r"'[^'\\]*(\\.[^'\\]*)*'", content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text_widget.tag_add("string", start_idx, end_idx)
        
        # Highlight comments
        if self.language in ['python', 'ruby', 'bash']:
            comment_pattern = r'#[^\n]*'
        elif self.language in ['javascript', 'java', 'cpp', 'c', 'csharp']:
            comment_pattern = r'//[^\n]*'
        else:
            comment_pattern = r'#[^\n]*'
            
        for match in re.finditer(comment_pattern, content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text_widget.tag_add("comment", start_idx, end_idx)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text_widget.tag_add("number", start_idx, end_idx)
        
        # Highlight functions
        for match in re.finditer(r'\b\w+(?=\()', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text_widget.tag_add("function", start_idx, end_idx)


class AutocompletePopup(tk.Toplevel):
    """Autocomplete popup window"""
    
    def __init__(self, parent, text_widget):
        super().__init__(parent)
        self.text_widget = text_widget
        self.withdraw()  # Hide initially
        self.overrideredirect(True)  # Remove window decorations
        
        # Configure window
        self.configure(bg="#252526", relief="solid", borderwidth=1)
        
        # Listbox for suggestions
        self.listbox = tk.Listbox(
            self,
            bg="#252526",
            fg="#cccccc",
            selectbackground="#094771",
            selectforeground="white",
            font=("Consolas", 10),
            height=10,
            width=30,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.listbox.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Bind selection
        self.listbox.bind("<Double-Button-1>", lambda e: self.insert_selection())
        self.listbox.bind("<Return>", lambda e: self.insert_selection())
        
        self.suggestions = []
        self.current_word = ""
        
    def show_suggestions(self, suggestions, word, x, y):
        """Show autocomplete suggestions"""
        if not suggestions:
            self.hide()
            return
            
        self.suggestions = suggestions
        self.current_word = word
        
        # Clear and populate listbox
        self.listbox.delete(0, tk.END)
        for suggestion in suggestions[:15]:  # Limit to 15 suggestions
            self.listbox.insert(tk.END, suggestion)
        
        # Select first item
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self.listbox.activate(0)
        
        # Position near cursor
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.lift()
        
    def hide(self):
        """Hide autocomplete popup"""
        self.withdraw()
        
    def insert_selection(self):
        """Insert selected suggestion"""
        selection = self.listbox.curselection()
        if selection:
            selected = self.listbox.get(selection[0])
            
            # Remove the partial word
            self.text_widget.delete(f"insert-{len(self.current_word)}c", "insert")
            
            # Insert the full word
            self.text_widget.insert("insert", selected)
            
            self.hide()
            self.text_widget.focus_set()
            
    def navigate(self, direction):
        """Navigate suggestions with arrow keys"""
        current = self.listbox.curselection()
        if not current:
            return
            
        index = current[0]
        size = self.listbox.size()
        
        if direction == "up" and index > 0:
            self.listbox.selection_clear(index)
            self.listbox.selection_set(index - 1)
            self.listbox.activate(index - 1)
            self.listbox.see(index - 1)
        elif direction == "down" and index < size - 1:
            self.listbox.selection_clear(index)
            self.listbox.selection_set(index + 1)
            self.listbox.activate(index + 1)
            self.listbox.see(index + 1)


class LineNumbers(tk.Canvas):
    """Line numbers widget"""
    
    def __init__(self, parent, text_widget, **kwargs):
        super().__init__(parent, width=50, bg="#2b2b2b", highlightthickness=0, **kwargs)
        self.text_widget = text_widget
        
    def redraw(self, *args):
        """Redraw line numbers"""
        self.delete("all")
        
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill="#858585", font=("Consolas", 10))
            i = self.text_widget.index(f"{i}+1line")


class CodeEditor(ctk.CTkFrame):
    """Code editor with line numbers and syntax highlighting"""
    
    def __init__(self, parent, language='python'):
        super().__init__(parent, fg_color="#1e1e1e")
        
        self.language = language
        self.file_path = None
        
        # Create text widget with scrollbar
        text_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        text_frame.pack(fill="both", expand=True)
        
        # Line numbers
        self.line_numbers = LineNumbers(text_frame, None)
        self.line_numbers.pack(side="left", fill="y")
        
        # Text widget
        self.text_widget = tk.Text(
            text_frame,
            wrap="none",
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            font=("Consolas", 11),
            undo=True,
            maxundo=-1
        )
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        # Update line numbers reference
        self.line_numbers.text_widget = self.text_widget
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, command=self.text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=scrollbar.set)
        
        # Syntax highlighter
        self.highlighter = SyntaxHighlighter(self.text_widget, language)
        
        # Autocomplete popup
        self.autocomplete = AutocompletePopup(self, self.text_widget)
        
        # Bind events
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<KeyPress>", self.on_key_press)
        self.text_widget.bind("<Control-space>", lambda e: self.show_autocomplete())
        self.text_widget.bind("<MouseWheel>", lambda e: self.line_numbers.redraw())
        self.text_widget.bind("<Button-1>", lambda e: self.on_click())
        
    def on_click(self):
        """Handle mouse click"""
        self.autocomplete.hide()
        self.line_numbers.redraw()
        
    def on_key_press(self, event):
        """Handle key press for autocomplete navigation"""
        # Handle autocomplete navigation when popup is visible
        if self.autocomplete.winfo_viewable():
            if event.keysym == "Escape":
                self.autocomplete.hide()
                return "break"
            elif event.keysym == "Return" or event.keysym == "Tab":
                self.autocomplete.insert_selection()
                return "break"
            elif event.keysym == "Up":
                self.autocomplete.navigate("up")
                return "break"
            elif event.keysym == "Down":
                self.autocomplete.navigate("down")
                return "break"
    
    def on_key_release(self, event):
        """Handle key release for syntax highlighting and autocomplete"""
        self.highlighter.highlight()
        self.line_numbers.redraw()
        
        # Trigger autocomplete on alphanumeric keys
        if event.char.isalnum() or event.char == '_':
            self.show_autocomplete()
        elif event.keysym in ["BackSpace", "Delete"]:
            # Update autocomplete on deletion
            current_word = self.get_current_word()
            if len(current_word) >= 2:
                self.show_autocomplete()
            else:
                self.autocomplete.hide()
        elif event.keysym in ["space", "parenleft", "parenright", "bracketleft", "bracketright", "semicolon", "comma"]:
            self.autocomplete.hide()
    
    def get_current_word(self):
        """Get the word currently being typed"""
        # Get cursor position
        cursor_pos = self.text_widget.index("insert")
        line, col = map(int, cursor_pos.split('.'))
        
        # Get current line text
        line_text = self.text_widget.get(f"{line}.0", f"{line}.end")
        
        # Find word boundaries
        start = col
        while start > 0 and (line_text[start-1].isalnum() or line_text[start-1] == '_'):
            start -= 1
        
        word = line_text[start:col]
        return word
    
    def get_all_words(self):
        """Get all words from the text for suggestions"""
        content = self.text_widget.get("1.0", "end-1c")
        # Extract all words (alphanumeric + underscore)
        words = set(re.findall(r'\b\w+\b', content))
        return sorted(words)
    
    def get_suggestions(self, word):
        """Get autocomplete suggestions for a word"""
        if len(word) < 2:  # Only show suggestions for 2+ characters
            return []
        
        suggestions = set()
        
        # Add language keywords
        keywords = self.highlighter.get_keywords()
        for keyword in keywords:
            if keyword.lower().startswith(word.lower()):
                suggestions.add(keyword)
        
        # Add words from current file
        all_words = self.get_all_words()
        for w in all_words:
            if w.lower().startswith(word.lower()) and w != word:
                suggestions.add(w)
        
        # Add common built-in functions for Python
        if self.language == 'python':
            builtins = ['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 
                       'tuple', 'open', 'read', 'write', 'input', 'type', 'isinstance', 
                       'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 
                       'min', 'max', 'abs', 'round', 'pow', 'format', 'split', 'join', 
                       'append', 'extend', 'insert', 'remove', 'pop', 'index', 'count',
                       'keys', 'values', 'items', 'get', 'update', 'clear']
            for builtin in builtins:
                if builtin.lower().startswith(word.lower()):
                    suggestions.add(builtin)
        
        # Add common JavaScript functions
        elif self.language == 'javascript':
            js_funcs = ['console', 'log', 'const', 'let', 'var', 'function', 'return', 
                       'document', 'getElementById', 'querySelector', 'addEventListener',
                       'setTimeout', 'setInterval', 'parseInt', 'parseFloat', 'isNaN',
                       'JSON', 'stringify', 'parse', 'Array', 'Object', 'String', 'Number',
                       'push', 'pop', 'shift', 'unshift', 'slice', 'splice', 'map', 'filter',
                       'reduce', 'forEach', 'length', 'indexOf', 'includes']
            for func in js_funcs:
                if func.lower().startswith(word.lower()):
                    suggestions.add(func)
        
        return sorted(suggestions)
    
    def show_autocomplete(self):
        """Show autocomplete suggestions"""
        current_word = self.get_current_word()
        
        if len(current_word) < 2:
            self.autocomplete.hide()
            return
        
        suggestions = self.get_suggestions(current_word)
        
        if not suggestions:
            self.autocomplete.hide()
            return
        
        # Get cursor position on screen
        cursor_bbox = self.text_widget.bbox("insert")
        if cursor_bbox:
            x = self.text_widget.winfo_rootx() + cursor_bbox[0]
            y = self.text_widget.winfo_rooty() + cursor_bbox[1] + cursor_bbox[3]
            
            self.autocomplete.show_suggestions(suggestions, current_word, x, y)
        
    def get_text(self):
        """Get text content"""
        return self.text_widget.get("1.0", "end-1c")
    
    def set_text(self, content):
        """Set text content"""
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", content)
        self.highlighter.highlight()
        self.line_numbers.redraw()
        
    def set_language(self, language):
        """Set programming language"""
        self.language = language
        self.highlighter.set_language(language)
        self.highlighter.highlight()


class OutputPanel(ctk.CTkTextbox):
    """Output panel for displaying program output"""
    
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="#1e1e1e",
            text_color="#d4d4d4",
            font=("Consolas", 10),
            wrap="word"
        )
        
    def append_output(self, text, color='white'):
        """Append text to output"""
        self.insert("end", text)
        self.see("end")
        
    def clear_output(self):
        """Clear output panel"""
        self.delete("1.0", "end")


class FileExplorer(ctk.CTkFrame):
    """File explorer widget"""
    
    def __init__(self, parent, on_file_open):
        super().__init__(parent, fg_color="#252526")
        self.on_file_open = on_file_open
        
        # Title
        title = ctk.CTkLabel(self, text="📁 File Explorer", font=("Segoe UI", 12, "bold"))
        title.pack(pady=5)
        
        # Treeview for files
        self.tree = ttk.Treeview(self, selectmode='browse', show='tree')
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Load current directory
        self.load_directory(os.getcwd())
        
    def load_directory(self, path):
        """Load directory structure"""
        self.tree.delete(*self.tree.get_children())
        self.root_path = path
        
        node = self.tree.insert("", "end", text=os.path.basename(path), open=True, values=[path])
        self.load_tree(node, path)
        
    def load_tree(self, parent, path):
        """Recursively load directory tree"""
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    node = self.tree.insert(parent, "end", text=f"📁 {item}", values=[item_path])
                    # Load subdirectories (limited depth)
                    try:
                        if len(os.listdir(item_path)) > 0:
                            self.tree.insert(node, "end", text="...")  # Placeholder
                    except:
                        pass
                else:
                    self.tree.insert(parent, "end", text=f"📄 {item}", values=[item_path])
        except PermissionError:
            pass
            
    def on_double_click(self, event):
        """Handle double-click on file"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if values:
                path = values[0]
                if os.path.isfile(path):
                    self.on_file_open(path)


class ActivityBar(ctk.CTkFrame):
    """VS Code-style activity bar on the left"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, fg_color=VSCODE_COLORS['bg_darkest'], width=50)
        self.callbacks = callbacks
        
        # Explorer button
        self.explorer_btn = ctk.CTkButton(
            self, text="📁", width=48, height=48,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color=VSCODE_COLORS['accent_hover'],
            command=lambda: callbacks['toggle_explorer']()
        )
        self.explorer_btn.pack(pady=5)
        
        # Search button
        self.search_btn = ctk.CTkButton(
            self, text="🔍", width=48, height=48,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color=VSCODE_COLORS['accent_hover'],
            command=lambda: callbacks.get('search', lambda: None)()
        )
        self.search_btn.pack(pady=5)
        
        # Run button
        self.run_btn = ctk.CTkButton(
            self, text="▶️", width=48, height=48,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color=VSCODE_COLORS['accent_hover'],
            command=lambda: callbacks['run']()
        )
        self.run_btn.pack(pady=5)
        
        # Settings button (bottom)
        self.settings_btn = ctk.CTkButton(
            self, text="⚙️", width=48, height=48,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color=VSCODE_COLORS['accent_hover'],
            command=lambda: callbacks.get('settings', lambda: None)()
        )
        self.settings_btn.pack(side="bottom", pady=5)


class IDEApp(ctk.CTk):
    """Main IDE Application - VS Code Style"""
    
    def __init__(self):
        super().__init__()
        
        self.title("VS Code IDE - CustomTkinter")
        self.geometry("1400x900")
        self.configure(fg_color=VSCODE_COLORS['bg_dark'])
        
        # Variables
        self.current_file = None
        self.running_process = None
        self.editors = []  # List of editor tabs
        self.explorer_visible = True
        
        # Create UI
        self.create_activity_bar()
        self.create_main_layout()
        self.create_statusbar()
        
        # Create first editor tab
        self.new_file()
        
        # Bind shortcuts
        self.bind_shortcuts()
        
    def create_activity_bar(self):
        """Create VS Code-style activity bar"""
        callbacks = {
            'toggle_explorer': self.toggle_explorer,
            'run': self.run_code,
            'search': lambda: messagebox.showinfo("Search", "Search feature coming soon!"),
            'settings': lambda: messagebox.showinfo("Settings", "Settings coming soon!")
        }
        self.activity_bar = ActivityBar(self, callbacks)
        self.activity_bar.pack(side="left", fill="y")
        
    def toggle_explorer(self):
        """Toggle file explorer visibility"""
        if self.explorer_visible:
            self.sidebar_frame.pack_forget()
            self.explorer_visible = False
        else:
            self.sidebar_frame.pack(side="left", fill="y", after=self.activity_bar)
            self.explorer_visible = True
        
    def create_main_layout(self):
        """Create main layout with sidebar, editor, and output"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color=VSCODE_COLORS['bg_dark'])
        main_container.pack(side="left", fill="both", expand=True)
        
        # Top section (menubar)
        self.create_menubar(main_container)
        
        # Content area
        content_frame = ctk.CTkFrame(main_container, fg_color=VSCODE_COLORS['bg_dark'])
        content_frame.pack(fill="both", expand=True)
        
        # Sidebar with file explorer
        self.sidebar_frame = ctk.CTkFrame(content_frame, fg_color=VSCODE_COLORS['bg_darker'], width=280)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        # Explorer title
        explorer_title = ctk.CTkFrame(self.sidebar_frame, fg_color=VSCODE_COLORS['bg_darker'], height=35)
        explorer_title.pack(fill="x", padx=5, pady=5)
        
        title_label = ctk.CTkLabel(
            explorer_title, 
            text="EXPLORER",
            font=("Segoe UI", 11, "bold"),
            text_color=VSCODE_COLORS['text_primary']
        )
        title_label.pack(side="left", padx=5)
        
        # File explorer
        self.file_explorer = FileExplorer(self.sidebar_frame, self.load_file)
        self.file_explorer.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Editor section
        editor_frame = ctk.CTkFrame(content_frame, fg_color=VSCODE_COLORS['bg_dark'])
        editor_frame.pack(side="left", fill="both", expand=True)
        
        # Tab bar area
        tab_area = ctk.CTkFrame(editor_frame, fg_color=VSCODE_COLORS['bg_darker'], height=35)
        tab_area.pack(fill="x")
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(editor_frame)
        self.notebook.pack(fill="both", expand=True)
        self.style_notebook()
        
        # Output panel with title
        output_container = ctk.CTkFrame(editor_frame, fg_color=VSCODE_COLORS['bg_darker'])
        output_container.pack(fill="x", pady=(2, 0))
        
        output_header = ctk.CTkFrame(output_container, fg_color=VSCODE_COLORS['bg_darker'], height=30)
        output_header.pack(fill="x")
        
        output_title = ctk.CTkLabel(
            output_header,
            text="  OUTPUT",
            font=("Segoe UI", 10, "bold"),
            text_color=VSCODE_COLORS['text_primary'],
            anchor="w"
        )
        output_title.pack(side="left", fill="x", padx=10)
        
        # Clear button in output header
        clear_output_btn = ctk.CTkButton(
            output_header,
            text="🗑",
            width=30,
            height=25,
            fg_color="transparent",
            hover_color=VSCODE_COLORS['accent_hover'],
            command=self.clear_output
        )
        clear_output_btn.pack(side="right", padx=5)
        
        self.output_panel = OutputPanel(output_container)
        self.output_panel.pack(fill="both", expand=True, padx=5, pady=5)
        self.output_panel.configure(height=180)
    
    def create_menubar(self, parent):
        """Create VS Code-style menu bar"""
        menubar = ctk.CTkFrame(parent, fg_color=VSCODE_COLORS['bg_darker'], height=30)
        menubar.pack(fill="x")
        
        # File menu
        file_label = ctk.CTkLabel(menubar, text="  File  ", text_color=VSCODE_COLORS['text_primary'])
        file_label.pack(side="left", padx=5)
        file_label.bind("<Button-1>", lambda e: self.show_file_menu(e))
        
        # Edit menu
        edit_label = ctk.CTkLabel(menubar, text="  Edit  ", text_color=VSCODE_COLORS['text_primary'])
        edit_label.pack(side="left", padx=5)
        
        # Run menu
        run_label = ctk.CTkLabel(menubar, text="  Run  ", text_color=VSCODE_COLORS['text_primary'])
        run_label.pack(side="left", padx=5)
        run_label.bind("<Button-1>", lambda e: self.show_run_menu(e))
        
        # View menu
        view_label = ctk.CTkLabel(menubar, text="  View  ", text_color=VSCODE_COLORS['text_primary'])
        view_label.pack(side="left", padx=5)
        
        # Help menu
        help_label = ctk.CTkLabel(menubar, text="  Help  ", text_color=VSCODE_COLORS['text_primary'])
        help_label.pack(side="left", padx=5)
        
    def show_file_menu(self, event):
        """Show file menu options"""
        menu = tk.Menu(self, tearoff=0, bg=VSCODE_COLORS['bg_darker'], fg=VSCODE_COLORS['text_primary'])
        menu.add_command(label="New File          Ctrl+N", command=self.new_file)
        menu.add_command(label="Open File         Ctrl+O", command=self.open_file)
        menu.add_command(label="Save              Ctrl+S", command=self.save_file)
        menu.add_command(label="Save As           Ctrl+Shift+S", command=self.save_file_as)
        menu.add_separator()
        menu.add_command(label="Exit              Alt+F4", command=self.quit)
        menu.post(event.x_root, event.y_root)
        
    def show_run_menu(self, event):
        """Show run menu options"""
        menu = tk.Menu(self, tearoff=0, bg=VSCODE_COLORS['bg_darker'], fg=VSCODE_COLORS['text_primary'])
        menu.add_command(label="Run Code          F5", command=self.run_code)
        menu.add_command(label="Debug             F9", command=self.debug_code)
        menu.add_command(label="Build             Ctrl+B", command=self.build_project)
        menu.add_separator()
        menu.add_command(label="Stop Process      Shift+F5", command=self.stop_process)
        menu.post(event.x_root, event.y_root)
    
    def style_notebook(self):
        """Style the notebook to look like VS Code tabs"""
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure('TNotebook', 
            background=VSCODE_COLORS['bg_dark'],
            borderwidth=0
        )
        style.configure('TNotebook.Tab',
            background=VSCODE_COLORS['bg_darker'],
            foreground=VSCODE_COLORS['text_primary'],
            padding=[15, 8],
            borderwidth=0
        )
        style.map('TNotebook.Tab',
            background=[('selected', VSCODE_COLORS['bg_dark'])],
            foreground=[('selected', VSCODE_COLORS['text_primary'])]
        )
        
    def create_statusbar(self):
        """Create VS Code-style status bar"""
        statusbar_frame = ctk.CTkFrame(self, fg_color=VSCODE_COLORS['accent_blue'], height=22)
        statusbar_frame.pack(side="bottom", fill="x")
        
        # Left side - file info
        self.status_left = ctk.CTkLabel(
            statusbar_frame,
            text="  Ready",
            anchor="w",
            text_color="white",
            font=("Segoe UI", 9)
        )
        self.status_left.pack(side="left", fill="x", expand=True)
        
        # Right side - language, encoding, position
        self.status_right = ctk.CTkLabel(
            statusbar_frame,
            text="Python  |  UTF-8  |  Ln 1, Col 1  ",
            anchor="e",
            text_color="white",
            font=("Segoe UI", 9)
        )
        self.status_right.pack(side="right")
        
    def update_statusbar(self, message):
        """Update status bar with message"""
        self.status_left.configure(text=f"  {message}")
        
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<F5>", lambda e: self.run_code())
        self.bind("<F9>", lambda e: self.debug_code())
        self.bind("<Shift-F5>", lambda e: self.stop_process())
        self.bind("<Control-b>", lambda e: self.build_project())
        
    def detect_language(self, filename):
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python', '.pyw': 'python',
            '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.html': 'html', '.htm': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.sh': 'bash',
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext_map.get(ext, 'python')
        
    def get_current_editor(self):
        """Get currently active editor"""
        try:
            current_tab = self.notebook.index(self.notebook.select())
            return self.editors[current_tab]
        except:
            return None
            
    def new_file(self):
        """Create new file tab"""
        editor = CodeEditor(self.notebook)
        self.editors.append(editor)
        self.notebook.add(editor, text="Untitled")
        self.notebook.select(len(self.editors) - 1)
        self.update_statusbar("New file created")
        
    def open_file(self):
        """Open file dialog"""
        filename = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("All Files", "*.*"), ("Python", "*.py"), ("JavaScript", "*.js")]
        )
        if filename:
            self.load_file(filename)
            
    def load_file(self, filename):
        """Load file into editor"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            language = self.detect_language(filename)
            editor = CodeEditor(self.notebook, language)
            editor.file_path = filename
            editor.set_text(content)
            
            self.editors.append(editor)
            tab_name = os.path.basename(filename)
            self.notebook.add(editor, text=tab_name)
            self.notebook.select(len(self.editors) - 1)
            
            self.current_file = filename
            self.title(f"VS Code IDE - {filename}")
            self.update_statusbar(f"Opened {filename} ({language})")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
            
    def save_file(self):
        """Save current file"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        if hasattr(editor, 'file_path') and editor.file_path:
            try:
                with open(editor.file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.get_text())
                self.update_statusbar(f"Saved {editor.file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Save file with new name"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Python", "*.py"), ("JavaScript", "*.js")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(editor.get_text())
                editor.file_path = filename
                
                tab_index = self.editors.index(editor)
                self.notebook.tab(tab_index, text=os.path.basename(filename))
                self.update_statusbar(f"Saved as {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                
    def clear_output(self):
        """Clear output panel"""
        self.output_panel.clear_output()
        self.update_statusbar("Output cleared")
        
    def get_interpreter_command(self, language, filename):
        """Get command to run file"""
        commands = {
            'python': ['python', filename],
            'javascript': ['node', filename],
            'java': ['java', filename.replace('.java', '')],
            'cpp': [filename.replace('.cpp', '.exe')],
            'c': [filename.replace('.c', '.exe')],
            'ruby': ['ruby', filename],
            'go': ['go', 'run', filename],
            'php': ['php', filename],
            'bash': ['bash', filename],
        }
        return commands.get(language, None)
        
    def run_code(self):
        """Run current file"""
        editor = self.get_current_editor()
        if not editor or not hasattr(editor, 'file_path') or not editor.file_path:
            messagebox.showwarning("No File", "Please save the file before running.")
            return
            
        filename = editor.file_path
        language = self.detect_language(filename)
        
        # Save first
        self.save_file()
        
        # Clear output
        self.output_panel.clear_output()
        self.output_panel.append_output(f"▶ Running {os.path.basename(filename)}...\n")
        self.output_panel.append_output(f"Language: {language}\n")
        self.output_panel.append_output("-" * 50 + "\n")
        
        # Get command
        command = self.get_interpreter_command(language, filename)
        if not command:
            self.output_panel.append_output(f"Error: No interpreter found for {language}\n")
            return
            
        # Run in thread
        def run_process():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(filename)
                )
                self.running_process = process
                
                # Read output
                stdout, stderr = process.communicate()
                
                if stdout:
                    self.output_panel.append_output(stdout)
                if stderr:
                    self.output_panel.append_output(stderr)
                    
                self.output_panel.append_output("\n" + "-" * 50 + "\n")
                if process.returncode == 0:
                    self.output_panel.append_output(f"✓ Process finished successfully\n")
                else:
                    self.output_panel.append_output(f"✗ Process finished with errors (exit code: {process.returncode})\n")
                    
                self.running_process = None
                self.update_statusbar(f"Process finished with exit code {process.returncode}")
            except Exception as e:
                self.output_panel.append_output(f"\nError: {str(e)}\n")
                self.running_process = None
                
        threading.Thread(target=run_process, daemon=True).start()
        self.update_statusbar(f"Running {os.path.basename(filename)}...")
        
    def stop_process(self):
        """Stop running process"""
        if self.running_process:
            self.running_process.kill()
            self.output_panel.append_output("\n⬛ Process terminated by user\n")
            self.update_statusbar("Process stopped")
            self.running_process = None
        else:
            self.update_statusbar("No process running")
            
    def debug_code(self):
        """Debug current file"""
        editor = self.get_current_editor()
        if not editor or not hasattr(editor, 'file_path') or not editor.file_path:
            messagebox.showwarning("No File", "Please save the file before debugging.")
            return
            
        self.output_panel.clear_output()
        self.output_panel.append_output("🐛 Debugging feature - Running in normal mode\n")
        self.output_panel.append_output("For advanced debugging, use external debuggers (pdb, gdb, etc.)\n\n")
        self.run_code()
        
    def build_project(self):
        """Build/compile current file"""
        editor = self.get_current_editor()
        if not editor or not hasattr(editor, 'file_path') or not editor.file_path:
            messagebox.showwarning("No File", "Please save the file before building.")
            return
            
        filename = editor.file_path
        language = self.detect_language(filename)
        
        # Save first
        self.save_file()
        
        # Clear output
        self.output_panel.clear_output()
        self.output_panel.append_output(f"🔨 Building {os.path.basename(filename)}...\n")
        self.output_panel.append_output(f"Language: {language}\n")
        self.output_panel.append_output("-" * 50 + "\n")
        
        # Build commands
        build_commands = {
            'java': ['javac', filename],
            'cpp': ['g++', filename, '-o', filename.replace('.cpp', '.exe'), '-std=c++17'],
            'c': ['gcc', filename, '-o', filename.replace('.c', '.exe')],
            'rust': ['rustc', filename, '-o', filename.replace('.rs', '.exe')],
            'go': ['go', 'build', filename],
            'typescript': ['tsc', filename],
        }
        
        command = build_commands.get(language)
        if not command:
            self.output_panel.append_output(f"Note: {language} doesn't require compilation.\n")
            self.output_panel.append_output("You can run it directly with the Run button.\n")
            return
            
        # Build in thread
        def build_process():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(filename)
                )
                
                stdout, stderr = process.communicate()
                
                if stdout:
                    self.output_panel.append_output(stdout)
                if stderr:
                    self.output_panel.append_output(stderr)
                    
                self.output_panel.append_output("\n" + "-" * 50 + "\n")
                if process.returncode == 0:
                    self.output_panel.append_output("✓ Build successful!\n")
                else:
                    self.output_panel.append_output(f"✗ Build failed (exit code: {process.returncode})\n")
                    
                self.update_statusbar(f"Build finished with exit code {process.returncode}")
            except Exception as e:
                self.output_panel.append_output(f"\nError: {str(e)}\n")
                
        threading.Thread(target=build_process, daemon=True).start()
        self.update_statusbar(f"Building {os.path.basename(filename)}...")


def main():
    app = IDEApp()
    app.mainloop()


if __name__ == '__main__':
    main()
