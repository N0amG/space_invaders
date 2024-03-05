import pygame  # necessaire pour charger les images et les sons
from random import randint
import webbrowser as web
import time

# Variable utilisée pour jouer un son aléatoire lorsque le joueur tire
channel_piou = 1

class File: # classe de gestion du fichier options.txt

    def __init__(self):
        # Ouverture du fichier en mode lecture et écriture
        self.file_name = f"options.txt"
        self.file = open(f"options.txt", "r+")

    def start_from_line(self,starting_line, write = None):
        # Lecture de toutes les lignes du fichier
        lines = self.file.readlines()
        lineCounter = 1
        for line in lines:
            # Si on est arrivé à la ligne souhaitée
            if lineCounter == starting_line:
                # Si on veut écrire une valeur dans le fichier
                if write:
                    # Modification de la valeur dans la liste de lignes
                    lines[3] = write
                    # Ouverture du fichier en mode écriture
                    file = open(self.file_name,"w")
                    # Conversion de la liste de lignes en chaîne de caractères
                    lines = "".join(lines)
                    # Écriture de la nouvelle chaîne dans le fichier
                    file.write(lines)
                # On replace le curseur au début du fichier
                self.file.seek(0)
                return line
            lineCounter += 1
        self.file.close()
    
    # Méthode permettant de récupérer la vitesse de jeu
    def get_vitesse_global(self):
        # Récupération de la vitesse depuis le fichier
        vitesse = self.start_from_line(1).split()[-1]
        return float(vitesse)
    
    # Méthode permettant de récupérer les stats de bonus
    def get_stats_bonus(self):
        # Récupération des stats depuis le fichier
        stat = self.start_from_line(2).split()[-1]
        return float(stat)
    
    # Méthode permettant de récupérer le high score
    def get_high_score(self):
        hightscore = self.start_from_line(4).split()[-1]
        return hightscore

    def if_score_is_high_score(self,score):
        """
        Vérifie si le score passé en paramètre est supérieur au high score enregistré dans le fichier options.txt
        Si c'est le cas, le high score est mis à jour avec la valeur du score passé en paramètre.
        """
        # Récupération du high score enregistré dans le fichier
        high_score = self.get_high_score()
        # Si le score passé en paramètre est supérieur au high score précédent
        if score > int(high_score):
            # Récupération de la ligne du high score dans le fichier
            new_high_score = self.start_from_line(4).split()
            # Modification de la valeur du high score dans la liste de lignes
            new_high_score[-1] = str(score)
            # Conversion de la liste de lignes en chaîne de caractères
            new_high_score = " ".join(new_high_score)
            # Ecriture de la nouvelle chaîne de caractères dans le fichier, en remplaçant la ligne du high score
            self.start_from_line(3,new_high_score)


file = File()

vitesse_global = round(12 * file.get_vitesse_global()) # 12 = vitesse par défaut
                            #recupere la vitesse mis en option pour adapté la vitesse de jeu en conscéquent

class Joueur: # classe pour créer le vaisseau du joueur
    
    NbEnnemisTue = 0

    def __init__(self) :
        # Initialisation des attributs du vaisseau
        self.sens = "" # Sens de déplacement du vaisseau (gauche ou droite)
        self.hauteur = 530 # Hauteur de la position du vaisseau
        self.position = 350 # Position du vaisseau sur l'axe des x
        self.image =  pygame.image.load(f"images/vaisseau.png") # Image du vaisseau
        self.vie = 3 # Nombre de vies du vaisseau
        self.score = 0 # Score du vaisseau
        self.active = True # Booléen indiquant si le vaisseau est actif ou non
        self.rect = self.image.get_rect(x = self.position, y = self.hauteur) # Rectangle englobant l'image du vaisseau
        self.liste_bonus = [] # Liste des bonus collectés par le vaisseau

    def deplacer(self) :
        # Fonction pour déplacer le vaisseau
        vitesse = 0.15 * vitesse_global # Calcul de la vitesse de déplacement en fonction de la vitesse globale
        if self.sens == "droite":
            self.position += vitesse
        if self.position >= 736: # Bord droit de la fenêtre
            self.position -= vitesse # La position s'incrémente puis se décremente de la même valeur, il reste immobile
        elif self.sens == "gauche":
            self.position -= vitesse
        if self.position <= 0: # Bord gauche de l'écran
            self.position += vitesse
        self.rect.x , self.rect.y = self.position, self.hauteur
        return self.position

    def marquer(self,Ennemi):
        # Fonction pour ajouter des points au score du vaisseau lorsqu'il tue un ennemi
        self.score += Ennemi.points

    def tirer(self,Balle) :
        # Fonction pour tirer une balle
        if Balle.etat == "chargee":
            # Si la balle est chargée (c'est-à-dire qu'elle est prête à être tirée), on joue un son aléatoire
            sound = pygame.mixer.Sound(f"sounds/piou_{randint(1,9)}.ogg")
            sound.set_volume(0.6)
            sound.play()
        Balle.etat = "tiree" # On met à jour l'état de la balle en "tirée"

    def toucher(self, Ennemi):
        # Fonction pour gérer la collision entre le vaisseau et un ennemi
        if Ennemi.rect.colliderect(self.rect):
            # Si les rectangles qui englobent l'ennemi et le vaisseau entrent en collision, on met à jour la vie de l'ennemi et on appelle la fonction pour faire disparaître l'ennemi
            Ennemi.vie = 0
            Ennemi.disparaitre()
            self.degat(Ennemi)
            return True
    
    def degat(self, Ennemi):
        #Fonction pour mettre à jour le nombre de vies du vaisseau et son score lorsqu'il est touché par un ennemi
        self.score -= Ennemi.points # On enlève au score du vaisseau le nombre de points de l'ennemi
        self.vie -= 1 # On enlève une vie au vaisseau
        if self.vie <= 0:
            self.active = False # Si le vaisseau n'a plus de vies, on met à jour son état en "inactif"
        sound = pygame.mixer.Sound(f"sounds/lose_one_life.ogg")
        sound.play()
        return self.active
    
    def active_bonus(self, Bonus):
        # Fonction pour activer un bonus
        if self.is_not_looted(Bonus):
            # Si le bonus n'a pas été collecté par le vaisseau, on l'ajoute à la liste des bonus collectés
            self.liste_bonus.append(Bonus)
        else:
            # Si le bonus a déjà été collecté, on le retire de la liste et on le rajoute à nouveau afin de réinitialiser le bonus
            for i in self.liste_bonus:
                if i.type == Bonus.type:
                    self.liste_bonus.remove(i)
                    self.liste_bonus.append(Bonus) 
        # Selon le type de bonus, on joue un son spécifique
        if Bonus.type == "Laser":
            sound = pygame.mixer.Sound(f"sounds/laser.ogg")
            sound.play()
        elif Bonus.type == "stoptime":
            sound = pygame.mixer.Sound(f"sounds/za_warudo.ogg")
            sound.play()
        Bonus.active = False # On met à jour l'état du bonus en "inactif"

    def is_not_looted(self, Bonus):
        # Fonction pour vérifier si le bonus passé en argument a déjà été collecté par le vaisseau
        condition = True # On initialise la condition à True
        for i in self.liste_bonus:
            if i.type == Bonus.type: # Si le type de bonus de l'élément de la liste est le même que celui passé en argument
                condition = False # La condition devient False
            else:
                continue # On continue la boucle
        return condition # On retourne la valeur de la condition
        
    def fin(self):
        #ouvre un lien internet, aucun virus soyez rassurez :)
        return web.open_new("https://bit.ly/3GxjUhz")

class Balle:
    
    def __init__(self, player, hauteur=540, etat=""):
        # Le joueur qui a tiré la balle
        self.tireur = player
        # La position de la balle sur l'axe des x
        self.depart = 0
        # La position de la balle sur l'axe des y
        self.hauteur = hauteur
        # L'image de la balle
        self.image = pygame.image.load(f"images/balle.png")
        # L'état de la balle : "chargee" ou "tiree"
        self.etat = "chargee" or "tiree"
        # Le rectangle englobant l'image de la balle
        self.rect = self.image.get_rect(x=self.depart, y=self.hauteur)

    def bouger(self):
        # La vitesse de déplacement de la balle
        vitesse = 2.3 * vitesse_global
        # Si la balle est chargée
        if self.etat == "chargee":
            # La hauteur de la balle revient à celle du vaisseau
            self.hauteur = 540
            # La position de la balle sur l'axe des x est cachée par le vaisseau
            self.depart = self.tireur.deplacer() + 17
        # Si la balle est tirée et qu'elle n'a pas atteint le haut de l'écran
        elif self.hauteur > 0 and self.etat == "tiree":
            # La balle se déplace vers le haut
            self.hauteur -= vitesse
        # Si la balle a atteint le haut de l'écran ou qu'elle est tirée mais pas encore arrivée au haut de l'écran
        else:
            # L'état de la balle est remis à "chargee"
            self.etat = "chargee"
            # La hauteur de la balle est remise à celle du vaisseau
            self.hauteur = self.tireur.position

        # Mise à jour de la position de la balle
        self.rect.x, self.rect.y = self.depart, self.hauteur

    def toucher(self, Ennemi):
        # Si la balle et l'ennemi sont en collision
        if self.rect.colliderect(Ennemi.rect):
            # L'état de la balle est remis à "chargee"
            self.etat = "chargee"
            return True
        return False


class Ennemi:
    
    # Nombre d'ennemis = 6, + 1 tous les 1000 points
    NbEnnemis = 6
    # Vitesse des ennemis lorsque le bonus stoptime est actif
    vitesse_stoptime = 1 or 0

    def __init__(self):
        # Position aléatoire en x et y pour l'apparition de l'ennemi
        self.depart = randint(0,736)
        self.hauteur = randint(0,10)
        # Vitesse de l'ennemi qui dépend de la vitesse globale
        self.vitesse =  0.05
        # Points de vie de l'ennemi
        self.vie = 1
        # Type d'ennemi aléatoire
        self.type = randint(1,100)
        # Si l'ennemi est actif
        self.active = True

        # Affectation de l'image de l'ennemi en fonction de son type
        # Modification de la vitesse et des points de vie en fonction du type
        if 1<= self.type <= 50:
            self.image = pygame.image.load(f"images/invader1.png")
            self.vitesse *= 1.5
        elif 50 < self.type <= 90:
            self.image = pygame.image.load(f"images/invader2.png")
            self.vie += 1
        elif 90 < self.type <= 100:
            self.image = pygame.image.load(f"images/invader3.png")
            self.vie += 4
            self.vitesse /= 1.5
        # determine le nombre de point que vaut l'ennemi en fonction de sa vie
        self.points = self.vie 
        # créer la hitboxe de l'ennemi
        self.rect = self.image.get_rect(x = self.depart, y = self.hauteur)

    def avancer(self, Joueur):
        # Si l'ennemi n'est pas encore arrivé en bas de l'écran
        if self.hauteur <= 540:
            # On fait avancer l'ennemi vers le bas de l'écran
            self.hauteur += self.vitesse * self.vitesse_stoptime * vitesse_global
            self.rect.y = self.hauteur
            return True
        # Si l'ennemi a atteint le bas de l'écran
        elif self.hauteur >= 535:
            # On enlève une vie au joueur
            self.vie = 0
            Joueur.degat(self)
            # On fait disparaître l'ennemi
            self.disparaitre()

    def disparaitre(self, degat = 1):
        # On enlève des points de vie à l'ennemi
        self.vie -= degat
        # Si l'ennemi n'a plus de points de vie
        if self.vie <= 0:
            # On désactive l'ennemi
            self.active = False
            # On enlève un ennemi du compteur d'ennemis
            self.NbEnnemis -= 1
            # On ajoute un ennemi tué au compteur du joueur
            Joueur.NbEnnemisTue += 1
            # On crée une explosion à l'endroit où l'ennemi se trouvait
            Explode.all_explosions.add(Explode(self.depart, self.hauteur))
            # On joue le son de l'explosion
            Explode.sound()
            # On invoque un bonus
            return Bonus.summon()


class Explode(pygame.sprite.Sprite):
    # Création d'un groupe de sprites pour stocker toutes les explosions
    all_explosions = pygame.sprite.Group()

    def __init__(self, x, y):
        # Initialisation du sprite
        super().__init__()
        # Chargement de l'image de la première frame de l'explosion
        self.image = pygame.image.load(f"explosion_frame/frame-1-0.GIF")
        # Création d'un rectengle pour la collision de l'explosion
        self.rect = self.image.get_rect()
        # Positionnement de l'explosion
        self.rect.x = x
        self.rect.y = y
        # Numéro de la frame actuelle de l'explosion
        self.frame = 1
        # Numéro de la sous-frame actuelle de l'explosion
        self.sub_frame = 0
        # Indicateur de l'état d'animation de l'explosion
        self.is_animate = True

    def load_frame(self):
        # Chargement de l'image de la frame actuelle de l'explosion
        frame_path = f"explosion_frame/frame-{self.frame}-{self.sub_frame}.GIF"
        return pygame.image.load(frame_path)

    def animation(self, frame_rate = 3, loop = False):
        # Si l'explosion est en cours d'animation
        if self.animation:
            # Chargement de l'image de la frame suivante de l'explosion
            self.image = self.load_frame()
            # Passage à la sous-frame suivante
            self.sub_frame += 1
            
            # Si la sous-frame actuelle est supérieure au taux de frame par seconde
            if self.sub_frame > frame_rate:
                # Retour à la première sous-frame
                self.sub_frame = 0
                # Passage à la frame suivante
                self.frame += 1
                # Si la frame actuelle est supérieure à la dernière frame
                if self.frame > 11:
                    # Retour à la première frame
                    self.frame = 0
                    # Retour à la première sous-frame
                    self.sub_frame = 0
                    # Si l'explosion n'est pas en boucle
                    if loop is False:
                        # On arrête l'animation de l'explosion
                        self.is_animate = False

    def sound():
        son = pygame.mixer.Sound(f"sounds/Explosion-{randint(1,6)}.ogg")
        son.set_volume(0.75)
        son.play()


class Bonus:
    def __init__(self, player):
        # Référence au joueur qui récupère le bonus
        self.player = player
        # Coordonnées aléatoires de l'apparition du bonus
        self.coor_x = randint(0,736)
        self.coor_y = randint(0,10)
        # Vitesse de descente du bonus
        self.vitesse =  0.09 
        # Indicateur si le bonus a été récupéré par le joueur
        self.looted = False
        # Indicateur si le bonus est actif
        self.active = True
        # Type de bonus aléatoire (entier entre 0 et 3000)
        self.type = randint(0,3000)
        # Durée de vie du bonus (en secondes)
        self.timer = 10
        # Tour de jeu où le bonus est apparue
        self.round = 0
        # Tour de jeu où le bonus a été récupéré
        self.start_timer = 0
        # Image du bonus récupéré
        self.looted_image = None
        # Durée de vie du bonus (en nombre d'utilisations)
        self.durabilite = None
        # Zone de collision du bonus
        self.rect = None
        # Si le type de bonus est "Shield" (entre 0 et 1000)
        if 0 <= self.type < 1000: 
            self.type = "Shield"
            # Chargement de l'image du bonus en chute
            self.falling_image = pygame.image.load(f"images/bonus_shield.png")
            # Chargement de l'image du bonus récupéré
            self.looted_image = pygame.image.load(f"images/Shield.png")
            # Durée de vie du bonus en nombre d'utilisations
            self.durabilite = 3
            # Durée de vie du bonus en secondes (le bouclier dure 1 minute au lieu de 10 secondes)
            self.timer = 60
        # Si le type de bonus est "Laser" (entre 1000 et 2000)
        elif 1000 <= self.type < 2000:
            self.type = "Laser"
            # Chargement de l'image du bonus en chute
            self.falling_image = pygame.image.load(f"images/bonus_laser.png")
            # Chargement de l'image du bonus récupéré
            self.looted_image = pygame.image.load(f"images/Laser.png")
        # Si le type de bonus est "stoptime" (entre 2000 et 3000)
        elif 2000 <= self.type <= 3000:
            self.type = "stoptime"
            # Chargement de l'image du bonus en chute
            self.falling_image = pygame.image.load(f"images/bonus_stoptime.png")   
        
        """

        3 bonus c'est déjà pas mal :)

        elif 3000 <= self.type <= 4000:
            self.type = "Multishot"
            self.falling_image = pygame.image.load(f"images/bonus_multishot.png")
        """
        
        # adapte la taille de l'image
        self.falling_image = pygame.transform.scale(self.falling_image, (50,50))    
        
        # si l'objet a une image quand elle est récupérer, créer une hitboxe de cette image
        if self.looted_image:
            self.rect = self.looted_image.get_rect(x = self.coor_x, y = self.coor_y)

    def summon():
        # définis une chance d'aparition d'un bonus, est appelé a chaque mort d'un ennemi
        n = randint(0,round(100000*file.get_stats_bonus()))
        if n >= 95000 :             #proba mutliplié par le % de chance dans les options
            return True
        return False

    def deplacer(self):
        # Si le bonus n'a pas été récupéré par le joueur
        if not self.looted:
            # Si le bonus est actif
            if self.active == True:
                # Si le bonus n'est pas encore arrivé en bas de l'écran
                if self.coor_y <= 540:
                    # On fait descendre le bonus vers le bas de l'écran
                    self.coor_y += self.vitesse * Ennemi.vitesse_stoptime * vitesse_global 
                    return True
                # Si le bonus a atteint le bas de l'écran
                elif self.coor_y > 540:
                    # On désactive le bonus
                    self.active = False
                    return False
            # Si le bonus n'est pas actif et n'a pas été récupéré
            if self.active and self.looted == False :
                return False
        # Si le bonus a été récupéré par le joueur
        elif self.looted:
            # On met à jour les coordonnées du bonus pour qu'il soit sur le joueur
            self.coor_x, self.coor_y = self.player.position, self.player.hauteur
            # Si le bonus a une zone de collision
            if self.rect:
                # Si le type de bonus est "Shield"
                if self.type == "Shield":
                    # Si le bouclier a encore de la durabilité
                    if self.durabilite:
                    # On déplace le bouclier pour qu'il soit sur le joueur
                        self.coor_x -= 10
                        self.coor_y -= 20
                    else:
                        #Si il n'as plus de durabilité, on le désactive
                        self.active = False
                        self.looted = False
                
                else: # Le bonus est un Laser
                    # On le place sur le joueur
                    self.coor_x += 20
                    self.coor_y -= 610
                # On change la hitboxe de positio nen fonction de la position de l'image
                self.rect.x = self.coor_x
                self.rect.y = self.coor_y

    def destruct(self):
        # Désactive le bonus
        self.active = False
        return True

    def is_looted(self,Joueur):
        # Si le bonus est en contact avec le joueur
        if Joueur.hauteur -50 <= self.coor_y <= Joueur.hauteur + 50 \
            and Joueur.position -50 <= self.coor_x <= Joueur.position + 50:
            # Le bonus est récupérer
            self.looted = True
            return True
        return False

    def timer_bonus(self,start):
        # Définis un timer avec comme parametre start = time.monotic() activer dans le main
        end = time.monotonic()
        if end - start >= self.timer:
            # Si le temps écouler est supérieur ou égale au temps d'activation du bonus, on retourne vrai
            return True
        else:
            return False

    def is_collide(self, Ennemi):
        # Si le bonus, a une hitboxe, retourne s'il est en collision avec l'ennemi
        if self.rect:
            return self.rect.colliderect(Ennemi.rect)


