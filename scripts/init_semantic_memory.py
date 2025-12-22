"""
Initialization script for Semantic Memory System

Run this script once to:
1. Create the Qdrant memory collection
2. Verify the setup
3. Optionally seed with initial memories
"""

import sys
sys.path.insert(0, '.')

from memory.semantic_memory import (
    create_memory_collection,
    store_memory,
    retrieve_memories,
    get_memory_stats,
    store_preference_memory,
    store_pattern_memory
)


def initialize_memory_system():
    """Initialize the semantic memory system"""
    print("🚀 Initializing Semantic Memory System...")
    print()
    
    # Step 1: Create collection
    print("📦 Step 1: Creating memory collection...")
    try:
        create_memory_collection()
        print("✅ Memory collection created successfully!")
    except Exception as e:
        print(f"❌ Failed to create collection: {e}")
        return False
    
    print()
    
    # Step 2: Verify collection
    print("🔍 Step 2: Verifying collection...")
    try:
        stats = get_memory_stats()
        if "error" in stats:
            print(f"❌ Collection verification failed: {stats['error']}")
            return False
        
        print(f"✅ Collection verified!")
        print(f"   - Total memories: {stats['total_memories']}")
        print(f"   - Vector size: {stats['vector_size']}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    print()
    
    # Step 3: Seed initial memories (optional)
    print("🌱 Step 3: Seeding initial memories...")
    try:
        seed_initial_memories()
        print("✅ Initial memories seeded!")
    except Exception as e:
        print(f"⚠️  Warning: Could not seed memories: {e}")
    
    print()
    print("=" * 60)
    print("✨ Semantic Memory System is ready!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("1. Run your Streamlit app: streamlit run app.py")
    print("2. Ask questions and interact with the system")
    print("3. Memories will be automatically stored after each interaction")
    print("4. View memories in the sidebar 'Semantic Memory' section")
    print()
    
    return True


def seed_initial_memories():
    """Seed some initial domain knowledge and patterns"""
    
    # Domain knowledge about the database
    store_memory(
        content="The database contains three main tables: cars, customers, and sales. "
                "The cars table has 500 records across 7 brands: Toyota, BMW, Mercedes, "
                "Nissan, Tesla, Kia, and Hyundai. Price range is $15,000 to $100,000.",
        memory_type="fact",
        metadata={
            "category": "database_schema",
            "tables": ["cars", "customers", "sales"],
            "brands": ["Toyota", "BMW", "Mercedes", "Nissan", "Tesla", "Kia", "Hyundai"]
        }
    )
    
    # SQL pattern
    store_pattern_memory(
        pattern_description="For brand comparison queries, use GROUP BY brand with appropriate aggregation",
        pattern_type="sql_pattern",
        example="SELECT brand, AVG(price) FROM cars GROUP BY brand ORDER BY AVG(price) DESC",
        metadata={
            "use_case": "brand_comparison",
            "tables": ["cars"]
        }
    )
    
    # Visualization preference
    store_preference_memory(
        preference="Bar charts work well for comparing values across categories like brands or models",
        category="visualization",
        metadata={
            "chart_type": "bar",
            "use_case": "categorical_comparison"
        }
    )
    
    print("   ✓ Seeded 3 initial memories (domain knowledge, SQL pattern, visualization preference)")


def test_memory_retrieval():
    """Test memory retrieval"""
    print("🧪 Testing memory retrieval...")
    print()
    
    # Test query
    test_query = "What brands are in the database?"
    print(f"Query: '{test_query}'")
    print()
    
    memories = retrieve_memories(
        query=test_query,
        top_k=3,
        min_score=0.5
    )
    
    if memories:
        print(f"✅ Found {len(memories)} relevant memories:")
        for i, mem in enumerate(memories, 1):
            print(f"\n{i}. [{mem['memory_type']}] (score: {mem['score']:.3f})")
            print(f"   {mem['content'][:150]}...")
    else:
        print("⚠️  No memories found (this is normal if database is empty)")


if __name__ == "__main__":
    success = initialize_memory_system()
    
    if success:
        # Optional: Run a test
        print()
        response = input("Would you like to test memory retrieval? (y/n): ")
        if response.lower() == 'y':
            print()
            test_memory_retrieval()
