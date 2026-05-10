import pygame
import sys
import os
import random

from game import Dino, Cactus, Bird, get_state, WIDTH, HEIGHT, GROUND_Y
import game
from neural_network import NeuralNet

def test_generalization():
    print("\n=================================")
    print("   VALIDADOR DE GENERALIZACIÓN   ")
    print("=================================\n")
    
    models = sorted([f for f in os.listdir("data") if f.endswith(".npz")])
    if not models:
        print("No hay modelos en 'data/'. Entrena uno primero usando src/main.py.")
        return
        
    print("Modelos disponibles para evaluar:")
    for i, m in enumerate(models):
        print(f"[{i+1}] {m}")
    print("[A] AUTOMATIZAR TODO (Corre todos los modelos y casos)")
        
    choice = input(f"\nElige una opción: ").strip().upper()
    
    if choice == 'A':
        automate_all(models)
        return

    if not (choice.isdigit() and 1 <= int(choice) <= len(models)):
        print("Selección inválida.")
        return
        
    model_name = models[int(choice)-1]
    model_path = os.path.join("data", model_name)
    weights, gen, all_time_best, fitness_history = NeuralNet.load_model(model_path)
    
    print("\nElige el Nivel de Estrés:")
    print("[1] Velocidad Extrema (Empieza al doble de velocidad)")
    print("[2] Gravedad Alterada (Gravedad de 2.2 en lugar de 1.6)")
    print("[3] Lluvia de Obstáculos (Alta frecuencia de aparición)")
    stress_choice = input("Opción (1-3): ").strip()
    
    run_simulation(weights, stress_choice, model_name, visual=True)

def run_simulation(weights, stress_choice, model_name, visual=True):
    # Configuración base
    current_speed = game.GAME_SPEED_START
    spawn_chance = 0.05
    min_dist = 300
    gravity_val = 1.6
    
    # Aplicar modificadores de estrés
    if stress_choice == '1':
        current_speed = 22
    elif stress_choice == '2':
        gravity_val = 2.2
    elif stress_choice == '3':
        spawn_chance = 0.12
        min_dist = 220
        
    # Temporalmente cambiar gravedad si es necesario
    original_gravity = game.GRAVITY
    game.GRAVITY = gravity_val
        
    if visual:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        pygame.display.set_caption(f"Validando: {model_name}")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 24)
    
    dino = Dino(nn=NeuralNet(input_size=5, output_size=2, weights=weights))
    obstacles = []
    frames = 0
    
    running = True
    # Si no es visual, limitamos a 20,000 frames para no estar infinitamente si es muy bueno
    max_frames = 20000 
    
    while running and dino.is_alive and frames < max_frames:
        if visual:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
        frames += 1
        if frames % 500 == 0:
            current_speed += 0.2
            
        if len(obstacles) == 0 or obstacles[-1].x < WIDTH - random.randint(min_dist, 450):
            if random.random() < spawn_chance:
                if random.random() < 0.3:
                    obstacles.append(Bird(speed=current_speed))
                else:
                    obstacles.append(Cactus(speed=current_speed))
                    
        for obs in obstacles:
            obs.update()
        obstacles = [obs for obs in obstacles if obs.x + obs.width > 0]
        
        state = get_state(dino, obstacles, current_speed)
        action = dino.nn.predict(state)
        
        if action[0] > 0.5:
            dino.jump()
            dino.duck(False)
        elif action[1] > 0.5:
            dino.duck(True)
        else:
            dino.duck(False)
            
        dino.update()
        
        for obs in obstacles:
            if dino.rect.colliderect(obs.rect):
                dino.is_alive = False
                break
        
        if visual:
            screen.fill((255, 255, 255))
            pygame.draw.line(screen, (100, 100, 100), (0, GROUND_Y + 44), (WIDTH, GROUND_Y + 44), 2)
            for obs in obstacles:
                obs.draw(screen)
            dino.draw(screen)
            text_frames = font.render(f"Frames: {frames} | Stress: {stress_choice}", True, (0,0,0))
            screen.blit(text_frames, (20, 20))
            pygame.display.flip()
            # En modo turbo visual podemos quitar el tick o subirlo
            clock.tick(120) 

    # Restaurar gravedad
    game.GRAVITY = original_gravity
    
    verdict = "EXITOSA" if frames > 1000 else "SOBREAJUSTE"
    if visual:
        print(f"\n[Resultado] {model_name} | Estrés {stress_choice} | Frames: {frames} | Veredicto: {verdict}")
        pygame.quit()
        
    return frames, verdict

def automate_all(models):
    import csv
    import numpy as np
    results_file = os.path.join("results", "validation_results.csv")
    
    try:
        num_trials = int(input("\n¿Cuántas veces quieres repetir cada prueba para obtener un promedio? (ej: 5): ").strip())
    except:
        num_trials = 3
        
    print(f"\nIniciando automatización ({num_trials} repeticiones por caso).")
    print(f"Resultados en: {results_file}")
    
    with open(results_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Modelo", "Caso de Estrés", "Promedio Frames", "Veredicto Promedio", "Intentos"])
        
        stress_modes = {
            "1": "Velocidad Extrema",
            "2": "Gravedad Alterada",
            "3": "Lluvia Obstáculos"
        }
        
        for m_name in models:
            model_path = os.path.join("data", m_name)
            weights, _, _, _ = NeuralNet.load_model(model_path)
            for s_code, s_name in stress_modes.items():
                print(f"Evaluando {m_name} en {s_name}...", end=" ", flush=True)
                
                trial_results = []
                for t in range(num_trials):
                    frames, _ = run_simulation(weights, s_code, m_name, visual=False)
                    trial_results.append(frames)
                
                avg_frames = int(np.mean(trial_results))
                verdict = "EXITOSA" if avg_frames > 1000 else "SOBREAJUSTE"
                
                writer.writerow([m_name, s_name, avg_frames, verdict, num_trials])
                print(f"Promedio: {avg_frames} frames")
                
    print("\n¡Automatización y análisis estadístico completado!")


if __name__ == "__main__":
    test_generalization()
