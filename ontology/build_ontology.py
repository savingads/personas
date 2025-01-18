from owlready2 import *

# Create a new ontology
onto = get_ontology("http://example.org/simulated_user_ontology.owl")

# Define classes and categories
with onto:
    # Root class
    class SimulatedUser(Thing):
        """Root class for simulated users in testing environments."""
        pass

    # Facets of Persona
    class DemographicData(Thing):
        """Demographic attributes of a simulated user."""
        pass

    class BehavioralData(Thing):
        """Behavioral patterns and activities."""
        pass

    class PsychographicData(Thing):
        """Psychological attributes, values, and interests."""
        pass

    class ContextualData(Thing):
        """Contextual environment and settings."""
        pass

# Define relationships (ObjectProperties)
with onto:
    class has_demographics(ObjectProperty):
        domain = [SimulatedUser]
        range = [DemographicData]
        comment = "Links a simulated user to its demographic attributes."

    class has_behavior(ObjectProperty):
        domain = [SimulatedUser]
        range = [BehavioralData]
        comment = "Links a simulated user to its behavioral data."

    class has_psychographics(ObjectProperty):
        domain = [SimulatedUser]
        range = [PsychographicData]
        comment = "Links a simulated user to its psychographic data."

    class has_context(ObjectProperty):
        domain = [SimulatedUser]
        range = [ContextualData]
        comment = "Links a simulated user to its contextual data."

# Define Data Properties (Attributes)
with onto:
    # Demographic Attributes
    class age(DataProperty, FunctionalProperty):
        domain = [DemographicData]
        range = [int]
        comment = "Age of the simulated user."

    class gender(DataProperty, FunctionalProperty):
        domain = [DemographicData]
        range = [str]
        comment = "Gender of the simulated user."

    class occupation(DataProperty, FunctionalProperty):
        domain = [DemographicData]
        range = [str]
        comment = "Occupation of the simulated user."

    # Behavioral Attributes
    class browsing_patterns(DataProperty):
        domain = [BehavioralData]
        range = [str]
        comment = "Typical browsing patterns or interests."

    class click_rate(DataProperty, FunctionalProperty):
        domain = [BehavioralData]
        range = [int]
        comment = "Number of clicks per session."

    class conversion_rate(DataProperty, FunctionalProperty):
        domain = [BehavioralData]
        range = [float]
        comment = "Simulated likelihood of making a purchase."

    # Psychographic Attributes
    class personality_traits(DataProperty):
        domain = [PsychographicData]
        range = [str]
        comment = "Dictionary of personality traits (e.g., Big Five)."

    class goal(DataProperty, FunctionalProperty):
        domain = [PsychographicData]
        range = [str]
        comment = "User's short-term goal, e.g., 'shopping' or 'researching.'"

    # Contextual Attributes
    class environment(DataProperty, FunctionalProperty):
        domain = [ContextualData]
        range = [str]
        comment = "Simulated user's environment, e.g., 'home,' 'work,' etc."

    class network_conditions(DataProperty, FunctionalProperty):
        domain = [ContextualData]
        range = [str]
        comment = "Quality of network, e.g., 'slow,' 'fast.'"

# Create Instances for Simulation
with onto:
    # Create a simulated user
    user_1 = SimulatedUser("User_TechSavvy_30s")
    user_1.comment = "Simulates a tech-savvy user in their 30s."

    # Demographic Data
    demo = DemographicData("TechSavvy_Demographics")
    demo.age = 35
    demo.gender = "female"
    demo.occupation = "software engineer"
    user_1.has_demographics = [demo]

    # Behavioral Data
    behavior = BehavioralData("TechSavvy_Behavior")
    behavior.browsing_patterns.append("technology blogs")
    behavior.browsing_patterns.append("coding tutorials")
    behavior.click_rate = 60
    behavior.conversion_rate = 0.2
    user_1.has_behavior = [behavior]

    # Psychographic Data
    psych = PsychographicData("TechSavvy_Psychographics")
    psych.personality_traits.append('{"openness": 0.9, "extraversion": 0.6}')
    psych.goal = "learning new tech skills"
    user_1.has_psychographics = [psych]

    # Contextual Data
    context = ContextualData("TechSavvy_Context")
    context.environment = "office"
    context.network_conditions = "high-speed"
    user_1.has_context = [context]

# Save the ontology
onto.save(file="simulated_user_ontology.owl", format="rdfxml")

print(f"Ontology saved to simulated_user_ontology.owl")
