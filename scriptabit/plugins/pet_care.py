# -*- coding: utf-8 -*-
""" Habitica pet care.

Options for batch hatching and feeding pets.
"""
# Ensure backwards compatibility with Python 2
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)
from builtins import *
import logging
from pprint import pprint

import scriptabit

class PetCare(scriptabit.IPlugin):
    """ Habitica pet care
    """
    def __init__(self):
        """ Initialises the plugin.
        Generally nothing to do here other than initialise any class attributes.
        """
        super().__init__()
        self.__items = None
        self.__print_help = None
        self.__any_food = False
        self.__good_food = {
            'Base': ['Meat'],
            'CottonCandyBlue': ['CottonCandyBlue'],
            'CottonCandyPink': ['CottonCandyPink'],
            'Desert': ['Potatoe'],
            'Golden': ['Honey'],
            'Red': ['Strawberry'],
            'Skeleton': ['Fish'],
            'White': ['Milk'],
            'Zombie': ['RottenMeat'],
            'Shade': ['Chocolate'],
        }

    def get_arg_parser(self):
        """Gets the argument parser containing any CLI arguments for the plugin.

        Returns: argparse.ArgParser:  The `ArgParser` containing the argument
        definitions.
        """
        parser = super().get_arg_parser()

        parser.add(
            '--pets-list-items',
            required=False,
            action='store_true',
            help='Lists all pet-related items')

        parser.add(
            '--pets-feed',
            required=False,
            action='store_true',
            help='Feed all pets')

        parser.add(
            '--pets-any-food',
            required=False,
            action='store_true',
            help='When feeding pets, allows the use of non-preferred food')

        self.__print_help = parser.print_help

        return parser

    def initialise(self, configuration, habitica_service, data_dir):
        """ Initialises the plugin.

        Generally, any initialisation should be done here rather than in
        activate or __init__.

        Args:
            configuration (ArgParse.Namespace): The application configuration.
            habitica_service: the Habitica Service instance.
            data_dir (str): A writeable directory that the plugin can use for
                persistent data.
        """
        super().initialise(configuration, habitica_service, data_dir)
        logging.getLogger(__name__).info('Scriptabit Pet Care Services: looking'
                                         ' after your pets since yesterday')

        self.__items = self._hs.get_user()['items']
        self.__any_food = self._config.pets_any_food

    def update_interval_minutes(self):
        """ Indicates the required update interval in minutes.

        Returns: float: The required update interval in minutes.
        """
        return 30

    def update(self):
        """ This update method will be called once on every update cycle,
        with the frequency determined by the value returned from
        `update_interval_minutes()`.

        If a plugin implements a single-shot function, then update should
        return `False`.

        Returns: bool: True if further updates are required; False if the plugin
        is finished and the application should shut down.
        """

        # do work here
        if self._config.pets_list_items:
            self.list_pet_items(self.__items)
            return False

        if self._config.pets_feed:
            self.feed_pets()
            return False

        # if no other options selected, print plugin specific help and exit
        self.__print_help()

        # return False if finished, and True to be updated again.
        return False

    def feed_pets(self):
        """ Feeds all current pets. """
        # TODO: filter pets by normal and special pets.
        # Probably want an option to only feed normal pets

        # TODO: This algorithm is ugly, but it works.
        # I think a version built around a food generator might be more elegant.
        # The generator would keep returning an in-stock food item suitable for
        # a given pet until no more suitable foods are in stock.
        # Could then loop until the food is gone, or the pet becomes a mount.
        pets = self.__items['pets']
        for pet, growth in pets.items():
            # get the first food item
            food = self.get_food_for_pet(pet)
            count = 0
            while food:
                logging.getLogger(__name__).info(
                    '%s (%d): %s', pet, growth, food)

                # TODO: feed the pet
                self.consume_food(food)

                # TODO: break if pet became a mount
                count += 1
                if count > 2:
                    break

                # get the next food item
                food = self.get_food_for_pet(pet)

            logging.getLogger(__name__).debug(
                '%s (%d): no food', pet, growth)

    def get_food_for_pet(self, pet):
        """ Gets a food item for a pet

        Args:
            pet (str): The composite pet name (animal-potion)

        Returns:
            str: The name of a suitable food if that food is in stock.
                If no suitable food is available, then None is returned.
        """
        # split the pet name
        _, potion = pet.split('-')

        if self.__any_food:
            for food, quantity in self.__items['food']:
                if quantity > 0:
                    return food
        else:
            # get a list of candidate preferred foods
            pantry = self.get_good_food_for_potion(potion)
            # then iterate
            for food in pantry:
                if self.has_food(food):
                    return food
        return None

    def has_food(self, food):
        """ Returns True if the food is in stock, otherwise False.

        Args:
            food (str): The food to check

        Returns:
            bool: True if the food is in stock, otherwise False.
        """
        return self.__items['food'].get(food, 0) > 0

    def consume_food(self, food):
        """ Consumes a food, updating the cached quantity.

        Args:
            food (str): The food.
        """
        quantity = self.__items['food'].get(food, 0)
        if quantity > 0:
            self.__items['food'][food] = quantity - 1

    def get_good_food_for_potion(self, potion):
        """ Gets a list of known good foods for a given potion type.

        Args:
            potion (str): The potion type for which a
        """
        # TODO: I don't need this function. Just run it once during start up and cache the results. They don't change
        foods = []

        # standard foods
        if potion in self.__good_food:
            foods.extend(self.__good_food[potion])

        # special foods
        foods.append('Cake_{0}'.format(potion))

        # TODO: special potions that like all foods

        return foods

    @staticmethod
    def list_pet_items(items):
        """ Lists all pet-related inventory items.

        Args:
            items (dict): The Habitica user.items dictionary.
        """
        print()
        print('Food:')
        pprint(items['food'])
        print()
        print('Eggs:')
        pprint(items['eggs'])
        print()
        print('Hatching potions:')
        pprint(items['hatchingPotions'])
        print()
        print('Pets:')
        pprint(items['pets'])
        print()
        print('Mounts:')
        pprint(items['mounts'])
