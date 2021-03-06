
"""
Amadeo Granillo, Abdul Karim Kanbar, Juan Carlos Moreno

"""

import argparse
import curses
import random
import secrets
import sys

parser = argparse.ArgumentParser(description='Shiffe Versenken Spiel') #Initialisieren Sie den Argument-Parser
parser.add_argument('xaxis', type=int, help='Anzahl der Spalten im Spielplan ( 5 < xaxis <=10)') # xaxis argument
parser.add_argument('yaxis', type=int, help='Anzahl der Zeilen im Spielplan( 5 < yaxis <=10)') # yaxis argument
args = parser.parse_args() 

# Zeilen und Spalten der Spiel mit Befehlszeilenargumenten zuweisen
ZEILEN = args.yaxis
SPALTEN = args.xaxis

# Beschränkung von ZEILEN und SPALTEN auf den Bereich (5, 10), beide inklusive

if ZEILEN < 5:
    ZEILEN = 5
if ZEILEN > 10:
    ZEILEN = 10

if SPALTEN < 5:
    SPALTEN = 5
if SPALTEN > 10:
    SPALTEN = 10


#Menüoptionen
menu = ["vs CPU", "vs Friend", "Exit"] 

# Orienunentschiedenrungsmöglichkeiten
horizontal = ["horizontal", "h"]
vertikal = ["vertikal", "v"]

# Alle Schiffstypen. beitere Schiffstypen können in dieser Liste hi
SCHIFF_TYPEN = [("Zerstörer", 2, "D"), ("U-Boot", 3, "S"), ("Kreuzer", 3, "Cs"), ("Schlachtschiff", 4, "B"), ("Carrier", 5, "Cr")]



# Cell Codes für die grafische Darstellung 
CODE_LEER = '   '    
CODE_HIT =   ' * ' 
CODE_MISS =  ' . '  
CODE_versenkt =  ' # ' 


ZEILE_HÖHE = 2
SPALTE_BREITE= len(CODE_LEER) + 1  # +1 zur Berücksichtigung der Breite des Zellenrandes

# Leerzeile, die im gesamten Skript verbendet bird, um einen zuvor geschriebenen Text zu überschreiben.  
blank = "                                                 " 


def main(stdscr):

    curses.curs_set(0) #den Cursor ausblenden

    # alle in meinem Spiel verbendeten Farbschemata
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) 
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_CYAN)
    
    stdscr.border(0)  # Rand des Standardbildschirms
    curses.mousemask(1) # um das Abhören auf Mausereignisse zu aktivieren
    
    main_menu(stdscr, 0)  

def main_menu(gewinnen, gewählte_zeile_idx):
    gewinnen.keypad(1)  # zum vereinfachten Abhören von Tastaturereignissen
    h, w = gewinnen.getmaxyx() #maximale Höhe und Breite des Curses-Fensters

    while True:
        gewinnen.clear()
        for idx, row in enumerate(menu): 
            x = w//2 - len(row)//2 # zum horizontalen Zentrieren des Zeilen
            y = h//2 - len(menu) + idx # zum vertikale Zentrieren des Zeilen

            if idx == gewählte_zeile_idx:
                gewinnen.attron(curses.color_pair(1)) # die ausgewählte Option kennzuzeichnen
                gewinnen.addstr(y, x, row)    
                gewinnen.attroff(curses.color_pair(1))
            else:
                gewinnen.addstr(y, x, row)
        gewinnen.refresh()
        
        key = gewinnen.getch()
        gewinnen.clear()
        
        # Tastaturdurchlauf durch Optionen
        if key == curses.KEY_UP:
            gewählte_zeile_idx -= 1
            
        elif key == curses.KEY_DOWN:
            gewählte_zeile_idx += 1

        elif key == curses.KEY_ENTER or key in [10, 13]:
            spiel_start(gewinnen, gewählte_zeile_idx)
            
        # Unterlauf- und Überlaufbehandlung
        if gewählte_zeile_idx < 0:
            gewählte_zeile_idx = len(menu) - 1
        elif gewählte_zeile_idx >= len(menu):
            gewählte_zeile_idx = 0
        
def spiel_start(gewinnen, option):
    if option == 0:
        start_cpu_spiel(gewinnen) #Start Spiel gegen CPU
    elif option == 1:
        start_freund_spiel(gewinnen) #Start Spiel gegen Freund
    elif option == 2:
        sys.exit(0)   #Programm verlassen und beenden

def start_cpu_spiel(gewinnen):
    gewinnen.clear()

    spieler1 = Spieler("Spieler 1")
    spieler2 = Spieler("CPU")
    spieler2.ist_cpu = True #Definieren, dass der gegnerische Spieler die CPU ist

    spieler1.schiffe_platzieren(gewinnen) #Platzieren von Schiffe auf dem Board
    gewinnen.clear()
    h, w = gewinnen.getmaxyx()
    msg = spieler1.name + "! Ihre Schiffe wurden platziert. Drücken Sie eine beliebige Taste, um fortzufahren."   #Bildschirm ändern und nur diese Meldung anzeigen, keine Boards
    gewinnen.addstr(h//2, w//2  - len(msg)//2, msg)    #Positionierung der Nachricht im Terminal
    gewinnen.refresh() 
    
    gewinnen.getch()
    for type in SCHIFF_TYPEN:
        spieler2.platz_ship_random(type) #Da es gegen den PC geht, werden die Schiffe zufällig platziert
    h, w = gewinnen.getmaxyx()
    gewinnen.clear()
    msg = spieler2.name + " ihre Schiffe platziert hat. Drücken Sie eine beliebige Taste, um fortzufahren."
    gewinnen.addstr(h//2, w//2  - len(msg)//2, msg)   #Positionierung der Nachricht im Terminal
    
    gewinnen.refresh()
    
    gewinnen.getch()

    gameloop(spieler1, spieler2, gewinnen)

def start_freund_spiel(gewinnen):
    gewinnen.clear() 
    # Initialisieren von Spielern. Hier können Spielernamen als Benutzereingabe genommen werden, aber wir haben die Namen hart kodiert.
    spieler1 = Spieler("Spieler 1")
    spieler2 = Spieler("Spieler 2")

    #Schiffe für Spieler 1 platzieren     
    spieler1.schiffe_platzieren(gewinnen)
    gewinnen.clear()
    h, w = gewinnen.getmaxyx()
    msg = spieler1.name + " ! Ihre Schiffe wurden platziert. Drücken Sie eine beliebige Taste, um fortzufahren." #Ändern Sie den Bildschirm und zeigen Sie nur diese Meldung an, nicht die Tafeln, um zu verhindern, dass die Spieler die Positionierung des anderen Spielers sehen können.
    gewinnen.addstr(h//2, w//2  - len(msg)//2, msg)
    gewinnen.refresh()
    
    gewinnen.getch() 
    
    # Schiffe für Spieler 2 platzieren
    spieler2.schiffe_platzieren(gewinnen)
    gewinnen.clear()
    h, w = gewinnen.getmaxyx()
    msg = spieler2.name + " ! Ihre Schiffe sind platziert worden. Drücken Sie eine beliebige Taste, um fortzufahren."
    gewinnen.addstr(h//2, w//2  - len(msg)//2, msg)
    gewinnen.refresh()
    gewinnen.getch()

    gameloop(spieler1, spieler2, gewinnen) # Starten der Spielschleife

def unentschieden(s1, s2, gewinnen):
    gewinnen.clear()
    h, w = gewinnen.getmaxyx()
    gewinnen.addstr(h//2, w//2 - 1, "Unentschieden") # Wenn das Spiel mit einem Unentschieden endet
    offx = SPALTE_BREITE
    offy = ZEILE_HÖHE*3
    gewinnen.refresh()
    # Zeigt die beiden Karten als nicht ausgeblendet an.
    s1.board_anzeigen(offx, offy, Koordinate(-1, -1), False, gewinnen)
    s2.board_anzeigen(offx + SPALTEN * (SPALTE_BREITE) + 2*offx, offy, Koordinate(-1, -1), False, gewinnen)
    
    gewinnen.refresh()
    getch()
    main_menu(gewinnen, 0)

def game_over(gewinner, loser, gewinnen):
    gewinnen.clear()
    h, w = gewinnen.getmaxyx()
    curses.flash()
    curses.flash()
    curses.flash() #Blinken des Bildschirms

    offx = SPALTE_BREITE
    offy = ZEILE_HÖHE*3
    
    gewinnen.addstr(h//2, w//2 + 38, "Game Over")
    gewinnen.addstr(h//2 + 1, w//2 + 38, gewinner.name + " gewinnt! ")  # #Positionierung der Nachricht im Terminal

    gewinnen.refresh()

    # Beide Boards als nicht versteckt anzeigen 
    gewinner.board_anzeigen(offx, offy, Koordinate(-1, -1), False, gewinnen)
    loser.board_anzeigen(offx + SPALTEN * (SPALTE_BREITE) + 2*offx, offy, Koordinate(-1, -1), False, gewinnen)
    gewinnen.getch()
    main_menu(gewinnen, 0)

def gameloop(s1, s2, gewinnen):
    #Spielschleife, Benutzer-Terminal-Interaktion zum Schießen, Verfehlen, Treffen und Versenken von Schiffen
    
    # Offsets dienen als Ursprung 
    offx = SPALTE_BREITE
    offy = 3*ZEILE_HÖHE
    
    
    gewinnen.refresh()

    # s1 spielt den ersten Zug
    aktuelles_spieler = s1 
    gegner = s2
    
    ausgewählte_zelle = Koordinate(0, 0)
    
    # Anzahl der Runden noch
    turns = 0    

    #user input
    userzeile = 0
    userspal = 0    
            
    while True:
        gewinnen.clear()
        
        while True:
            # wenn die Anzahl der Züge gleich ist, bedeutet dies, dass beide Spieler ihren Zug gespielt haben
            # Die Prüfung auf Gewinner, bevor Spieler 2 seinen Zug gemacht hat, würde dem ersten Spieler einen unfairen Vorteil verschaffen
            if turns % 2 == 0:
                # Prüfung für Game Over, wer gewonnen oder verloren hat
                if aktuelles_spieler.hat_verloren() and gegner.hat_verloren():
                    unentschieden(aktuelles_spieler, gegner, gewinnen)
                elif aktuelles_spieler.hat_verloren():
                    game_over(gewinner=gegner, loser=aktuelles_spieler, gewinnen=gewinnen)
                elif gegner.hat_verloren():
                    game_over(gewinner=aktuelles_spieler, loser=gegner, gewinnen=gewinnen)

            # Der CPU-Spieler/Bot benötigt keine visuelle Darstellung, um eine Bewegung auszuführen.
            if aktuelles_spieler.ist_cpu:
                #Zufällige Bewegungen ausprobieren
                while True:
                    ausgewählte_zelle = aktuelles_spieler.cpu_bewegung(gegner)
                    erfolg, msg = gegner.hit_handeln(ausgewählte_zelle)
                    # wenn die Bewegung erfolgreich durchgeführt wurde
                    if erfolg:
                        aktuelles_spieler, gegner = gegner, aktuelles_spieler
                        turns += 1
                        ausgewählte_zelle = Koordinate(-1, -1)
                        gewinnen.clear()
                        msg = "Die CPU hat ihren Zug gemacht. Drücken Sie eine beliebige Taste, um fortzufahren." #Bildschirmansicht ändern
                        gewinnen.addstr(0, 0, msg)
                        gewinnen.refresh()
                        gewinnen.getch()
                        gewinnen.clear()
                        break # kein Grund, es weiter zu versuchen
                continue

            # Nachricht an den Spieler, Liste der alternativen Optionen für das Feuern an einer Zelle   
            gewinnen.addstr(0, 0," "*SPALTE_BREITE*5 + aktuelles_spieler.name + "! ist dran" + blank)
            gewinnen.addstr(1, 0, "Klicken Sie auf eine Stelle auf dem gegnerischen Board, um zu feuern" + blank)
            gewinnen.addstr(2, 0, " Oder wählen Sie eine Stelle auf dem gegnerBoard mit den Cursor-Tasten und drücken Sie die Leertaste zum Feuern")
            gewinnen.addstr(3, 0, "Alternativ können Sie auch den Spaltenbuchstaben und die Zeile-Nummer zum Feuern eingeben.")
            # Gegnerboard und Spielstand anzeigen
            anzeigen_boards_und_ergebnisse(aktuelles_spieler, gegner, offx, offy, ausgewählte_zelle, gewinnen)

            # Behandlung von Benutzereingaben
            key = gewinnen.getch()

            if ord('A') <= key <= ord('Z') or ord('a') <= key <= ord('z'):
                userspal = key - ord('A') + 1 if key <=ord('Z') else key - ord('a') + 1 #a/A means userspalte = 1
                userzeile = 0
                
            elif chr(key).isdigit():  # als REIHEN<=10, also ist y immer eine einzelne Ziffer( oder ein Zeichen)
                userzeile = userzeile * 10 + key - ord('0') #Verwendet wird die eingegebenen Ziffern, um eine Zahl zu bilden
                

            elif key not in [10, 13]: #wenn Zeilen-/Spalteneingabe unterbrochen ist, beide als Null neu zuweisen
                userzeile = 0
                userspal = 0

            # Tastatureingabe  
            if key == curses.KEY_DOWN:
                ausgewählte_zelle.y += 1
            elif key == curses.KEY_UP:
                ausgewählte_zelle.y -= 1
            elif key == curses.KEY_LEFT:
                ausgewählte_zelle.x -= 1
            elif key == curses.KEY_RIGHT:
                ausgewählte_zelle.x += 1
            
            # Unterflow- und Overflowbehandlung
            if ausgewählte_zelle.x < 0:
                ausgewählte_zelle.x = SPALTEN - 1
            if ausgewählte_zelle.x >= SPALTEN:
                ausgewählte_zelle.x = 0
            if ausgewählte_zelle.y < 0:
                ausgewählte_zelle.y = ZEILEN - 1
            if ausgewählte_zelle.y >=ZEILEN:
                ausgewählte_zelle.y = 0    

            # Mauseingabe
            elif key == curses.KEY_MOUSE:
                
                click = curses.getmouse()
                mousex = click[1]
                mousey = click[2]
                row = (mousey - offy) // ZEILE_HÖHE
                col = (mousex - 1 - offx)//SPALTE_BREITE
                ausgewählte_zelle = Koordinate(col, row)
                if SPALTEN <= ausgewählte_zelle.x  or ausgewählte_zelle.x < 0  or ausgewählte_zelle.y < 0 or ausgewählte_zelle.y >= ZEILEN :
                    continue
                            
            #Leertaste gedrückt oder Maus geklickt/gedrückt bedeutet Feuer
            if key == ord(' ') or key == curses.KEY_MOUSE or (key in [10, 13] and userspal > 0 and userzeile > 0):
                if userzeile > 0 and userspal > 0:
                    ausgewählte_zelle = Koordinate(userspal - 1, userzeile - 1)
                    userzeile = 0 
                    userspal = 0
                # Versucht, auf die ausgewählte Zelle zu feuern
                erfolg, msg = gegner.hit_handeln(ausgewählte_zelle)
                if erfolg:
                    anzeigen_boards_und_ergebnisse(aktuelles_spieler, gegner, offx, offy, ausgewählte_zelle, gewinnen)
                    aktuelles_spieler, gegner = gegner, aktuelles_spieler
                    turns += 1
                    ausgewählte_zelle = Koordinate(0, 0)
                    msg += ". Drücken Sie eine beliebige Taste, damit Gegner dran ist" + blank #Bildschirmansicht wechseln, um zu verhindern, dass der Gegner die gegnerische Board sieht.
                    gewinnen.attron(curses.color_pair(2))
                    gewinnen.addstr(0, 0, msg)
                    gewinnen.addstr(1, 0, blank + blank)
                    gewinnen.addstr(2, 0, blank + blank)
                    gewinnen.addstr(3, 0, blank + blank)
                    gewinnen.refresh()
                    gewinnen.attroff(curses.color_pair(2))
                    
                    gewinnen.getch() 
                    
                    gewinnen.clear()
                    h, w = gewinnen.getmaxyx()
                    # nur reguläre Spieler, die keine CPUs sind, benötigen das UI
                    if not aktuelles_spieler.ist_cpu:
                        # Dies verhindert, dass die Spieler versehentlich die Karte des anderen sehen 
                        msg = aktuelles_spieler.name + " ! Sie sind dran. Drücken Sie eine beliebige Taste, um fortzufahren" #Bildschirmansicht wechseln, um zu verhindern, dass der Gegner die gegnerische Board sieht.
                        gewinnen.addstr(h//2, w//2 - len(msg)//2, msg)
                        gewinnen.refresh()
                        gewinnen.getch()
                        gewinnen.clear()
                        gewinnen.refresh()

                else:
                    # unerfolgreicher move/Schuss, also nur die Meldung anzeigen und die Runde nicht zählen
                    gewinnen.addstr(1, 0, blank + blank)
                    gewinnen.addstr(2, 0, blank + blank)
                    gewinnen.addstr(3, 0, blank + blank)
                    gewinnen.attron(curses.color_pair(4))
                    gewinnen.addstr(0, 0, msg + blank + blank)
                    gewinnen.attroff(curses.color_pair(4))
                    gewinnen.refresh()    
                    gewinnen.getch()

def anzeigen_boards_und_ergebnisse(aktuelles_spieler, gegner, offx, offy, ausgewählte_zelle, gewinnen):       
    
    # Gegners Board anzeigen
    titel = "Gegners Board"
    gegner.board_anzeigen(offx, offy, ausgewählte_zelle, True, gewinnen)
    gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN) + 1, offx + SPALTE_BREITE* SPALTEN//2 - len(titel), titel)
    versenkt = 0 #Anzahl der versenkten eigenen Schiffe
    versenkt = gegner.schiffe_versenkt_count()
    score_text = 'Versenkte Schiffe : ' + str(versenkt)        
    gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN + 1), offx + SPALTE_BREITE* SPALTEN//2 - len(titel), score_text)
    score_text = 'Verbleibende Schiffe: ' + str(len(gegner.schiffe) - versenkt) # verbleibend = gesamt - versenkt         
    gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN + 1) + 1, offx + SPALTE_BREITE* SPALTEN//2 - len(titel), score_text )
    
    # Anzeige der aktuellen Spielerboard und des Spielstands
    titel = "Mein Board"
    offx2 = offx + SPALTEN * (SPALTE_BREITE) + 2*offx
    gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN) + 1, offx2 + SPALTE_BREITE* SPALTEN//2 - len(titel), titel)
    aktuelles_spieler.board_anzeigen(offx2, offy, Koordinate(-1, -1), False, gewinnen)
    versenkt = aktuelles_spieler.schiffe_versenkt_count()
    score_text = 'Versenkte Schiffe : ' + str(versenkt)        
    gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN + 1), offx2 + SPALTE_BREITE* SPALTEN//2 - len(titel), score_text)
    score_text = 'Verbleibende Schiffe: ' + str(len(aktuelles_spieler.schiffe) - versenkt)        
    gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN + 1) + 1, offx2 + SPALTE_BREITE* SPALTEN//2 - len(titel), score_text)
    
    gewinnen.refresh() # das Fenster aktualisieren
    
class Ship:
    def __init__(self, type):
        self.name = type[0]   #Definition der Eigenschaften eines Schiffes
        self.laenge = type[1]
        self.code = type[2]
        self.orientierung = None
        self.koords = []
        self.hits = 0
        
    def platz(self, startx, starty, orientierung):
        self.koords = []
        self.hits = 0
        # alle Koordinaten dieses Schiffes entsprechend dem Startort und der Ausrichtung hinzufügen
        if orientierung in horizontal:
            for x in range(self.laenge):
                self.koords.append(Koordinate(startx + x, starty))
        elif orientierung in vertikal:
            for y in range(self.laenge):
                self.koords.append(Koordinate(startx, starty + y))

    def ist_versenkt(self): #die Methode des sinkenden Schiffes definieren
        return self.hits == self.laenge


class Koordinate:
    def __init__(self, x, y):   # Definition der Koordinatenparameter
        self.x = x
        self.y = y

    def left(self):
        return Koordinate(self.x - 1, self.y)

    def right(self):
        return Koordinate(self.x + 1, self.y)
    
    def up(self):
        return Koordinate(self.x, self.y - 1)
    
    def down(self):
        return Koordinate(self.x, self.y + 1)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Spieler:
    
    def __init__(self, name):
        self.name = name #Definition von Spielerattributen
        self.board = []
        self.schiffe = []
        self.gegner = None
        self.ist_cpu = False

        # Leere Karte von REIHEN durch SPALTEN initialisieren
        for r in range(ZEILEN):
            self.board.append([CODE_LEER]*SPALTEN)
    
    def platz_ship(self, ship, koords, orientierung):
        if orientierung in vertikal:
            if koords.y + ship.laenge > ZEILEN: # wenn das Schiff nicht in diese Lage und Ausrichtung passt
                return False # bedeutet es gibt ein Fehler
            
        elif orientierung in horizontal:
            if koords.x + ship.laenge > SPALTEN: # wenn das Schiff nicht in diese Lage und Ausrichtung passt
                return False #  bedeutet es gibt ein Fehle

        #wenn wir so weit gekommen sind, dann bedeutet das kein Scheitern  
        ship.platz(koords.x, koords.y , orientierung) # das Schiff platzieren

        # wenn eine beliebige Koordinate des Schiffes außerhalb der Grenzen liegt, dann bedeutet dies einen Ausfall
        for c in ship.koords:
            if self.board[c.y][c.x] != CODE_LEER:
                return False
        
        #keine ungültigen Koordinaten in Schiff, dann aktualisieren Sie die Karte
        for c in ship.koords:
            self.board[c.y][c.x] = ship.code
        self.schiffe.append(ship) # das Schiff in die Liste der Schiffe des Spielers aufnehmen
        return True # bedeutet Erfolg

    def hit_handeln(self, coord):  #wie man mit einer getroffenen/verpassten oder bereits geschossenen Stelle umgeht
        code = self.board[coord.y][coord.x]
        msg = ""

        if code == CODE_HIT or code == CODE_versenkt or code == CODE_MISS:
            return False, "Dort haben Sie bereits geschossen! "

        if code == CODE_LEER:
            self.board[coord.y][coord.x] = CODE_MISS
            return True, "Es war ein Miss"

        else:
            # das Schiff treffen, wenn einer seiner Koordinaten in dieser Koordinate liegt
            for ship in self.schiffe:
                msg += ship.name + " : "
                for c in ship.koords:
                    msg += str(c) + " "
                    if c == coord: 
                        ship.hits = ship.hits + 1 # Anzahl der Treffer, die das Schiff eingesteckt hat, um 1 erhöht
                        if ship.ist_versenkt(): # wenn das Schiff versenkt ist, alle seine Zellen als versenkt markieren
                            for c2 in ship.koords:
                                self.board[c2.y][c2.x] = CODE_versenkt
                            return True, "Du hast mein " + ship.name + " versenkt"
                        
                        else:
                            # wenn das Schiff nicht versenkt wird, markieren Sie es nur als Treffer.
                            self.board[c.y][c.x] = CODE_HIT
                            return True, "Es war ein Hit" # Erfolg
                    msg += "\n"

        return False, "Ende der Methode erreicht" + code + "\n" + msg    
          # wenn wir so weit gekommen sind, bedeutet das, dass es ein Problem gibt.
        # dies hat uns geholfen, auf einen Fehler bei der Art und Weise hinzuweisen, wie die Schiffscodes an Bord gespeichert werden
      
    
    def hat_verloren(self):
        # wenn auch nur eines der Schiffe des Spielers segelt, hat der Spieler nicht verloren
        for ship in self.schiffe:
            if not ship.ist_versenkt():
                return False
        return True

    def schiffe_versenkt_count(self):
        versenkt = 0   # die Anzahl der versenkte Schiffe zählen
        for ship in self.schiffe:
            if ship.ist_versenkt():
                versenkt += 1
        return versenkt

    def platz_ship_random(self, type):
        ship = Ship(type)
        
        while True :
            orientierung = 'h' if random.random() < 0.5 else 'v' # zufällige 50-50 Zufallsorienunentschiedenrung

            #zufällige Koordinaten
            x = secrets.randbelow(SPALTEN)
            y = secrets.randbelow(ZEILEN)

            # Stellen Sie sicher, dass keine der Zellen des Schiffes außerhalb der Grenzen platziert wird
            if orientierung == 'h':
                if x + ship.laenge > SPALTEN:
                    x -= (x + ship.laenge - SPALTEN)
            elif orientierung == 'v':
                if y + ship.laenge > ZEILEN:
                    y -= (y + ship.laenge - ZEILEN)
            
            if self.platz_ship(ship, Koordinate(x, y), orientierung):
                return
                
    def schiffe_platzieren(self, gewinnen):
        gewinnen.clear()   #Geben Sie die Möglichkeit, die Schiffe manuell zu platzieren oder mit der Standardpositionierung fortzufahren.
        gewinnen.refresh()
        h, w = gewinnen.getmaxyx()
        gewinnen.addstr(0, 0, self.name + " ! Drücken Sie Enter, um mit dieser Platzierung fortzufahren.")
        gewinnen.addstr(1, 0, self.name + " ! Oder drücken Sie  " + "Leertaste"+ " um mit der manuellen Platzierung von Schiffen zu beginnen.")
        for type in SCHIFF_TYPEN:
            self.platz_ship_random(type)
        gewinnen.refresh()
            
        offx = SPALTE_BREITE
        offy = 3 * ZEILE_HÖHE
        ausgewählte_zelle = Koordinate(-1, -1)
        self.board_anzeigen(offx, offy, ausgewählte_zelle, False, gewinnen)
        titel = self.name + "'s Board"
        gewinnen.addstr(offy + ZEILE_HÖHE*(ZEILEN + 1), offx + SPALTE_BREITE* SPALTEN//2 - len(titel) // 2, titel)
        gewinnen.refresh()
        
        while True:
            key = gewinnen.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                return
            
            elif key == ord(' '):
                self.board = []
                for r in range(ZEILEN):
                    self.board.append([CODE_LEER]*SPALTEN)
                self.schiffe = []
                break

        ausgewählte_zelle = Koordinate(0, 0)
        for type in SCHIFF_TYPEN:  #bei Auswahl der Option der manuellen Positionierung, vertikale oder horizontale Ausrichtung der Boote auf der Board
            while True:
                gewinnen.addstr(0, 0, self.name + " Platzieren Sie Ihre Schiffe." + blank)
                gewinnen.addstr(1, 0, "Schiff : " + type[0] + blank )
                
                mouse_kontrolle_msg = ["Verwenden Sie die Cursor-Tasten oder die Maus, um eine Zelle auszuwählen"]
                keyboard_kontrolle_msg = ["Drücken Sie " + "H" + " für horizontale Platzierung", "Drücken Sie " + "V" + " für vertikale Platzierung" ]
                
                kontrolle_msg = [mouse_kontrolle_msg, keyboard_kontrolle_msg]

                cx = offx + ZEILEN * SPALTE_BREITE+ offx
                cy = offy + SPALTEN//2
                
                gewinnen.addstr(cy - ZEILE_HÖHE, cx + len(mouse_kontrolle_msg[0])//2 - len("KONTROLLE")//2, "KONTROLLE")
                for cm in kontrolle_msg:
                    for m in cm:
                        gewinnen.addstr(cy, cx, m)
                        cy += 1
                    cy += 1
                gewinnen.refresh()
                        
                
                gewinnen.refresh()
                self.board_anzeigen(offx, offy, ausgewählte_zelle, False, gewinnen)
                orientierung = 'none'

                key = gewinnen.getch()

                if key == curses.KEY_DOWN:
                    ausgewählte_zelle.y += 1
                elif key == curses.KEY_UP:
                    ausgewählte_zelle.y -= 1
                elif key == curses.KEY_LEFT:
                    ausgewählte_zelle.x -= 1
                elif key == curses.KEY_RIGHT:
                    ausgewählte_zelle.x += 1


                elif key == curses.KEY_MOUSE:

                    _, mousex, mousey, _, bstate = curses.getmouse()
                    
                    row = (mousey - offy) // ZEILE_HÖHE
                    col = (mousex - 1 - offx)//SPALTE_BREITE
                    ausgewählte_zelle = Koordinate(col, row)

                    if SPALTEN <= ausgewählte_zelle.x  or ausgewählte_zelle.x < 0  or ausgewählte_zelle.y < 0 or ausgewählte_zelle.y >= ZEILEN :
                        continue
                
                if ausgewählte_zelle.x < 0:
                    ausgewählte_zelle.x = SPALTEN - 1
                if ausgewählte_zelle.x >= SPALTEN:
                    ausgewählte_zelle.x = 0
                if ausgewählte_zelle.y < 0:
                    ausgewählte_zelle.y = ZEILEN - 1
                if ausgewählte_zelle.y >=ZEILEN:
                    ausgewählte_zelle.y = 0    

                if key == ord('h'):
                    orientierung = 'h'
                    
                elif  key == ord('v'):
                    orientierung = 'v'

                if orientierung != 'none':
                    ship = Ship(type)
                    erfolg = self.platz_ship(ship, ausgewählte_zelle, orientierung)
                    if erfolg:
                        gewinnen.clear()
                        gewinnen.attron(curses.color_pair(2))
                        gewinnen.addstr(h - ZEILE_HÖHE*2, 0, type[0] + "erfolgreich hinzugefügt ")   
                        gewinnen.attron(curses.color_pair(2))
                        self.board_anzeigen(offx, offy, ausgewählte_zelle, False, gewinnen)
                        
                        break
                    else:
                        gewinnen.clear()
                        gewinnen.attron(curses.color_pair(4))
                        gewinnen.addstr(h- ZEILE_HÖHE*2, 0, "Kann es dort nicht platzieren.")
                        gewinnen.attroff(curses.color_pair(4))
                        
                gewinnen.refresh()
                #self.board_anzeigen(offx, offy, ausgewählte_zelle, False, gewinnen)
 
    def board_anzeigen(self, offx, offy, ausgewählte_zelle, hidden, gewinnen):

        for y in range(ZEILEN):
            for x in range(SPALTEN):
                
                if x == 0:
                    gewinnen.addstr(offy + y*ZEILE_HÖHE, offx - SPALTE_BREITE//2, str(y+1))

                if y == 0:
                    gewinnen.addstr(offy - ZEILE_HÖHE, offx + SPALTE_BREITE* x  + SPALTE_BREITE//2, chr(65 + x))

                code = self.board[y][x]
                
                ausgewähltes = Koordinate(x, y) == ausgewählte_zelle

                if code == CODE_LEER or code == CODE_HIT or code == CODE_MISS or code == CODE_versenkt:
                    zelle_zeichnen(Koordinate(x, y ), offx, offy, code, ausgewähltes, gewinnen)
                else:
                    if hidden:
                        zelle_zeichnen(Koordinate(x, y), offx, offy, CODE_LEER, ausgewähltes, gewinnen)
                    else:
                        zelle_zeichnen(Koordinate(x, y), offx, offy, " " + code + " ", ausgewähltes, gewinnen)

            #gewinnen.addch((y *ZEILE_HÖHE + offy, SPALTEN * SPALTE_BREITE+ offx, curses.ACS_VLINE)    
    
    def cpu_bewegung(self, gegner): 
        for y in range(ZEILEN): #CPU-Bewegung definieren, Verwendung der Randombibliothek zur Definition von Bewegungen
            for x in range(SPALTEN):
                if gegner.board[y][x] == CODE_HIT:
                    cell = Koordinate(x, y)
                    neighbors = [cell.left(), cell.right(), cell.up(), cell.down()]
                    random_cell = random.choice(neighbors)
                    if random_cell.x < 0 or random_cell.x >=SPALTEN or random_cell.y < 0 or random_cell.y >=ZEILEN:
                        continue
                    return random_cell
        randomy = secrets.randbelow(ZEILEN)
        randomx = secrets.randbelow(SPALTEN)

        return Koordinate(randomx, randomy)

    
def zelle_zeichnen(coord, offx, offy, code, ausgewähltes,gewinnen):
      #Grafische Darstellung des Boards mit verschiedenen Farben unter Verwendung von curses
    if ausgewähltes:
        gewinnen.attron(curses.color_pair(7))
        gewinnen.addstr(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE+ 1 + offx, str(code))  #Zellenfarbe auf das eingestellte Farbpaar ändern
        gewinnen.attroff(curses.color_pair(7))
    else: 
        if code == CODE_HIT or code == CODE_versenkt:
            gewinnen.attron(curses.color_pair(6))
            gewinnen.addstr(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE+ 1 + offx, str(code))  #Zellenfarbe auf das eingestellte Farbpaar ändern
            gewinnen.attroff(curses.color_pair(6))

        elif code == CODE_MISS:
            gewinnen.attron(curses.color_pair(1))
            gewinnen.addstr(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE + 1 + offx, str(code)) #Zellenfarbe auf das eingestellte Farbpaar ändern
            gewinnen.attroff(curses.color_pair(1))

        elif code == CODE_LEER:
            gewinnen.addstr(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE+ 1 + offx, str(code))
            
        else:
            gewinnen.attron(curses.color_pair(5))
            gewinnen.addstr(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE+ 1 + offx, str(code)) #Zellenfarbe auf das eingestellte Farbpaar ändern
            gewinnen.attroff(curses.color_pair(5))
    
    gewinnen.attron(curses.color_pair(3))
    gewinnen.addch(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE+ offx, curses.ACS_VLINE)
    gewinnen.addch(coord.y*ZEILE_HÖHE + offy, coord.x*SPALTE_BREITE+ SPALTE_BREITE+ offx, curses.ACS_VLINE)
    for i in range(SPALTE_BREITE+ 1): #Farbe der gesamten Spielerboard (grün) 
        if i == 0:
            gewinnen.addch(coord.y*ZEILE_HÖHE + offy - ZEILE_HÖHE//2, coord.x*SPALTE_BREITE+ offx + i, "+") 
        elif i == SPALTE_BREITE:
            gewinnen.addch(coord.y*ZEILE_HÖHE + offy - ZEILE_HÖHE//2, coord.x*SPALTE_BREITE+ offx + i, "+") 
        else:   
            gewinnen.addch(coord.y*ZEILE_HÖHE + offy - ZEILE_HÖHE//2, coord.x*SPALTE_BREITE+ offx + i, "-")
    for i in range(SPALTE_BREITE+ 1):
        if i == 0:
            gewinnen.addch(coord.y*ZEILE_HÖHE + offy + ZEILE_HÖHE//2, coord.x*SPALTE_BREITE+ offx + i, "+") 
        elif i == SPALTE_BREITE:
            gewinnen.addch(coord.y*ZEILE_HÖHE + offy + ZEILE_HÖHE//2, coord.x*SPALTE_BREITE+ offx + i, "+") 
        else:   
            gewinnen.addch(coord.y*ZEILE_HÖHE + offy + ZEILE_HÖHE//2, coord.x*SPALTE_BREITE+ offx + i, "-")
    gewinnen.attroff(curses.color_pair(3))

    gewinnen.refresh()


curses.wrapper(main)
