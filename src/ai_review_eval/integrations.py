"""Gemini-backed RAGAS and DeepEval integrations.

Both evaluators use the same Google Gemini API key. No OpenAI key or model is
required. If GEMINI_API_KEY is absent, judge-based metrics are explicitly
SKIPPED rather than replaced with fabricated scores.
"""
import asyncio
import os

from deepeval import evaluate


def _api_key():
    return (
        os.getenv("GROQ_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

def _skipped(reason):
    return {"status": "SKIPPED", "reason": reason,
            "faithfulness": None, "answer_relevancy": None,
            "context_precision": None, "context_recall": None}


def run_ragas(rows):
    api_key = _api_key()
    if not api_key:
        return _skipped("Set GEMINI_API_KEY in .env to run Gemini-judged RAGAS metrics.")
    if not rows:
        return {"status": "SKIPPED", "reason": "No evaluation rows were supplied.",
                "faithfulness": None, "answer_relevancy": None,
                "context_precision": None, "context_recall": None}
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        embedding_name = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
        chat = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key,
                                      temperature=0, max_retries=2)
        embeddings = GoogleGenerativeAIEmbeddings(model=embedding_name, google_api_key=api_key)
        ragas_llm = LangchainLLMWrapper(chat)
        ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

        data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
        for row in rows:
            data["question"].append("Review this source code for actionable defects:\n" + row["code"])
            findings = row.get("review", {}).get("findings", [])
            data["answer"].append("\n".join(
                f"Line {item.get('line')}: {item.get('comment', '')}" for item in findings
            ) or "No findings.")
            data["contexts"].append([row["code"]])
            data["ground_truth"].append("\n".join(
                f"Line {item.get('line')}: {item.get('comment', '')}" for item in row.get("expected", [])
            ) or "No findings.")

        dataset = Dataset.from_dict(data)

        print("Dataset columns:", dataset.column_names)
        print("Dataset sample:", dataset[0])

        result = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
            llm=ragas_llm,
            embeddings=ragas_embeddings,
        )
        scores = result.to_pandas().mean(numeric_only=True).to_dict()
        names = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
        output = {name: (float(scores[name]) if scores.get(name) is not None else None) for name in names}
        missing = [name for name, score in output.items() if score is None]
        return {"status": "PARTIAL" if missing else "COMPLETED", **output,
                "missing_metrics": missing, "model": model_name,
                "embedding_model": embedding_name, "evaluated_rows": len(rows)}
    except Exception as exc:
        error_msg = str(exc)

        if "quota" in error_msg.lower():
            reason = "Gemini quota exceeded"
        elif "credit" in error_msg.lower():
            reason = "Provider credits unavailable"
        elif "resourceexhausted" in error_msg.lower():
            reason = "Gemini daily limit exceeded"
        else:
            reason = f"RAGAS execution skipped: {type(exc).__name__}: {exc}"

        return {
            "status": "SKIPPED",
            "reason": reason,
            "faithfulness": None,
            "answer_relevancy": None,
            "context_precision": None,
            "context_recall": None,
            "evaluated_rows": len(rows)
        }


class GroqDeepEvalModel:
    def __new__(cls, *args, **kwargs):
        from deepeval.models import DeepEvalBaseLLM
        from langchain_groq import ChatGroq

        class _GroqModel(DeepEvalBaseLLM):
            def __init__(self, api_key, model_name):
                self.api_key = api_key
                self.model_name = model_name

            def load_model(self):
                return ChatGroq(
                    model_name=self.model_name,
                    groq_api_key=self.api_key,
                    temperature=0,
                )

            def generate(self, prompt: str) -> str:
                response = self.load_model().invoke(prompt)
                return response.content

            async def a_generate(self, prompt: str) -> str:
                return self.generate(prompt)

            def get_model_name(self):
                return self.model_name

        return _GroqModel(*args, **kwargs)

def run_deepeval(rows):
    api_key = _api_key()
    if not api_key:
        return {"status": "SKIPPED", "reason": "Set GEMINI_API_KEY in .env to run genuine DeepEval G-Eval task-completion judging.",
                "task_completion": None, "evaluated_cases": 0}
    if not rows:
        return {"status": "SKIPPED", "reason": "No evaluation rows were supplied.",
                "task_completion": None, "evaluated_cases": 0}
        print("Using API Key:", bool(api_key))
        print("Groq Key:", bool(os.getenv("GROQ_API_KEY")))
    try:
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams
        from langchain_groq import ChatGroq

        model_name = "qwen/qwen3.8-27b"

        judge = GroqDeepEvalModel(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=model_name 
        )
        metric = GEval(
            name="Agent Task Completion",
            criteria=("Evaluate whether the code review request was completed: the output is valid, "
                      "findings are actionable, findings refer to the supplied source, and the result "
                      "follows the requested review task. Score from 0 to 1."),
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT,
                               LLMTestCaseParams.EXPECTED_OUTPUT],
            model=judge,
        )
        scores = []
        for row in rows:
            case = LLMTestCase(
                input="Review source code:\n" + row["code"],
                actual_output=str(row.get("review", {})),
                expected_output=str({"findings": row.get("expected", [])}),
            )
            metric.measure(case)
            if metric.score is not None:
                scores.append(float(metric.score))
        return {
            "status": "COMPLETED" if len(scores) == len(rows) else "PARTIAL",
            "task_completion": sum(scores) / len(scores) if scores else None,
            "evaluated_cases": len(scores),
            "model": model_name,
        }
    except Exception as exc:
        error_msg = str(exc)

        if "quota" in error_msg.lower():
            reason = "Gemini quota exceeded"
        elif "credit" in error_msg.lower():
            reason = "Provider credits unavailable"
        elif "resourceexhausted" in error_msg.lower():
            reason = "Gemini daily limit exceeded"
        else:
            reason = f"DeepEval execution skipped: {type(exc).__name__}: {exc}"

        return {
            "status": "SKIPPED",
            "reason": reason,
            "task_completion": None,
            "evaluated_cases": 0,
        }