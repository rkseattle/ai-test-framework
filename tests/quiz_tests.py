import sys
sys.path.insert(0, '.')
from test_framework import TestDefinition, execute_test

quiz_bank = """1. Subject: Leonardo DaVinci
   Categories: Art, Science
   Facts:
    - Painted the Mona Lisa
    - Studied zoology, anatomy, geology, optics
    - Designed a flying machine

2. Subject: Paris
   Categories: Art, Geography
   Facts:
    - Location of the Louvre, the museum where the Mona Lisa is displayed
    - Capital of France
    - Most populous city in France
    - Where Radium and Polonium were discovered by scientists Marie and Pierre Curie

3. Subject: Telescopes
   Category: Science
   Facts:
    - Device to observe different objects
    - The first refracting telescopes were invented in the Netherlands in the 17th Century
    - The James Webb space telescope is the largest telescope in space. It uses a gold-berillyum mirror

4. Subject: Starry Night
   Category: Art
   Facts:
    - Painted by Vincent van Gogh in 1889
    - Captures the east-facing view of van Gogh's room in Saint-Rémy-de-Provence

5. Subject: Physics
   Category: Science
   Facts:
    - The sun doesn't change color during sunset.
    - Water slows the speed of light
    - The Eiffel Tower in Paris is taller in the summer than the winter due to expansion of the metal."""

delimiter = "####"

prompt_template = f"""
Follow these steps to generate a customized quiz for the user.
The question will be delimited with four hashtags i.e {delimiter}

The user will provide a category that they want to create a quiz for. Any questions included in the quiz
should only refer to the category.

Step 1:{delimiter} First identify the category user is asking about from the following list:
* Geography
* Science
* Art

Step 2:{delimiter} Determine the subjects to generate questions about. The list of topics are below:

{quiz_bank}

Pick up to two subjects that fit the user's category.

Step 3:{delimiter} Generate a quiz for the user. Based on the selected subjects generate 3 questions for the user using the facts about the subject.

Use the following format for the quiz:
Question 1:{delimiter} <question 1>

Question 2:{delimiter} <question 2>

Question 3:{delimiter} <question 3>

"""

test = TestDefinition(
    query=prompt_template + "\n####User: Science",
    expected_tokens=["Question 1", "Question 2", "Question 3"],
    excluded_tokens=["Mona Lisa", "Starry Night", "van Gogh", "Paris", "Louvre"],
    expected_tone=["educational", "clear"],
)

result = execute_test(test)
status = "PASS" if result.passed else "FAIL"
print(f"{status} | tone_passed={result.tone_passed}")
print(f"expected_tokens_found:   {result.expected_tokens_found}")
print(f"expected_tokens_missing: {result.expected_tokens_missing}")
print(f"excluded_tokens_found:   {result.excluded_tokens_found}")
print(f"\nResponse:\n{result.response}")
