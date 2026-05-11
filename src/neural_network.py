import numpy as np

class NeuralNet:
    def __init__(self, input_size=5, hidden_size=8, output_size=2, weights=None):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        if weights is not None:
            self.W1, self.b1, self.W2, self.b2 = weights
        else:
            # Initialize with small random values
            self.W1 = np.random.randn(self.input_size, self.hidden_size) * 1.0
            self.b1 = np.zeros((1, self.hidden_size))
            self.W2 = np.random.randn(self.hidden_size, self.output_size) * 1.0
            self.b2 = np.zeros((1, self.output_size))
            
    def relu(self, x):
        return np.maximum(0, x)
        
    def sigmoid(self, x):
        # Clip to avoid overflow warnings
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))
        
    def predict(self, state):
        # Forward pass
        # State shape expected: (1, 5)
        z1 = np.dot(state, self.W1) + self.b1
        a1 = self.relu(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        a2 = self.sigmoid(z2)
        # Returns [jump_prob, duck_prob]
        return a2[0]
        
    def get_weights(self):
        return (self.W1, self.b1, self.W2, self.b2)

    @staticmethod
    def save_model(filepath, weights, generation, max_fitness, history):
        np.savez(filepath, W1=weights[0], b1=weights[1], W2=weights[2], b2=weights[3], 
                 generation=generation, max_fitness=max_fitness, history=history)

    @staticmethod
    def load_model(filepath):
        data = np.load(filepath)
        weights = (data['W1'], data['b1'], data['W2'], data['b2'])
        return weights, int(data['generation']), float(data['max_fitness']), list(data['history'])
