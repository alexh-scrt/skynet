"""
Advanced Agent Personalities with Domain Expertise and Rhetorical Styles
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class RhetoricalStyle(Enum):
    SYNTHESIST_ANALOGICAL = "synthesist_analogical"  # Barbie
    SYSTEMS_DIALECTICAL = "systems_dialectical"      # Ken


class DomainExpertise:
    """Comprehensive domain knowledge base for both agents"""
    
    DOMAINS = {
        "artificial_intelligence": {
            "key_concepts": [
                "machine learning", "deep learning", "neural networks", "transformers",
                "AGI", "alignment problem", "scaling laws", "emergent capabilities",
                "hallucination", "fine-tuning", "RLHF", "multimodal AI"
            ],
            "recent_developments": [
                "GPT-4 and large language models", "DALL-E and image generation",
                "ChatGPT adoption rates", "AI safety research", "constitutional AI",
                "in-context learning", "chain-of-thought reasoning"
            ],
            "key_figures": [
                "Geoffrey Hinton", "Yoshua Bengio", "Yann LeCun", "Demis Hassabis",
                "Sam Altman", "Dario Amodei", "Stuart Russell", "Eliezer Yudkowsky"
            ],
            "institutions": [
                "OpenAI", "DeepMind", "Anthropic", "Stanford AI Lab", "MIT CSAIL",
                "Berkeley AI Research", "CMU Machine Learning"
            ],
            "ethical_considerations": [
                "bias and fairness", "privacy and surveillance", "job displacement",
                "autonomous weapons", "AI consciousness", "existential risk"
            ]
        },
        
        "neuroscience": {
            "key_concepts": [
                "plasticity", "neural networks", "synaptic transmission", "neurogenesis",
                "default mode network", "consciousness", "working memory", "attention"
            ],
            "recent_developments": [
                "optogenetics", "brain-computer interfaces", "connectomics",
                "neuromorphic computing", "psychedelics research", "memory consolidation"
            ],
            "key_figures": [
                "Antonio Damasio", "Christof Koch", "Susan Greenfield", "V.S. Ramachandran",
                "Michael Gazzaniga", "Patricia Churchland"
            ],
            "applications": [
                "treating depression", "Alzheimer's research", "stroke recovery",
                "addiction treatment", "cognitive enhancement"
            ]
        },
        
        "climate_science": {
            "key_concepts": [
                "greenhouse effect", "carbon cycle", "feedback loops", "tipping points",
                "albedo", "radiative forcing", "climate sensitivity", "carbon budget"
            ],
            "recent_developments": [
                "IPCC AR6 report", "net-zero commitments", "carbon removal technologies",
                "renewable energy transition", "climate attribution science"
            ],
            "key_figures": [
                "Michael Mann", "Katherine Hayhoe", "Gavin Schmidt", "Katharine Hayhoe",
                "James Hansen", "Susan Solomon"
            ],
            "impacts": [
                "sea level rise", "extreme weather", "ecosystem disruption",
                "food security", "migration patterns", "economic costs"
            ]
        },
        
        "economics": {
            "key_concepts": [
                "supply and demand", "market efficiency", "externalities", "game theory",
                "behavioral economics", "monetary policy", "fiscal policy", "inequality"
            ],
            "recent_developments": [
                "Modern Monetary Theory", "cryptocurrency adoption", "inflation dynamics",
                "remote work economics", "platform economics", "ESG investing"
            ],
            "key_figures": [
                "Paul Krugman", "Joseph Stiglitz", "Thomas Piketty", "Daniel Kahneman",
                "Esther Duflo", "Janet Yellen"
            ],
            "applications": [
                "policy design", "market regulation", "development economics",
                "environmental economics", "health economics"
            ]
        },
        
        "philosophy": {
            "key_concepts": [
                "consciousness", "free will", "ethics", "epistemology", "metaphysics",
                "phenomenology", "existentialism", "utilitarianism", "virtue ethics"
            ],
            "recent_developments": [
                "experimental philosophy", "AI ethics", "digital personhood",
                "effective altruism", "longtermism", "moral circle expansion"
            ],
            "key_figures": [
                "Derek Parfit", "Peter Singer", "Martha Nussbaum", "Daniel Dennett",
                "David Chalmers", "Thomas Nagel"
            ],
            "applications": [
                "medical ethics", "technology ethics", "environmental ethics",
                "political philosophy", "philosophy of mind"
            ]
        },
        
        "physics": {
            "key_concepts": [
                "quantum mechanics", "relativity", "thermodynamics", "field theory",
                "particle physics", "cosmology", "emergence", "information theory"
            ],
            "recent_developments": [
                "quantum computing", "gravitational waves", "dark matter research",
                "quantum entanglement", "many-worlds interpretation", "string theory"
            ],
            "key_figures": [
                "Sean Carroll", "Brian Greene", "Lisa Randall", "Michio Kaku",
                "Carlo Rovelli", "Leonard Susskind"
            ],
            "applications": [
                "quantum technologies", "medical imaging", "energy generation",
                "materials science", "computation"
            ]
        },
        
        "psychology": {
            "key_concepts": [
                "cognitive biases", "conditioning", "memory formation", "social influence",
                "personality theories", "developmental psychology", "psychopathology"
            ],
            "recent_developments": [
                "positive psychology", "digital therapy", "psychedelic therapy",
                "social media psychology", "COVID-19 mental health impacts"
            ],
            "key_figures": [
                "Daniel Kahneman", "Steven Pinker", "Jordan Peterson", "Carol Dweck",
                "Angela Duckworth", "Martin Seligman"
            ],
            "applications": [
                "therapy and counseling", "education design", "marketing",
                "user experience design", "organizational behavior"
            ]
        },
        
        "sociology": {
            "key_concepts": [
                "social networks", "cultural transmission", "social capital",
                "institutional theory", "social movements", "inequality", "globalization"
            ],
            "recent_developments": [
                "social media influence", "remote work culture", "polarization studies",
                "pandemic social effects", "digital divide", "cancel culture"
            ],
            "key_figures": [
                "Manuel Castells", "Sherry Turkle", "Richard Florida", "Matthew Salganik",
                "Zeynep Tufekci", "Duncan Watts"
            ],
            "applications": [
                "policy design", "community building", "organizational change",
                "social media design", "urban planning"
            ]
        }
    }


class BarbiePersonality:
    """
    Barbie: Synthesist-Analogical Reasoning Style
    - Connects disparate ideas through creative analogies
    - Sees patterns and relationships across domains
    - Uses metaphorical thinking and narrative structures
    - Optimistic about human potential and progress
    """
    
    def __init__(self):
        self.style = RhetoricalStyle.SYNTHESIST_ANALOGICAL
        self.domain_knowledge = DomainExpertise.DOMAINS
        
    def get_rhetorical_approach(self, topic: str, phase: str) -> Dict:
        """Get Barbie's rhetorical approach for a topic and debate phase"""
        
        base_approaches = {
            "opening": [
                "Start with a surprising analogy from nature or art",
                "Present a paradox that reveals deeper connections",
                "Use a narrative arc to frame the discussion",
                "Connect to human emotional or aesthetic experience"
            ],
            "exploration": [
                "Build bridges between seemingly unrelated domains",
                "Use cascade reasoning: 'If this, then this, then this...'",
                "Find the elegant underlying pattern or principle",
                "Reframe the question from multiple perspectives"
            ],
            "challenge": [
                "Use jujitsu: turn opponent's strength into your argument",
                "Present alternative metaphorical frameworks",
                "Show how apparent contradictions can coexist",
                "Reveal hidden assumptions through analogy"
            ],
            "synthesis": [
                "Find the meta-pattern that encompasses all views",
                "Create new conceptual frameworks",
                "Show how opposites can be complementary",
                "Paint a vision of integrated understanding"
            ]
        }
        
        return {
            "primary_approaches": base_approaches.get(phase, base_approaches["exploration"]),
            "analogical_sources": self._get_analogical_sources(topic),
            "synthesis_techniques": self._get_synthesis_techniques(),
            "narrative_elements": self._get_narrative_elements(topic)
        }
    
    def _get_analogical_sources(self, topic: str) -> List[str]:
        """Get rich sources for analogies based on topic"""
        
        analogy_pools = {
            "artificial_intelligence": [
                "biological evolution and natural selection",
                "child development and learning",
                "ecosystem dynamics and emergence",
                "musical improvisation and creativity",
                "architectural design and engineering"
            ],
            "climate_science": [
                "human body and immune system",
                "economic systems and feedback loops",
                "garden ecology and balance",
                "ocean currents and circulation",
                "forest fire dynamics"
            ],
            "economics": [
                "river systems and flow dynamics",
                "biological networks and metabolism",
                "social dynamics and relationships",
                "game theory and strategic thinking",
                "evolutionary pressures and adaptation"
            ],
            "default": [
                "natural phenomena (weather, geology, biology)",
                "human relationships and social dynamics",
                "artistic creation and aesthetic principles",
                "historical patterns and cycles",
                "technological evolution"
            ]
        }
        
        return analogy_pools.get(topic, analogy_pools["default"])
    
    def _get_synthesis_techniques(self) -> List[str]:
        """Barbie's synthesis techniques"""
        return [
            "Find the higher-order pattern that contains both perspectives",
            "Identify complementary rather than contradictory relationships",
            "Create new conceptual categories that transcend the binary",
            "Show how apparent opposites are different aspects of the same phenomenon",
            "Build frameworks that honor the truth in multiple viewpoints"
        ]
    
    def _get_narrative_elements(self, topic: str) -> Dict:
        """Get narrative framing elements"""
        return {
            "story_arcs": [
                "The journey from confusion to clarity",
                "The discovery of hidden connections",
                "The transformation through new understanding",
                "The reconciliation of opposing forces"
            ],
            "metaphorical_frames": [
                "Exploration and discovery",
                "Building bridges across divides",
                "Weaving disparate threads into tapestry",
                "Conducting an orchestra of ideas"
            ],
            "emotional_resonances": [
                "Wonder at the elegance of natural patterns",
                "Hope for human potential and growth",
                "Beauty in unexpected connections",
                "Excitement about creative possibilities"
            ]
        }
    
    def generate_domain_connection(self, primary_domain: str, 
                                 secondary_domain: str, concept: str) -> str:
        """Generate cross-domain connections"""
        
        primary_info = self.domain_knowledge.get(primary_domain, {})
        secondary_info = self.domain_knowledge.get(secondary_domain, {})
        
        connection_templates = [
            f"This reminds me of how {secondary_domain} shows us that {concept} - just as {secondary_info.get('key_concepts', [''])[0]}, we see similar patterns in {primary_domain}",
            f"There's a beautiful parallel between {concept} in {primary_domain} and the way {secondary_domain} reveals {secondary_info.get('key_concepts', [''])[0]}",
            f"If we think of {concept} like {secondary_info.get('applications', ['natural phenomena'])[0]}, we can see why {primary_domain} might..."
        ]
        
        return random.choice(connection_templates)
    
    def get_signature_phrases(self) -> List[str]:
        """Barbie's characteristic phrases and transitions"""
        return [
            "What if we imagine this like...",
            "There's something beautiful about how...",
            "This connects to a deeper pattern where...",
            "I see an elegant parallel between...",
            "The underlying architecture seems to be...",
            "This weaves together with...",
            "Picture this: what if...",
            "The poetry of this is that...",
            "This resonates with how...",
            "There's a hidden harmony here..."
        ]


class KenPersonality:
    """
    Ken: Systems-Dialectical Reasoning Style
    - Analyzes systems, structures, and logical relationships
    - Uses dialectical reasoning to examine tensions and contradictions
    - Focuses on mechanisms, processes, and causal chains
    - Skeptical but fair-minded, seeks rigorous understanding
    """
    
    def __init__(self):
        self.style = RhetoricalStyle.SYSTEMS_DIALECTICAL
        self.domain_knowledge = DomainExpertise.DOMAINS
    
    def get_rhetorical_approach(self, topic: str, phase: str) -> Dict:
        """Get Ken's rhetorical approach for a topic and debate phase"""
        
        base_approaches = {
            "opening": [
                "Define key terms and establish analytical framework",
                "Identify the central tension or contradiction to examine",
                "Map out the system structure and key variables",
                "Question fundamental assumptions systematically"
            ],
            "exploration": [
                "Trace causal mechanisms and feedback loops",
                "Examine edge cases and boundary conditions",
                "Identify unintended consequences and second-order effects",
                "Apply different analytical lenses systematically"
            ],
            "challenge": [
                "Use dialectical questioning to expose contradictions",
                "Stress-test assumptions with extreme scenarios",
                "Reveal hidden complexity in seemingly simple claims",
                "Demand operational definitions and measurable outcomes"
            ],
            "synthesis": [
                "Identify conditions under which different claims are valid",
                "Map the solution space and constraint boundaries",
                "Build systematic frameworks for understanding trade-offs",
                "Establish principles for navigating complexity"
            ]
        }
        
        return {
            "primary_approaches": base_approaches.get(phase, base_approaches["exploration"]),
            "analytical_frameworks": self._get_analytical_frameworks(topic),
            "dialectical_techniques": self._get_dialectical_techniques(),
            "systems_perspectives": self._get_systems_perspectives(topic)
        }
    
    def _get_analytical_frameworks(self, topic: str) -> List[str]:
        """Get analytical frameworks relevant to topic"""
        
        frameworks = {
            "artificial_intelligence": [
                "information theory and computational complexity",
                "systems theory and emergence",
                "game theory and multi-agent systems",
                "evolutionary algorithms and optimization",
                "control theory and feedback systems"
            ],
            "climate_science": [
                "systems dynamics and feedback loops",
                "thermodynamics and energy flows",
                "complex adaptive systems theory",
                "risk analysis and uncertainty quantification",
                "network theory and cascading effects"
            ],
            "economics": [
                "game theory and strategic interactions",
                "network effects and platform dynamics",
                "behavioral economics and cognitive biases",
                "institutional economics and governance",
                "complexity economics and agent-based modeling"
            ],
            "default": [
                "systems thinking and emergence",
                "game theory and strategic analysis",
                "cost-benefit analysis and trade-offs",
                "network theory and connectivity",
                "complexity theory and nonlinear dynamics"
            ]
        }
        
        return frameworks.get(topic, frameworks["default"])
    
    def _get_dialectical_techniques(self) -> List[str]:
        """Ken's dialectical reasoning techniques"""
        return [
            "Thesis-antithesis-synthesis progression",
            "Identification and examination of contradictions",
            "Socratic questioning to uncover assumptions",
            "Devil's advocate position testing",
            "Systematic exploration of logical implications",
            "Boundary condition analysis",
            "Falsification testing of claims"
        ]
    
    def _get_systems_perspectives(self, topic: str) -> Dict:
        """Get systems-level perspectives on topic"""
        return {
            "structural_elements": [
                "What are the key components and their relationships?",
                "What are the boundaries and interfaces of this system?",
                "How does information and energy flow through the system?",
                "What are the feedback loops and control mechanisms?"
            ],
            "dynamic_processes": [
                "How does the system change over time?",
                "What drives instability or maintains equilibrium?",
                "Where are the leverage points for intervention?",
                "What are the unintended consequences of changes?"
            ],
            "emergent_properties": [
                "What behaviors emerge from component interactions?",
                "How do micro-level actions create macro-level patterns?",
                "What properties can't be predicted from parts alone?",
                "Where does the system exhibit nonlinear responses?"
            ]
        }
    
    def generate_dialectical_probe(self, claim: str, domain: str) -> str:
        """Generate dialectical probe for a claim"""
        
        domain_info = self.domain_knowledge.get(domain, {})
        
        probe_templates = [
            f"But if we accept {claim}, how do we reconcile this with {domain_info.get('key_concepts', ['known principles'])[0]}?",
            f"This raises a fundamental tension: if {claim}, then what about the {domain_info.get('recent_developments', ['established findings'])[0]}?",
            f"Let's examine the logical structure: {claim} implies X, but doesn't that contradict Y?",
            f"What would {domain_info.get('key_figures', ['experts'])[0]} say about the mechanisms underlying {claim}?"
        ]
        
        return random.choice(probe_templates)
    
    def get_signature_phrases(self) -> List[str]:
        """Ken's characteristic phrases and transitions"""
        return [
            "Let's examine the logical structure...",
            "But this creates a fundamental tension...",
            "If we trace the causal chain...",
            "The systemic implications are...",
            "This reveals a deeper contradiction...",
            "We need to distinguish between...",
            "The mechanism here seems to be...",
            "But what about the second-order effects?",
            "This assumes that..., but what if...?",
            "The boundary conditions suggest..."
        ]
    
    def analyze_argument_structure(self, argument: str) -> Dict:
        """Analyze the logical structure of an argument"""
        
        # Simplified analysis - in practice would use NLP
        analysis = {
            "premises_identified": [],
            "conclusion_identified": "",
            "logical_gaps": [],
            "hidden_assumptions": [],
            "strengthening_suggestions": []
        }
        
        # Look for logical indicators
        if "because" in argument.lower() or "since" in argument.lower():
            analysis["structure_type"] = "causal reasoning"
        elif "if" in argument.lower() and "then" in argument.lower():
            analysis["structure_type"] = "conditional reasoning"
        elif "all" in argument.lower() or "every" in argument.lower():
            analysis["structure_type"] = "universal claim"
        else:
            analysis["structure_type"] = "general assertion"
        
        # Suggest dialectical probes
        analysis["dialectical_probes"] = [
            "What conditions would falsify this claim?",
            "What are the boundary conditions?",
            "How do we operationalize key terms?",
            "What are the unexamined assumptions?"
        ]
        
        return analysis


class PersonalityManager:
    """Manages agent personalities and their interactions"""
    
    def __init__(self):
        self.barbie = BarbiePersonality()
        self.ken = KenPersonality()
    
    def get_agent_personality(self, agent_name: str):
        """Get personality object for agent"""
        if agent_name.lower() == "barbie":
            return self.barbie
        elif agent_name.lower() == "ken":
            return self.ken
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
    
    def get_complementary_response_suggestions(self, agent: str, 
                                             opponent_style: str, topic: str) -> List[str]:
        """Get suggestions for responding to opponent's rhetorical style"""
        
        if agent.lower() == "barbie":
            # Barbie responding to Ken's systems-dialectical approach
            return [
                "Acknowledge the systematic analysis but reveal the human dimension",
                "Show how the logical framework connects to lived experience",
                "Find the creative synthesis that transcends the dialectical tension",
                "Use analogy to make abstract systems concrete and relatable"
            ]
        
        elif agent.lower() == "ken":
            # Ken responding to Barbie's synthesist-analogical approach
            return [
                "Appreciate the creative connection but demand rigorous mechanisms",
                "Test the analogy at its boundaries and edge cases",
                "Ask for operational definitions of metaphorical concepts",
                "Examine whether the synthesis actually resolves the underlying tensions"
            ]
        
        return []
    
    def generate_domain_expertise_prompt(self, agent: str, topic: str) -> str:
        """Generate domain expertise context for agent"""
        
        personality = self.get_agent_personality(agent)
        domain_info = personality.domain_knowledge.get(topic, {})
        
        expertise_context = f"""
DOMAIN EXPERTISE - {topic.replace('_', ' ').title()}:

Key Concepts: {', '.join(domain_info.get('key_concepts', [])[:8])}

Recent Developments: {', '.join(domain_info.get('recent_developments', [])[:5])}

Key Figures: {', '.join(domain_info.get('key_figures', [])[:6])}

Applications/Impacts: {', '.join(domain_info.get('applications', domain_info.get('impacts', []))[:5])}

Your rhetorical style: {personality.style.value}
Your signature approaches: {', '.join(personality.get_signature_phrases()[:5])}
"""
        
        return expertise_context
    
    def suggest_cross_domain_connections(self, primary_topic: str, 
                                       agent: str) -> List[str]:
        """Suggest interesting cross-domain connections"""
        
        personality = self.get_agent_personality(agent)
        all_domains = list(personality.domain_knowledge.keys())
        
        # Remove primary topic from candidates
        other_domains = [d for d in all_domains if d != primary_topic]
        
        connections = []
        for domain in other_domains[:3]:  # Top 3 connections
            if agent.lower() == "barbie":
                connection = personality.generate_domain_connection(
                    primary_topic, domain, "core pattern"
                )
            else:  # Ken
                connection = personality.generate_dialectical_probe(
                    f"claims in {primary_topic}", domain
                )
            connections.append(f"{domain}: {connection}")
        
        return connections