import pygame
import os

pygame.init()

# Create Dino Sprite
dino_surface = pygame.Surface((40, 44), pygame.SRCALPHA)
dino_surface.fill((0, 0, 0, 0))
pygame.draw.rect(dino_surface, (83, 83, 83), (10, 0, 20, 20)) # Head
pygame.draw.rect(dino_surface, (83, 83, 83), (20, 4, 20, 8))  # Snout
pygame.draw.rect(dino_surface, (83, 83, 83), (0, 20, 30, 16)) # Body
pygame.draw.rect(dino_surface, (83, 83, 83), (6, 36, 6, 8))   # Leg 1
pygame.draw.rect(dino_surface, (83, 83, 83), (18, 36, 6, 8))  # Leg 2
pygame.image.save(dino_surface, os.path.join("assets", "dino.png"))

# Create Cactus Sprite
cactus_surface = pygame.Surface((20, 40), pygame.SRCALPHA)
cactus_surface.fill((0, 0, 0, 0))
pygame.draw.rect(cactus_surface, (34, 139, 34), (6, 0, 8, 40)) # Main trunk
pygame.draw.rect(cactus_surface, (34, 139, 34), (0, 10, 6, 12)) # Left branch
pygame.draw.rect(cactus_surface, (34, 139, 34), (14, 16, 6, 12)) # Right branch
pygame.image.save(cactus_surface, os.path.join("assets", "cactus.png"))

print("Sprites generated successfully!")
