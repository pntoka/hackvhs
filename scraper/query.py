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
            "may be vaccine hesitant themselves"
        ]
        self.forums = [
            "vaccine confidence project",
            "reddit.com",
            "twitter",
            "X.com",
            "facebook",
            "meta",
            "mumsnet"
        ]
        self.base_topics = [
            "vaccine reluctance",
            "vaccine side effects",
            "vaccine low coverage",
            "vaccine microchips",
            "vaccine hesitancy",
            "vaccination misinformation",
            "public perception of vaccines",
            "vaccination trends",
            "community engagement in vaccination"
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
            "suburban communities"
        ]
    
    def generate_query(self):
        context = random.choice(self.context)
        topic = random.choice(self.base_topics)
        perspective = random.choice(self.perspectives)
        demographic = random.choice(self.demographics)
        forum = random.choice(self.forums)
        
        query_templates = [
            f"{topic} in {demographic} {forum}",
            f"how {context} affects {topic} {forum}",
            f"{perspective} on {topic} {forum}",
        ]
        return random.choice(query_templates)