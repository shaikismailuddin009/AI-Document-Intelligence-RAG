from app.services.llm_service import generate_answer


question = "What machine learning methods are discussed in this paper?"

context = """
The paper discusses several machine learning methods for skin disease
detection and classification. These include Support Vector Machine (SVM),
K-Nearest Neighbors (KNN), and Decision Tree (DT). The paper also compares
their performance with approaches such as CNN and OP-DNN.
"""

answer = generate_answer(question, context)

print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(answer)