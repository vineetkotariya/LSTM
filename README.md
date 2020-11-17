# LSTM
Using LSTMs for Sentiment Analysis

Learning objective: Develop programming skills and intuition for designing, training, and hyperparameter tuning of neural networks for an NLP task.

1. Word embedding: Import a pre-trained word embedding such as word2vec or glove, and show how it works for some analogy tasks. For example, prince – boy + girl should give princess. Confirm this by measuring the L2 norm of the difference between the v(‘prince’) – v(‘boy’) + v(‘girl’) and v(‘princess’), where v(.) is the vector embedding. Try two different vector dimensions, e.g. 50 and 300, or word embeddings pre-trained on different corpora to check the differences in their accuracies.

2. Sentiment classification: Train a sentiment classifier for IMDB movie database (available in pytorch and tensorflow as a standard dataset) using the following layers: word embedding, LSTM, and classification (softmax or sigmoid).

3. Hyperparameter tuning: Check out the differences between different number of units, adding an additional LSTM layer, using GRU or LSTM, adding a dense layer with ReLU, using different learning rates schedules, weight decay, and dropouts.
