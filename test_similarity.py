from app.services.embedding_service import generate_embeddings
import numpy as np


texts = [
    "Machine learning allows computers to learn from data.",
    "Artificial intelligence learns patterns from examples.",
    "Pizza is a popular food."
]


embeddings = generate_embeddings(texts)


similarity_1 = np.dot(embeddings[0], embeddings[1])
similarity_2 = np.dot(embeddings[0], embeddings[2])


print("Similarity between ML sentences:", similarity_1)
print("Similarity between ML and pizza:", similarity_2)