import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import networkx as nx
import ast
import webbrowser


def process_data(json_file='sentiment_data.json', k=25):
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    df = pd.DataFrame.from_dict(json_data, orient='index')
    df = df.drop(columns = 'content')
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    text_features = df['title'].tolist()
    embeddings = model.encode(text_features, show_progress_bar=True)
    normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1)[:, np.newaxis]
    kmeans = KMeans(n_clusters=k, random_state=42)
    df['cluster'] = kmeans.fit_predict(normalized_embeddings)
    df['embeddings'] = embeddings.tolist()
    sid = SentimentIntensityAnalyzer()
    df['negative'] = df['title'].apply(lambda x: sid.polarity_scores(x)['neg'])
    df['neutral'] = df['title'].apply(lambda x: sid.polarity_scores(x)['neu'])
    df['positive'] = df['title'].apply(lambda x: sid.polarity_scores(x)['pos'])
    df['sentiment_compound'] = df['title'].apply(lambda x: sid.polarity_scores(x)['compound'])
    return df

def plot_bubble(df):
    G = nx.Graph()
    clusters = df['cluster'].unique()

    # Add nodes with cluster sizes
    for cluster in clusters:
        cluster_size = len(df[df['cluster'] == cluster])
        titles = df[df['cluster'] == cluster]['title'].tolist()
        G.add_node(f'Cluster {cluster}', 
                  size=cluster_size*1.5,
                  color=px.colors.qualitative.Light24[int(cluster) % 24],
                  titles=titles)

    # Calculate packed bubble layout
    pos = {}
    nodes_by_size = sorted(G.nodes(data=True), key=lambda x: x[1]['size'], reverse=True)

    # Initialize with largest bubble in center
    center_node = nodes_by_size[0][0]
    pos[center_node] = (0, 0)

    # Place remaining bubbles in a spiral pattern around center
    angle = 0
    radius = 0.2
    spiral_constant = 0.2

    for i, (node, data) in enumerate(nodes_by_size[1:], 1):
        # Calculate spiral position
        angle += 2.4  # Golden angle in radians
        radius += spiral_constant / (i + 1)  # Gradually increase radius
        
        # Convert polar to cartesian coordinates
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        # Add some random jitter to make it look more natural
        jitter_x = np.random.normal(-1, 0.5) if i%2 == 0 else np.random.normal(1, 0.5)
        jitter_y = np.random.uniform(-0.25, 0.25)
        
        pos[node] = (x + jitter_x, y + jitter_y)
    
    # Create visualization
    fig_network = go.Figure()

    # Add nodes
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    hover_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_size.append(G.nodes[node]['size'])
        node_color.append(G.nodes[node]['color'])
        titles = '<br>'.join(G.nodes[node]['titles'][:10])
        hover_text.append(f"{node}<br>{titles}")

    fig_network.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        hoverinfo='text',
        text=hover_text,
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white'),
            opacity=0.7
        )
    ))

    # Update layout
    fig_network.update_layout(
        showlegend=False,
        hovermode='closest',
        height=1000,  # Increase height for better spacing
        width=800,
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-3, 3]  # Control horizontal spread
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-1, 1]  # Adjust vertical range
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    # Add hover effects
    fig_network.update_traces(
        hovertemplate='%{text}',
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    return fig_network


if __name__ == '__main__':
    np.random.seed(20)

    # df = process_data()
    # df.to_csv('sentiment_tag.csv')

    # Set page configuration
    st.set_page_config(layout="wide", page_title="Text Analysis Dashboard")

    # Function to load and process data
    @st.cache_data
    def load_data():
        # Replace with your actual data loading method
        df = pd.read_csv('sentiment_tag.csv')
        df['embeddings'] = df['embeddings'].apply(ast.literal_eval)
        return df
    
    # Load data
    df = load_data()

    # Title
    st.title("Vax Vibes")

    # Cluster Network and Topic Distribution
    # Cluster Network
    st.subheader("Topic Clusters")

    bubbles = plot_bubble(df)
    st.plotly_chart(bubbles, use_container_width=True)

    st.subheader("Hot Topics")
    col1, col2 = st.columns([1,5])
    cluster = col1.selectbox("Choose your cluster", sorted(df['cluster'].unique()))
    sub = df[df['cluster']==cluster].sort_values(['neutral'])
    # Sentiment Distribution
    sentiment_data = pd.DataFrame({
        'Sentiment': ['Negative', 'Positive'],
        'Value': [
            sub['negative'].mean(),
            sub['positive'].mean()
        ]
    })
    
    fig_sentiment = px.pie(
        sentiment_data,
        values='Value',
        names='Sentiment',
        hole=0.6,
        color_discrete_sequence=px.colors.qualitative.G10
    )
    col2.plotly_chart(fig_sentiment, use_container_width=True)

    count, top = 0, 10
    # Format each post as a card
    for _, row in sub.iterrows():
        count += 1
        if count < top:
            a, b = st.columns([1,1])
            col = a if count < top/2 else b
            col.write(row['title'], unsafe_allow_html=True)
            if col.button("Read More", key=row['url']):
                webbrowser.open_new_tab(row['url'])
    
    st.subheader(f"Tell Me More")
    st.write(sub[['title','url','negative','positive','neutral']], use_container_width=True)