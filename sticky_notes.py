import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import sqlite3

class StickyNotesApp:
    def __init__(self, root):
        """Initialize the Sticky Notes application."""
        self.root = root
        self.root.title("Sticky Notes")
        self.notes = {}
        
        # Database setup
        self.conn = sqlite3.connect("sticky_notes.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                color TEXT
            )
        """)
        self.conn.commit()
        
        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.create_note, accelerator="Ctrl+N")
        file_menu.add_command(label="List Notes", command=self.list_notes, accelerator="Ctrl+L")
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Key bindings
        self.root.bind("<Control-n>", lambda event: self.create_note())
        self.root.bind("<Control-l>", lambda event: self.list_notes())
        
        # Load existing notes
        # self.load_notes()
    
    def load_notes(self):
        """Load existing notes from the database and display them."""
        self.cursor.execute("SELECT id, content, color FROM notes")
        for note_id, content, color in self.cursor.fetchall():
            self.display_note(note_id, content, color)
    
    def display_note(self, note_id, content="", color="yellow"):
        """Display a sticky note in a separate window."""
        note_window = tk.Toplevel(self.root)
        note_window.title(f"Note {note_id}")
        note_window.geometry("200x200")
        note_window.resizable(True, True)
        
        # Create the text widget
        text_area = tk.Text(note_window, wrap=tk.WORD, bg=color, fg="black")
        text_area.insert("1.0", content)
        text_area.pack(expand=True, fill=tk.BOTH)
        
        # Bind the text widget to save changes automatically
        text_area.bind("<KeyRelease>", lambda event: self.save_note(note_id, text_area))
        
        # Context menu
        note_menu = tk.Menu(note_window, tearoff=0)
        note_menu.add_command(label="Change Color", command=lambda: self.change_color(note_id, text_area))
        note_menu.add_command(label="Export to File", command=lambda: self.export_to_file(note_id, text_area))
        note_menu.add_command(label="Delete Note", command=lambda: self.delete_note(note_id, note_window))
        
        # Right-click to show the context menu
        text_area.bind("<Button-3>", lambda event: self.show_context_menu(event, note_menu))
        
        # Save the note window and its content in the dictionary
        self.notes[note_id] = {"window": note_window, "content": text_area, "color": color}
    
    def show_context_menu(self, event, menu):
        """Display a context menu at the cursor location."""
        menu.tk_popup(event.x_root, event.y_root)
    
    def create_note(self):
        """Create a new sticky note and add it to the database."""
        self.cursor.execute("INSERT INTO notes (content, color) VALUES ('', 'yellow')")
        self.conn.commit()
        note_id = self.cursor.lastrowid
        self.display_note(note_id)
    
    def save_note(self, note_id, text_area):
        """Save the note content and color to the database."""
        content = text_area.get("1.0", tk.END).strip()
        color = text_area.cget("bg")
        self.cursor.execute("UPDATE notes SET content = ?, color = ? WHERE id = ?", (content, color, note_id))
        self.conn.commit()
    
    def delete_note(self, note_id, note_window):
        """Delete a note from the database and close its window."""
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            self.conn.commit()
            note_window.destroy()
            del self.notes[note_id]
    
    def change_color(self, note_id, text_area):
        """Change the background color of a note."""
        color = colorchooser.askcolor(title="Choose Note Color")[1]
        if color:
            text_area.config(bg=color)
            self.save_note(note_id, text_area)
    
    def export_to_file(self, note_id, text_area):
        """Export note content to a text file."""
        content = text_area.get("1.0", tk.END).strip()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(content)
            messagebox.showinfo("Export Successful", f"Note {note_id} exported to {file_path}")
    
    def list_notes(self):
        """List all notes saved in the database."""
        list_window = tk.Toplevel(self.root)
        list_window.title("List of Notes")
        list_window.geometry("300x400")
        
        list_box = tk.Listbox(list_window)
        list_box.pack(expand=True, fill=tk.BOTH)
        
        self.cursor.execute("SELECT id, content FROM notes")
        for note_id, content in self.cursor.fetchall():
            preview = content[:30] + "..." if len(content) > 30 else content
            list_box.insert(tk.END, f"Note {note_id}: {preview}")
        
        def open_note(event):
            """Open the selected note when double-clicked."""
            selection = list_box.curselection()
            if selection:
                note_id = int(list_box.get(selection[0]).split()[1][:-1])
                self.cursor.execute("SELECT content, color FROM notes WHERE id = ?", (note_id,))
                content, color = self.cursor.fetchone()
                self.display_note(note_id, content, color)
        
        list_box.bind("<Double-1>", open_note)
    
    def exit_app(self):
        """Close the database connection and exit the application."""
        self.conn.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()
