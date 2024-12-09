import tkinter as tk
from tkinter import simpledialog, Toplevel, Button

class MinesweeperNoMines:
    def __init__(self, master, grid_size):
        self.master = master
        self.grid_size = grid_size
        self.master.title(f"Kriegssimulation ({self.grid_size}x{self.grid_size})")
        
        self.buttons = []
        self.flags = set()
        self.selected_symbol = "🏠"  # Standardfahne
        self.selected_color = "lightblue"  # Standard-Hintergrundfarbe (Startfarbe)
        self.selected_rocket = None # ausgewählte Rakete
        self.rocket_selected = False # ist eine Rakete ausgewählt

        self.rocket_prices = {
            1: 300,
            2: 2000,
            3: 6000
        }

        self.rocket_ranges = {
            1: 1,
            2: 2,
            3: 3
        }

        # Zähler für 🏠-Symbole pro Team
        self.blue_house_count = 0
        self.red_house_count = 0

        # Zähler für 🏛️-Symbole pro Team
        self.blue_bank_count = 0
        self.red_bank_count = 0

        # Zähler für 🏭/🛫-Symbole pro Team
        self.blue_factory_count = 0
        self.red_factory_count = 0
        self.blue_airport_count = 0
        self.red_airport_count = 0

        # Variablen für Team Blau und Team Rot
        self.blue_money = 200
        self.blue_income = 0  # Initiales Einkommen von Team Blau
        self.red_money = 200
        self.red_income = 0  # Initiales Einkommen von Team Rot

        # Symbolpreise: Jede Symbol hat einen unterschiedlichen Preis
        self.symbol_prices = {
            "🏠": 50,  
            "🏛️": 250,
            "🚗": 100,
            "🚒": 150,
            "🛩️": 100,
            "🏭": 200,
            "🛫": 250
        }

        self.vehicles = {'🚗': [], '🚒': [], '🛩️': []}  # Positionsliste für jedes Fahrzeug

        # Erstelle das Spielfeld mit dynamischer Größe
        for row in range(self.grid_size):
            row_buttons = []
            for col in range(self.grid_size):
                button = tk.Button(self.master, width=4, height=2, 
                                   command=lambda r=row, c=col: self.place_symbol(r, c))
                button.grid(row=row, column=col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        # Anzeigetext für Team Blau und Team Rot
        self.blue_money_label = tk.Label(self.master, text=f"Team Blau - Geld: {self.blue_money}  Einkommen: {self.blue_income}", font=('Arial', 12))
        self.blue_money_label.grid(row=self.grid_size, column=0, columnspan=self.grid_size//2)

        self.red_money_label = tk.Label(self.master, text=f"Team Rot - Geld: {self.red_money}  Einkommen: {self.red_income}", font=('Arial', 12))
        self.red_money_label.grid(row=self.grid_size, column=self.grid_size//2, columnspan=self.grid_size//2)

        # Label, um das aktuelle Team anzuzeigen
        self.current_team_label = tk.Label(self.master, text="Aktuelles Team: Blau", font=('Arial', 12))
        self.current_team_label.grid(row=self.grid_size+1, column=0, columnspan=self.grid_size)

        # Button zum Beenden der Runde
        self.end_round_button = tk.Button(self.master, text="Runde Beenden", font=('Arial', 12), command=self.end_round)
        self.end_round_button.grid(row=self.grid_size+2, column=0, columnspan=self.grid_size)

        # Anweisungen und Interaktionsmöglichkeiten
        self.instructions_label = tk.Label(self.master, text="Rechtsklick, um Symbol auszuwählen. Linksklick, um zu platzieren. Mittlere Maustaste, um zu entfernen.", font=('Arial', 10))
        self.instructions_label.grid(row=self.grid_size+3, column=0, columnspan=self.grid_size)
        
        # Bind den Mittelklick (Button-2) zum Entfernen von Symbolen
        self.master.bind('<Button-2>', self.middle_click)  # Mittlere Maustaste

        self.master.bind('<Button-3>', self.right_click)  # Rechtsklick zum Öffnen des Kontextmenüs

        self.master.bind('<b>', self.open_rocket_menu) # Maus 4 für Raketenmenü

        self.master.bind('<Button-1>', self.select_rocket) # Rakete auswählen

        self.master.after(100, self.update_team_data)  # Sicherstellen, dass die Teamdaten bei Beginn angezeigt werden

        self.master.bind("<x>", self.select_vehicle_with_key)  # Fahrzeugauswahl mit x
        self.master.bind("<Up>", lambda event: self.move_vehicle("up"))
        self.master.bind("<Down>", lambda event: self.move_vehicle("down"))
        self.master.bind("<Left>", lambda event: self.move_vehicle("left"))
        self.master.bind("<Right>", lambda event: self.move_vehicle("right"))

    def place_symbol(self, row, col):
        # Funktion, um das ausgewählte Symbol auf einem Feld zu platzieren
        button = self.buttons[row][col]
        current_symbol = button.cget("text")  # Holen des aktuellen Symbols

        # Überprüfen, ob auf dem Feld bereits ein Symbol vorhanden ist
        if current_symbol != "":
            #self.show_error_message("Fehler", "Dieses Feld ist bereits belegt!")  # Feld ist bereits belegt
            return

        # Überprüfen, ob genug Geld vorhanden ist und ob das aktuelle Team die richtige Farbe hat
        symbol_cost = self.symbol_prices.get(self.selected_symbol, 0)  # Preis für das ausgewählte Symbol

        # Prüfen, ob das Team die richtige Farbe gewählt hat
        if self.selected_color == "lightblue" and self.blue_money >= symbol_cost:
            # Nur Team Blau kann mit lightblue Symbole platzieren

            if self.selected_symbol == "🚗" or self.selected_symbol == "🚒":
            # Überprüfen, ob auf dem Feld bereits ein 🏭-Symbol vorhanden ist
                if not self.factory_nearby(row, col):
                    self.show_error_message("Fehler", "Du musst zuerst ein 🏭-Symbol platzieren, um 🚗 oder 🚒 zu setzen.")
                    return

            if self.selected_symbol == "🛩️":
            # Überprüfen, ob auf dem Feld bereits ein 🛫-Symbol vorhanden ist
                if not self.airport_nearby(row, col):
                    self.show_error_message("Fehler", "Du musst zuerst ein 🛫-Symbol platzieren, um 🛩️ zu setzen.")
                    return

            if self.selected_color == "lightblue":  # Team Blau
                button.config(text=self.selected_symbol, relief=tk.SUNKEN, bg=self.selected_color)
                if self.selected_symbol == "🏠":
                    self.blue_house_count += 1
                if self.selected_symbol == "🏛️":
                    self.blue_bank_count += 1
                if self.selected_symbol == "🏭":
                    self.blue_factory_count += 1
                if self.selected_symbol == "🛫":
                    self.blue_airport_count += 1

                self.blue_money -= symbol_cost  # Abzug von Team Blau's Geld
                self.blue_money_label.config(text=f"Team Blau - Geld: {self.blue_money}  Einkommen: {self.blue_income}")
                self.update_income()  # Einkommen jedes Teams nach jedem Klick aktualisieren
                self.update_team_data()  # Anzeige der Teamdaten aktualisieren
                self.check_for_loss()  # Überprüfe, ob eines der Teams verloren hat
        elif self.selected_color == "lightpink" and self.red_money >= symbol_cost:
            # Nur Team Rot kann mit lightpink Symbole platzieren

            if self.selected_symbol == "🚗" or self.selected_symbol == "🚒":
            # Überprüfen, ob auf dem Feld bereits ein 🏭-Symbol vorhanden ist
                if not self.factory_nearby(row, col):
                    self.show_error_message("Fehler", "Du musst zuerst ein 🏭-Symbol platzieren, um 🚗 oder 🚒 zu setzen.")
                    return

            if self.selected_symbol == "🛩️":
            # Überprüfen, ob auf dem Feld bereits ein 🛫-Symbol vorhanden ist
                if not self.airport_nearby(row, col):
                    self.show_error_message("Fehler", "Du musst zuerst ein 🛫-Symbol platzieren, um 🛩️ zu setzen.")
                    return

            if self.selected_color == "lightpink":  # Team Rot
                button.config(text=self.selected_symbol, relief=tk.SUNKEN, bg=self.selected_color)
                if self.selected_symbol == "🏠":
                    self.red_house_count += 1
                if self.selected_symbol == "🏛️":
                    self.red_bank_count += 1
                if self.selected_symbol == "🏭":
                    self.red_factory_count += 1
                if self.selected_symbol == "🛫":
                    self.red_airport_count += 1

                self.red_money -= symbol_cost  # Abzug von Team Rot's Geld
                self.red_money_label.config(text=f"Team Rot - Geld: {self.red_money}  Einkommen: {self.red_income}")
                self.update_income()  # Einkommen jedes Teams nach jedem Klick aktualisieren
                self.update_team_data()  # Anzeige der Teamdaten aktualisieren
                self.check_for_loss()  # Überprüfe, ob eines der Teams verloren hat
                
        else:
            self.show_insufficient_funds_message()  # Wenn nicht genug Geld vorhanden ist

    def middle_click(self, event):
        # Funktion, um Symbol zu entfernen (mit der mittleren Maustaste)
        widget = event.widget
        row = widget.grid_info()['row']
        col = widget.grid_info()['column']

            # Holen des aktuellen Symbols und der Hintergrundfarbe des Feldes
        current_symbol = self.buttons[row][col].cget("text")
        current_bg = self.buttons[row][col].cget("bg")  # Hintergrundfarbe des Buttons

        # Überprüfe, ob das Team die richtige Farbe hat, um zu löschen
        current_symbol = self.buttons[row][col].cget("text")
        if current_symbol != "" and current_symbol != "🚩":
            if self.selected_color == "lightblue" and current_symbol != "" and current_bg == "lightblue":
                if current_symbol in ["🏠", "🏛️", "🏭", "🛫", "🚗", "🚒", "🛩️"]:
                    self.remove_symbol(row, col)  # Team Blau entfernt nur seine Symbole
                    self.blue_money_label.config(text=f"Team Blau - Geld: {self.blue_money}  Einkommen: {self.blue_income}")
                    self.update_income()  # Einkommen jedes Teams nach jedem Klick aktualisieren
                    self.update_team_data()  # Anzeige der Teamdaten aktualisieren
                    self.check_for_loss()  # Überprüfe, ob eines der Teams verloren hat
                else:
                    self.show_error_message("Fehler", "Du kannst nur deine eigenen Symbole löschen!")
            elif self.selected_color == "lightpink" and current_symbol != "" and current_bg == "lightpink":
                if current_symbol in ["🏠", "🏛️", "🏭", "🛫", "🚗", "🚒", "🛩️"]:
                    self.remove_symbol(row, col)  # Team Rot entfernt nur seine Symbole
                    self.red_money_label.config(text=f"Team Rot - Geld: {self.red_money}  Einkommen: {self.red_income}")
                    self.update_income()  # Einkommen jedes Teams nach jedem Klick aktualisieren
                    self.update_team_data()  # Anzeige der Teamdaten aktualisieren
                    self.check_for_loss()  # Überprüfe, ob eines der Teams verloren hat
                else:
                    self.show_error_message("Fehler", "Du kannst nur deine eigenen Symbole löschen!")

    def remove_symbol(self, row, col):
        # Entfernt das Symbol auf dem Feld und setzt es auf den ursprünglichen Zustand zurück
        button = self.buttons[row][col]
        removed_symbol = button.cget("text")  # Holen des Symbols, das entfernt wird
        button.config(text="", relief=tk.RAISED, bg="SystemButtonFace")  # Zurücksetzen auf den Ursprungszustand

        # Wenn das entfernte Symbol ein Haus war, verringere das Einkommen
        if removed_symbol == "🏠":
            if self.selected_color == "lightblue":
                self.blue_house_count -= 1
            elif self.selected_color == "lightpink":
                self.red_house_count -= 1
        
        if removed_symbol == "🏛️":
            if self.selected_color == "lightblue":
                self.blue_bank_count -= 1
            elif self.selected_color == "lightpink":
                self.red_bank_count -= 1

        if removed_symbol == "🏭":
            if self.selected_color == "lightblue":
                self.blue_factory_count -= 1
            elif self.selected_color == "lightpink":
                self.red_factory_count -= 1

        if removed_symbol == "🛫":
            if self.selected_color == "lightblue":
                self.blue_airport_count -= 1
            elif self.selected_color == "lightpink":
                self.red_airport_count -= 1

        self.update_income()  # Einkommen nach dem Entfernen des Symbols aktualisieren
        self.update_team_data()  # Anzeige der Teamdaten aktualisieren

    def show_error_message(self, title, message):
        # Zeigt eine Fehlermeldung an
        error_window = Toplevel(self.master)
        error_window.title(title)
        error_label = tk.Label(error_window, text=message, font=('Arial', 12))
        error_label.pack(padx=10, pady=10)
        close_button = tk.Button(error_window, text="Schließen", command=error_window.destroy)
        close_button.pack(padx=10, pady=10)

    def right_click(self, event):
        # Öffnet das Auswahlfenster bei Rechtsklick
        widget = event.widget
        row = widget.grid_info()['row']
        col = widget.grid_info()['column']
        self.show_symbol_menu(row, col)

    def show_symbol_menu(self, row, col):
        # Kontextmenü mit den sieben neuen Symbolen und zwei Farben, aber abhängig vom Team (Blau oder Rot)
        menu_window = Toplevel(self.master)
        menu_window.title("Symbol wählen")
        
        symbols = ["🏠", "🏛️", "🏭", "🛫", "🚗", "🚒", "🛩️"]

        # Bestimme die Farbe basierend auf dem aktuellen Team
        if self.selected_color == "lightblue":
            valid_symbols = symbols  # Alle Symbole für Team Blau
            menu_window.configure(bg="lightblue")  # Hintergrund auf lightblue setzen
        else:
            valid_symbols = symbols  # Alle Symbole für Team Rot
            menu_window.configure(bg="lightpink")  # Hintergrund auf lightpink setzen
        
        def select_symbol(symbol):
            self.selected_symbol = symbol
            menu_window.destroy()  # Schließe das Auswahlmenü

        # Erstelle Buttons für Symbole und Farben
        for i, symbol in enumerate(valid_symbols):
            button = Button(menu_window, text=symbol, width=5, height=2, 
                                command=lambda s=symbol: select_symbol(s))
            button.grid(row=i, column=0)

    def update_team_data(self):
        # Berechne das Einkommen jedes Teams basierend auf den 🏠-Symbole
        self.blue_income = self.blue_house_count * 10 + self.blue_bank_count * 75 # Beispiel: jedes 🏠 bringt 10 Einkommen
        self.red_income = self.red_house_count * 10 + self.red_bank_count * 75

        # Berechne das Gesamtgeld, wenn ein Symbol platziert wurde
        self.blue_money += self.blue_income
        self.red_money += self.red_income

        # Aktualisiert die Anzeige der Teamdaten
        self.blue_money_label.config(text=f"Team Blau - Geld: {self.blue_money}  Einkommen: {self.blue_income}")
        self.red_money_label.config(text=f"Team Rot - Geld: {self.red_money}  Einkommen: {self.red_income}")

        # Anzeige des aktuellen Teams
        self.current_team_label.config(text=f"Aktuelles Team: {'Blau' if self.selected_color == 'lightblue' else 'Rot'}")

    def show_insufficient_funds_message(self):
        # Zeige eine Nachricht an, wenn ein Team nicht genug Geld hat
        insufficient_funds_window = Toplevel(self.master)
        insufficient_funds_window.title("Nicht genug Geld!")
        message = tk.Label(insufficient_funds_window, text="Nicht genug Geld, um das Symbol zu platzieren!", font=('Arial', 12))
        message.pack(padx=10, pady=10)
        button = tk.Button(insufficient_funds_window, text="Schließen", command=insufficient_funds_window.destroy)
        button.pack(padx=10, pady=10)

    def end_round(self):
        # Runde beenden: Erhöht das Geld um das Einkommen der beiden Teams
        self.update_team_data()  # Daten vor dem Rundenabschluss aktualisieren
        self.check_for_loss()  # Überprüfe, ob ein Team verloren hat
        self.switch_team()  # Wechsle zum anderen Team nach der Runde
        """Führt Rundenwechsel durch."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                button = self.buttons[row][col]
                symbol = button.cget("text")
                if symbol in self.vehicles.keys():  # Nur Fahrzeuge anpassen
                    if button.cget("bg") == "lightblue":
                        button.config(bg="blue")
                    elif button.cget("bg") == "lightpink":
                        button.config(bg="red")
        print("Runde beendet")

    def switch_team(self):
        # Wechselt zum anderen Team
        if self.selected_color == "lightblue":
            self.selected_color = "lightpink"
            self.current_team_label.config(text="Aktuelles Team: Rot")  # Anzeige auf Rot ändern
        else:
            self.selected_color = "lightblue"
            self.current_team_label.config(text="Aktuelles Team: Blau")  # Anzeige auf Blau ändern

    def check_for_loss(self):
        # Prüfe, ob ein Team verloren hat
        if self.blue_money < 50 and self.blue_income == 0:
            self.end_game("Team Blau hat verloren!")
        elif self.red_money < 50 and self.red_income == 0:
            self.end_game("Team Rot hat verloren!")

    def end_game(self, message):
        # Fenster zeigen, wenn ein Team verloren hat
        game_over_window = Toplevel(self.master)
        game_over_window.title("Spiel beendet")
        end_label = tk.Label(game_over_window, text=message, font=('Arial', 14))
        end_label.pack(padx=10, pady=10)
        close_button = tk.Button(game_over_window, text="Spiel schließen", command=self.master.quit)
        close_button.pack(padx=10, pady=10)

    def open_rocket_menu(self, event):
        """Maus 4 öffnet das Raketen-Auswahlmenü."""
        menu_window = Toplevel(self.master)
        menu_window.title("Raketen auswählen")
        menu_window.geometry("300x200")

        # Anzeigen der Raketenoptionen mit Preis
        for i in range(1, 4):
            button = Button(menu_window, text=f"Rakete {i} - Preis: {self.rocket_prices[i]}$", width=20,
                            command=lambda i=i: self.buy_rocket(i))
            button.pack(pady=10)

    def buy_rocket(self, rocket_type):
        """Kauft die ausgewählte Rakete, wenn der Spieler genug Geld hat."""
        if self.selected_color == "lightblue" and self.blue_money >= self.rocket_prices[rocket_type]:
            self.selected_rocket = rocket_type
            self.blue_money -= self.rocket_prices[rocket_type]
            self.blue_money_label.config(text=f"Team Blau - Geld: {self.blue_money}  Einkommen: {self.blue_income}")
            print(f"Rakete {rocket_type} gekauft! Explosionsradius: {self.rocket_ranges[rocket_type]}")
        elif self.selected_color == "lightpink" and self.red_money >= self.rocket_prices[rocket_type]:
            self.selected_rocket = rocket_type
            self.red_money -= self.rocket_prices[rocket_type]
            self.red_money_label.config(text=f"Team Rot - Geld: {self.red_money}  Einkommen: {self.red_income}")
            print(f"Rakete {rocket_type} gekauft! Explosionsradius: {self.rocket_ranges[rocket_type]}")
        else:
            self.show_error_message("Nicht genug Geld!", "Du hast nicht genug Geld für diese Rakete.")

    def select_rocket(self, event):
        """Maus 5, um Raketen auszuwählen und sie auf ein Ziel abzufeuern."""
        if self.selected_rocket is not None:
            row, col = self.get_clicked_field(event)
            self.fire_rocket(row, col)
        #else:
            #self.show_error_message("Rakete nicht ausgewählt", "Wähle zuerst eine Rakete aus!")

    def get_clicked_field(self, event):
        """Hilfsmethode, um die Zeile und Spalte des angeklickten Feldes zu erhalten."""
        widget = event.widget
        row = widget.grid_info()['row']
        col = widget.grid_info()['column']
        return row, col
    
    def fire_rocket(self, row, col):
        """Feuert die Rakete ab und zerstört Felder im Explosionsradius."""
        radius = self.rocket_ranges[self.selected_rocket]  # Explosionsradius
        for r in range(row - radius + 1, row + radius):
            for c in range(col - radius + 1, col + radius):
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                    self.destroy_field(r, c)

        print(f"Rakete mit Radius {radius} abgefeuert auf ({row}, {col})!")
        self.reset_rocket_selection()  # Rakete nach dem Abschuss zurücksetzen

    def destroy_field(self, row, col):
        """Zerstört das Feld und ersetzt es mit einem schwarzen Loch."""
        button = self.buttons[row][col]

            # Überprüfen, ob das Symbol auf dem Feld 🏠 ist und den Hintergrund beachten
        if button.cget("text") == "🏠":
            if button.cget("background") == "lightblue":  # Blaues Haus
                self.blue_house_count -= 1  # Blaues Haus wird zerstört
                print(f"Ein blaues Haus auf ({row}, {col}) zerstört! Verbleibende blaue Häuser: {self.blue_house_count}")
            elif button.cget("background") == "lightpink":  # Rotes Haus
                self.red_house_count -= 1  # Rotes Haus wird zerstört
                print(f"Ein rotes Haus auf ({row}, {col}) zerstört! Verbleibende rote Häuser: {self.red_house_count}")

        if button.cget("text") == "🏛️":
            if button.cget("background") == "lightblue":  # Blaues Haus
                self.blue_bank_count -= 1  # Blaue Bank wird zerstört
                print(f"Eine blaue Bank auf ({row}, {col}) zerstört! Verbleibende blaue Banken: {self.blue_bank_count}")
            elif button.cget("background") == "lightpink":  # Rotes Haus
                self.red_bank_count -= 1  # Rote Bank wird zerstört
                print(f"Eine rote Bank auf ({row}, {col}) zerstört! Verbleibende rote Banken: {self.red_bank_count}")

        if button.cget("text") == "🛫":
            if button.cget("background") == "lightblue":  # Blaues Haus
                self.blue_airport_count -= 1  # Blauer Flughafen wird zerstört
                print(f"Ein blauer Flughafen auf ({row}, {col}) zerstört! Verbleibende blaue Flughäfen: {self.blue_airport_count}")
            elif button.cget("background") == "lightpink":  # Rotes Haus
                self.red_airport_count -= 1  # Roter Flughafen wird zerstört
                print(f"Ein roter Flughafen auf ({row}, {col}) zerstört! Verbleibende rote Flughäfen: {self.red_airport_count}")

        if button.cget("text") == "🏭":
            if button.cget("background") == "lightblue":  # Blaues Haus
                self.blue_factory_count -= 1  # Blaue Fabrik wird zerstört
                print(f"Eine blaue Farbik auf ({row}, {col}) zerstört! Verbleibende blaue Fabriken: {self.blue_factory_count}")
            elif button.cget("background") == "lightpink":  # Rotes Haus
                self.red_factory_count -= 1  # Rote Fabrik wird zerstört
                print(f"Eine rote Fabrik auf ({row}, {col}) zerstört! Verbleibende rote Fabriken: {self.red_factory_count}")

        button.config(text="🕳️", relief=tk.SUNKEN, bg="black")  # Zerstörungsfeld erstellen
        print(f"Feld ({row}, {col}) zerstört!")

    def reset_rocket_selection(self):
        """Setzt die Rakete als ausgewählt zurück."""
        self.selected_rocket = None  # Keine Rakete mehr ausgewählt
        print("Raketenwahl zurückgesetzt!")

    def show_error_message(self, title, message):
        """Zeigt eine Fehlermeldung an."""
        error_window = Toplevel(self.master)
        error_window.title(title)
        error_label = tk.Label(error_window, text=message, font=('Arial', 12))
        error_label.pack(padx=10, pady=10)
        close_button = tk.Button(error_window, text="Schließen", command=error_window.destroy)
        close_button.pack(padx=10, pady=10)

    def factory_nearby(self, row, col):
        """Überprüft, ob ein 🏭-Symbol des eigenen Teams in benachbarten Feldern vorhanden ist."""
        # Überprüft die benachbarten Felder (horizontal, vertikal und diagonal)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Oben, unten, links, rechts und diagonale Richtungen

        for direction in directions:
            neighbor_row = row + direction[0]
            neighbor_col = col + direction[1]

            # Überprüfen, ob der Nachbar innerhalb der Spielfeldgrenzen ist
            if 0 <= neighbor_row < len(self.buttons) and 0 <= neighbor_col < len(self.buttons[0]):
                button = self.buttons[neighbor_row][neighbor_col]
                current_symbol = button.cget("text")  # Text des Symbols im Button
                current_bg = button.cget("background")  # Hintergrundfarbe des Buttons

                # Überprüfen, ob es ein 🏭-Symbol des eigenen Teams ist
                if current_symbol == "🏭" and current_bg == self.selected_color:
                    return True

        # Wenn kein 🏭 des eigenen Teams in der Nähe ist
        return False


    def airport_nearby(self, row, col):
        """Überprüft, ob ein 🛫-Symbol des eigenen Teams in benachbarten Feldern vorhanden ist."""
        # Überprüft die benachbarten Felder (horizontal, vertikal und diagonal)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Oben, unten, links, rechts und diagonale Richtungen

        for direction in directions:
            neighbor_row = row + direction[0]
            neighbor_col = col + direction[1]

            # Überprüfen, ob der Nachbar innerhalb der Spielfeldgrenzen ist
            if 0 <= neighbor_row < len(self.buttons) and 0 <= neighbor_col < len(self.buttons[0]):
                button = self.buttons[neighbor_row][neighbor_col]
                current_symbol = button.cget("text")  # Text des Symbols im Button
                current_bg = button.cget("background")  # Hintergrundfarbe des Buttons

                # Überprüfen, ob es ein 🛫-Symbol des eigenen Teams ist
                if current_symbol == "🛫" and current_bg == self.selected_color:
                    return True

        # Wenn kein 🏭 des eigenen Teams in der Nähe ist
        return False

    def handle_click(self, row, col):
        button = self.buttons[row][col]
        symbol = button.cget("text")
        color = button.cget("bg")

        if self.selected_vehicle:
            self.move_vehicle(row, col)
        elif symbol in self.vehicles:
            self.select_vehicle(row, col, symbol, color)

    def select_vehicle(self, row, col, symbol, color):
        if (color == "blue" and self.selected_color == "lightblue") or (color == "red" and self.selected_color == "lightpink"):
            self.selected_vehicle = (symbol, row, col)
            print(f"{symbol} ausgewählt bei ({row}, {col})")

    def move_vehicle(self, row, col):
        if not self.selected_vehicle:
            return

        symbol, old_row, old_col = self.selected_vehicle
        if self.can_move(symbol, old_row, old_col, row, col):
            self.buttons[old_row][old_col].config(text="", bg="SystemButtonFace")
            self.buttons[row][col].config(text=symbol, bg=self.selected_color)
            self.selected_vehicle = None
            print(f"{symbol} bewegt zu ({row}, {col})")

    def can_move(self, symbol, old_row, old_col, new_row, new_col):
        if not (0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size):
            return False

        target = self.buttons[new_row][new_col].cget("text")
        valid_targets = {
            '🚗': ["", "🏭", "🏛️", "🏠", "🛫", "🚒"],
            '🚒': ["", "🛩️"],
            '🛩️': ["", "🚗"]
        }
        return target in valid_targets[symbol]

    def is_vehicle_ready(self, color):
        """Prüft, ob das Fahrzeug bereit ist, bewegt zu werden."""
        return (color == "blue" and self.selected_color == "lightblue") or \
               (color == "red" and self.selected_color == "lightpink")

    def select_vehicle_with_key(self, event):
        """Fahrzeug auswählen, wenn `x` gedrückt wird."""
        widget = self.master.winfo_containing(event.x_root, event.y_root)
        if widget:
            grid_info = widget.grid_info()
            row = grid_info.get("row")
            col = grid_info.get("column")
            if row is not None and col is not None:
                button = self.buttons[row][col]
                symbol = button.cget("text")
                color = button.cget("bg")
                
                if symbol in self.vehicles.keys() and self.is_vehicle_ready(color):
                    self.selected_vehicle = (symbol, row, col)
                    print(f"{symbol} ausgewählt bei ({row}, {col})")

    def move_vehicle(self, direction):
        """Fahrzeug in die angegebene Richtung bewegen."""
        if not self.selected_vehicle:
            return

        symbol, old_row, old_col = self.selected_vehicle
        new_row, new_col = old_row, old_col

        if direction == "up":
            new_row -= 1
        elif direction == "down":
            new_row += 1
        elif direction == "left":
            new_col -= 1
        elif direction == "right":
            new_col += 1

        if self.can_move(symbol, old_row, old_col, new_row, new_col):
            self.buttons[old_row][old_col].config(text="", bg="SystemButtonFace")
            self.buttons[new_row][new_col].config(text=symbol, bg="lightblue" if self.selected_color == "lightblue" else "lightpink")
            self.selected_vehicle = None
            print(f"{symbol} bewegt zu ({new_row}, {new_col})")

# Initialisiere Tkinter
root = tk.Tk()
game = MinesweeperNoMines(root, grid_size=16)
root.mainloop()
