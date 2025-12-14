import tkinter as tk
from pokemon_ui import PokemonApp, get_all_pokemon_names

if __name__ == "__main__":
    # Create main window
    root = tk.Tk()
    
    # Extract names (data preparation)
    print("Loading Pokémon data, please wait...")
    pokemon_names = get_all_pokemon_names()
    
    # Start the App
    app = PokemonApp(root, pokemon_names)
    
    # Loop
    root.mainloop()