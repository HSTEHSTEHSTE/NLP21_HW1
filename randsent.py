#!/usr/bin/env python
"""
601.465/665 - Natural Language Processing
Assignment 1: Designing Context-Free Grammars

Assignment written by Jason Eisner
Modified by Kevin Duh
Re-modified by Alexandra DeLucia

Code template written by Alexandra DeLucia,
based on the submitted assignment with Keith Harrigian
and Carlos Aguirre Fall 2019
"""
import os
import sys
import random
import argparse
from numpy.random import uniform, choice

# Want to know what command-line arguments a program allows?
# Commonly you can ask by passing it the --help option, like this:
#     python randsent.py --help
# This is possible for any program that processes its command-line
# arguments using the argparse module, as we do below.
#
# NOTE: When you use the Python argparse module, parse_args() is the
# traditional name for the function that you create to analyze the
# command line.  Parsing the command line is different from parsing a
# natural-language sentence.  It's easier.  But in both cases,
# "parsing" a string means identifying the elements of the string and
# the roles they play.


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        args (an argparse.Namespace): Stores command-line attributes
    """
    # Initialize parser
    parser = argparse.ArgumentParser(
        description="Generate random sentences from a PCFG")
    # Grammar file (required argument)
    parser.add_argument(
        "-g",
        "--grammar-file",
        type=str, required=True,
        help="Path to grammar file",
    )
    # Start symbol of the grammar
    parser.add_argument(
        "-s",
        "--start-symbol",
        type=str,
        help="Start symbol of the grammar",
        default="ROOT",
    )
    # Number of sentences
    parser.add_argument(
        "-n",
        "--number-of-sentences",
        type=int,
        help="Number of sentences to generate",
        default=1,
    )
    # Maximum number of nonterminal expansions when generating the sentence
    parser.add_argument(
        "-M",
        "--max-expansions",
        type=int,
        help="Max number of nonterminal expansions when generating the sentence",
        default=450,
    )
    # Print the derivation tree for each generated sentence
    parser.add_argument(
        "-t",
        "--tree",
        action="store_true",
        help="Print the derivation tree for each generated sentence",
        default=False,
    )
    return parser.parse_args()


class Grammar:
    def __init__(self, grammar_file, start_symbol):
        """
        Context-Free Grammar (CFG) Sentence Generator

        Args:
            grammar_file (str): Path to a .gr grammar file
            start_symbol (str): Starting symbol

        Returns:
            self
        """
        # Parse the input grammar file
        self.rules = {}
        self.start_symbol = start_symbol
        self._load_rules_from_file(grammar_file)

    def _load_rules_from_file(self, grammar_file):
        """
        Read grammar file and store its rules in self.rules

        Args:
            grammar_file (str): Path to the raw grammar file 
        """

        file = open(grammar_file, 'r')
        file_content = file.read()
        lines = file_content.split('\n')
        rules = []
        for line in lines:
            if len(line) > 0 and line[0] != '#':
                rule = line.split('#', 1)[0]
                rule = rule.strip()
                rules.append(rule)
        for rule in rules:
            rule_elements = rule.split()
            key = rule_elements.pop(1)
            weight = float(rule_elements.pop(0))
            if key in self.rules:
                new_rule = {
                    "weight": weight,
                    "expanded_symbols": rule_elements
                }
                self.rules[key]["total_weight"] += weight
                self.rules[key]["rules"].append(new_rule)
            else:
                new_rule_set = {
                    "total_weight": 0,
                    "rules": []
                }
                self.rules[key] = new_rule_set
                new_rule = {
                    "weight": weight,
                    "expanded_symbols": rule_elements
                }
                self.rules[key]["total_weight"] += weight
                self.rules[key]["rules"].append(new_rule)

    def sample(self, derivation_tree, max_expansions):
        """
        Sample a random sentence from this grammar

        Args:
            derivation_tree (bool): if true, the returned string will represent 
                the tree (using bracket notation) that records how the sentence 
                was derived

            max_expansions (int): max number of nonterminal expansions we allow

        Returns:
            str: the random sentence or its derivation tree
        """

        sentence = [self.start_symbol]
        expansion_number = 0
        sentence_final = []
        tree = ""
        tree_key = 0
        while len(sentence) > 0:
            symbol_to_expand = sentence.pop(0)
            if symbol_to_expand == ' ':
                tree_key += 1
            elif symbol_to_expand not in self.rules:
                sentence_final.append(symbol_to_expand)
                tree = tree[:tree_key] + ' ' + \
                    symbol_to_expand + tree[tree_key:]
                tree_key += len(symbol_to_expand) + 1
            elif expansion_number > max_expansions:
                sentence_final.append("...")
                tree = tree[:tree_key] + ' ' + \
                    "..." + tree[tree_key:]
                tree_key += 4
            else:
                expansion_number += 1
                substitutions = self.rules[symbol_to_expand]
                random_weight = uniform(0, substitutions["total_weight"])
                current_weight = 0
                replacement_list = []
                for rule in substitutions["rules"]:
                    current_weight += rule["weight"]
                    if current_weight >= random_weight:
                        replacement_list = rule["expanded_symbols"]
                        break
                sentence = replacement_list + [' '] + sentence
                tree = tree[:tree_key] + \
                    ' (' + symbol_to_expand + ')' + tree[tree_key:]
                tree_key += len(symbol_to_expand) + 2

        sentence_string = ""
        for word in sentence_final:
            sentence_string = sentence_string + word
            sentence_string = sentence_string + ' '
        return sentence_string, tree


####################
# Main Program
####################


def main():
    # Parse command-line options
    args = parse_args()

    # Initialize Grammar object
    grammar = Grammar(args.grammar_file, args.start_symbol)

    # Generate sentences
    for i in range(args.number_of_sentences):
        # Use Grammar object to generate sentence
        sentence, tree = grammar.sample(
            derivation_tree=args.tree, max_expansions=args.max_expansions
        )

        # Print the sentence with the specified format.
        # If it's a tree, we'll pipe the output through the prettyprint script.
        if args.tree:
            prettyprint_path = os.path.join(os.getcwd(), 'prettyprint.pl')
            t = os.system(f"echo '{tree}' | perl {prettyprint_path}")
        print(sentence)


if __name__ == "__main__":
    main()
