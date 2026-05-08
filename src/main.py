import pygame
import sys
import os
import random
from game import Dino, Cactus, Bird, get_state, WIDTH, HEIGHT, GROUND_Y, GAME_SPEED_START
from neural_network import NeuralNet
from genetic_algorithm import Population

system_logs = []

def add_log(text):
    print(text)
    system_logs.append(text)
    if len(system_logs) > 8:
        system_logs.pop(0)

def draw_dashboard(screen, font, history, all_time_best):
    # Fondo del dashboard
    pygame.draw.rect(screen, (240, 240, 240), (WIDTH, 0, 400, HEIGHT))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH, 0), (WIDTH, HEIGHT), 3)
    
    title = font.render("Dashboard de Evolución", True, (0, 0, 0))
    screen.blit(title, (WIDTH + 20, 20))
    
    best_text = font.render(f"Récord Global: {int(all_time_best)}", True, (34, 139, 34))
    screen.blit(best_text, (WIDTH + 20, 60))
    
    # Gráfica y ejes
    y_label = font.render("Fitness", True, (100, 100, 100))
    screen.blit(y_label, (WIDTH + 20, 95))
    
    graph_rect = pygame.Rect(WIDTH + 20, 120, 360, 230)
    pygame.draw.rect(screen, (255, 255, 255), graph_rect)
    pygame.draw.rect(screen, (0, 0, 0), graph_rect, 2)
    
    x_label = font.render("Generaciones", True, (100, 100, 100))
    screen.blit(x_label, (WIDTH + 150, 355))
    
    if len(history) > 1:
        max_val = max(max(history), 1)
        points = []
        for i, val in enumerate(history):
            x = graph_rect.x + (i / (len(history) - 1)) * graph_rect.width
            y = graph_rect.bottom - (val / max_val) * graph_rect.height
            points.append((x, y))
        pygame.draw.lines(screen, (0, 0, 255), False, points, 2)

# Initialize Pygame
pygame.init()

def main():
    print("\n--- DINO GEN AI ---")
    load_saved = input("¿Deseas intentar cargar el modelo guardado previamente? (s/n): ").strip().lower() == 's'
    print("Iniciando entorno gráfico...\n")
    
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dino GenAI - All Obstacles")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier New", 18) # Better font for logs
    font_ui = pygame.font.SysFont("Arial", 20)
    
    POPULATION_SIZE = 50
    ga = Population(size=POPULATION_SIZE, mutation_rate=0.1)
    
    training_speed = 60 # FPS base
    is_turbo = False
    is_paused = False
    
    pause_btn_rect = pygame.Rect(WIDTH + 20, 360, 160, 30)
    
    all_time_best = 0
    fitness_history = []
    
    os.makedirs("data", exist_ok=True)
    model_path = os.path.join("data", "best_model.npz")
    
    # Cargar modelo si se solicitó y existe
    if load_saved and os.path.exists(model_path):
        weights, gen, all_time_best, fitness_history = NeuralNet.load_model(model_path)
        ga.generation = gen
        add_log(f"Modelo cargado: Gen {gen}, Récord: {all_time_best}")
        
        dinos = []
        elite_count = max(2, int(POPULATION_SIZE * 0.1))
        for _ in range(elite_count):
            dinos.append(Dino(nn=NeuralNet(input_size=5, output_size=2, weights=weights)))
            
        while len(dinos) < POPULATION_SIZE:
            child_weights = tuple(w.copy() for w in weights)
            ga._mutate(child_weights)
            dinos.append(Dino(nn=NeuralNet(input_size=5, output_size=2, weights=child_weights)))
    else:
        # Initialize first generation with random NNs (5 inputs, 2 outputs)
        dinos = [Dino(nn=NeuralNet(input_size=5, output_size=2)) for _ in range(POPULATION_SIZE)]
    
    game_speed = GAME_SPEED_START
    obstacles = []
    frames = 0
    gen_max_fitness = 0
    
    running = True
    while running:
        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Control de velocidad con teclas
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f: # 'F' para Fast Forward
                    is_turbo = not is_turbo
                if event.key == pygame.K_UP:
                    training_speed += 30
                    is_turbo = False
                if event.key == pygame.K_DOWN:
                    training_speed = max(30, training_speed - 30)
                    is_turbo = False
            
            # Control de botones
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_btn_rect.collidepoint(event.pos):
                    is_paused = not is_paused
                    add_log("Juego Pausado" if is_paused else "Juego Reanudado")
                
        # Update Game Logic
        if not is_paused:
            frames += 1
            
            # Increase speed slightly over time
            if frames % 500 == 0:
                game_speed += 0.2
                
            # Spawn obstacles
            if len(obstacles) == 0 or obstacles[-1].x < WIDTH - random.randint(300, 450):
                if random.random() < 0.05:
                    # 25% chance of bird after frame 1000 to give them time to learn cactus first
                    if frames > 1000 and random.random() < 0.25:
                        obstacles.append(Bird(speed=game_speed))
                    else:
                        obstacles.append(Cactus(speed=game_speed))
                    
            # Update obstacles
            for obs in obstacles:
                obs.update()
            obstacles = [obs for obs in obstacles if obs.x + obs.width > 0]
            
            # Update Dinos
            alive_count = 0
            
            for dino in dinos:
                if dino.fitness > gen_max_fitness:
                    gen_max_fitness = dino.fitness
                    
                if dino.is_alive:
                    alive_count += 1
                    state = get_state(dino, obstacles, game_speed)
                    action = dino.nn.predict(state)
                    
                    # Action[0]: Jump, Action[1]: Duck
                    if action[0] > 0.5:
                        dino.jump()
                        dino.duck(False)
                    elif action[1] > 0.5:
                        dino.duck(True)
                    else:
                        dino.duck(False)
                        
                    dino.update()
                    
                    # Check collisions
                    for obs in obstacles:
                        if dino.rect.colliderect(obs.rect):
                            dino.is_alive = False
                            break
                            
            # Check if generation died
            if alive_count == 0:
                fitness_history.append(gen_max_fitness)
                if gen_max_fitness > all_time_best:
                    all_time_best = gen_max_fitness
                    best_dino = max(dinos, key=lambda d: d.fitness)
                    NeuralNet.save_model(model_path, best_dino.nn.get_weights(), ga.generation, all_time_best, fitness_history)
                    add_log(f"¡NUEVO RÉCORD GLOBAL! ({all_time_best}) Guardado.")
                    
                add_log(f"Gen {ga.generation} | Max Fitness: {gen_max_fitness}")
                new_nns = ga.next_generation(dinos)
                
                # Reset environment
                dinos = [Dino(nn=nn) for nn in new_nns]
                obstacles.clear()
                game_speed = GAME_SPEED_START
                frames = 0
                gen_max_fitness = 0
                continue

            
        # Drawing
        screen.fill((255, 255, 255))
        # Ground
        pygame.draw.line(screen, (100, 100, 100), (0, GROUND_Y + 44), (WIDTH, GROUND_Y + 44), 2)
        
        for obs in obstacles:
            obs.draw(screen)
            
        for dino in dinos:
            dino.draw(screen)
            
        # Dibujar Panel de Logs inferior
        log_panel_rect = pygame.Rect(0, HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - HEIGHT)
        pygame.draw.rect(screen, (30, 30, 30), log_panel_rect)
        pygame.draw.line(screen, (200, 200, 200), (0, HEIGHT), (SCREEN_WIDTH, HEIGHT), 3)
        
        for idx, log_text in enumerate(system_logs):
            log_surf = font.render(log_text, True, (0, 255, 0))
            screen.blit(log_surf, (20, HEIGHT + 15 + (idx * 22)))
            
        # UI (ahora usa font_ui)
        speed_text = "TURBO" if is_turbo else f"{training_speed} FPS"
        ui_text = font_ui.render(f"Gen: {ga.generation} | Vivos: {alive_count} | Fitness Max: {gen_max_fitness} | Speed: {speed_text}", True, (0, 0, 0))
        screen.blit(ui_text, (10, 10))
        help_text = font_ui.render("F: Turbo | Flechas: +/- FPS", True, (150, 150, 150))
        screen.blit(help_text, (10, 35))
        
        # Dibujar el dashboard
        draw_dashboard(screen, font_ui, fitness_history, all_time_best)
        
        # Dibujar botón de pausa
        pygame.draw.rect(screen, (200, 50, 50) if is_paused else (50, 200, 50), pause_btn_rect)
        pygame.draw.rect(screen, (0, 0, 0), pause_btn_rect, 2)
        btn_text = font_ui.render("REANUDAR" if is_paused else "PAUSAR", True, (255, 255, 255))
        screen.blit(btn_text, (pause_btn_rect.x + 35, pause_btn_rect.y + 4))
        
        pygame.display.flip()
        
        if not is_turbo:
            clock.tick(training_speed)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
