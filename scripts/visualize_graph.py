"""
Script to visualize the LangGraph workflow
"""
from graph.rag_graph import build_graph

def visualize_graph():
    """Generate and display the graph visualization"""
    compiled_graph = build_graph()
    
    # Get the graph as a Mermaid diagram
    try:
        # Try to generate PNG (requires graphviz)
        from IPython.display import Image, display
        png_data = compiled_graph.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("graph_visualization.png", "wb") as f:
            f.write(png_data)
        print("✅ Graph saved as 'graph_visualization.png'")
        
    except Exception as e:
        print(f"⚠️  Could not generate PNG: {e}")
        print("\n📊 Generating Mermaid diagram instead...\n")
        
        # Fallback to Mermaid text
        mermaid = compiled_graph.get_graph().draw_mermaid()
        
        # Save to file
        with open("graph_visualization.mmd", "w") as f:
            f.write(mermaid)
        
        print("✅ Mermaid diagram saved as 'graph_visualization.mmd'")
        print("\n📋 Mermaid Diagram:\n")
        print(mermaid)
        print("\n💡 You can visualize this at: https://mermaid.live")

if __name__ == "__main__":
    visualize_graph()
