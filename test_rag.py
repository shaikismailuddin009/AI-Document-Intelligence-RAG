from app.services.rag_service import answer_question


question = "What machine learning methods are discussed in this paper?"

result = answer_question(question)


print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(question)

print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)
print(result["answer"])

print("\n" + "=" * 60)
print("RETRIEVED CONTEXT")
print("=" * 60)
print(result["context"])