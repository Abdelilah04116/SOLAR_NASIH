import streamlit as st
import requests
import json
from typing import Dict, Any, List
import time

# Configure page
st.set_page_config(
    page_title="RAG Multimodal System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def upload_files(files) -> Dict[str, Any]:
    """Upload files to the API."""
    try:
        files_data = []
        for file in files:
            files_data.append(('files', (file.name, file.getvalue(), file.type)))
        
        response = requests.post(f"{API_BASE_URL}/upload/files", files=files_data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def search_documents(query: str, method: str = "hybrid", top_k: int = 5, 
                    doc_type: str = None, generate_response: bool = True) -> Dict[str, Any]:
    """Search documents via API."""
    try:
        payload = {
            "query": query,
            "method": method,
            "top_k": top_k,
            "generate_response": generate_response
        }
        
        if doc_type and doc_type != "All":
            payload["doc_type"] = doc_type.lower()
        
        response = requests.post(f"{API_BASE_URL}/search/", json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main Streamlit application."""
    st.title("🔍 RAG Multimodal System")
    st.markdown("Search across text, images, audio, and video content")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'mp3', 'wav', 'mp4', 'avi', 'mov']
        )
        
        if uploaded_files:
            if st.button("📤 Upload Files"):
                with st.spinner("Uploading and processing files..."):
                    result = upload_files(uploaded_files)
                    
                    if "error" in result:
                        st.error(f"Upload failed: {result['error']}")
                    else:
                        st.success(f"Successfully uploaded {len(uploaded_files)} files!")
                        st.json(result)
        
        st.header("⚙️ Search Settings")
        
        search_method = st.selectbox(
            "Search Method",
            ["hybrid", "vector", "keyword"],
            help="Method for retrieving documents"
        )
        
        doc_type_filter = st.selectbox(
            "Document Type",
            ["All", "Text", "Image", "Audio", "Video"],
            help="Filter by document type"
        )
        
        top_k = st.slider(
            "Number of Results",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of results to return"
        )
        
        generate_response = st.checkbox(
            "Generate AI Response",
            value=True,
            help="Generate a comprehensive response using retrieved context"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Search")
        
        # Search input
        query = st.text_input(
            "Enter your search query:",
            placeholder="What would you like to search for?"
        )
        
        if st.button("🔍 Search", type="primary") and query:
            with st.spinner("Searching..."):
                start_time = time.time()
                
                results = search_documents(
                    query=query,
                    method=search_method,
                    top_k=top_k,
                    doc_type=doc_type_filter if doc_type_filter != "All" else None,
                    generate_response=generate_response
                )
                
                search_time = time.time() - start_time
                
                if "error" in results:
                    st.error(f"Search failed: {results['error']}")
                else:
                    # Display generated response
                    if generate_response and "generated_response" in results:
                        st.header("🤖 AI Response")
                        response_data = results["generated_response"]
                        st.write(response_data["response"])
                        
                        with st.expander("Response Details"):
                            st.json(response_data["metadata"])
                    
                    # Display search results
                    st.header(f"📄 Search Results ({results['total_results']} found in {search_time:.2f}s)")
                    
                    for i, result in enumerate(results["results"]):
                        with st.expander(f"Result {i+1} - Score: {result['score']:.3f}"):
                            # Document info
                            col_info, col_content = st.columns([1, 2])
                            
                            with col_info:
                                st.write("**Source:**", result.get("source", "Unknown"))
                                st.write("**Type:**", result["metadata"].get("doc_type", "Unknown"))
                                st.write("**Method:**", result.get("retrieval_method", "Unknown"))
                            
                            with col_content:
                                st.write("**Content:**")
                                st.write(result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"])
                                
                                # Show metadata
                                if st.checkbox(f"Show metadata {i+1}"):
                                    st.json(result["metadata"])
    
    with col2:
        st.header("📊 System Status")
        
        # Health check
        try:
            health_response = requests.get(f"{API_BASE_URL}/health/detailed")
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.success("✅ System Healthy")
                
                # Display system metrics
                if "system_metrics" in health_data:
                    metrics = health_data["system_metrics"]
                    
                    st.metric("CPU Usage", f"{metrics['cpu_percent']:.1f}%")
                    st.metric("Memory Usage", f"{metrics['memory']['percent']:.1f}%")
                    st.metric("Disk Usage", f"{metrics['disk']['percent']:.1f}%")
            else:
                st.error("❌ System Unhealthy")
                
        except Exception as e:
            st.error(f"❌ Cannot connect to API: {str(e)}")
        
        # Usage tips
        st.header("💡 Tips")
        st.markdown("""
        - **Upload diverse content**: Mix text, images, audio, and video for rich search
        - **Use specific queries**: Detailed questions get better results
        - **Try different methods**: Vector search for semantic similarity, keyword for exact matches
        - **Enable AI responses**: Get comprehensive answers synthesized from multiple sources
        """)

if __name__ == "__main__":
    main()
