import sys
sys.path.insert(0, ".")
from backend.core.rag.rag_chain import load_document, ask

stored = load_document("data/uploads/test.pdf")
print()

questions = [
    "What is the purpose of point and figure charts?",
    "What chart patterns are discussed in this book?"
]

for question in questions:
    print("=" * 50)
    print("QUESTION: " + question)
    print()
    result = ask(question)
    print("ANSWER:")
    print(result["answer"])
    print()
    if result["citations"]:
        print("CITATIONS:")
        for c in result["citations"]:
            print("  Page " + str(c["page_number"]) + " | Similarity: " + str(c["similarity"]))
    print()
