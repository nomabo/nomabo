"""Une fenêtre festive : ton texte, des feux d'artifice et des chats qui dansent."""

import base64
import colorsys
import io
import math
import random
import tkinter as tk

import customtkinter as ctk

# Seule la fonction "fete" est exportée par "from .fete import *"
__all__ = ["fete"]

_FOND = "#0b0b1e"
_COULEURS_FEU = ["#ff4d6d", "#ffd166", "#06d6a0", "#4cc9f0",
                 "#c77dff", "#ff9f1c", "#f72585", "#ffffff"]
# (couleur du pelage, couleur du contour)
_COULEURS_CHAT = [("#f4a259", "#a0522d"), ("#b0b8c1", "#5c6670"),
                  ("#f5f5f5", "#9a9a9a"), ("#3a3a3a", "#9a9a9a"),
                  ("#e8c39e", "#8b6b4a")]


def _vers_rgb(couleur):
    couleur = couleur.lstrip("#")
    return tuple(int(couleur[i:i + 2], 16) for i in (0, 2, 4))


def _melanger(c1, c2, t):
    """Mélange deux couleurs : t=0 donne c1, t=1 donne c2."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _vers_rgb(c1)
    r2, g2, b2 = _vers_rgb(c2)
    return "#%02x%02x%02x" % (int(r1 + (r2 - r1) * t),
                              int(g1 + (g2 - g1) * t),
                              int(b1 + (b2 - b1) * t))


def _arc_en_ciel(t):
    r, g, b = colorsys.hsv_to_rgb(t % 1, 0.55, 1)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def _image_latex(texte, taille, couleur):
    """Transforme un texte LaTeX en image PNG (encodée en base64) avec matplotlib."""
    # Import ici : matplotlib n'est chargé que si on utilise le LaTeX
    import matplotlib
    from matplotlib import patheffects
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    with matplotlib.rc_context({"mathtext.fontset": "cm"}):
        fig = Figure(figsize=(0.01, 0.01), dpi=100)
        FigureCanvasAgg(fig)
        fig.text(0, 0, texte, fontsize=taille, color=couleur,
                 path_effects=[patheffects.withStroke(linewidth=max(2, taille / 10),
                                                      foreground="#000000")])
        tampon = io.BytesIO()
        try:
            fig.savefig(tampon, format="png", transparent=True,
                        bbox_inches="tight", pad_inches=0.15)
        except ValueError as erreur:
            raise ValueError(f"Texte LaTeX invalide : {texte!r}\n{erreur}") from None
    return base64.b64encode(tampon.getvalue()).decode("ascii")


class _Fete:
    def __init__(self, texte, largeur, hauteur, nb_chats, duree, latex):
        ctk.set_appearance_mode("dark")
        self.fenetre = ctk.CTk()
        self.fenetre.title("C'est la fête !")
        self.fenetre.geometry(f"{largeur}x{hauteur}")
        self.fenetre.resizable(False, False)
        self.L, self.H = largeur, hauteur

        self.canvas = tk.Canvas(self.fenetre, width=largeur, height=hauteur,
                                bg=_FOND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._clic)

        self.temps = 0
        self.fusees = []
        self.particules = []
        self.actif = True

        # Étoiles qui scintillent
        self.etoiles = []
        for _ in range(80):
            x = random.uniform(0, largeur)
            y = random.uniform(0, hauteur * 0.75)
            r = random.choice([1, 1, 1.5])
            ident = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                            fill="#ffffff", outline="")
            self.etoiles.append((ident, random.uniform(0, 2 * math.pi)))

        # Texte
        self.latex = latex
        if latex:
            self._preparer_latex(texte)
        else:
            self.taille_texte = max(22, min(64, int(largeur / max(len(texte), 1) * 1.4)))
            police = ("Helvetica", self.taille_texte, "bold")
            self.ombre = self.canvas.create_text(largeur / 2 + 3, hauteur * 0.3 + 3,
                                                 text=texte, fill="#000000", font=police,
                                                 width=largeur - 60, justify="center")
            self.texte = self.canvas.create_text(largeur / 2, hauteur * 0.3,
                                                 text=texte, fill="#ffffff", font=police,
                                                 width=largeur - 60, justify="center")

        # Chats
        self.echelle = max(0.5, min(1.2, largeur / (nb_chats + 1) / 120))
        self.chats = []
        for i in range(nb_chats):
            corps, contour = _COULEURS_CHAT[i % len(_COULEURS_CHAT)]
            self.chats.append({
                "x": largeur * (i + 1) / (nb_chats + 1),
                "phase": random.uniform(0, 2 * math.pi),
                "vitesse": random.uniform(0.12, 0.2),
                "corps": corps,
                "contour": contour,
                "tag": f"chat{i}",
            })

        self.fenetre.protocol("WM_DELETE_WINDOW", self.fermer)
        if duree:
            self.fenetre.after(int(duree * 1000), self.fermer)

        self._boucle()
        self.fenetre.mainloop()

    def _preparer_latex(self, texte, nb_images=32):
        """Prépare à l'avance des images du texte (couleurs et tailles qui varient),
        car redessiner du LaTeX à chaque image de l'animation serait trop lent."""
        # On mesure d'abord le texte pour qu'il tienne dans la fenêtre
        taille = 40
        essai = tk.PhotoImage(master=self.canvas, data=_image_latex(texte, taille, "#ffffff"))
        reduction = min(1.0, (self.L - 60) / essai.width(), (self.H * 0.45) / essai.height())
        taille = taille * reduction / 1.08  # marge pour la pulsation

        self.images_latex = []
        for i in range(nb_images):
            t = i / nb_images
            pulsation = 1 + 0.08 * math.sin(2 * math.pi * 2 * t)
            donnees = _image_latex(texte, taille * pulsation, _arc_en_ciel(t))
            self.images_latex.append(tk.PhotoImage(master=self.canvas, data=donnees))
        self.texte = self.canvas.create_image(self.L / 2, self.H * 0.3,
                                              image=self.images_latex[0])

    def fermer(self):
        self.actif = False
        try:
            # Annule les animations en attente pour éviter des messages d'erreur
            for ident in self.fenetre.tk.call("after", "info"):
                self.fenetre.after_cancel(ident)
            self.fenetre.destroy()
        except tk.TclError:
            pass

    # ---------- Feux d'artifice ----------

    def _clic(self, event):
        self._lancer_fusee(event.x, event.y)

    def _lancer_fusee(self, cible_x=None, cible_y=None):
        if cible_x is None:
            x = random.uniform(self.L * 0.1, self.L * 0.9)
            cible = random.uniform(self.H * 0.08, self.H * 0.5)
            vx = random.uniform(-0.6, 0.6)
        else:
            x, cible, vx = cible_x, cible_y, 0
        couleur = random.choice(_COULEURS_FEU)
        ident = self.canvas.create_oval(x - 2, self.H - 5, x + 2, self.H + 5,
                                        fill=couleur, outline="")
        self.fusees.append({"x": x, "y": float(self.H), "vx": vx, "cible": cible,
                            "couleur": couleur, "id": ident})

    def _exploser(self, x, y, couleur):
        nb = random.randint(40, 70)
        multicolore = random.random() < 0.3
        for k in range(nb):
            angle = 2 * math.pi * k / nb + random.uniform(-0.05, 0.05)
            vitesse = random.uniform(2, 5.5)
            c = random.choice(_COULEURS_FEU) if multicolore else couleur
            r = random.choice([1.5, 2, 2.5])
            ident = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                            fill=c, outline="")
            self.particules.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * vitesse, "vy": math.sin(angle) * vitesse,
                "vie": 1.0, "usure": random.uniform(0.012, 0.022),
                "couleur": c, "r": r, "id": ident,
            })

    # ---------- Chats ----------

    def _dessiner_chat(self, chat):
        c, s, ph, tag = self.canvas, self.echelle, chat["phase"], chat["tag"]
        corps, contour = chat["corps"], chat["contour"]
        trait = max(1, int(2 * s))
        sombre = sum(_vers_rgb(corps)) < 300
        couleur_yeux = "#ffd166" if sombre else "#222222"

        saut = abs(math.sin(ph)) * 22 * s
        x = chat["x"] + math.sin(ph * 0.5) * 10 * s
        y = self.H - 20 * s - saut  # bas du corps

        # Queue qui ondule
        pts = []
        for k in range(8):
            t = k / 7
            pts += [x - 20 * s - t * 30 * s,
                    y - 15 * s - t * 35 * s + math.sin(ph * 2 + t * 3) * 10 * s]
        c.create_line(*pts, fill=contour, width=10 * s, smooth=True,
                      capstyle="round", tags=tag)
        c.create_line(*pts, fill=corps, width=7 * s, smooth=True,
                      capstyle="round", tags=tag)

        # Pattes arrière qui se lèvent à tour de rôle
        for cote, decalage in ((-1, 0), (1, math.pi)):
            lever = max(0, math.sin(ph * 2 + decalage)) * 6 * s
            px = x + cote * 12 * s
            c.create_oval(px - 9 * s, y - 8 * s - lever, px + 9 * s, y + 4 * s - lever,
                          fill=corps, outline=contour, width=trait, tags=tag)

        # Corps
        c.create_oval(x - 24 * s, y - 45 * s, x + 24 * s, y,
                      fill=corps, outline=contour, width=trait, tags=tag)
        c.create_oval(x - 12 * s, y - 35 * s, x + 12 * s, y - 8 * s,
                      fill=_melanger(corps, "#ffffff", 0.35), outline="", tags=tag)

        # Bras qui s'agitent
        for cote, decalage in ((-1, 0), (1, math.pi)):
            angle = math.radians(60 + 50 * math.sin(ph * 2 + decalage))
            ex, ey = x + cote * 18 * s, y - 35 * s
            mx = ex + cote * math.cos(angle) * 24 * s
            my = ey - math.sin(angle) * 24 * s
            c.create_line(ex, ey, mx, my, fill=contour, width=10 * s,
                          capstyle="round", tags=tag)
            c.create_line(ex, ey, mx, my, fill=corps, width=7 * s,
                          capstyle="round", tags=tag)

        # Tête (penche d'un côté à l'autre)
        hx = x + math.sin(ph) * 6 * s
        hy = y - 62 * s
        frisson = math.sin(ph * 3) * 3 * s
        for cote in (-1, 1):
            oreille = [hx + cote * 20 * s, hy - 6 * s,
                       hx + cote * 14 * s + frisson, hy - 34 * s,
                       hx + cote * 3 * s, hy - 19 * s]
            c.create_polygon(*oreille, fill=corps, outline=contour,
                             width=trait, tags=tag)
            interieur = [hx + cote * 16 * s, hy - 10 * s,
                         hx + cote * 13 * s + frisson, hy - 26 * s,
                         hx + cote * 7 * s, hy - 17 * s]
            c.create_polygon(*interieur, fill="#ffb3c6", outline="", tags=tag)
        c.create_oval(hx - 23 * s, hy - 21 * s, hx + 23 * s, hy + 19 * s,
                      fill=corps, outline=contour, width=trait, tags=tag)

        # Yeux heureux ^^
        for cote in (-1, 1):
            ox = hx + cote * 9 * s
            c.create_arc(ox - 5 * s, hy - 7 * s, ox + 5 * s, hy + 3 * s,
                         start=0, extent=180, style="arc",
                         outline=couleur_yeux, width=trait, tags=tag)
            # joues roses
            jx = hx + cote * 14 * s
            c.create_oval(jx - 4 * s, hy + 3 * s, jx + 4 * s, hy + 8 * s,
                          fill="#ff8fab", outline="", tags=tag)

        # Nez et bouche
        c.create_polygon(hx - 3 * s, hy + 2 * s, hx + 3 * s, hy + 2 * s, hx, hy + 6 * s,
                         fill="#ff6b8b", outline="", tags=tag)
        for cote in (-1, 1):
            c.create_arc(hx + min(0, cote * 6 * s), hy + 2 * s,
                         hx + max(0, cote * 6 * s), hy + 10 * s,
                         start=180, extent=180, style="arc",
                         outline=couleur_yeux, width=trait, tags=tag)

        # Moustaches
        for cote in (-1, 1):
            for dy in (-2, 4):
                c.create_line(hx + cote * 10 * s, hy + 5 * s,
                              hx + cote * 30 * s, hy + (5 + dy) * s,
                              fill=couleur_yeux, width=1, tags=tag)

    # ---------- Animation ----------

    def _boucle(self):
        if not self.actif:
            return
        try:
            self._etape()
            self.fenetre.after(30, self._boucle)
        except tk.TclError:
            pass  # la fenêtre a été fermée

    def _etape(self):
        c = self.canvas
        self.temps += 1

        # Étoiles
        if self.temps % 3 == 0:
            for ident, decalage in self.etoiles:
                t = (math.sin(self.temps * 0.08 + decalage) + 1) / 2
                c.itemconfig(ident, fill=_melanger("#444466", "#ffffff", t))

        # Fusées
        if random.random() < 0.06:
            self._lancer_fusee()
        restantes = []
        for f in self.fusees:
            f["y"] -= 9
            f["x"] += f["vx"]
            if f["y"] <= f["cible"]:
                c.delete(f["id"])
                self._exploser(f["x"], f["y"], f["couleur"])
            else:
                c.coords(f["id"], f["x"] - 2, f["y"] - 5, f["x"] + 2, f["y"] + 5)
                restantes.append(f)
        self.fusees = restantes

        # Étincelles (gravité + fondu)
        vivantes = []
        for p in self.particules:
            p["vy"] += 0.08
            p["vx"] *= 0.98
            p["vy"] *= 0.98
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vie"] -= p["usure"]
            if p["vie"] <= 0:
                c.delete(p["id"])
                continue
            r = p["r"]
            c.coords(p["id"], p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r)
            c.itemconfig(p["id"], fill=_melanger(_FOND, p["couleur"], p["vie"]))
            vivantes.append(p)
        self.particules = vivantes

        # Texte qui pulse et change de couleur
        if self.latex:
            image = self.images_latex[(self.temps // 3) % len(self.images_latex)]
            c.itemconfig(self.texte, image=image)
        else:
            taille = int(self.taille_texte * (1 + 0.08 * math.sin(self.temps * 0.12)))
            police = ("Helvetica", taille, "bold")
            c.itemconfig(self.texte, font=police, fill=_arc_en_ciel(self.temps * 0.01))
            c.itemconfig(self.ombre, font=police)
            c.tag_raise(self.ombre)
        c.tag_raise(self.texte)

        # Chats qui dansent
        for chat in self.chats:
            chat["phase"] += chat["vitesse"]
            c.delete(chat["tag"])
            self._dessiner_chat(chat)


def fete(texte="Bravo !", largeur=800, hauteur=600, nb_chats=5, duree=None,
         latex=False):
    """Ouvre une fenêtre avec un texte, des feux d'artifice et des chats qui dansent.

    texte    : le message à afficher
    largeur  : largeur de la fenêtre en pixels
    hauteur  : hauteur de la fenêtre en pixels
    nb_chats : nombre de chats qui dansent
    duree    : si indiqué (en secondes), la fenêtre se ferme toute seule
    latex    : si True, le texte est interprété comme du LaTeX
               (les formules s'écrivent entre $...$, par exemple
               r"$e^{i\\pi} + 1 = 0$" ; pense au r devant les guillemets)

    Astuce : clique dans la fenêtre pour lancer un feu d'artifice !
    """
    _Fete(texte, largeur, hauteur, nb_chats, duree, latex)