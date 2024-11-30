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
        self.recommendations = [
            "training",
            "communication skill",
            "medical and epidemiological knowledge",
        ]
        self.forums = [
            "reddit.com",
            "facebook.com",
        ]
        self.base_topics = [
            "anti-vax",
            "vaccine reluctancy",
            "vaccine side effects",
            "microchips in vaccines",
            "vaccine hesitancy",
            "vaccination misinformation",
            "public perception of vaccines",
            "vaccination trends",
            "vaccine misinformation",
            "vaccination myths",
            "vaccine programs",
            "vaccine safety",
        ]
        self.perspectives = [
            "cultural",
            "religious",
            "medical",
            "socioeconomic",
            "educational",
            "political"
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
    
    def generate_query(self, topic=None, n=5):
        if topic is None:
            topic = random.choice(self.base_topics)
        else:
            topic = topic
        context = random.choices(self.context, k=n)
        perspective = random.choices(self.perspectives, k=n)
        demographic = random.choices(self.demographics, k=n)
        forum = random.choices(self.forums, k=n)
        
        query_templates = []
        for i in range(n):
            query_templates.append([
                f"site:{forum[i]} {topic}",
                f"site:{forum[i]} {demographic[i]} and {topic}",
                f"site:{forum[i]} {perspective[i]} view on {topic}",
                f"site:{forum[i]} {demographic[i]} view on {topic}",
                f"site:{forum[i]} {context[i]} and {topic}"
            ])
        
        return [q for qset in query_templates for q in qset]