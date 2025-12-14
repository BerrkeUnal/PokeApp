import requests
import random
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# draws pokemon names
def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1010"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        names = [item['name'] for item in data['results']]
        return names
    except Exception as e:
        print(f"Failed to fetch Pokémon names: {e}")
        return []

class AutocompleteEntry(ttk.Entry):
    def __init__(self, autocompleteList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocompleteList = sorted(autocompleteList, key=str.lower)
        self.var = self["textvariable"]
        if not self.var:
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)

        self.lb_up = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.lb_up:
                self.lb.destroy()
                self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    x = self.winfo_rootx() - self.master.winfo_rootx()
                    y = self.winfo_rooty() - self.master.winfo_rooty() + self.winfo_height()
                    self.lb.place(x=x, y=y, width=self.winfo_width())
                    self.lb_up = True

                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END,w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

    def move_up(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]

            if index != '0':
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def move_down(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '-1'
            else:
                index = self.lb.curselection()[0]

            if index != tk.END:
                self.lb.selection_clear(first=index)
                index = str(int(index)+1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        pattern = self.var.get().lower()
        return [w for w in self.autocompleteList if w.lower().startswith(pattern)]


class PokemonApp:
    def __init__(self, root, pokemon_names):
        self.root = root
        self.root.title("Pokémon Viewer")

        self.pokemon_names = pokemon_names
        self.favorites = []

        style = ttk.Style(root)
        style.theme_use('clam')

        # Autocomplete Entry
        self.entry = AutocompleteEntry(self.pokemon_names, root, width=30)
        self.entry.grid(row=0, column=0, padx=10, pady=10)

        self.search_btn = ttk.Button(root, text="Search Pokémon", command=self.search_pokemon)
        self.search_btn.grid(row=0, column=1, padx=5, pady=10)

        self.random_btn = ttk.Button(root, text="Random Pokémon", command=self.random_pokemon)
        self.random_btn.grid(row=0, column=2, padx=5, pady=10)

        self.add_fav_btn = ttk.Button(root, text="Add to Favorites", command=self.add_to_favorites)
        self.add_fav_btn.grid(row=0, column=3, padx=10, pady=10)

        self.remove_fav_btn = ttk.Button(root, text="Remove Favorite", command=self.remove_favorite)
        self.remove_fav_btn.grid(row=1, column=3, padx=10, pady=10)

        self.fav_listbox = tk.Listbox(root, width=30, height=15)
        self.fav_listbox.grid(row=2, column=3, rowspan=6, padx=10, pady=5)
        self.fav_listbox.bind('<<ListboxSelect>>', self.on_fav_select)

        self.info_label = ttk.Label(root, text="", justify="left", font=("Arial", 10))
        self.info_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=10)

        self.image_label = ttk.Label(root)
        self.image_label.grid(row=2, column=0, rowspan=3, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(4,3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=3)

        self.current_pokemon_data = None

    def fetch_pokemon(self, name_or_id):
        url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id.lower()}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.current_pokemon_data = data
            self.display_pokemon(data)
            self.display_stats_graph(data)
            self.fetch_evolution_chain(data)
        except requests.exceptions.HTTPError:
            messagebox.showerror("Error", "Pokémon not found. Check the name or ID.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve Pokémon.\n{e}")

    def display_pokemon(self, data):
        name = data['name'].title()
        poke_id = data['id']
        height = data['height']
        weight = data['weight']
        types = [t['type']['name'] for t in data['types']]
        abilities = [a['ability']['name'] for a in data['abilities']]

        info_text = (
            f"Name: {name}\n"
            f"ID: {poke_id}\n"
            f"Height: {height}\n"
            f"Weight: {weight}\n"
            f"Types: {', '.join(types)}\n"
            f"Abilities: {', '.join(abilities)}\n"
        )
        self.info_label.config(text=info_text)

        image_url = data['sprites']['front_default']
        if image_url:
            img_data = requests.get(image_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            self.image_label.config(image=photo)
            self.image_label.image = photo
        else:
            self.image_label.config(image='')

    def display_stats_graph(self, data):
        self.ax.clear()
        stats = data['stats']
        names = [stat['stat']['name'] for stat in stats]
        values = [stat['base_stat'] for stat in stats]

        # Create positions for the x-axis (0, 1, 2, 3...)

        x_positions = range(len(names))

        # Draw the bar chart according to these positions.
        self.ax.bar(x_positions, values, color='skyblue')
        
        self.ax.set_title('Stats')
        self.ax.set_ylim(0, max(values) + 20)
        
        # First, fix the positions of the ticks, then assign the labels.
        self.ax.set_xticks(x_positions)
        self.ax.set_xticklabels(names, rotation=45, ha='right')
        
        self.fig.tight_layout()
        self.canvas.draw()

    def fetch_evolution_chain(self, data):
        species_url = data['species']['url']
        try:
            species_response = requests.get(species_url)
            species_response.raise_for_status()
            species_data = species_response.json()

            evo_url = species_data['evolution_chain']['url']
            evo_response = requests.get(evo_url)
            evo_response.raise_for_status()
            evo_data = evo_response.json()

            evo_chain = []
            current = evo_data['chain']
            while current:
                evo_chain.append(current['species']['name'].title())
                if current['evolves_to']:
                    current = current['evolves_to'][0]
                else:
                    break

            evo_text = "Evolution Chain: " + " -> ".join(evo_chain)
            self.info_label.config(text=self.info_label.cget("text") + "\n" + evo_text)

            moves = data['moves']
            move_names = [move['move']['name'] for move in moves[:10]]
            moves_text = "\nMoves (Top 10): " + ", ".join(move_names)
            self.info_label.config(text=self.info_label.cget("text") + moves_text)

        except Exception as e:
            print(f"Error fetching evolution chain: {e}")

    def search_pokemon(self):
        query = self.entry.get().strip()
        if query:
            self.fetch_pokemon(query)
        else:
            messagebox.showwarning("Input Needed", "Please enter a Pokémon name or ID.")

    def random_pokemon(self):
        random_id = random.randint(1, 1010)
        self.fetch_pokemon(str(random_id))

    def add_to_favorites(self):
        if not self.current_pokemon_data:
            messagebox.showwarning("No Pokémon", "Please search or get a Pokémon first.")
            return
        name = self.current_pokemon_data['name'].title()
        if name not in self.favorites:
            self.favorites.append(name)
            self.fav_listbox.insert(tk.END, name)

    def remove_favorite(self):
        selection = self.fav_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a favorite to remove.")
            return
        index = selection[0]
        name = self.fav_listbox.get(index)
        self.fav_listbox.delete(index)
        self.favorites.remove(name)

    def on_fav_select(self, event):
        if not self.fav_listbox.curselection():
            return
        index = self.fav_listbox.curselection()[0]
        name = self.fav_listbox.get(index)
        self.fetch_pokemon(name)