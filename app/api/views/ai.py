import os
import re
import json
import chromadb
import traceback
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, List
from langchain_chroma import Chroma
from langchain.llms.base import LLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from flask import Blueprint, request, jsonify


load_dotenv()

ai_search_bp = Blueprint("ai_search", __name__, url_prefix="/ai_search")

chromadb_host = os.getenv("CHROMADB_HOST", "chroma")
ollama_api = os.getenv("OLLAMA_API", "http://ollama:11434/api/chat")
llm_model_name = os.getenv("LLM_MODEL_NAME", "mistral:7b-instruct")
client = chromadb.HttpClient(host=chromadb_host, port=8000)
chromadb_collections = "products"
top_results_n = 100


class OllamaLLM(LLM, BaseModel):

    """Custom Ollama LLM client to query the Ollama API with prompts."""

    model_name: str
    base_url: str

    @property
    def _llm_type(self) -> str:
        return "ollama"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        import requests

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(self.base_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        try:
            return data["message"]["content"] or data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return data.get("result", "")


def get_chroma_collection():

    """Retrieve or create the ChromaDB collection for products."""

    return client.get_or_create_collection(name=chromadb_collections)


product_prompt_template = """
You are a strict product search AI assistant.

You receive a user query and a list of product data.

Match products ONLY if the query is fully or partially present in the product's name or description with minor typos or synonyms, but DO NOT guess unrelated products or invent connections.

RULES - YOU MUST STRICTLY FOLLOW:
1. Output ONLY matching products that clearly relate to the query.
2. Do NOT output any products that do not match.
3. DO NOT add any explanations, comments, summaries, opinions, or any extra text.
4. DO NOT replace, omit, or modify any data fields.
5. Output EXACTLY in the following format (without any extra dots or punctuation inside fields):

Product #1: Name: <name>, Price: <price>, Description: <description>
Product #2: Name: <name>, Price: <price>, Description: <description>
... and so on for all matches.

If no products match, output exactly: No matching products.

Products data (do NOT modify any field; output exactly as provided):
{context}

User query:
{question}

Your reply:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=product_prompt_template,
)


def parse_and_filter_products(text: str, metadatas: List[dict]) -> str:

    """Parse LLM output and filter matching products with proper formatting."""

    product_pattern = re.compile(
        r"Product\s+#\d+:\s+Name:\s*(.+?),\s*Price:\s*(.+?),\s*Description:\s*(.+)"
    )
    matched = []
    price_map = {md["name"]: md.get("price", "Not specified") for md in metadatas}

    for line in text.splitlines():
        m = product_pattern.match(line.strip())
        if not m:
            continue
        name, _, description = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()

        description = re.sub(r"\s*\(.*?\)\s*", "", description).strip()

        price = price_map.get(name, "Not specified")
        price_str = f"{price} UAH" if isinstance(price, (int, float)) else str(price)

        matched.append((name, price_str, description))

    if not matched:
        return "No matching products."

    lines = []
    for i, (name, price, desc) in enumerate(matched, start=1):
        lines.append(f"Product #{i}: Name: {name}, Price: {price}, Description: {desc}")

    return "\n".join(lines)


@ai_search_bp.route("/search", methods=["POST"])
def search():

    """Handle product search requests by querying ChromaDB and the Ollama LLM."""

    try:
        data = request.json or {}
        user_query = data.get("query", "").strip()

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        collection = get_chroma_collection()
        if not collection.count():
            return jsonify({"error": "No products indexed"}), 500

        vectorstore = Chroma(client=client, collection_name=chromadb_collections)
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_results_n})
        llm = OllamaLLM(model_name=llm_model_name, base_url=ollama_api)

        docs = retriever.invoke(user_query)
        if not docs:
            return jsonify({"result": "No matching products."})

        context_str = "\n".join(
            f"Name: {doc.metadata.get('name')}, Price: {doc.metadata.get('price')} UAH, Description: {doc.metadata.get('description')}"
            for doc in docs
        )
        final_prompt = product_prompt_template.replace("{context}", context_str).replace("{question}", user_query)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )

        llm_response = qa_chain.invoke(user_query)
        answer_text = llm_response.get("result") if isinstance(llm_response, dict) else str(llm_response)

        corrected_answer = parse_and_filter_products(answer_text, [doc.metadata for doc in docs])

        return jsonify({"result": corrected_answer})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
