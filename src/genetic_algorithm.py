import numpy as np
import random
from neural_network import NeuralNet

class Population:
    def __init__(self, size=50, mutation_rate=0.05):
        self.size = size
        self.mutation_rate = mutation_rate
        self.generation = 0
        
    def next_generation(self, dinos):
        """
        dinos is a list of Dino objects that have a .nn property (NeuralNet) and a .fitness property
        """
        # Sort by fitness descending
        dinos.sort(key=lambda x: x.fitness, reverse=True)
        
        # Keep best 10% (Elitism)
        elite_count = max(2, int(self.size * 0.1))
        elites = dinos[:elite_count]
        
        new_networks = []
        
        # Carry over elites directly
        for dino in elites:
            new_networks.append(NeuralNet(weights=self._copy_weights(dino.nn.get_weights())))
            
        # Breed the rest
        while len(new_networks) < self.size:
            parent1 = self._select(dinos)
            parent2 = self._select(dinos)
            
            child_weights = self._crossover(parent1.nn.get_weights(), parent2.nn.get_weights())
            self._mutate(child_weights)
            
            new_networks.append(NeuralNet(weights=child_weights))
            
        self.generation += 1
        return new_networks
        
    def _select(self, dinos):
        # Tournament selection
        tournament = random.sample(dinos, 5)
        tournament.sort(key=lambda x: x.fitness, reverse=True)
        return tournament[0]
        
    def _copy_weights(self, weights):
        return tuple(w.copy() for w in weights)
        
    def _crossover(self, w1, w2):
        child_w = []
        for mat1, mat2 in zip(w1, w2):
            # Uniform crossover
            mask = np.random.rand(*mat1.shape) > 0.5
            child_mat = np.where(mask, mat1, mat2)
            child_w.append(child_mat)
        return tuple(child_w)
        
    def _mutate(self, weights):
        for mat in weights:
            # Add gaussian noise to random genes based on mutation rate
            mask = np.random.rand(*mat.shape) < self.mutation_rate
            noise = np.random.randn(*mat.shape) * 0.2
            mat[mask] += noise[mask]
