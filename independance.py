import pygame
import random
import sys
import os
import glob

# --- Initialisation ---
pygame.init()

# --- Constantes (Format 16:9) ---
LARGEUR_JEU = 1280
HAUTEUR_JEU = 720
FPS = 60

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT_MILITAIRE = (46, 139, 87)
GRIS_FONCE = (50, 50, 50)
GRIS_TORNADE_PETITE = (180, 180, 180)
GRIS_TORNADE_GROSSE = (80, 80, 80)
JAUNE = (255, 255, 0)
ROUGE = (255, 0, 0)
ORANGE = (255, 165, 0)
OR = (255, 215, 0)
BLEU_NUIT = (20, 20, 60)

# Configuration écran
ecran = pygame.display.set_mode((LARGEUR_JEU, HAUTEUR_JEU))
pygame.display.set_caption("Independance Day : Edition Deluxe")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
petite_font = pygame.font.Font(None, 24)
grosse_font = pygame.font.Font(None, 80)

# --- GESTIONNAIRE DE MUSIQUE ---
class GestionnaireMusique:
    """Gère la musique de fond par niveau et les effets sonores"""
    
    def __init__(self):
        pygame.mixer.init()
        
        # Paramètres audio
        self.volume_musique = 0.5
        self.volume_effets = 0.7
        self.musique_active = True
        self.effets_actifs = True
        
        # Listes de fichiers
        self.musiques_niveaux = {}
        self.effets_sonores = {}
        
        # État
        self.musique_en_cours = None
        self.type_musique_actuelle = None
        
        # Charger les fichiers audio
        self.charger_musiques()
        self.charger_effets()
    
    def charger_musiques(self):
        """Charge les musiques depuis le dossier 'musiques/'"""
        dossier_script = os.path.dirname(os.path.abspath(__file__))
        dossier_musiques = os.path.join(dossier_script, "musiques")
        
        os.makedirs(dossier_musiques, exist_ok=True)
        
        # Charger musiques par niveau
        self.musiques_niveaux = {}
        noms_niveaux = {
            1: ["Terre.mp3", "Terre.ogg", "Terre.wav", "terre.mp3", "terre.ogg"],
            2: ["Ciel.mp3", "Ciel.ogg", "Ciel.wav", "ciel.mp3", "ciel.ogg"],
            3: ["Espace.mp3", "Espace.ogg", "Espace.wav", "espace.mp3", "espace.ogg"]
        }
        
        for niveau, noms_possibles in noms_niveaux.items():
            for nom in noms_possibles:
                chemin = os.path.join(dossier_musiques, nom)
                if os.path.exists(chemin):
                    self.musiques_niveaux[niveau] = chemin
                    print(f"🎵 Niveau {niveau}: {nom}")
                    break
        
        print(f"🎵 Musiques chargées: {len(self.musiques_niveaux)}/3")
    
    def charger_effets(self):
        """Charge les effets sonores depuis le dossier 'sons/'"""
        dossier_script = os.path.dirname(os.path.abspath(__file__))
        dossier_sons = os.path.join(dossier_script, "sons")
        
        os.makedirs(dossier_sons, exist_ok=True)
        
        # Noms des effets à charger
        noms_effets = {
            "tir": ["tir.wav", "tir.ogg", "shoot.wav", "shoot.ogg"],
            "explosion": ["explosion.wav", "explosion.ogg", "boom.wav"],
            "degats": ["degats.wav", "degats.ogg", "hit.wav", "hurt.wav"],
            "piece": ["piece.wav", "piece.ogg", "coin.wav", "money.wav"],
            "gameover": ["gameover.wav", "gameover.ogg", "death.wav"]
        }
        
        for nom_effet, fichiers_possibles in noms_effets.items():
            for fichier in fichiers_possibles:
                chemin = os.path.join(dossier_sons, fichier)
                if os.path.exists(chemin):
                    try:
                        self.effets_sonores[nom_effet] = pygame.mixer.Sound(chemin)
                        self.effets_sonores[nom_effet].set_volume(self.volume_effets)
                        print(f"🔊 Effet chargé: {nom_effet}")
                        break
                    except Exception as e:
                        print(f"❌ Erreur chargement {fichier}: {e}")
    
    def jouer_musique_niveau(self, numero_niveau):
        """Lance la musique spécifique d'un niveau EN BOUCLE"""
        if not self.musique_active:
            return
        
        if numero_niveau in self.musiques_niveaux:
            musique = self.musiques_niveaux[numero_niveau]
            
            if self.musique_en_cours != musique:
                try:
                    pygame.mixer.music.load(musique)
                    pygame.mixer.music.set_volume(self.volume_musique)
                    pygame.mixer.music.play(-1)  # -1 = boucle infinie
                    self.musique_en_cours = musique
                    self.type_musique_actuelle = f"niveau_{numero_niveau}"
                    print(f"🎵 Niveau {numero_niveau}: {os.path.basename(musique)} (EN BOUCLE)")
                except Exception as e:
                    print(f"❌ Erreur lecture musique niveau {numero_niveau}: {e}")
        else:
            print(f"⚠️ Pas de musique pour le niveau {numero_niveau}")
    
    def arreter_musique(self):
        """Arrête la musique"""
        pygame.mixer.music.stop()
        self.musique_en_cours = None
        self.type_musique_actuelle = None
    
    def basculer_musique(self):
        """Active/désactive la musique"""
        self.musique_active = not self.musique_active
        
        if self.musique_active:
            print("🎵 Musique: ON")
        else:
            self.arreter_musique()
            print("🔇 Musique: OFF")
        
        return self.musique_active
    
    def basculer_effets(self):
        """Active/désactive les effets sonores"""
        self.effets_actifs = not self.effets_actifs
        print(f"🔊 Effets: {'ON' if self.effets_actifs else 'OFF'}")
        return self.effets_actifs
    
    def modifier_volume_musique(self, delta):
        """Modifie le volume de la musique"""
        self.volume_musique = max(0.0, min(1.0, self.volume_musique + delta))
        pygame.mixer.music.set_volume(self.volume_musique)
        print(f"🔊 Volume musique: {int(self.volume_musique * 100)}%")
    
    def modifier_volume_effets(self, delta):
        """Modifie le volume des effets"""
        self.volume_effets = max(0.0, min(1.0, self.volume_effets + delta))
        for effet in self.effets_sonores.values():
            effet.set_volume(self.volume_effets)
        print(f"🔊 Volume effets: {int(self.volume_effets * 100)}%")
    
    def jouer_effet(self, nom_effet):
        """Joue un effet sonore"""
        if not self.effets_actifs:
            return
        
        if nom_effet in self.effets_sonores:
            try:
                self.effets_sonores[nom_effet].play()
            except Exception as e:
                print(f"❌ Erreur lecture effet {nom_effet}: {e}")

# --- CLASSE BOUTON ---
class Bouton:
    def __init__(self, cx, cy, w, h, texte, action=None):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.texte = texte
        self.action = action
        self.couleur_base = GRIS_FONCE
        self.couleur_survol = ORANGE
        self.est_survole = False

    def dessiner(self, surface):
        couleur = self.couleur_survol if self.est_survole else self.couleur_base
        pygame.draw.rect(surface, couleur, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLANC, self.rect, 2, border_radius=10)
        
        txt_surf = font.render(self.texte, True, BLANC)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def verifier_survol(self, pos_souris):
        self.est_survole = self.rect.collidepoint(pos_souris)

    def verifier_clic(self, pos_souris):
        if self.rect.collidepoint(pos_souris) and self.action:
            return self.action()
        return None

# --- CLASSES DU JEU ---

class Soldat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            img_path = os.path.join(os.path.dirname(__file__), "soldier.png")
            loaded = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.smoothscale(loaded, (40, 50))
        except Exception:
            self.image = pygame.Surface([40, 50], pygame.SRCALPHA)
            self.image.fill(VERT_MILITAIRE)
            pygame.draw.rect(self.image, (30, 90, 55), [10, 0, 20, 10])
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGEUR_JEU // 2
        self.rect.bottom = HAUTEUR_JEU - 20
        
        # Stats
        self.cadence_base = 350
        self.niveau_cadence = 1
        self.dernier_tir = 0

    def update(self):
        pos_souris_x, _ = pygame.mouse.get_pos()
        self.rect.centerx = pos_souris_x
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGEUR_JEU: self.rect.right = LARGEUR_JEU

    def verifier_tir_auto(self):
        maintenant = pygame.time.get_ticks()
        delai = max(50, self.cadence_base - (self.niveau_cadence * 30))
        
        if maintenant - self.dernier_tir > delai:
            self.dernier_tir = maintenant
            return Balle(self.rect.centerx, self.rect.top)
        return None

class Tornade(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        is_big = random.random() < 0.2 
        
        if is_big:
            largeur = random.randint(90, 140)
            self.couleur = GRIS_TORNADE_GROSSE
            self.valeur = 20
            self.vitesse_y = random.randint(8, 10) 
        else:
            largeur = random.randint(40, 70)
            self.couleur = GRIS_TORNADE_PETITE
            self.valeur = 5
            self.vitesse_y = random.randint(3, 6)

        hauteur = int(largeur * 1.5)
        try:
            img_path = os.path.join(os.path.dirname(__file__), "tornado.png")
            loaded = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.smoothscale(loaded, (largeur, hauteur))
        except Exception:
            self.image = pygame.Surface([largeur, hauteur], pygame.SRCALPHA)
            points = [(0, 0), (largeur, 0), (largeur // 2, hauteur)]
            pygame.draw.polygon(self.image, self.couleur, points)
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR_JEU - largeur)
        self.rect.y = -hauteur

    def update(self):
        self.rect.y += self.vitesse_y

class Balle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            img_path = os.path.join(os.path.dirname(__file__), "bullet.png")
            loaded = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.smoothscale(loaded, (40, 60))
        except Exception:
            self.image = pygame.Surface([40, 60], pygame.SRCALPHA)
            self.image.fill(JAUNE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vitesse_y = -15

    def update(self):
        self.rect.y += self.vitesse_y
        if self.rect.bottom < 0:
            self.kill()

# --- GESTIONNAIRE DU JEU ---

class Jeu:
    def __init__(self):
        self.etat = "MENU"
        self.plein_ecran = False
        
        # 🎵 NOUVEAU: Gestionnaire de musique
        self.musique = GestionnaireMusique()
        
        self.creer_menus()
        self.creer_fond()
        self.reset_partie()
        pygame.mouse.set_visible(True)

    def creer_fond(self):
        dossier = os.path.dirname(__file__)
        img_path = None

        # PRIORITÉ : si l'utilisateur fournit explicitement 'fond.png'
        preferred = os.path.join(dossier, "fond.png")
        if os.path.exists(preferred):
            img_path = preferred
        else:
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"):
                matches = glob.glob(os.path.join(dossier, pattern))
                if matches:
                    img_path = matches[0]
                    break

        if img_path:
            try:
                loaded = pygame.image.load(img_path).convert()
                ow, oh = loaded.get_width(), loaded.get_height()
                scale = max(LARGEUR_JEU / ow, HAUTEUR_JEU / oh)
                new_w = int(ow * scale)
                new_h = int(oh * scale)
                loaded = pygame.transform.smoothscale(loaded, (new_w, new_h))
                self.image_fond = loaded
            except Exception as e:
                print("Impossible de charger l'image de fond:", e)
                img_path = None

        if not img_path:
            self.image_fond = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU))
            for y in range(HAUTEUR_JEU):
                c = 30 + (y * 40 // HAUTEUR_JEU)
                pygame.draw.line(self.image_fond, (c, c, c+10), (0, y), (LARGEUR_JEU, y))
            for i in range(0, HAUTEUR_JEU, 100):
                pygame.draw.line(self.image_fond, (80, 80, 90), (0, i), (LARGEUR_JEU, i), 2)

        self.fond_x = (LARGEUR_JEU - self.image_fond.get_width()) // 2
        self.hauteur_fond = self.image_fond.get_height()
        self.fond_y1 = 0
        self.fond_y2 = -self.hauteur_fond
        self.vitesse_fond = 1.5

    def update_fond(self):
        self.fond_y1 += self.vitesse_fond
        self.fond_y2 += self.vitesse_fond

        if self.fond_y1 >= self.hauteur_fond:
            self.fond_y1 = self.fond_y2 - self.hauteur_fond

        if self.fond_y2 >= self.hauteur_fond:
            self.fond_y2 = self.fond_y1 - self.hauteur_fond

    def reset_partie(self):
        self.joueur = Soldat()
        self.all_sprites = pygame.sprite.Group(self.joueur)
        self.mobs = pygame.sprite.Group()
        self.balles = pygame.sprite.Group()
        
        self.argent = 0
        self.score_total = 0 
        self.niveau = 1
        self.niveau_precedent = 0  # 🎵 Pour détecter changement de niveau
        self.vies = 3
        self.timer_degats = 0

    def creer_menus(self):
        cx, cy = LARGEUR_JEU // 2, HAUTEUR_JEU // 2
        
        self.btn_jouer = Bouton(cx, cy - 60, 300, 60, "JOUER", lambda: "LANCER_JEU")
        self.btn_options = Bouton(cx, cy + 20, 300, 60, "OPTIONS", lambda: "ALLER_OPTIONS")
        self.btn_quitter = Bouton(cx, cy + 100, 300, 60, "QUITTER", lambda: "QUITTER")
        self.liste_boutons_menu = [self.btn_jouer, self.btn_options, self.btn_quitter]

        self.btn_reprendre = Bouton(cx, cy - 180, 300, 60, "REPRENDRE", lambda: "REPRENDRE")
        self.btn_up_tir = Bouton(cx, cy - 80, 400, 60, "Tir Rapide (+1) : 100$", lambda: "UP_TIR")
        self.btn_menu_principal = Bouton(cx, cy + 50, 300, 60, "MENU PRINCIPAL", lambda: "RETOUR_MENU")
        self.liste_boutons_pause = [self.btn_reprendre, self.btn_up_tir, self.btn_menu_principal]

        # 🎵 NOUVEAU: Boutons audio
        self.btn_toggle_musique = Bouton(cx, cy - 120, 400, 60, "Musique : ON", lambda: "TOGGLE_MUSIQUE")
        self.btn_toggle_effets = Bouton(cx, cy - 40, 400, 60, "Effets : ON", lambda: "TOGGLE_EFFETS")
        self.btn_fullscreen = Bouton(cx, cy + 40, 400, 60, "Plein Écran : NON", lambda: "TOGGLE_FULLSCREEN")
        self.btn_retour_opt = Bouton(cx, cy + 140, 300, 60, "RETOUR", lambda: "RETOUR_DEPUIS_OPT")
        self.liste_boutons_options = [self.btn_toggle_musique, self.btn_toggle_effets, 
                                      self.btn_fullscreen, self.btn_retour_opt]

    def basculer_plein_ecran(self):
        self.plein_ecran = not self.plein_ecran
        if self.plein_ecran:
            try:
                pygame.display.set_mode((LARGEUR_JEU, HAUTEUR_JEU), pygame.FULLSCREEN)
                self.btn_fullscreen.texte = "Plein Écran : OUI"
            except:
                pygame.display.set_mode((LARGEUR_JEU, HAUTEUR_JEU))
                self.plein_ecran = False
                self.btn_fullscreen.texte = "Plein Écran : NON"
        else:
            pygame.display.set_mode((LARGEUR_JEU, HAUTEUR_JEU))
            self.btn_fullscreen.texte = "Plein Écran : NON"

    def gerer_entrees(self):
        pos_souris = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            
            if event.type == pygame.KEYDOWN:
                # Pause
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if self.etat == "JEU":
                        self.etat = "PAUSE"
                        pygame.mouse.set_visible(True)
                    elif self.etat == "PAUSE":
                        self.etat = "JEU"
                        pygame.mouse.set_visible(False)
                
                # Rejouer
                if self.etat == "GAMEOVER" and event.key == pygame.K_r:
                    self.reset_partie()
                    self.etat = "JEU"
                    pygame.mouse.set_visible(False)
                    # 🎵 Démarrer musique niveau 1
                    self.musique.jouer_musique_niveau(1)
                
                # 🎵 NOUVEAU: Contrôles audio
                if event.key == pygame.K_m:
                    actif = self.musique.basculer_musique()
                    self.btn_toggle_musique.texte = f"Musique : {'ON' if actif else 'OFF'}"
                
                if event.key == pygame.K_n:
                    actif = self.musique.basculer_effets()
                    self.btn_toggle_effets.texte = f"Effets : {'ON' if actif else 'OFF'}"
                
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    self.musique.modifier_volume_musique(0.1)
                
                if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.musique.modifier_volume_musique(-0.1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    action = None
                    liste = []
                    if self.etat == "MENU": liste = self.liste_boutons_menu
                    elif self.etat == "PAUSE": liste = self.liste_boutons_pause
                    elif self.etat == "OPTIONS": liste = self.liste_boutons_options
                    
                    for btn in liste:
                        res = btn.verifier_clic(pos_souris)
                        if res: action = res
                    
                    self.executer_action_menu(action)

        liste = []
        if self.etat == "MENU": liste = self.liste_boutons_menu
        elif self.etat == "PAUSE": liste = self.liste_boutons_pause
        elif self.etat == "OPTIONS": liste = self.liste_boutons_options
        for btn in liste: btn.verifier_survol(pos_souris)

        return True

    def executer_action_menu(self, action):
        if not action: return

        if action == "LANCER_JEU":
            self.reset_partie()
            self.etat = "JEU"
            pygame.mouse.set_visible(False)
            # 🎵 Démarrer musique du niveau 1
            self.musique.jouer_musique_niveau(1)
            
        elif action == "QUITTER":
            pygame.quit()
            sys.exit()
            
        elif action == "ALLER_OPTIONS":
            self.etat = "OPTIONS"
            
        elif action == "RETOUR_DEPUIS_OPT":
            self.etat = "MENU"
            
        elif action == "REPRENDRE":
            self.etat = "JEU"
            pygame.mouse.set_visible(False)
            
        elif action == "RETOUR_MENU":
            self.etat = "MENU"
            pygame.mouse.set_visible(True)
            # 🎵 Arrêter la musique en revenant au menu
            self.musique.arreter_musique()
            
        elif action == "TOGGLE_FULLSCREEN":
            self.basculer_plein_ecran()
            
        # 🎵 NOUVEAU: Actions audio
        elif action == "TOGGLE_MUSIQUE":
            actif = self.musique.basculer_musique()
            self.btn_toggle_musique.texte = f"Musique : {'ON' if actif else 'OFF'}"
            
        elif action == "TOGGLE_EFFETS":
            actif = self.musique.basculer_effets()
            self.btn_toggle_effets.texte = f"Effets : {'ON' if actif else 'OFF'}"
            
        elif action == "UP_TIR":
            prix = 100
            if self.argent >= prix and self.joueur.niveau_cadence < 10:
                self.argent -= prix
                self.joueur.niveau_cadence += 1
                # 🎵 Son d'achat
                self.musique.jouer_effet("piece")

    def update_jeu(self):
        self.update_fond()
        self.all_sprites.update()
        
        # Tir auto
        balle = self.joueur.verifier_tir_auto()
        if balle:
            self.all_sprites.add(balle)
            self.balles.add(balle)
            # 🎵 Son de tir
            self.musique.jouer_effet("tir")

        # Niveaux
        self.niveau = 1 + (self.score_total // 300)
        if self.niveau > 3: self.niveau = 3  # Maximum 3 niveaux
        
        # 🎵 NOUVEAU: Changer la musique quand le niveau change
        if self.niveau != self.niveau_precedent:
            self.musique.jouer_musique_niveau(self.niveau)
            self.niveau_precedent = self.niveau

        # Apparition
        seuil_apparition = max(20, 80 - (self.niveau * 12))
        if random.randint(1, seuil_apparition) == 1:
            t = Tornade()
            self.all_sprites.add(t)
            self.mobs.add(t)

        # Collisions
        hits = pygame.sprite.groupcollide(self.mobs, self.balles, True, True)
        for t, b_list in hits.items():
            self.argent += t.valeur
            self.score_total += t.valeur
            # 🎵 Son d'explosion
            self.musique.jouer_effet("explosion")

        # Dégâts
        toucher = False
        hits_joueur = pygame.sprite.spritecollide(self.joueur, self.mobs, True)
        if hits_joueur:
            toucher = True
            self.vies -= 1
            # 🎵 Son de dégâts
            self.musique.jouer_effet("degats")
        
        for m in self.mobs:
            if m.rect.top > HAUTEUR_JEU:
                m.kill()
                toucher = True
                self.vies -= 1
                # 🎵 Son de dégâts
                self.musique.jouer_effet("degats")
        
        if toucher: self.timer_degats = 15
        
        if self.vies <= 0:
            self.etat = "GAMEOVER"
            pygame.mouse.set_visible(True)
            # 🎵 Son de game over
            self.musique.jouer_effet("gameover")
            # 🎵 Arrêter la musique
            self.musique.arreter_musique()

    def dessiner(self):
        ecran.fill(BLEU_NUIT)

        if self.etat == "MENU":
            titre = grosse_font.render("INDEPENDANCE DAY", True, JAUNE)
            rect_titre = titre.get_rect(center=(LARGEUR_JEU//2, 150))
            ecran.blit(titre, rect_titre)
            for btn in self.liste_boutons_menu: btn.dessiner(ecran)
            
            # 🎵 NOUVEAU: Afficher les contrôles audio
            aide = petite_font.render("M: Musique | N: Effets | +/-: Volume", True, BLANC)
            ecran.blit(aide, (LARGEUR_JEU//2 - aide.get_width()//2, HAUTEUR_JEU - 50))

        elif self.etat == "OPTIONS":
            titre = grosse_font.render("OPTIONS", True, BLANC)
            rect_titre = titre.get_rect(center=(LARGEUR_JEU//2, 150))
            ecran.blit(titre, rect_titre)
            
            # 🎵 NOUVEAU: Info sur les musiques chargées
            nb_niveaux = len(self.musique.musiques_niveaux)
            nb_effets = len(self.musique.effets_sonores)
            
            info1 = petite_font.render(f"Musiques de niveaux: {nb_niveaux}/3", True, OR)
            info2 = petite_font.render(f"Effets sonores: {nb_effets}", True, OR)
            
            ecran.blit(info1, (LARGEUR_JEU//2 - info1.get_width()//2, 240))
            ecran.blit(info2, (LARGEUR_JEU//2 - info2.get_width()//2, 270))
            
            for btn in self.liste_boutons_options: btn.dessiner(ecran)

        elif self.etat == "JEU" or self.etat == "PAUSE" or self.etat == "GAMEOVER":
            ecran.blit(self.image_fond, (self.fond_x, self.fond_y1))
            ecran.blit(self.image_fond, (self.fond_x, self.fond_y2))
            
            self.all_sprites.draw(ecran)
            
            # HUD
            txt_argent = font.render(f"Caisse: {self.argent} $", True, OR)
            ecran.blit(txt_argent, (20, 20))
            
            txt_niveau = font.render(f"NIVEAU {self.niveau}", True, JAUNE)
            rect_niveau = txt_niveau.get_rect(center=(LARGEUR_JEU//2, 30))
            ecran.blit(txt_niveau, rect_niveau)
            
            couleur_vie = ROUGE if self.vies == 1 else BLANC
            txt_vies = font.render(f"Vies: {self.vies}", True, couleur_vie)
            ecran.blit(txt_vies, (LARGEUR_JEU - 150, 20))

            if self.timer_degats > 0:
                pygame.draw.rect(ecran, ROUGE, (0,0,LARGEUR_JEU,HAUTEUR_JEU), 20)
                self.timer_degats -= 1

            if self.etat == "PAUSE":
                s = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU))
                s.set_alpha(200)
                s.fill(NOIR)
                ecran.blit(s, (0,0))
                
                titre = grosse_font.render("BOUTIQUE & PAUSE", True, BLANC)
                ecran.blit(titre, titre.get_rect(center=(LARGEUR_JEU//2, 100)))
                
                self.btn_up_tir.texte = f"Tir Rapide (Niv {self.joueur.niveau_cadence}) : 100$"
                self.btn_up_tir.couleur_base = VERT_MILITAIRE if self.argent >= 100 else ROUGE
                
                for btn in self.liste_boutons_pause: btn.dessiner(ecran)

            elif self.etat == "GAMEOVER":
                s = pygame.Surface((LARGEUR_JEU, HAUTEUR_JEU))
                s.set_alpha(230)
                s.fill(NOIR)
                ecran.blit(s, (0,0))
                
                t1 = grosse_font.render("GAME OVER", True, ROUGE)
                t2 = font.render(f"Argent récolté: {self.argent} $", True, OR)
                t3 = font.render(f"Niveau atteint: {self.niveau}", True, JAUNE)
                t4 = font.render("Appuie sur 'R' pour rejouer", True, BLANC)
                
                ecran.blit(t1, t1.get_rect(center=(LARGEUR_JEU//2, HAUTEUR_JEU//2 - 60)))
                ecran.blit(t2, t2.get_rect(center=(LARGEUR_JEU//2, HAUTEUR_JEU//2 + 10)))
                ecran.blit(t3, t3.get_rect(center=(LARGEUR_JEU//2, HAUTEUR_JEU//2 + 50)))
                ecran.blit(t4, t4.get_rect(center=(LARGEUR_JEU//2, HAUTEUR_JEU//2 + 110)))

        pygame.display.flip()

    def run(self):
        while True:
            actif = self.gerer_entrees()
            if not actif: break
            
            if self.etat == "JEU":
                self.update_jeu()
            
            self.dessiner()
            clock.tick(FPS)

if __name__ == "__main__":
    jeu = Jeu()
    jeu.run()
    pygame.quit()
    sys.exit()