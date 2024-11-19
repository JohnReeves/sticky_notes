import tkinter as tk
from tkinter import simpledialog, messagebox

class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes")
        self.notes = {}
        
        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.create_note)
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
    
    def create_note(self):
        # Create a new sticky note
        note_id = len(self.notes) + 1
        note_window = tk.Toplevel(self.root)
        note_window.title(f"Note {note_id}")
        note_window.geometry("200x200")
        
        text_area = tk.Text(note_window, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH)
        
        close_button = tk.Button(note_window, text="Delete Note", 
                                 command=lambda: self.delete_note(note_id, note_window))
        close_button.pack(fill=tk.X)
        
        # Store the note window and its content
        self.notes[note_id] = {"window": note_window, "content": text_area}
    
    def delete_note(self, note_id, note_window):
        # Confirm before deleting
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            # Destroy the note window and remove it from the notes dictionary
            note_window.destroy()
            del self.notes[note_id]

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()
