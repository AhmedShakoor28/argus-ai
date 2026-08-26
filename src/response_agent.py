import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


class ResponseAgent:
    def __init__(self, knowledge_base_dir="data/knowledge_base"):
        self.api_key = os.getenv("GEMINI_API_KEY")

        # Load and split documents
        documents = []
        for filename in os.listdir(knowledge_base_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(knowledge_base_dir, filename)
                loader = TextLoader(filepath, encoding="utf-8")
                documents.extend(loader.load())

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        # Build embeddings + FAISS vector store
        embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=self.api_key
     )
        self.vectorstore = FAISS.from_documents(chunks, embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        # LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=self.api_key,
            temperature=0.3
        )

        # Prompt
        self.prompt = ChatPromptTemplate.from_template(
            """You are a disaster response advisor. Use the following retrieved
            protocol context to answer the question. If the context doesn't fully
            cover it, use your best judgment but stay grounded in the protocols.

            Context:
            {context}

            Question:
            {input}
            """
        )

        # Plain LCEL chain: prompt -> llm -> string output
        # (avoids langchain.chains / langchain_classic, which keep moving between versions)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_response(self, detection_report, verification_report):
        """
        Takes detection + verification reports, generates a recommended response.
        """
        detections = detection_report.get("detections", {})
        plausible = verification_report.get("plausible", True)
        reasons = verification_report.get("reasons", [])

        query = f"""
        A disaster detection system reported the following:
        Detections: {detections}
        Verification plausibility: {plausible}
        Verification notes: {reasons}

        Based on the disaster response protocols, provide:
        1. Immediate recommended actions (numbered list)
        2. Which response tier this likely warrants (local/provincial/national)
        3. Any key safety considerations

        Keep the response concise and actionable.
        """

        # Retrieve relevant chunks ourselves, then run the chain
        docs = self.retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in docs)

        answer = self.chain.invoke({"context": context, "input": query})

        return {
            "recommendation": answer,
            "sources": [doc.metadata.get("source", "unknown") for doc in docs]
        }


if __name__ == "__main__":
    agent = ResponseAgent()

    # Mock detection + verification for testing
    mock_detection = {
        "detections": {
            "fire": [{"class": "fire", "confidence": 0.82}],
            "landslide": {"class": "Non-Landslide", "confidence": 0.95}
        }
    }
    mock_verification = {
        "plausible": True,
        "reasons": ["High temperature and low humidity conditions detected"]
    }

    response = agent.generate_response(mock_detection, mock_verification)
    print("Response Agent Output:")
    print(response["recommendation"])
    print("\nSources used:", response["sources"])