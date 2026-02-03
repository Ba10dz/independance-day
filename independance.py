import pygame
import random
import sys
import os
import glob
import math

# --- Initialisation ---
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

# --- Constantes (Format 16:9) ---
LARGEUR_JEU = 1280
HAUTEUR_JEU = 720
FPS = 60

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 255, 0) # Ajout du Vert pour la barre de vie
VERT_MILITAIRE = (46, 139, 87)
GRIS_FONCE = (50, 50, 50)
GRIS_TORNADE_PETITE = (180, 180, 180)
GRIS_TORNADE_MOYENNE = (120, 100, 100)
GRIS_TORNADE_GROSSE = (80, 50, 50)
JAUNE = (255, 255, 0)
ROUGE = (255, 0, 0)
ROUGE_SANG = (180, 0, 0)
ORANGE = (255, 165, 0)
OR = (255, 215, 0)
BLEU_NUIT = (20, 20, 60)
BLEU_BOUCLIER = (0, 191, 255)

# Configuration écran
ecran = pygame.display.set_mode((LARGEUR_JEU, HAUTEUR_JEU))
pygame.display.set_caption("Independance Day : Ultimate Edition")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
petite_font = pygame.font.Font(None, 24)
grosse_font = pygame.font.Font(None, 80)

# --- SYSTEME DE PARTICULES (VFX) ---
class Particule:
    def __init__(self, x, y, couleur, vitesse, taille, vie):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.vx = random.uniform(-vitesse, vitesse)
        self.vy = random.uniform(-vitesse, vitesse)
        self.taille = taille
        self.vie = vie
        self.vie_max = vie

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vie -= 1
        self.taille *= 0.9

    def draw(self, surface):
        if self.vie > 0:
            alpha = int((self.vie / self.vie_max) * 255)
            s = pygame.Surface((int(self.taille*2), int(self.taille*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.couleur, alpha), (int(self.taille), int(self.taille)), int(self.taille))
            surface.blit(s, (self.x, self.y))

class GestionnaireVFX:
    def __init__(self):
        self.particules = []
        self.ecran_rouge = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU))
        self.ecran_rouge.fill(ROUGE)
        self.flash_nuke = 0

    def ajouter(self, x, y, couleur, count=5):
        for _ in range(count):
            self.particules.append(Particule(x, y, couleur, 3, random.randint(3, 6), 30))
    
    def declencher_nuke(self):
        self.flash_nuke = 255

    def update(self):
        for p in self.particules[:]:
            p.update()
            if p.vie <= 0: self.particules.remove(p)
        if self.flash_nuke > 0: self.flash_nuke -= 5

    def draw(self, surface):
        for p in self.particules: p.draw(surface)
        if self.flash_nuke > 0:
            s = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU))
            s.fill(BLANC)
            s.set_alpha(self.flash_nuke)
            surface.blit(s, (0,0))

    def draw_low_hp(self, surface):
        alpha = int(50 + math.sin(pygame.time.get_ticks() * 0.01) * 30)
        self.ecran_rouge.set_alpha(alpha)
        surface.blit(self.ecran_rouge, (0,0), special_flags=pygame.BLEND_ADD)


# --- GESTIONNAIRE DE MUSIQUE ---
class GestionnaireMusique:
    def __init__(self):
        self.volume_musique = 0.5
        self.volume_effets = 0.7
        self.musique_active = True
        self.effets_actifs = True
        self.musiques_niveaux = {}
        self.effets_sonores = {}
        self.musique_en_cours = None
        self.charger_tout()
    
    def charger_tout(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path_m = os.path.join(base, "musiques")
        if os.path.exists(path_m):
            files = sorted([f for f in os.listdir(path_m) if f.endswith(('.mp3','.ogg','.wav'))])
            for i, f in enumerate(files[:3]):
                self.musiques_niveaux[i+1] = os.path.join(path_m, f)
        
        path_s = os.path.join(base, "sons")
        map_effets = {
            "tir": ["tir", "shoot"], "explosion": ["boom", "explosion"],
            "degats": ["hit", "degats"], "piece": ["coin", "piece"],
            "gameover": ["death", "gameover"], "soin": ["heal", "heart"],
            "nuke": ["nuke"], "levelup": ["levelup"]
        }
        if os.path.exists(path_s):
            for f in os.listdir(path_s):
                for k, v in map_effets.items():
                    if any(x in f.lower() for x in v):
                        try:
                            self.effets_sonores[k] = pygame.mixer.Sound(os.path.join(path_s, f))
                            self.effets_sonores[k].set_volume(self.volume_effets)
                        except: pass

    def jouer_musique(self, niv):
        if not self.musique_active: return
        fichier = self.musiques_niveaux.get(niv, self.musiques_niveaux.get(1))
        if fichier and self.musique_en_cours != fichier:
            try:
                pygame.mixer.music.load(fichier)
                pygame.mixer.music.set_volume(self.volume_musique)
                pygame.mixer.music.play(-1)
                self.musique_en_cours = fichier
            except: pass

    def effet(self, nom):
        if self.effets_actifs and nom in self.effets_sonores:
            self.effets_sonores[nom].play()

    def arreter(self): pygame.mixer.music.stop()
    def toggle_m(self): 
        self.musique_active = not self.musique_active
        if not self.musique_active: self.arreter()
        return self.musique_active
    def toggle_e(self): 
        self.effets_actifs = not self.effets_actifs
        return self.effets_actifs

# --- CLASSES DU JEU ---

class Bouton:
    def __init__(self, cx, cy, w, h, texte, action=None):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.texte = texte
        self.action = action
        self.est_survole = False

    def dessiner(self, surface):
        col = ORANGE if self.est_survole else GRIS_FONCE
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLANC, self.rect, 2, border_radius=10)
        txt = font.render(self.texte, True, BLANC)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def verifier(self, pos, click):
        self.est_survole = self.rect.collidepoint(pos)
        if self.est_survole and click and self.action: return self.action()

class Soldat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), "soldier.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (50, 60))
        except:
            self.image = pygame.Surface([50, 60])
            self.image.fill(VERT_MILITAIRE)
            pygame.draw.rect(self.image, (30, 90, 55), [20, 0, 10, 20])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGEUR_JEU // 2
        self.rect.bottom = HAUTEUR_JEU - 20
        
        # Stats et Améliorations
        self.niveau_tir = 1 # 1, 2, 3
        self.niveau_cadence = 1 
        self.cadence_base = 350
        
        self.invincible = False
        self.fin_invincibilite = 0
        self.nukes = 0
        self.dernier_tir = 0

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.clamp_ip(ecran.get_rect())
        if self.invincible and pygame.time.get_ticks() > self.fin_invincibilite:
            self.invincible = False

    def tirer(self):
        now = pygame.time.get_ticks()
        delai = max(50, self.cadence_base - (self.niveau_cadence * 40))
        
        if now - self.dernier_tir > delai:
            self.dernier_tir = now
            balles = []
            x, y = self.rect.centerx, self.rect.top
            
            if self.niveau_tir == 1:
                balles.append(Balle(x, y))
            elif self.niveau_tir == 2:
                balles.append(Balle(x-10, y, -5))
                balles.append(Balle(x+10, y, 5))
            elif self.niveau_tir >= 3:
                for angle in [-15, -5, 5, 15]:
                    balles.append(Balle(x, y, angle))
            return balles
        return []

class Tornade(pygame.sprite.Sprite):
    def __init__(self, niveau_jeu):
        super().__init__()
        self.niveau_jeu = niveau_jeu
        
        # --- TAILLE ET VITESSE ---
        if niveau_jeu == 1: scale = random.randint(40, 60)
        elif niveau_jeu == 2: scale = random.randint(50, 80)
        else: scale = random.randint(60, 100)

        # Vitesse verticale (chute)
        self.vy = int(scale / 10) + random.randint(1, 3) 
        
        # --- POSITION DE DEPART (TOUJOURS EN HAUT) ---
        self.rect = pygame.Rect(0, 0, scale, int(scale*1.5))
        self.rect.x = random.randint(0, LARGEUR_JEU - scale)
        self.rect.y = -self.rect.height # Au dessus de l'écran
        
        # --- COMPORTEMENT SELON NIVEAU ---
        self.vx = 0 # Vitesse horizontale par défaut
        
        if niveau_jeu == 1:
            self.pv = 1
            self.vx = 0 # Tombe tout droit
            self.couleur = GRIS_TORNADE_PETITE
        elif niveau_jeu == 2:
            self.pv = 2
            self.vx = random.choice([-2, 2]) # Zigzag léger
            self.couleur = GRIS_TORNADE_MOYENNE
        else:
            self.pv = 3
            self.vx = random.choice([-3, 3]) # Zigzag rapide
            self.couleur = GRIS_TORNADE_GROSSE
        
        # Stockage PV Max pour la barre de vie
        self.max_pv = self.pv

        try:
            img = pygame.image.load(os.path.join(os.path.dirname(__file__), "tornado.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (scale, int(scale*1.5)))
        except:
            self.image = pygame.Surface([scale, int(scale*1.5)], pygame.SRCALPHA)
            pts = [(0, 0), (scale, 0), (scale//2, int(scale*1.5))]
            pygame.draw.polygon(self.image, self.couleur, pts)
        
        # On applique la taille au rect final
        self.rect.size = self.image.get_size()

    def update(self):
        # Mouvement
        self.rect.y += self.vy
        self.rect.x += self.vx

        # --- REBOND SUR LES CÔTÉS UNIQUEMENT ---
        # Si on n'est pas au niveau 1 (où vx est 0), on gère le rebond latéral
        if self.niveau_jeu > 1:
            if self.rect.left <= 0:
                self.rect.left = 0
                self.vx *= -1 # Inverse la direction X
            elif self.rect.right >= LARGEUR_JEU:
                self.rect.right = LARGEUR_JEU
                self.vx *= -1

class Balle(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        try:
            img = pygame.image.load(os.path.join(os.path.dirname(__file__), "bullet.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (15, 30))
        except:
            self.image = pygame.Surface([6, 20], pygame.SRCALPHA)
            pygame.draw.rect(self.image, JAUNE, [0,0,6,20], border_radius=3)
        
        if angle: 
            self.image = pygame.transform.rotate(self.image, -angle)
            
        self.rect = self.image.get_rect(center=(x,y))
        rad = math.radians(angle)
        self.vx = 15 * math.sin(rad)
        self.vy = -15 * math.cos(rad)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.bottom < 0: self.kill()

class Coeur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            img = pygame.image.load(os.path.join(os.path.dirname(__file__), "coeur.png")).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (30, 30))
        except:
            self.image = pygame.Surface([30, 30], pygame.SRCALPHA)
            pygame.draw.circle(self.image, ROUGE, (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, LARGEUR_JEU - 50)
        self.rect.y = -50

    def update(self):
        self.rect.y += 4
        if self.rect.top > HAUTEUR_JEU: self.kill()

# --- MOTEUR JEU ---

class Jeu:
    def __init__(self):
        self.etat = "MENU"
        self.musique = GestionnaireMusique()
        self.vfx = GestionnaireVFX()
        
        self.img_coeur = pygame.Surface([30,30], pygame.SRCALPHA)
        pygame.draw.circle(self.img_coeur, ROUGE, (15,15), 14)
        
        self.creer_menus()
        self.creer_fond()
        self.reset_partie()

    def creer_fond(self):
        path = glob.glob(os.path.join(os.path.dirname(__file__), "*.png"))
        fond_img = None
        for p in path:
            if "fond" in p or "background" in p: 
                try: fond_img = pygame.image.load(p).convert(); break
                except: pass
        if fond_img: self.image_fond = pygame.transform.scale(fond_img, (LARGEUR_JEU, HAUTEUR_JEU))
        else:
            self.image_fond = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU))
            for i in range(HAUTEUR_JEU):
                c = int(i/HAUTEUR_JEU * 50)
                pygame.draw.line(self.image_fond, (c,c,c+20), (0,i), (LARGEUR_JEU,i))
        self.fond_y = 0

    def update_fond(self):
        self.fond_y += 2
        if self.fond_y >= HAUTEUR_JEU: self.fond_y = 0

    def reset_partie(self):
        self.joueur = Soldat()
        self.all_sprites = pygame.sprite.Group(self.joueur)
        self.mobs = pygame.sprite.Group()
        self.balles = pygame.sprite.Group()
        self.bonus = pygame.sprite.Group()
        
        self.argent = 0 # Commencer à 0$
        self.score = 0
        self.niveau = 1
        self.niveau_precedent = 0
        self.vies = 3
        self.coeurs_generes = 0
        self.dernier_spawn = 0

    def creer_menus(self):
        cx, cy = LARGEUR_JEU // 2, HAUTEUR_JEU // 2
        
        # Menu Principal
        self.menu_principal = [
            Bouton(cx, cy-60, 300, 60, "JOUER", lambda: "LANCER"),
            Bouton(cx, cy+20, 300, 60, "OPTIONS", lambda: "OPTIONS"),
            Bouton(cx, cy+100, 300, 60, "QUITTER", lambda: "QUITTER")
        ]
        
        # Menu Options
        self.menu_options = [
            Bouton(cx, cy-60, 400, 60, "MUSIQUE: ON", lambda: "TOGGLE_M"),
            Bouton(cx, cy+20, 400, 60, "EFFETS: ON", lambda: "TOGGLE_E"),
            Bouton(cx, cy+100, 300, 60, "RETOUR", lambda: "RETOUR")
        ]
        
        # Boutons Pause / Boutique
        self.boutons_pause = [
            Bouton(cx - 300, HAUTEUR_JEU - 80, 200, 50, "OPTIONS", lambda: "OPTIONS"),
            Bouton(cx, HAUTEUR_JEU - 80, 200, 50, "MENU PRINCIPAL", lambda: "MENU"),
            Bouton(cx + 300, HAUTEUR_JEU - 80, 200, 50, "QUITTER JEU", lambda: "QUITTER")
        ]

    def inputs(self):
        mx, my = pygame.mouse.get_pos()
        clic = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN: clic = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.etat = "PAUSE" if self.etat == "JEU" else "JEU"
                    pygame.mouse.set_visible(self.etat != "JEU")
                
                if event.key == pygame.K_r and self.etat == "GAMEOVER":
                    self.reset_partie(); self.etat = "JEU"
                    self.musique.jouer_musique(1)
                    pygame.mouse.set_visible(False)
                
                if self.etat == "JEU":
                    if event.key == pygame.K_SPACE and not self.joueur.invincible: pass
                    if event.key == pygame.K_b and self.joueur.nukes > 0:
                        self.joueur.nukes -= 1
                        self.vfx.declencher_nuke()
                        self.musique.effet("nuke")
                        for m in self.mobs:
                            self.vfx.ajouter(m.rect.centerx, m.rect.centery, GRIS_FONCE, 20)
                            m.kill()
                            self.argent += 10
                            
        # Gestion Clics Menus
        active_menu = []
        if self.etat == "MENU": active_menu = self.menu_principal
        elif self.etat == "OPTIONS": active_menu = self.menu_options
        elif self.etat == "PAUSE": active_menu = self.boutons_pause

        for btn in active_menu:
            res = btn.verifier((mx, my), clic)
            if res == "LANCER": 
                self.reset_partie(); self.etat = "JEU"
                self.musique.jouer_musique(1); pygame.mouse.set_visible(False)
            elif res == "QUITTER": pygame.quit(); sys.exit()
            elif res == "OPTIONS": self.etat = "OPTIONS"
            elif res == "RETOUR": 
                self.etat = "MENU"
            elif res == "MENU": 
                self.etat = "MENU"; self.musique.arreter()
                pygame.mouse.set_visible(True)
            elif res == "TOGGLE_M": 
                etat = self.musique.toggle_m()
                btn.texte = f"MUSIQUE: {'ON' if etat else 'OFF'}"
            elif res == "TOGGLE_E":
                etat = self.musique.toggle_e()
                btn.texte = f"EFFETS: {'ON' if etat else 'OFF'}"

        if self.etat == "PAUSE" and clic:
            self.clic_boutique(mx, my)

        return True

    def clic_boutique(self, mx, my):
        cx = LARGEUR_JEU // 2
        y_start = 180
        
        prix_tir = 9999; txt_tir = "Tir MAX"
        if self.joueur.niveau_tir == 1: txt_tir = "Tir Double (200$)"; prix_tir = 200
        elif self.joueur.niveau_tir == 2: txt_tir = "Tir Quadruple (400$)"; prix_tir = 400
        
        prix_cad = self.joueur.niveau_cadence * 100
        txt_cad = f"Cadence Niv {self.joueur.niveau_cadence+1} ({prix_cad}$)"
        if self.joueur.niveau_cadence >= 6: txt_cad = "Cadence MAX"; prix_cad = 9999

        zones = [
            ("tir", prix_tir, y_start),
            ("cadence", prix_cad, y_start + 80),
            ("inv", 30, y_start + 160),
            ("nuke", 30, y_start + 240)
        ]

        for action, prix, y in zones:
            rect = pygame.Rect(cx-300, y, 600, 60)
            if rect.collidepoint(mx, my) and self.argent >= prix:
                buy = False
                if action == "tir":
                    if self.joueur.niveau_tir == 1: self.joueur.niveau_tir = 2; buy = True
                    elif self.joueur.niveau_tir == 2: self.joueur.niveau_tir = 3; buy = True
                elif action == "cadence":
                    if self.joueur.niveau_cadence < 6: self.joueur.niveau_cadence += 1; buy = True
                elif action == "inv":
                    self.joueur.invincible = True; self.joueur.fin_invincibilite = pygame.time.get_ticks() + 30000; buy = True
                elif action == "nuke":
                    self.joueur.nukes += 1; buy = True
                
                if buy:
                    self.argent -= prix
                    self.musique.effet("levelup")

    def logic(self):
        if self.etat != "JEU": return
        
        self.update_fond()
        self.vfx.update()
        self.all_sprites.update()
        
        # Tir Automatique
        balles = self.joueur.tirer()
        if balles:
            self.musique.effet("tir")
            self.vfx.ajouter(self.joueur.rect.centerx, self.joueur.rect.top, JAUNE, 2)
            for b in balles:
                self.balles.add(b); self.all_sprites.add(b)

        self.niveau = 1 + (self.score // 500)
        if self.niveau > 3: self.niveau = 3
        
        if self.niveau != self.niveau_precedent:
            self.musique.jouer_musique(self.niveau)
            self.niveau_precedent = self.niveau
            self.coeurs_generes = 0

        # --- SPAWN MAX 2 ---
        now = pygame.time.get_ticks()
        nb_mobs = len(self.mobs)
        if nb_mobs < 2:
            if now - self.dernier_spawn > 1000: # 1 seconde d'attente
                t = Tornade(self.niveau)
                self.mobs.add(t); self.all_sprites.add(t)
                self.dernier_spawn = now

        # Apparition Coeurs
        if self.coeurs_generes < 2 and random.randint(1, 800) == 1:
            c = Coeur()
            self.bonus.add(c); self.all_sprites.add(c)
            self.coeurs_generes += 1

        hits = pygame.sprite.groupcollide(self.mobs, self.balles, False, True)
        for mob, balles in hits.items():
            mob.pv -= 1
            self.musique.effet("degats")
            self.vfx.ajouter(mob.rect.centerx, mob.rect.centery, JAUNE, 3)
            if mob.pv <= 0:
                mob.kill()
                self.score += 20 * self.niveau
                self.argent += 10 * self.niveau
                self.musique.effet("explosion")
                self.vfx.ajouter(mob.rect.centerx, mob.rect.centery, GRIS_FONCE, 10)

        hit_player = pygame.sprite.spritecollide(self.joueur, self.mobs, False) 
        for m in hit_player:
            if not self.joueur.invincible:
                if random.randint(1,10) == 1: 
                    self.vies -= 1
                    self.vfx.ajouter(self.joueur.rect.centerx, self.joueur.rect.centery, ROUGE_SANG, 15)
                    self.musique.effet("degats")

        for c in pygame.sprite.spritecollide(self.joueur, self.bonus, True):
            if self.vies < 5: self.vies += 1
            self.musique.effet("soin")
            
        for m in self.mobs:
            if m.rect.top > HAUTEUR_JEU:
                m.kill()
                # On perd une vie si elle sort en bas
                if not self.joueur.invincible:
                    self.vies -= 1
                    self.musique.effet("degats")
                    self.vfx.ajouter(m.rect.centerx, HAUTEUR_JEU-10, ROUGE, 5)

        if self.vies <= 0:
            self.etat = "GAMEOVER"
            self.musique.effet("gameover")
            self.musique.arreter()
            pygame.mouse.set_visible(True)

    def draw(self):
        ecran.fill(NOIR)
        
        if self.etat == "MENU":
            titre = grosse_font.render("INDEPENDANCE DAY", True, OR)
            ecran.blit(titre, (LARGEUR_JEU//2 - titre.get_width()//2, 150))
            for btn in self.menu_principal: btn.dessiner(ecran)

        elif self.etat == "OPTIONS":
            titre = grosse_font.render("OPTIONS", True, BLANC)
            ecran.blit(titre, (LARGEUR_JEU//2 - titre.get_width()//2, 150))
            for btn in self.menu_options: btn.dessiner(ecran)

        elif self.etat == "JEU" or self.etat == "PAUSE" or self.etat == "GAMEOVER":
            ecran.blit(self.image_fond, (0, self.fond_y))
            ecran.blit(self.image_fond, (0, self.fond_y - HAUTEUR_JEU))
            
            self.all_sprites.draw(ecran)
            
            # --- DESSIN DES BARRES DE VIE ---
            for m in self.mobs:
                if m.max_pv > 1:
                    w = m.rect.width
                    h = 5
                    ratio = m.pv / m.max_pv
                    pygame.draw.rect(ecran, ROUGE, (m.rect.x, m.rect.y - 10, w, h))
                    pygame.draw.rect(ecran, VERT, (m.rect.x, m.rect.y - 10, w*ratio, h))

            self.vfx.draw(ecran)
            
            if self.joueur.invincible:
                pygame.draw.circle(ecran, BLEU_BOUCLIER, self.joueur.rect.center, 40, 3)

            if self.vies == 1: self.vfx.draw_low_hp(ecran)

            for i in range(self.vies):
                ecran.blit(self.img_coeur, (LARGEUR_JEU - 40 - (i*35), 20))

            t1 = font.render(f"Argent: {self.argent}$", True, OR)
            t2 = font.render(f"Niveau {self.niveau} | Score {self.score}", True, BLANC)
            t3 = font.render(f"Nuke: {self.joueur.nukes} [B]", True, ROUGE)
            ecran.blit(t1, (20, 20))
            ecran.blit(t2, (LARGEUR_JEU//2 - t2.get_width()//2, 20))
            ecran.blit(t3, (20, 60))

            if self.etat == "PAUSE":
                s = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU)); s.set_alpha(220); s.fill(NOIR)
                ecran.blit(s, (0,0))
                
                titre = grosse_font.render("BOUTIQUE", True, OR)
                ecran.blit(titre, (LARGEUR_JEU//2 - titre.get_width()//2, 50))
                
                cx = LARGEUR_JEU // 2
                y = 180
                mx, my = pygame.mouse.get_pos()
                
                prix_tir = 9999; txt_tir = "Tir MAX"
                if self.joueur.niveau_tir == 1: txt_tir = "Tir Double (200$)"; prix_tir = 200
                elif self.joueur.niveau_tir == 2: txt_tir = "Tir Quadruple (400$)"; prix_tir = 400
                
                prix_cad = self.joueur.niveau_cadence * 100
                txt_cad = f"Cadence Niv {self.joueur.niveau_cadence+1} ({prix_cad}$)"
                if self.joueur.niveau_cadence >= 6: txt_cad = "Cadence MAX"; prix_cad = 9999

                items_display = [
                    (prix_tir, txt_tir, self.joueur.niveau_tir < 3),
                    (prix_cad, txt_cad, self.joueur.niveau_cadence < 6),
                    (30, "Invincibilité 30s (30$)", True),
                    (30, "Bombe Nuke (30$)", True)
                ]

                for prix, txt, dispo in items_display:
                    rect = pygame.Rect(cx-300, y, 600, 60)
                    col = BLANC if (dispo and self.argent >= prix) else GRIS_FONCE
                    if not dispo: col = GRIS_FONCE
                    
                    if rect.collidepoint(mx, my) and dispo and self.argent >= prix:
                        pygame.draw.rect(ecran, (50,50,70), rect, border_radius=10)
                    
                    pygame.draw.rect(ecran, col, rect, 2, border_radius=10)
                    t = font.render(txt, True, col)
                    ecran.blit(t, (rect.x + 20, rect.centery - t.get_height()//2))
                    y += 80

                for btn in self.boutons_pause: btn.dessiner(ecran)

            if self.etat == "GAMEOVER":
                t = grosse_font.render("GAME OVER", True, ROUGE)
                t2 = font.render("Appuyez sur R pour rejouer", True, BLANC)
                ecran.blit(t, (LARGEUR_JEU//2 - t.get_width()//2, 300))
                ecran.blit(t2, (LARGEUR_JEU//2 - t2.get_width()//2, 400))

        pygame.display.flip()

    def run(self):
        while True:
            if not self.inputs(): break
            self.logic()
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    jeu = Jeu()
    jeu.run()