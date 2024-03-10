import re
from urllib.request import urlopen
from urllib.error import URLError
import sqlite3
import tkinter as tk
from tkinter import simpledialog

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS sites (url TEXT, content TEXT)")

    def add_site(self, url, content):
        self.cursor.execute("INSERT INTO sites (url, content) VALUES (?, ?)", (url, content))
        self.connection.commit()

    def clear_database(self):
        self.cursor.execute("DELETE FROM sites")
        self.connection.commit()

    def search_in_db(self, search_term):
        self.cursor.execute("SELECT url FROM sites WHERE content LIKE ?", ('%' + search_term + '%',))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()

class SiteParser:
    def __init__(self, url):
        self.url = url

    def parse(self):
        try:
            response = urlopen(self.url)
            html = response.read().decode('utf-8')
            content = self.extract_text(html)
            return content
        except URLError as e:
            print("Error reading URL:", e)
            return ""

    def extract_text(self, html):
        text = re.sub('<[^<]+?>', '', html)  # Удаляем все HTML-теги
        return text

class UserInterface:
    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.root.title("Web Search")

        self.add_site_button = tk.Button(self.root, text="Add Site", command=self.add_site_to_db)
        self.add_site_button.pack()

        self.clear_database_button = tk.Button(self.root, text="Clear Database", command=self.clear_database)
        self.clear_database_button.pack()

        self.search_label = tk.Label(self.root, text="Enter search term:")
        self.search_label.pack()

        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()

        self.search_button = tk.Button(self.root, text="Search", command=self.search)
        self.search_button.pack()

        self.search_results_label = tk.Label(self.root, text="Search Results:")
        self.search_results_label.pack()

        self.search_results_text = tk.Text(self.root, height=10, width=50)
        self.search_results_text.pack()

        self.root.mainloop()

    def add_site_to_db(self):
        url = simpledialog.askstring("Add Site", "Enter URL:")
        if url:
            parser = SiteParser(url)
            content = parser.parse()
            self.db.add_site(url, content)

    def clear_database(self):
        self.db.clear_database()

    def search(self):
        search_term = self.search_entry.get()
        if search_term:
            results = self.db.search_in_db(search_term)
            self.display_search_results(results)

    def display_search_results(self, results):
        self.search_results_text.delete(1.0, tk.END)
        for result in results:
            self.search_results_text.insert(tk.END, result[0] + "\n")

def run():
    db = Database("sites.db")
    ui = UserInterface(db)

if __name__ == "__main__":
    run()


