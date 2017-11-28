LETTER_GRAM_SIZE = 3  # See section 3.2.
WINDOW_SIZE = 3  # See section 3.2.
TOTAL_LETTER_GRAMS = int(3 * 1e4)  # Determined from data. See section 3.2.
WORD_DEPTH = WINDOW_SIZE * TOTAL_LETTER_GRAMS  # See equation (1).
K = 300 # Dimensionality of the max-pooling layer. See section 3.4.
L = 128 # Dimensionality of latent semantic space. See section 3.5.
J = 4 # Number of random unclicked documents serving as negative examples for a query. See section 4.
FILTER_LENGTH = 1 # We only consider one time step for convolutions.