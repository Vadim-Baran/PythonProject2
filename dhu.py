import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ------------------------
# Paramètres cartes
# ------------------------
LARGEUR, HAUTEUR, RAYON = 80, 100, 25
COULEURS = {"Rouge": (217,4,41), "Jaune": (255,234,0), "Vert": (31,170,0), "Bleu": (0,89,214), "Noir": (0,0,0)}
VALEURS = ["0","1","2","3","4","5","6","7","8","9","Inversion","Saut","+2"]
SPECIALES = ["Joker","+4"]

# Police
try:
    FONT = ImageFont.truetype("arial.ttf", 20)
except:
    FONT = ImageFont.load_default()

# ------------------------
# Création cartes PNG
# ------------------------
def rectangle_arrondi(draw, xy, r, fill):
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill)
    except:
        draw.rectangle(xy, fill=fill)

def creer_carte(couleur, valeur, nom_fichier):
    img = Image.new("RGBA", (LARGEUR, HAUTEUR), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    rectangle_arrondi(draw, (0,0,LARGEUR,HAUTEUR), RAYON, COULEURS[couleur])
    texte_couleur = "white" if couleur in ["Rouge","Bleu","Noir"] else "black"
    bbox = draw.textbbox((0,0), valeur, font=FONT)
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((LARGEUR-w)//2,(HAUTEUR-h)//2), valeur, font=FONT, fill=texte_couleur)
    img.save(nom_fichier)

if not os.path.exists("cartes"):
    os.makedirs("cartes")

# Cartes classiques
for couleur in ["Rouge","Jaune","Vert","Bleu"]:
    for valeur in VALEURS:
        reps = 1 if valeur=="0" else 2
        for i in range(reps):
            fichier = f"cartes/{couleur}_{valeur}_{i+1}.png"
            if not os.path.exists(fichier):
                creer_carte(couleur, valeur, fichier)

# Cartes noires
for valeur in SPECIALES:
    for i in range(4):
        fichier = f"cartes/Noir_{valeur}_{i+1}.png"
        if not os.path.exists(fichier):
            creer_carte("Noir", valeur, fichier)

# ------------------------
# Fonctions UNO
# ------------------------
def creer_paquet():
    paquet=[]
    for c in ["Rouge","Jaune","Vert","Bleu"]:
        for v in VALEURS:
            paquet.append((c,v))
            if v!="0":
                paquet.append((c,v))
    for s in SPECIALES:
        paquet += [("Noir",s)]*4
    random.shuffle(paquet)
    return paquet

def carte_valide(carte, sommet):
    c1,v1 = carte
    c2,v2 = sommet
    return c1==c2 or v1==v2 or c1=="Noir"

# ------------------------
# Création d'un fond d'écran dynamique
# ------------------------
def creer_fond_uno(largeur, hauteur):
    img = Image.new("RGB", (largeur, hauteur), (30,30,30))
    draw = ImageDraw.Draw(img)
    # Cercles colorés
    couleurs = [(217,4,41), (255,234,0), (31,170,0), (0,89,214)]
    rayon_cercle = 100
    positions = [(largeur//4, hauteur//3), (3*largeur//4, hauteur//3), (largeur//4, 2*hauteur//3), (3*largeur//4, 2*hauteur//3)]
    for pos, c in zip(positions, couleurs):
        draw.ellipse([pos[0]-rayon_cercle, pos[1]-rayon_cercle, pos[0]+rayon_cercle, pos[1]+rayon_cercle], fill=c+(100,), outline=None)
    # Texte UNO au centre
    try:
        font_big = ImageFont.truetype("arial.ttf", 80)
    except:
        font_big = ImageFont.load_default()
    texte = "UNO"
    bbox = draw.textbbox((0,0), texte, font=font_big)
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((largeur-w)//2,(hauteur-h)//2), texte, fill=(255,255,255,180), font=font_big)
    return img

# ------------------------
# Menu principal
# ------------------------
class MenuUno:
    def __init__(self, root):
        self.root = root
        self.root.title("UNO - Menu")
        tk.Label(root, text="=== Configuration UNO ===", font=("Arial",18)).pack(pady=20)
        tk.Label(root, text="Joueurs humains :", font=("Arial",14)).pack()
        self.var_humains = tk.IntVar(value=1)
        tk.Spinbox(root, from_=1,to=4, textvariable=self.var_humains, width=5, font=("Arial",14)).pack(pady=5)
        tk.Label(root, text="Bots :", font=("Arial",14)).pack()
        self.var_bots = tk.IntVar(value=1)
        tk.Spinbox(root, from_=0,to=4, textvariable=self.var_bots, width=5, font=("Arial",14)).pack(pady=5)
        tk.Button(root,text="Commencer", font=("Arial",16), bg="green",fg="white", command=self.lancer_partie).pack(pady=25)

    def lancer_partie(self):
        nb_humains = self.var_humains.get()
        nb_bots = self.var_bots.get()
        for widget in self.root.winfo_children():
            widget.destroy()
        UnoGUI(self.root, nb_humains, nb_bots)

# ------------------------
# UNO GUI complet
# ------------------------
class UnoGUI:
    def __init__(self, root, nb_humains=1, nb_bots=1):
        self.root = root
        self.root.title("UNO Graphique")
        self.nb_humains = nb_humains
        self.nb_joueurs = nb_humains + nb_bots
        self.sens_horaire = True
        self.joueur_actuel = 0

        # Créer le fond d'écran avec PIL, puis convertir en PhotoImage
        fond_pil = creer_fond_uno(1500, 1100)
        self.bg_image = ImageTk.PhotoImage(fond_pil)
        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Charger images cartes
        self.charger_images()

        # Paquet, mains, pile
        self.paquet = creer_paquet()
        self.mains = [[self.paquet.pop() for _ in range(7)] for _ in range(self.nb_joueurs)]
        premiere_carte = self.paquet.pop()
        if premiere_carte[0]=="Noir":
            premiere_carte=(random.choice(["Rouge","Jaune","Vert","Bleu"]), premiere_carte[1])
        self.pile=[premiere_carte]

        # Layout
        self.frame_pioche = tk.Frame(root, bd=0)
        self.frame_pioche.pack(pady=5)
        self.label_pioche = tk.Label(self.frame_pioche, image=self.dos_carte)
        self.label_pioche.pack(side="left")
        self.label_compteur = tk.Label(self.frame_pioche, text=f"{len(self.paquet)} cartes", font=("Arial",12))
        self.label_compteur.pack(side="left", padx=10)

        self.frame_pile = tk.Frame(root, bd=0)
        self.frame_pile.pack(pady=5)
        self.label_pile = tk.Label(self.frame_pile)
        self.label_pile.pack()

        self.frame_main = tk.Frame(root)
        self.frame_main.pack(pady=10)

        self.label_info = tk.Label(root, text="", fg="blue", font=("Arial",14))
        self.label_info.pack(pady=10)

        self.bouton_piocher = tk.Button(root, text="Piocher", command=self.piocher_carte)
        self.bouton_piocher.pack(pady=10)

        # Référence pour les images modifiées
        self.image_pile_modifiee = None

        self.mettre_a_jour()

    # ------------------------
    def charger_images(self):
        self.images={}
        self.dos_carte=None
        for fichier in os.listdir("cartes"):
            if fichier.endswith(".png"):
                nom=fichier.replace(".png","")
                parts=nom.split("_")
                if parts[0].lower()=="dos":
                    self.dos_carte=tk.PhotoImage(file=f"cartes/{fichier}")
                    continue
                if len(parts)==3:
                    couleur,valeur,_=parts
                elif len(parts)==2:
                    couleur,valeur=parts
                else:
                    continue
                self.images[(couleur,valeur)]=tk.PhotoImage(file=f"cartes/{fichier}")
        if self.dos_carte is None:
            self.dos_carte=tk.PhotoImage(width=150,height=240)

    # ------------------------
    def mettre_a_jour(self):
        # Mettre à jour pioche
        self.label_pioche.config(image=self.dos_carte)
        self.label_pioche.image = self.dos_carte
        self.label_compteur.config(text=f"{len(self.paquet)} cartes")

        # Pile
        sommet = self.pile[-1]
        if sommet[1] not in ["Joker","+4"]:
            image_carte = self.images.get((sommet[0], sommet[1]), self.dos_carte)
        else:
            # Joker → afficher carré coloré
            base = self.images.get(("Noir", sommet[1]), self.dos_carte)
            pil_img = ImageTk.getimage(base).convert("RGBA")
            draw = ImageDraw.Draw(pil_img)
            couleur_rgb = {"Rouge": (217,4,41), "Jaune": (255,234,0), "Vert": (31,170,0), "Bleu": (0,89,214)}.get(sommet[0], (255,255,255))
            draw.rectangle([LARGEUR//2-20, HAUTEUR//2-20, LARGEUR//2+20, HAUTEUR//2+20], fill=couleur_rgb)
            self.image_pile_modifiee = ImageTk.PhotoImage(pil_img)
            image_carte = self.image_pile_modifiee

        self.label_pile.config(image=image_carte)
        self.label_pile.image = image_carte

        # Main humaine
        for w in self.frame_main.winfo_children():
            w.destroy()
        for i, carte in enumerate(self.mains[0]):
            img = self.images.get((carte[0], carte[1]), self.dos_carte)
            lbl = tk.Label(self.frame_main, image=img)
            lbl.image = img
            lbl.grid(row=0, column=i, padx=5)
            lbl.bind("<Button-1>", lambda e, i=i: self.jouer_carte(i))

        # Bots
        for widget in self.root.pack_slaves():
            if isinstance(widget, tk.Frame) and widget not in [self.frame_pioche,self.frame_pile,self.frame_main]:
                widget.destroy()
        for j in range(self.nb_humains, self.nb_joueurs):
            frame_bot = tk.Frame(self.root)
            frame_bot.pack(pady=4)
            lbl = tk.Label(frame_bot, image=self.dos_carte)
            lbl.pack(side="left")
            tk.Label(frame_bot, text=f"Bot {j-self.nb_humains+1} ({len(self.mains[j])} cartes)").pack(side="left", padx=5)

        self.root.update()

    # ------------------------
    # Jouer carte humaine
    def jouer_carte(self, index):
        if self.joueur_actuel !=0:
            self.label_info.config(text="Pas ton tour !")
            return
        carte = self.mains[0][index]
        if carte[0]=="Noir":
            self.choisir_couleur(lambda c:self.jouer_noir(index,c))
            return
        if not carte_valide(carte,self.pile[-1]):
            self.label_info.config(text="Carte non valide !")
            return
        self.mains[0].pop(index)
        self.pile.append(carte)
        self.label_info.config(text=f"Tu joues {carte}")
        self.mettre_a_jour()
        self.appliquer_effet_carte(carte)

    def jouer_noir(self,index,couleur):
        carte=self.mains[0][index]
        self.mains[0].pop(index)
        self.pile.append((couleur,carte[1]))
        self.label_info.config(text=f"Joker → couleur : {couleur}")
        self.mettre_a_jour()
        self.appliquer_effet_carte((couleur,carte[1]))

    def choisir_couleur(self,callback):
        popup = tk.Toplevel(self.root)
        popup.title("Choisir couleur")
        for c in ["Rouge","Jaune","Vert","Bleu"]:
            tk.Button(popup,text=c,width=15,height=2,command=lambda c=c:(callback(c),popup.destroy())).pack(pady=5)

    # ------------------------
    # Effets cartes
    def appliquer_effet_carte(self,carte):
        valeur = carte[1]
        if valeur=="+2":
            self.root.after(800, lambda:self.punir_joueur_suivant(2))
        elif valeur=="+4":
            self.root.after(800, lambda:self.punir_joueur_suivant(4))
        elif valeur=="Saut":
            self.root.after(800,self.sauter_tour_suivant)
        elif valeur=="Inversion":
            self.sens_horaire = not self.sens_horaire
            self.label_info.config(text="Sens inversé !")
            self.root.after(800,self.tour_pnj)
        else:
            self.joueur_actuel=1
            self.root.after(600,self.tour_pnj)

    def piocher_carte(self):
        if not self.paquet:
            messagebox.showinfo("UNO","La pioche est vide !")
            return
        carte = self.paquet.pop()
        self.mains[0].append(carte)
        self.label_info.config(text=f"Tu pioches {carte}")
        self.mettre_a_jour()
        self.joueur_actuel=1
        self.root.after(600,self.tour_pnj)

    def punir_joueur_suivant(self,n):
        bot=1
        for _ in range(n):
            if self.paquet:
                self.mains[bot].append(self.paquet.pop())
        self.label_info.config(text=f"Bot pioche {n} cartes !")
        self.mettre_a_jour()
        self.joueur_actuel=1
        self.root.after(600,self.tour_pnj)

    def sauter_tour_suivant(self):
        self.label_info.config(text="Bot saute son tour !")
        self.mettre_a_jour()
        self.joueur_actuel=1
        self.root.after(600,self.tour_pnj)

    # ------------------------
    # Tour bot
    def tour_pnj(self):
        j=1
        coups=[c for c in self.mains[j] if carte_valide(c,self.pile[-1])]
        if coups:
            carte=random.choice(coups)
            self.mains[j].remove(carte)
            if carte[0]=="Noir":
                couleur=random.choice(["Rouge","Jaune","Vert","Bleu"])
                self.pile.append((couleur,carte[1]))
                self.label_info.config(text=f"Bot joue Joker → couleur : {couleur}")
            else:
                self.pile.append(carte)
                self.label_info.config(text=f"Bot joue {carte}")
            self.mettre_a_jour()
            self.appliquer_effet_bot(carte)
            return
        if self.paquet:
            self.mains[j].append(self.paquet.pop())
            self.label_info.config(text="Bot pioche")
            self.mettre_a_jour()
        self.joueur_actuel=0

    def appliquer_effet_bot(self,carte):
        v=carte[1]
        if v=="+2":
            self.root.after(700, lambda:self.punir_joueur_humain(2))
        elif v=="+4":
            self.root.after(700, lambda:self.punir_joueur_humain(4))
        elif v=="Saut":
            self.root.after(700,self.sauter_tour_joueur)
        elif v=="Inversion":
            self.sens_horaire = not self.sens_horaire
            self.joueur_actuel=0
        else:
            self.joueur_actuel=0

    def punir_joueur_humain(self,n):
        for _ in range(n):
            if self.paquet:
                self.mains[0].append(self.paquet.pop())
        self.label_info.config(text=f"Tu pioches {n} cartes !")
        self.mettre_a_jour()
        self.joueur_actuel=0

    def sauter_tour_joueur(self):
        self.label_info.config(text="Tu sautes ton tour !")
        self.mettre_a_jour()
        self.joueur_actuel=1
        self.root.after(600,self.tour_pnj)

# ------------------------
# Lancement
# ------------------------
if __name__=="__main__":
    root = tk.Tk()
    root.geometry("1400x1000")
    MenuUno(root)
    root.mainloop()
