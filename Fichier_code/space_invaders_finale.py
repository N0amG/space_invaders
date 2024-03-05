
def game():

    import pygame # importation de la librairie pygame
    import spaces as space
    import sys # pour fermer correctement l'application
    import time

    # lancement d'un timer
    start_game_timer = time.monotonic()

    # lancement des modules inclus dans pygame
    pygame.init()

    # création d'une fenêtre de 800 par 600
    screen = pygame.display.set_mode((800,600))

    pygame.display.set_caption("Space Invaders")

    # chargement de l'image de fond
    fond = pygame.image.load(f'images/background.jpg')
    #creation d'une playlist musicale
    playlist = ["tetris", "megalovania", "at_doom_gate"]

    # chargement de la musique de fond

    music = space.randint(0,2)

    file = f"music/{playlist[music]}.ogg"

    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(-1) # Si la musique termine, elle recommence en boucle 
    pygame.mixer.music.set_volume(0.7)

    # creation du joueur
    player = space.Joueur()

    # creation de la police d'écriture
    police = pygame.font.SysFont("arial",25)

    # creation de la balle
    tir = space.Balle(player)

    # creation des ennemis
    listeEnnemis = []
    for indice in range(space.Ennemi.NbEnnemis):
        vaisseau = space.Ennemi()
        listeEnnemis.append(vaisseau)

    liste_Bonus = []

    y_background = 0

    # Création d'une horloge
    clock = pygame.time.Clock()

    # Création d'une pause = a False
    pause= False

    # Touche escape
    escape = False
    # Création d'un palier de points
    palier_score = 1
    ### BOUCLE DE JEU  ###
    running = True # variable pour laisser la fenêtre ouverte

    while True : # boucle infinie pour laisser la fenêtre ouverte


    ### Défilement du fond d'écran ###
        
        y_background += 0.15 * space.vitesse_global * space.Ennemi.vitesse_stoptime
        
        if y_background <= 600:
            screen.blit(fond,(0,y_background))
            screen.blit(fond,(0, y_background-600))
        else:
            y_background = 0
            screen.blit(fond,(0,y_background))

        # Limation des FPS
        clock.tick(60)
        
        # condition pour empecher de tirer des balles si le laser ets actifs
        condition = True

        ### Gestion des événements  ###
        for event in pygame.event.get(): # parcours de tous les event pygame dans cette fenêtre
            if event.type == pygame.QUIT : # si l'événement est le clic sur la fermeture de la fenêtre
                sys.exit() # pour fermer correctement

        # gestion du clavier
            if event.type == pygame.KEYDOWN : # si une touche a été tapée KEYUP quand on relache la touche
                if event.key == pygame.K_LEFT : # si la touche est la fleche gauche
                    player.sens = "gauche" # on déplace le vaisseau de 1 pixel sur la gauche
                if event.key == pygame.K_RIGHT : # si la touche est la fleche droite
                    player.sens = "droite" # on déplace le vaisseau de 1 pixel sur la gauche
                if event.key == pygame.K_SPACE : # espace pour tirer
                    for i in player.liste_bonus:
                        if i.type == "Laser":
                            condition = False
                    if condition:    
                        player.tirer(tir)
                if event.key == pygame.K_LCTRL: # Si ctrl gauche est pressé, passe change la variable pause d'état
                    pause = not pause
                if event.key == pygame.K_ESCAPE:
                    player.active = False # tue instantanément le joueur, faites pas gaffe c'est juste pratique pour les test
                    escape = True
        
        while pause:
            
            pause_police = pygame.font.SysFont("arial",50)
            pygame.mixer.music.pause()
            screen.blit(pause_police.render("Partie en Pause ...",1,(255,255,255)), (200,250))
            pygame.mixer.stop()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT : # si l'événement est le clic sur la fermeture de la fenêtre
                    sys.exit() # pour fermer correctement
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        pause = not pause
                        pygame.mixer.music.unpause()
                    
        ### Actualisation de la scene ###
    
        # Gestions des collisions
        
        for ennemi in listeEnnemis:
            if tir.toucher(ennemi):
                if ennemi.disparaitre(): # Certain % de chance de faire apparaitre un bonus si un ennemi est détruit
                    liste_Bonus.append(space.Bonus(player)) 

        # placement des objets #

        # le joueur
        player.deplacer()
        # la balle
        tir.bouger()
        
        # Si le joueur est actif
        if player.active:
            # On affiche l'image du tir à l'écran
            screen.blit(tir.image, [tir.depart, tir.hauteur])

            # Pour chaque ennemi de la liste
            for ennemi in listeEnnemis:
                # On avance l'ennemi et on vérifie si le joueur est touché
                ennemi.avancer(player)
                player.toucher(ennemi)
                # Pour chaque bonus du joueur
                for bonus in player.liste_bonus:
                    # Si le bonus entre en collision avec l'ennemi
                    if bonus.is_collide(ennemi):
                        # Si c'est un bonus Laser
                        if bonus.type == "Laser":
                            # On inflige 0.1 degat a l'ennemi par tour de boucle (60 fps = 6 degats/secondes)
                            ennemi.disparaitre(0.1)
                        # Si c'est un bonus Shield
                        elif bonus.type == "Shield":
                            # On décrémente la durabilité du bonus et on joue un son
                            bonus.durabilite -= 1
                            sound = pygame.mixer.Sound(f"sounds/shield.ogg")
                            sound.set_volume(0.75)
                            sound.play()
                            # On inflige 25 degat a l'ennemi
                            ennemi.disparaitre(25)
                # Si l'ennemi est actif
                if ennemi.active:
                    # On affiche l'image de l'ennemi à l'écran
                    screen.blit(ennemi.image, [ennemi.depart, ennemi.hauteur])
                # Si l'ennemi n'est plus actif
                else:
                    # On le retire de la liste, on incrémente le score du joueur et on ajoute un nouvel ennemi à la liste
                    listeEnnemis.remove(ennemi)
                    player.marquer(ennemi)
                    listeEnnemis.append(space.Ennemi())
                # On affiche le score et les points de vie du joueur à l'écran
                image_score = police.render(f"Score = {player.score}", 1, (255, 0, 0))
                image_vie = police.render(f"Vie = {player.vie}", 1, (0, 255, 0))
                screen.blit(image_score, (0, 0))
                screen.blit(image_vie, (700, 570))
            # Pour chaque bonus de la liste
            for bonus in liste_Bonus:
                # On vérifie si le bonus est ramassé par le joueur
                bonus.is_looted(player)
                # On déplace le bonus
                bonus.deplacer()
                # Si le bonus est actif et qu'il n'a pas encore été ramassé
                if bonus.active and not bonus.looted:
                    # On affiche l'image du bonus à l'écran
                    screen.blit(bonus.falling_image, [bonus.coor_x, bonus.coor_y])
                    # Si le bonus est actif et qu'il a été ramassé
                if bonus.active and bonus.looted:
                    # On active le bonus sur le joueur
                    player.active_bonus(bonus)
                    # Si le bonus n'est plus actif et qu'il a été ramassé
                if not bonus.active and bonus.looted:
                    # Si c'est la première fois que le bonus est ramassé dans ce tour de boucle
                    if not bonus.round:
                        # On incrémente le compteur de tour de boucle
                        bonus.round += 1
                        # On incrémente le score du joueur
                        player.score += 10
                        # On crée un nouveau bonus actif sur le joueur
                        bonus_actif = space.Bonus(player)
                        # On démarre le chronomètre du bonus
                        bonus.start_timer = time.monotonic()
                        # Si c'est un bonus Stoptime
                        if bonus.type == "stoptime":
                            # On change l'image de la balle en couteau
                            tir.image = pygame.transform.scale(pygame.image.load(f"images/couteau.png"), (50, 50))
                            # On change l'image du vaisseau avec celle qui a les cheveux de Dio
                            player.image = pygame.image.load(f"images/dio_hair_vaisseau.png")
                            # On fige tous les ennemis
                            space.Ennemi.vitesse_stoptime = 0
                            # On met en pause la musique
                            pygame.mixer.music.pause()
                    # Si ce n'est pas la première fois que le bonus est ramassé dans cette manche
                    else:
                        # Si le chronomètre du bonus est terminé (10 secondes)
                        if bonus.timer_bonus(bonus.start_timer):
                            # Si c'est un bonus Stoptime
                            if bonus.type == "stoptime":
                                # On défige tous les ennemis
                                space.Ennemi.vitesse_stoptime = 1
                                # On relance la musique
                                pygame.mixer.music.unpause()
                                # On remet l'image de la balle
                                tir.image = pygame.image.load(f"images/balle.png")
                                player.image = pygame.image.load(f"images/vaisseau.png")
                            # On désactive le bonus
                            bonus.looted = False
                # Si le bonus n'est plus actif et qu'il n'a pas été ramassé
                if not bonus.active and not bonus.looted:
                    # Si le bonus est dans la liste des bonus du joueur
                    if bonus in player.liste_bonus:
                        # On le retire de la liste
                        player.liste_bonus.remove(bonus)
                    # On retire le bonus de la liste
                    liste_Bonus.remove(bonus)

            for i in range(len(player.liste_bonus)):
                # On affiche l'image du bonus à l'écran
                screen.blit(pygame.transform.scale(player.liste_bonus[i].falling_image, (32, 32)), (34 * i, 500))
                # Si l'image du bonus ramassé existe
                if player.liste_bonus[i].looted_image:
                    # On affiche l'image du bonus ramassé à l'écran
                    screen.blit(player.liste_bonus[i].looted_image, (player.liste_bonus[i].coor_x, player.liste_bonus[i].coor_y))
            # On affiche l'image du vaisseau du joueur à l'écran
            screen.blit(player.image, [player.position, player.hauteur])
            # Pour chaque explosion
            for explode in space.Explode.all_explosions:
                # Si l'explosion est en cours d'animation
                if explode.is_animate:
                    # On lance l'animation de l'explosion
                    explode.animation()
                # Si l'animation de l'explosion est terminée
                else:
                    # On retire l'explosion de la liste des explosions
                    space.Explode.all_explosions.remove(explode)
            
            # A chaque fois que le score du joueur augmente de 1000
            if 0 <= (player.score - palier_score*1000) <= 10: 
                # Le palier augmente de 1
                palier_score += 1
                # Si la vie du joueur est inferieur a 3, on lui ajoute une vie
                if player.vie < 3:
                    player.vie += 1
                    new_life = pygame.mixer.Sound(f"sounds/new_life.ogg")
                    new_life.play()
                # Sinon on lui rajoute 250 points
                else:
                    player.score += 250
                    win_points = pygame.mixer.Sound(f"sounds/win_250_points.ogg")
                    win_points.play()
                
                space.vitesse_global += 1
                space.Ennemi.NbEnnemis += 1
                vaisseau = space.Ennemi()
                listeEnnemis.append(vaisseau)
        # Si le joueur n'est plus actif
        if not player.active:
            # On enregistre le score du joueur
            score = player.score
            # On récupère le high score enregistré
            high_score = int(space.file.get_high_score())
            # On vérifie si le score du joueur est un nouveau high score
            space.file.if_score_is_high_score(score)
            # On enregistre le nombre d'ennemis tués par le joueur
            NbEnnemisTue = player.NbEnnemisTue
            # On retire l'image du vaisseau du joueur
            player.image = None
            # On retire l'objet tir
            tir = None
            # On vide la liste des ennemis
            listeEnnemis = []
            # On arrête la boucle principale
            running = False
            # On calcul la durée de la partie
            end_game_timer = time.monotonic()
            
            game_time = (0,round(end_game_timer - start_game_timer))
            if game_time[1] >= 60:
                for i in range(0,game_time[1],60):
                    game_minutes = i/60
                game_time = (round(game_minutes), round(game_time[1]-60*game_minutes))
            # On vide la liste des explosions
            space.Explode.all_explosions = pygame.sprite.Group()
        
        # On affiche les explosions à l'écran
        space.Explode.all_explosions.draw(screen)

        pygame.display.update() # pour ajouter tout changement à l'écran
        
        if not running :
            
            # couleur blanche
            color = (255,255,255)
            
            # ombre claire du bouton
            color_light = (170,170,170)
            
            # ombre foncée du bouton
            color_dark = (100,100,100)

            width = screen.get_width()
            
            height = screen.get_height()
            
            # definir une police  
            leave_smallfont = pygame.font.SysFont('Arial',35)
            
            # faire le rendu du texte rejouer avec cette police
            replay_text = leave_smallfont.render('Rejouer' , True , color)
            # faire le rendu du text quitter avec cette police
            leave_text = leave_smallfont.render('Quitter' , True , color)
            
            pygame.mixer.stop()
            pygame.mixer.music.load(f"sounds/game_over.ogg")
            pygame.mixer.music.play()
            tour = 0

            
            if tour == 0:
                player.fin()
                tour += 1
                
            while True:
                # défilement du fond d'écran
                y_background += 0.15
                if y_background <= 600:
                    screen.blit(fond,(0,y_background))
                    screen.blit(fond,(0, y_background-600))
                else:
                    y_background = 0
                    screen.blit(fond,(0,y_background))
                

                for ev in pygame.event.get():
                    
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    # vérifie si la sourie est cliqué
                    if ev.type == pygame.MOUSEBUTTONDOWN:
                        
                        # Si la souris clique sur le bouton quitter, quitter
                        if width/2.5 <= mouse[0] <= width/2.5+140 and height/2+15 <= mouse[1] <= height/2+55:
                            pygame.quit()
                            sys.exit()
                        # Si la souris clique sur rejouer, fermer la fenêtre et rappeler la fonction de la partie pour en relancer une
                        if width/2.5 <= mouse[0] <= width/2.5+140 and height/2+60 <= mouse[1] <= height/2+105:
                            pygame.quit()
                            game()
                
                # stock les coordonnée de la souris dans un tuple
                mouse = pygame.mouse.get_pos()
                
                # si la souris passe sur le bouton, changer la couleur de l'ombre 
                if width/2.5 <= mouse[0] <= width/2.5+140 and height/2+15 <= mouse[1] <= height/2+55:
                    pygame.draw.rect(screen,color_light,[width/2.5,height/2+15,140,40])
                
                else:
                    pygame.draw.rect(screen,color_dark,[width/2.5,height/2+15,140,40])
                
                if width/2.5 <= mouse[0] <= width/2.5+140 and height/2+65 <= mouse[1] <= height/2+105:
                    pygame.draw.rect(screen,color_light,[width/2.5,height/2+65,140,40])
                    
                else:
                    pygame.draw.rect(screen,color_dark,[width/2.5,height/2+65,140,40])
                
                # superposer les textes aux boutons
                screen.blit(leave_text , (width/2.5+10,height/2+15))
                screen.blit(replay_text , (width/2.5+10,height/2+63))
                screen.blit(police.render(f"Partie terminée, vous avez obtenue {score} points,",1,(255,255,255)), (150,200))
                screen.blit(police.render(f"Meilleur score : {high_score}",1.5,(255,255,255)),(280,227))
                screen.blit(police.render(f"Vous avez tué {NbEnnemisTue} ennemis.",1,(255,255,255)),(250,255))
                screen.blit(police.render(f"La partie à durée {game_time[0]} minutes et {game_time[1]} secondes.",1,(255,255,255)),(170,280))

                # met a jour l'écran
                pygame.display.update()
game()