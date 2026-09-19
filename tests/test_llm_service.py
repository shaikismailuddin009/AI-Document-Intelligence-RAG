from types import SimpleNamespace

import app.services.llm_service as llm_service


class FakeResponses:
    def __init__(self, output_text: str):
        self._output_text = output_text
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(output_text=self._output_text)


class FakeClient:
    def __init__(self, output_text: str):
        self.responses = FakeResponses(output_text)


def test_generate_answer_returns_model_output(monkeypatch):
    fake_client = FakeClient("The paper uses SVM and KNN.")
    monkeypatch.setattr(llm_service, "_client", fake_client)

    answer = llm_service.generate_answer(
        question="What methods are used?",
        context="[Source 1: paper.pdf, chunk 0]\nSVM and KNN are used.",
    )

    assert answer == "The paper uses SVM and KNN."


def test_generate_answer_includes_question_and_context_in_prompt(monkeypatch):
    fake_client = FakeClient("some answer")
    monkeypatch.setattr(llm_service, "_client", fake_client)

    llm_service.generate_answer(
        question="What is X?",
        context="X is a variable.",
    )

    prompt = fake_client.responses.last_kwargs["input"]
    assert "What is X?" in prompt
    assert "X is a variable." in prompt


def test_get_client_raises_without_api_key(monkeypatch):
    monkeypatch.setattr(llm_service, "_client", None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    try:
        llm_service._get_client()
        assert False, "expected ValueError"
    except ValueError:
        pass
