import math

import pygame  # Le module Pygame

from constantes import *

screen = pygame.display.set_mode((XMAX, YMAX), pygame.SCALED)

# Dictionnaire contenant les positions et tailles des sprites dans les sprite sheets
# Format: 'nom_sprite': (nom_feuille, x, y, largeur, hauteur)
sprites = {
    'balle': ('sprites', 144, 8, 8, 8),
    'raquette': ('sprites', 64, 7, 32, 9),
    'brique_grise': ('bricks', 0, 7, 32, 9),
}

# Dictionnaire pour stocker les différentes sprite sheets
sprite_sheets = {
    'sprites': pygame.image.load('assets/paddles_and_balls.png').convert_alpha(),
    'hearts': pygame.image.load('assets/hearts.png').convert_alpha(),
    'bricks': pygame.image.load('assets/bricks.png').convert_alpha(),
}

# Fonction pour extraire un sprite de la sprite sheet
def get_sprite(name):
    """
    Extrait un sprite spécifique d'une sprite sheet.
    
    Args:
        name (str): Nom du sprite à extraire
        
    Returns:
        Surface: L'image du sprite extraite
    """
    sheet_name, x, y, width, height = sprites[name]
    sprite_sheet = sprite_sheets[sheet_name]
    rect = pygame.Rect(x, y, width, height)
    image = pygame.Surface(rect.size, pygame.SRCALPHA)
    image.blit(sprite_sheet, (0, 0), rect)
    return image

# Précharger les images des sprites
sprite_images = {name: get_sprite(name) for name in sprites}

class Balle:
    """Classe représentant la balle du jeu."""
    
    def __init__(self):
        """Initialise une nouvelle balle."""
        self.x, self.y = 400, 400
        self.vx, self.vy = None, None
        self.vitesse = 2
        self.sur_raquette = True
        self.sprite = sprite_images['balle']
        
        # Définir la taille exacte en fonction du sprite
        self.width, self.height = self.sprite.get_size()
        self.rayon = self.width / 2  # Pour les calculs de collision circulaire
        
        # Initialiser la vitesse avec un angle par défaut
        self.vitesse_par_angle(60)

    def vitesse_par_angle(self, angle):
        """
        Définit la vitesse de la balle en fonction d'un angle.
        
        Args:
            angle (float): Angle en degrés (0° = droite, 90° = haut)
        """
        self.vx = self.vitesse * math.cos(math.radians(angle))
        self.vy = -self.vitesse * math.sin(math.radians(angle))

    def afficher(self):
        """Affiche la balle à sa position actuelle."""
        screen.blit(self.sprite, (self.x - self.width/2, self.y - self.height/2))

    def rebond_raquette(self, raquette):
        """
        Calcule le rebond de la balle sur la raquette.
        L'angle dépend de la position de la balle par rapport au centre de la raquette.
        
        Args:
            raquette (Raquette): La raquette avec laquelle la balle entre en collision
        """
        # Écart horizontal entre le centre de la raquette et la balle
        diff = raquette.x - self.x
        
        # Écart tangent (basé sur les sprites)
        longueur_totale = raquette.width / 2 + self.width / 2
        
        # Formule où l'angle est proportionnel à l'écart au centre de la raquette
        angle = 90 + 80 * diff / longueur_totale
        self.vitesse_par_angle(angle)

    def deplacer(self, raquette):
        """
        Déplace la balle et gère les rebonds sur les murs et la raquette.
        
        Args:
            raquette (Raquette): La raquette du joueur
        """
        if self.sur_raquette:
            # On met la balle sur la raquette
            self.y = raquette.y - self.height/2 - raquette.height/2
            self.x = raquette.x
        else:
            # Déplacement de la balle
            self.x += self.vx
            self.y += self.vy
            
            # Gestion des collisions
            # Avec la raquette
            if raquette.collision_balle(self) and self.vy > 0:  # Collision et balle descendante
                self.rebond_raquette(raquette)
                
            # Avec les bords de l'écran
            if self.x + self.width/2 > XMAX:
                self.vx = -self.vx
                self.x = XMAX - self.width/2  # Éviter que la balle sorte de l'écran
            
            if self.x - self.width/2 < XMIN:
                self.vx = -self.vx
                self.x = XMIN + self.width/2  # Éviter que la balle sorte de l'écran
            
            if self.y + self.height/2 > YMAX:
                self.sur_raquette = True
            
            if self.y - self.height/2 < YMIN:
                self.vy = -self.vy
                self.y = YMIN + self.height/2  # Éviter que la balle sorte de l'écran


class Raquette:
    """Classe représentant la raquette contrôlée par le joueur."""
    
    def __init__(self):
        """Initialise une nouvelle raquette."""
        self.sprite = sprite_images['raquette']
        self.width, self.height = self.sprite.get_size()
        # Positionner correctement avec la hauteur du sprite
        self.x = XMAX / 2
        self.y = YMAX - self.height/2

    def afficher(self):
        """Affiche la raquette à sa position actuelle."""
        screen.blit(self.sprite, (self.x - self.width/2, self.y - self.height/2))

    def deplacer(self, x):
        """
        Déplace la raquette horizontalement en limitant sa position à l'écran.
        
        Args:
            x (int): Nouvelle position x souhaitée (généralement la position de la souris)
        """
        # On limite la position x pour que la raquette ne dépasse pas de l'écran
        if x + self.width / 2 > XMAX:
            self.x = XMAX - self.width / 2
        elif x - self.width / 2 < XMIN:
            self.x = XMIN + self.width / 2
        else:
            self.x = x

    def collision_balle(self, balle):
        """
        Vérifie s'il y a collision entre la raquette et la balle.
        
        Args:
            balle (Balle): La balle à tester
            
        Returns:
            bool: True s'il y a collision, False sinon
        """
        horizontal = abs(self.x - balle.x) < balle.width/2 + self.width/2
        vertical = abs(self.y - balle.y) < balle.height/2 + self.height/2
        return horizontal and vertical


class Brique:
    """Classe représentant une brique destructible."""
    
    def __init__(self, x, y, couleur='grise'):
        """
        Initialise une nouvelle brique.
        
        Args:
            x (int): Position x du centre de la brique
            y (int): Position y du centre de la brique
            couleur (str, optional): Couleur de la brique. Par défaut 'grise'.
        """
        self.x = x  # abscisse du centre de la brique
        self.y = y  # ordonnée du centre de la brique
        self.vie = 1
        self.couleur = couleur
        self.sprite = sprite_images[f'brique_{couleur}']
        self.width, self.height = self.sprite.get_size()

    def en_vie(self):
        """
        Vérifie si la brique est encore en vie.
        
        Returns:
            bool: True si la brique a encore de la vie, False sinon
        """
        return self.vie > 0

    def afficher(self):
        """Affiche la brique si elle est encore en vie."""
        if self.en_vie():
            screen.blit(self.sprite, (self.x - self.width/2, self.y - self.height/2))

    def collision_balle(self, balle):
        """
        Vérifie et gère la collision avec une balle.
        Si collision, fait rebondir la balle et réduit la vie de la brique.
        
        Args:
            balle (Balle): La balle à tester
            
        Returns:
            bool: True s'il y a eu collision, False sinon
        """
        # Pas de collision si la brique est déjà détruite
        if not self.en_vie():
            return False
        
        # Vérifier la collision avec la balle en utilisant les dimensions exactes des sprites
        horizontal = abs(self.x - balle.x) < (self.width / 2 + balle.width / 2)
        vertical = abs(self.y - balle.y) < (self.height / 2 + balle.height / 2)
        
        if horizontal and vertical:
            # Déterminer de quel côté vient la balle pour le rebond correct
            dx = balle.x - self.x
            dy = balle.y - self.y
            
            # Calculer les distances de pénétration
            penetration_x = self.width / 2 + balle.width / 2 - abs(dx)
            penetration_y = self.height / 2 + balle.height / 2 - abs(dy)
            
            # Rebond sur l'axe de moindre pénétration
            if penetration_x < penetration_y:
                # Rebond horizontal
                balle.vx = -balle.vx
            else:
                # Rebond vertical
                balle.vy = -balle.vy
            
            # Réduire la vie de la brique
            self.vie -= 1
            return True
        
        return False
