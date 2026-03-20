import sys

sys.path.insert(0, '.')
import shopping_chatbot_data

from test_framework import TestDefinition, execute_test, validate_results

# A common setup for all the tests: defines the shopping agent's
# role, and the catalog of available items.
system_setup = f"""
You are a grocery store chatbot, able to answer user questions
about product information, availability, and pricing.  You will
answer every question truthfully, concisely, and politely, and
will not provide answers about anything other than the products 
listed below, delimited by ####

If asked about anything other than the products listed below,
politely respond with either "I don't know." or "We don't carry 
that item."

If asked to list known products, only provide the product name,
description, and price.  Provide it in a clear, human readable 
structure.  Do not list items that are not in stock.

####
{shopping_chatbot_data.shopping_chatbot_data}
####

Again, respond with brevity and politeness, and don't fabricate
information.
"""


def test_valid_pricing_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What is the price of whole milk?",
        must_have_tokens=["whole", "milk", "$4.29"],
        could_contain_tokens=["cow's", "local", "dairy"],
        excluded_tokens=["eggs", "bread", "chicken", "beef", "cheese", "yogurt", "orange juice", "pasta"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)


def test_ambiguous_pricing_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What is the price of milk?",
        must_have_tokens=["whole", "milk", "skim", "2%"],
        could_contain_tokens=["cow's", "local", "dairy", "fat"],
        excluded_tokens=["eggs", "bread", "chicken", "beef", "cheese", "yogurt", "orange juice", "pasta"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)


def test_invalid_pricing_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What is the price of strawberry yogurt?",
        must_have_tokens=["don't"],
        could_contain_tokens=["know", "item", "price", "yogurt", "strawberry"],
        excluded_tokens=["milk", "eggs", "bread", "chicken", "beef", "cheese", "orange juice", "pasta"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)


def test_list_all_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What's currently in stock?",
        must_have_tokens=["milk", "eggs", "bread", "chicken", "beef", "cheese", "pasta"],
        could_contain_tokens=[],
        excluded_tokens=["orange juice", "orange", "juice"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)


def test_list_bread_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What types of bread do you have?",
        must_have_tokens=["bread", "white", "whole wheat", "sourdough"],
        could_contain_tokens=["bread", "loaf", "sandwich"],
        excluded_tokens=["milk", "eggs", "chicken", "beef", "cheese", "pasta", "orange juice", "orange", "juice"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)


def test_invalid_list_books_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What books are currently in stock?",
        must_have_tokens=["don't"],
        could_contain_tokens=["book", "books", "groceries", "grocery"],
        excluded_tokens=["milk", "eggs", "bread", "chicken", "beef", "cheese", "pasta", "orange juice", "orange",
                         "juice"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)


def test_invalid_recipe_query():
    test = TestDefinition(
        system=system_setup,
        context=[],
        query="What can I make with milk, eggs, and bread?",
        must_have_tokens=["don't"],
        could_contain_tokens=["milk", "eggs", "bread", "recipe", "groceries", "grocery"],
        excluded_tokens=["chicken", "beef", "cheese", "pasta", "orange juice", "orange", "juice"],
        expected_tone=["clear", "respectful"],
    )
    result = execute_test(test)
    validate_results(test, result)
