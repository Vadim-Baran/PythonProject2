from PIL import Image, ImageDraw, ImageFont
import os

# --------------------------
# PARAMÈTRES GÉNÉRAUX
# --------------------------
LARGEUR = 80
HAUTEUR = 100
RAYON = 25  # coins arrondis

COULEURS = {
    "Rouge":  (217, 4, 41),
    "Jaune":  (255, 234, 0),
    "Vert":   (31, 170, 0),
    "Bleu":   (0, 89, 214),
    "Noir":   (0, 0, 0)
}

VALEURS = ["0","1","2","3","4","5","6","7","8","9","Inversion","Saut","+2"]
SPECIALES = ["Joker","+4"]

# Chargement police
try:
    FONT = ImageFont.truetype("arial.ttf", 20)
except:
    FONT = ImageFont.load_default()

# --------------------------
# RECTANGLE ARRONDI
# --------------------------
def rectangle_arrondi(draw, xy, r, fill):
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill)
    except:
        # Fallback si version Pillow ancienne
        draw.rectangle(xy, fill=fill)

# --------------------------
# CRÉATION D’UNE CARTE
# --------------------------
def creer_carte(couleur, valeur, nom_fichier):
    img = Image.new("RGBA", (LARGEUR, HAUTEUR), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # fond
    rectangle_arrondi(draw, (0, 0, LARGEUR, HAUTEUR), RAYON, COULEURS[couleur])

    # Couleur texte
    texte_couleur = "white" if couleur in ["Rouge","Bleu","Noir"] else "black"

    # Mesure du texte (Pillow 10+)
    bbox = draw.textbbox((0,0), valeur, font=FONT)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    # Texte centré
    draw.text(
        ((LARGEUR - w)//2, (HAUTEUR - h)//2),
        valeur,
        font=FONT,
        fill=texte_couleur
    )

    img.save(nom_fichier)


# --------------------------
# DOSSIER
# --------------------------
if not os.path.exists("cartes"):
    os.makedirs("cartes")

# --------------------------
# CARTES CLASSIQUES
# --------------------------
for couleur in ["Rouge","Jaune","Vert","Bleu"]:
    for valeur in VALEURS:
        reps = 1 if valeur == "0" else 2
        for i in range(reps):
            fichier = f"cartes/{couleur}_{valeur}_{i+1}.png"
            creer_carte(couleur, valeur, fichier)

# --------------------------
# CARTES NOIRES
# --------------------------
for valeur in SPECIALES:
    for i in range(4):
        fichier = f"cartes/Noir_{valeur}_{i+1}.png"
        creer_carte("Noir", valeur, fichier)


print("✔️ Toutes les cartes UNO ont été générées avec succès dans /cartes/")
