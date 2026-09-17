def build_context(results):
    documents = results["documents"][0]

    context_parts = []

    for index, document in enumerate(documents, start=1):
        context_parts.append(
            f"[Context {index}]\n{document}"
        )

    return "\n\n".join(context_parts)