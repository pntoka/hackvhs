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

def load_tweet_data():
    df = pd.read_csv('covid-19_tweets.csv')
    return df

def get_similar_tweets(user_input, df, n=5):
    vectorizer = TfidfVectorizer(stop_words='english')
    all_text = list(df['tweet_text']) + [user_input]
    tfidf_matrix = vectorizer.fit_transform(all_text)
    similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
    top_indices = similarities.argsort()[-n:][::-1]
    return df.iloc[top_indices]

def display_tweet(tweet_text, sentiment, i):
    quote_colors = {
        2: "🔴", # Negative
        3: "⚪", # Neutral
        1: "🟢"  # Positive
    }
    col1, col2 = st.columns([5,1])
    
    with col1:
        st.markdown(f"""
    <div style='padding: 20px; 
                border-radius: 15px; 
                background-color: rgba(255,255,255,0.05); 
                margin: 15px 0;
                border-left: 4px solid #1DA1F2;'>
        <div style='font-family: Georgia, serif; 
                    font-size: 1.1em; 
                    font-style: italic;'>
            "{tweet_text}"
        </div>
        <div style='text-align: left; 
                    color: #888; 
                    margin-top: 10px;'>
            {quote_colors.get(sentiment, "⚪")} Tweet Sentiment
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with col2:
        # Add thumbs up/down buttons vertically
        col2.write("\n")
        col2.button("👍", key=f"like_{i}", help="I can relate")
        col2.button("👎", key=f"dislike_{i}", help="Not what I was thinking")

def create_quadrant_chart(df):
    # Create the scatter plot
    fig = px.scatter(
        df,
        x='Passive-to-Proactive',
        y='Skeptic-to-Pro',
        text='Name',
        labels={
            'Skeptic-to-Pro': 'Skeptical          →          Pro',
            'Passive-to-Proactive': 'Passive          →          Proactive'
        },
        title='Touch Points'
    )

    # Add arrows
    for i in range(len(df)-1):
        fig.add_annotation(
            x=df.iloc[len(df)-1-i]['Passive-to-Proactive'],
            y=df.iloc[len(df)-1-i]['Skeptic-to-Pro'],
            xref="x",
            yref="y",
            ax=df.iloc[len(df)-2-i]['Passive-to-Proactive'],
            ay=df.iloc[len(df)-2-i]['Skeptic-to-Pro'],
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#90D5FF"
        )
    
    # Add quadrant lines
    fig.add_shape(
        type='line',
        x0=0.5, y0=0, x1=0.5, y1=1,
        line=dict(color='LightGray')
    )
    fig.add_shape(
        type='line',
        x0=0, y0=0.5, x1=1, y1=0.5,
        line=dict(color='LightGray')
    )
    
    # Customize layout
    fig.update_traces(
        textposition='top center',
        marker=dict(size=12)
    )
    fig.update_layout(
        showlegend=False,
        height=600,
        width=600,
        plot_bgcolor='white',
        xaxis={'visible': False},  # Completely hide x-axis
        yaxis={'visible': False}   # Completely hide y-axis
    )
    fig.add_annotation(x=1, y=0.5, text='Pro', showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0, y=0.5, text='Skeptical', showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0.5, y=1, text='Proactive', showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0.5, y=0, text='Passive', showarrow=False, font=dict(size=14))
    return fig

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