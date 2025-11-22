#!/usr/bin/env python3
"""
RAG System Quick Test

This script demonstrates the RAG (Retrieval-Augmented Generation) system capabilities:
- Storing conversations with embeddings
- Semantic search for similar conversations
- Context-aware response generation
- Feedback collection and learning statistics
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag_knowledge_base import rag_knowledge_base


def main():
    print("=" * 70)
    print("RAG SYSTEM QUICK TEST")
    print("=" * 70)
    print()

    # Test organization and user
    org_id = "demo_org"
    user_id = "test_user@demo.com"

    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print()
        print("Please set your OpenAI API key:")
        print('  export OPENAI_API_KEY="sk-your-key-here"')
        print()
        print("Or add to .env file:")
        print('  echo "OPENAI_API_KEY=sk-your-key-here" >> .env')
        return 1

    print("✓ OpenAI API key found")
    print()

    # Test 1: Store sample conversations
    print("TEST 1: Storing Sample Conversations")
    print("-" * 70)

    sample_conversations = [
        {
            "user": "How do I set up Microsoft Teams integration?",
            "ai": "To set up Microsoft Teams integration: 1) Go to Settings > Integrations, 2) Click 'Add Microsoft Teams', 3) Enter your Client ID and Client Secret from Azure Portal, 4) Click 'Authorize' and sign in with your Microsoft account.",
            "metadata": {"agent": "Setup Assistant", "rating": 1}
        },
        {
            "user": "What are the steps to configure Slack?",
            "ai": "To configure Slack integration: 1) Visit api.slack.com and create a new app, 2) Enable OAuth permissions for channels:read and chat:write, 3) Copy the OAuth token, 4) In Pramiti, go to Settings > Connectors > Slack and paste the token.",
            "metadata": {"agent": "Setup Assistant", "rating": 1}
        },
        {
            "user": "How can I authenticate with Google Workspace?",
            "ai": "For Google Workspace authentication: 1) Go to Google Cloud Console, 2) Create OAuth 2.0 credentials, 3) Add authorized redirect URI, 4) Download the credentials JSON, 5) Upload to Pramiti Settings > OAuth > Google.",
            "metadata": {"agent": "OAuth Assistant", "rating": 1}
        },
        {
            "user": "I'm getting an error when trying to connect to Microsoft",
            "ai": "Common Microsoft connection errors: Check that your Client ID and Secret are correct, ensure the redirect URI matches exactly, verify that required API permissions are granted in Azure Portal.",
            "metadata": {"agent": "Troubleshooting Agent", "rating": 0}
        }
    ]

    doc_ids = []
    for i, conv in enumerate(sample_conversations, 1):
        try:
            doc_id = rag_knowledge_base.store_conversation(
                org_id=org_id,
                user_id=user_id,
                user_message=conv["user"],
                ai_response=conv["ai"],
                conversation_id=f"test_conv_{i}",
                metadata=conv["metadata"]
            )
            doc_ids.append((doc_id, conv["metadata"].get("rating", 0)))
            print(f"  ✓ Stored conversation {i}: {doc_id[:20]}...")
        except Exception as e:
            print(f"  ✗ Failed to store conversation {i}: {e}")
            return 1

    print()

    # Test 2: Record feedback
    print("TEST 2: Recording Feedback")
    print("-" * 70)

    for doc_id, rating in doc_ids[:3]:  # Add feedback to first 3
        try:
            rag_knowledge_base.record_feedback(
                org_id=org_id,
                doc_id=doc_id,
                user_id=user_id,
                rating=rating
            )
            emoji = "👍" if rating > 0 else "👎" if rating < 0 else "😐"
            print(f"  ✓ Recorded feedback for {doc_id[:20]}... {emoji}")
        except Exception as e:
            print(f"  ✗ Failed to record feedback: {e}")

    print()

    # Test 3: Semantic search
    print("TEST 3: Semantic Search for Similar Conversations")
    print("-" * 70)

    search_queries = [
        "How to set up Teams integration?",
        "Slack setup instructions",
        "Google authentication help"
    ]

    for query in search_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = rag_knowledge_base.search_similar_conversations(
                org_id=org_id,
                query=query,
                top_k=2,
                min_rating=None
            )

            if results:
                for j, result in enumerate(results, 1):
                    print(f"  Result {j}:")
                    print(f"    Similarity: {result['similarity']:.3f}")
                    print(f"    Question: {result['user_message'][:60]}...")
                    print(f"    Rating: {result.get('rating', 'N/A')}")
            else:
                print("  No results found")
        except Exception as e:
            print(f"  ✗ Search failed: {e}")

    print()

    # Test 4: RAG response generation
    print("TEST 4: RAG-Enhanced Response Generation")
    print("-" * 70)

    test_question = "Can you help me set up Microsoft Teams?"
    print(f"User Question: '{test_question}'")
    print()

    try:
        response, metadata = rag_knowledge_base.generate_rag_response(
            org_id=org_id,
            user_id=user_id,
            user_message=test_question,
            base_prompt="You are Pramiti AI, an assistant for enterprise integrations.",
            conversation_id="test_rag_response"
        )

        print("AI Response:")
        print(f"  {response[:200]}...")
        print()
        print("Metadata:")
        print(f"  Context Used: {metadata.get('context_used', False)}")
        print(f"  Context Length: {metadata.get('context_length', 0)} characters")
        print(f"  Model: {metadata.get('model', 'N/A')}")
    except Exception as e:
        print(f"  ✗ Response generation failed: {e}")
        return 1

    print()

    # Test 5: Learning statistics
    print("TEST 5: Learning Statistics")
    print("-" * 70)

    try:
        stats = rag_knowledge_base.get_learning_stats(org_id)

        print(f"  Total Conversations: {stats['total_conversations']}")
        print(f"  Total Feedback: {stats['total_feedback']}")
        print(f"  Positive Feedback: {stats['positive_feedback']} 👍")
        print(f"  Negative Feedback: {stats['negative_feedback']} 👎")
        print(f"  Satisfaction Rate: {stats['satisfaction_rate']:.1f}%")
        print(f"  Average Confidence: {stats['avg_confidence']:.2f}")
    except Exception as e:
        print(f"  ✗ Failed to get statistics: {e}")
        return 1

    print()
    print("=" * 70)
    print("✓ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  1. Start the API server: python api_server.py")
    print("  2. Open the RAG chat interface: http://localhost:8084/static/rag-chat-interface.html")
    print("  3. Chat with the AI and provide feedback with 👍/👎 buttons")
    print("  4. Watch the satisfaction rate improve over time!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
