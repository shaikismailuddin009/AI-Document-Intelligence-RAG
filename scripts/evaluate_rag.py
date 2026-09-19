"""Small RAG evaluation script.

This is a lightweight, keyword-based check — not a rigorous benchmark. It
answers two narrow questions: "did retrieval pull back chunks that contain
the expected terms?" (retrieval recall) and, optionally, "does the generated
answer also mention them?" (answer coverage). That's useful as a sanity
check and an interview talking point, but it does NOT prove general
retrieval quality or factual correctness beyond keyword presence, and it
says nothing about performance on questions outside this small set.

Usage:
    python scripts/evaluate_rag.py [--dataset scripts/eval_dataset.json] [--top-k 3] [--skip-answers]

Requires a document to already be uploaded/processed (so its chunks exist
in ChromaDB) before running this — it evaluates retrieval (and optionally
generation), it doesn't upload anything itself.

By default it also calls the real LLM to check answer coverage, which
requires OPENAI_API_KEY to be set. Pass --skip-answers to evaluate
retrieval only, with no API key or network call needed.

Dataset format (scripts/eval_dataset.json):
    [
      {"question": "...", "expected_keywords": ["term1", "term2"]}
    ]

Edit scripts/eval_dataset.json with real questions and keywords drawn from
your own document(s) before treating these numbers as meaningful — the
shipped file contains only illustrative placeholder entries.
"""

import argparse
import json
from pathlib import Path

from app.services.vector_store_service import search_document


def load_dataset(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _keyword_recall(text: str, expected_keywords: list[str]) -> tuple[list[str], float | None]:
    text_lower = text.lower()
    matched = [kw for kw in expected_keywords if kw.lower() in text_lower]
    recall = len(matched) / len(expected_keywords) if expected_keywords else None
    return matched, recall


def evaluate_question(question: str, expected_keywords: list[str], top_k: int, check_answer: bool) -> dict:
    results = search_document(query=question, top_k=top_k)
    documents = results.get("documents", [[]])[0]
    combined_text = " ".join(documents)

    matched, retrieval_recall = _keyword_recall(combined_text, expected_keywords)

    result = {
        "question": question,
        "retrieved_chunks": len(documents),
        "expected_keywords": expected_keywords,
        "matched_keywords": matched,
        "retrieval_recall": retrieval_recall,
        "answer_recall": None,
        "answer_error": None,
    }

    if check_answer and documents:
        try:
            from app.services.rag_service import answer_question

            answer_result = answer_question(question=question, top_k=top_k)
            _, answer_recall = _keyword_recall(answer_result["answer"], expected_keywords)
            result["answer_recall"] = answer_recall
        except Exception as exc:
            result["answer_error"] = str(exc)

    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval (and optionally answer) quality")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(__file__).parent / "eval_dataset.json",
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--skip-answers", action="store_true",
        help="Only evaluate retrieval — skips calling the real LLM, no API key needed.",
    )
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    check_answer = not args.skip_answers

    results = [
        evaluate_question(item["question"], item["expected_keywords"], args.top_k, check_answer)
        for item in dataset
    ]

    retrieval_recalls = [r["retrieval_recall"] for r in results if r["retrieval_recall"] is not None]
    avg_retrieval_recall = sum(retrieval_recalls) / len(retrieval_recalls) if retrieval_recalls else 0.0

    answer_recalls = [r["answer_recall"] for r in results if r["answer_recall"] is not None]
    avg_answer_recall = sum(answer_recalls) / len(answer_recalls) if answer_recalls else None

    print(f"\nEvaluated {len(results)} question(s) at top_k={args.top_k}\n")

    for r in results:
        print(f"- {r['question']}")
        print(f"    retrieved {r['retrieved_chunks']} chunks")
        print(f"    retrieval keyword recall: {r['retrieval_recall']:.2f} ({r['matched_keywords']} / {r['expected_keywords']})")
        if r["answer_error"]:
            print(f"    answer check skipped (error): {r['answer_error']}")
        elif r["answer_recall"] is not None:
            print(f"    answer keyword recall: {r['answer_recall']:.2f}")

    print(f"\nAverage retrieval keyword recall: {avg_retrieval_recall:.2f}")
    if avg_answer_recall is not None:
        print(f"Average answer keyword recall: {avg_answer_recall:.2f}")

    print(
        "\nNote: these are keyword-presence heuristics, not validated retrieval "
        "or answer-quality metrics. Treat this as a smoke test, not a benchmark."
    )


if __name__ == "__main__":
    main()
