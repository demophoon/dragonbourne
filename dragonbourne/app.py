#!/usr/bin/env python
# encoding: utf-8

"""Dragonbourne

Usage:
  dragonbourne.py run command <command>...
  dragonbourne.py use <item> [<attributes>...]
  dragonbourne.py pickup <item>
  dragonbourne.py say <message>
  dragonbourne.py inspect [<object>]
  dragonbourne.py trade <target>
  dragonbourne.py shop
  dragonbourne.py (-h | --help)
  dragonbourne.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import re
import yaml
from docopt import docopt

MAIN_ACTIONS = [
    'use',
    'say',
    'pickup',
    'inspect',
]

world = {
    'player': {
        'alliance': 'good',
        'level': 10,
        'backpack': [],
        'equipped': [],
    }
}


class Item:

    def __init__(self, name, attributes, **kwargs):
        self.name = name
        self.description = attributes.get('description', 'Nothing interesting')
        self.type = "Item"
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.is_avaliable = True
        self.attributes = attributes
        self._parse_attributes(attributes)

    def __repr__(self):
        return self.examine()

    def _parse_attributes(self, attributes):
        if 'conditions' in attributes:
            self.is_avaliable = all(map(self._parse_conditions, attributes['conditions']))

    def _parse_conditions(self, raw):
        operators = {
            '==': lambda l, r: l == r,
            '!=': lambda l, r: l != r,
            '>=': lambda l, r: l >= r,
            '<=': lambda l, r: l <= r,
            '>': lambda l, r: l > r,
            '<': lambda l, r: l < r,
            ' in ': lambda l, r: l in r,
        }
        tokens = re.split(r'\s*({})\s*'.format('|'.join(operators.keys())), raw)
        l = tokens[0]
        o = tokens[1]
        r = tokens[2]
        if l.startswith("$"):
            l = self._interpolate_variable(l[1:], world)
        elif l.isdigit():
            l = int(l)
        if r.startswith("$"):
            r = self._interpolate_variable(r[1:], world)
        elif r.isdigit():
            r = int(r)
        return operators.get(o, lambda *args: None)(l, r)

    def _interpolate_variable(self, name, scope):
        current_scope = scope
        current_scope['self'] = self
        for branch in name.split('.'):
            current_scope = current_scope.get(branch)
        return current_scope

    def use(self):
        raise Exception("Must be implemented")

    def examine(self):
        return "{}.{} (Equippable: {}): {}".format(
            self.type,
            self.name,
            self.is_avaliable,
            self.description,
        )


class Weapon(Item):
    pass


class Wearable(Item):
    pass


def decompose(items, composer):
    final_hash = {}
    for k, v in items.items():
        item = composer.get(k, composer.get('default'))
        if not item:
            continue
        if isinstance(item, dict):
            final_hash[k] = decompose(v, item)
        else:
            final_hash[k] = {}
            for name, attributes in v.items():
                final_hash[k][name] = item(name, attributes, type=k)
                print final_hash[k][name]
    return final_hash


def main(config):
    composer = {
        'items': {
            'weapon': Weapon,
            'wearable': Wearable,
            'default': Item,
        },
    }
    items = decompose(config, composer)
    return items


if __name__ == '__main__':
    f = open('sample_game.yaml', 'r')
    config = yaml.load(f.read())
    main(config)
    exit(0)

    arguments = docopt(__doc__, version='Naval Fate 2.0')
    for action in MAIN_ACTIONS:
        if arguments.get(action):
            print("Action {} was used".format(action))
            exit(0)
    print(arguments)
