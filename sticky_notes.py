import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3

class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes")
        self.notes = {}
        
        # Database setup
        self.conn = sqlite3.connect("sticky_notes.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT
            )
        """)
        self.conn.commit()
        
        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.create_note)
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Load existing notes
        self.load_notes()
    
    def load_notes(self):
        # Retrieve notes from the database and create sticky notes for each
        self.cursor.execute("SELECT id, content FROM notes")
        for note_id, content in self.cursor.fetchall():
            self.display_note(note_id, content)
    
    def display_note(self, note_id, content=""):
        # Create a sticky note window
        note_window = tk.Toplevel(self.root)
        note_window.title(f"Note {note_id}")
        note_window.geometry("200x200")
        
        text_area = tk.Text(note_window, wrap=tk.WORD)
        text_area.insert("1.0", content)
        text_area.pack(expand=True, fill=tk.BOTH)
        
        close_button = tk.Button(note_window, text="Delete Note", 
                                 command=lambda: self.delete_note(note_id, note_window))
        close_button.pack(fill=tk.X)
        
        # Save the note window and its content in the dictionary
        self.notes[note_id] = {"window": note_window, "content": text_area}
        
        # Bind the text widget to save changes automatically
        text_area.bind("<KeyRelease>", lambda event: self.save_note(note_id, text_area))
    
    def create_note(self):
        # Add a new note to the database
        self.cursor.execute("INSERT INTO notes (content) VALUES ('')")
        self.conn.commit()
        note_id = self.cursor.lastrowid
        self.display_note(note_id)
    
    def save_note(self, note_id, text_area):
        # Update the note content in the database
        content = text_area.get("1.0", tk.END).strip()
        self.cursor.execute("UPDATE notes SET content = ? WHERE id = ?", (content, note_id))
        self.conn.commit()
    
    def delete_note(self, note_id, note_window):
        # Confirm deletion and remove note from the database
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            self.conn.commit()
            note_window.destroy()
            del self.notes[note_id]
    
    def exit_app(self):
        # Close the database connection and exit the application
        self.conn.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()
