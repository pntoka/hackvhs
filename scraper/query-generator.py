import random

class VaccineQueryGenerator:
    # TODO: add some keywords from the research
    def __init__(self):
        self.context = [
            "personal knowledge",
            "social media",
            "influence of peers",
            "past experiences",
            "family history",
            "perceived importance of vaccines",
            "access to vaccines",
            "access to healthcare",
            "concern of risk"
            "risk perception",
            "trust",
            "societal norms",
            "cults",
            "religious convictions",
            "morals",
            "trust in government"
        ]
        self.policies = [
            "vaccine programs",
            "promotion and communication",
            "safety evaluation and monitoring"
        ]
        self.recommendations = [
            "training",
            "communication skill",
            "medical and epidemiological knowledge",
        ]
        self.forums = [
            "vaccine confidence project",
            "reddit",
            "twitter",
            "facebook",
        ]
        self.base_topics = [
            "vaccine reluctancy",
            "vaccine side effects",
            "vaccine low coverage",
            "microchips in vaccines",
            "vaccine hesitancy",
            "vaccination misinformation",
            "public perception of vaccines",
            "vaccination trends",
            "community engagement in vaccination",
            "vaccine misinformation",
            "vaccination myths"
        ]
        self.perspectives = [
            "cultural barriers",
            "religious views",
            "medical concerns",
            "socioeconomic factors",
            "educational background"
        ]
        
        self.demographics = [
            "rural communities",
            "urban populations",
            "ethnic minorities",
            "young parents",
            "elderly population",
            "developed countries",
            "developing countries",
            "suburban communities",
            "low-income communities",
            "high-income communities",
            "middle-class communities",
            "highly educated individuals",
            "religious communities",
        ]
    
    def generate_query(self, topic=None):
        # TODO: make some combos from the above
        if topic is None:
            topic = random.choice(self.base_topics)
        else:
            topic = topic
        perspective = random.choice(self.perspectives)
        demographic = random.choice(self.demographics)
        forum = random.choice(self.forums)
        policy = random.choice(self.policies)
        recommendation = random.choice(self.recommendations)
        
        query_templates = [
            f"{topic} in {demographic}",
            f"impact of {perspective} on {topic}",
            f"{demographic} attitudes towards vaccination",
            f"{perspective} affecting {demographic} vaccination rates",
            f"{forum} discussions on {topic}",
            f"impact of {policy} in addressing {topic}",
            f"{recommendation} for addressing {topic}",
        ]
        
        return query_templates
    
    # TODO: incorporate query-generator into tavily search client in main.py