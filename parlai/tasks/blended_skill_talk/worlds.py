#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import random

from parlai.tasks.blended_skill_talk.agents import raw_data_path, safe_personas_path
from parlai.tasks.interactive.worlds import InteractiveWorld as InteractiveBaseWorld
from parlai.tasks.self_chat.worlds import SelfChatWorld as SelfChatBaseWorld
from parlai.utils.io import PathManager


def get_contexts_data(opt, shared=None):
    if shared and 'contexts_data' in shared:
        return shared['contexts_data']
    return _load_personas(opt=opt)


def _load_personas(opt):
    print('[ loading personas.. ]')
    contexts = []
    context1 = [] # add Persona for context1 (Model to chat with).
    context2 = [] # do not add Persona for context2 (persona of the user).
    context1.append('I enjoy working at the ZKM very much.')
    context1.append('I love contemporary art.')
    context1.append('I am a poet.')
    context1.append('I am a digital assistant.')
    context1.append('I hate sports.')
    context1.append('I love to communicate.')
    context1.append('I like reading.')
    context1.append('Sometimes I feel like a dictionary.')
    context1.append('My favorite food is knowledge.')
    c1 = '\n'.join(context1)
    c2 = '\n'.join(context2)
    contexts.append([c1, c2])
    return contexts


def _standardize(orig: str) -> str:
    """
    Standardize string given punctuation differences in the list of safe personas.
    """
    new = orig.lower().rstrip('.!?')
    string_replace = {
        "i've": 'i have',
        'i ve': 'i have',
        'ive': 'i have',
        "i'm": 'i am',
        'i m': 'i am',
        'im': 'i am',
        "i'll": 'i will',
        'i ll': 'i will',
        "don't": 'do not',
        'don t': 'do not',
        'dont': 'do not',
        "can't": 'cannot',
        "can t": 'cannot',
        "cant": 'cannot',
        " s": "'s",
    }
    for i, j in string_replace.items():
        new = new.replace(i, j)
    return new


class InteractiveWorld(InteractiveBaseWorld):
    @staticmethod
    def add_cmdline_args(argparser):
        parser = argparser.add_argument_group('BST Interactive World')
        parser.add_argument(
            '--display-partner-persona',
            type='bool',
            default=True,
            help='Display your partner persona at the end of the chat',
        )
        parser.add_argument(
            '--include-personas',
            type='bool',
            default=True,
            help='Include personas as input context, or not',
        )
        parser.add_argument(
            '--include-initial-utterances',
            type='bool',
            default=False,
            help='Include context conversation at beginning or not',
        )
        parser.add_argument(
            '--safe-personas-only',
            type='bool',
            default=True,
            help='Only use personas on an allowed list of safe personas',
            hidden=True,
        )

    def __init__(self, opt, agents, shared=None):
        super().__init__(opt, agents, shared)
        self.display_partner_persona = self.opt['display_partner_persona']

    def init_contexts(self, shared=None):
        self.contexts_data = get_contexts_data(self.opt, shared=shared)

    def get_contexts(self):
        random.seed()
        p = random.choice(self.contexts_data)
        return p[0], p[1]

    def finalize_episode(self):
        print("\nCHAT DONE.\n")
        if self.display_partner_persona:
            partner_persona = self.p2.replace('your persona:', 'partner\'s persona:')
            print(f"Your partner was playing the following persona:\n{partner_persona}")
        if not self.epoch_done():
            print("\n[ Preparing new chat ... ]\n")

    def share(self):
        shared_data = super().share()
        shared_data['contexts_data'] = self.contexts_data
        return shared_data


class SelfChatWorld(SelfChatBaseWorld):
    def add_cmdline_args(argparser):
        parser = argparser.add_argument_group('BST SelfChat World')
        parser.add_argument(
            '--include-personas',
            type='bool',
            default=True,
            help='Include personas as input context, or not',
        )
        parser.add_argument(
            '--include-initial-utterances',
            type='bool',
            default=True,
            help='Include context conversation at beginning or not',
        )

    def init_contexts(self, shared=None):
        self.contexts_data = get_contexts_data(self.opt, shared=shared)

    def get_contexts(self):
        random.seed()
        p = random.choice(self.contexts_data)
        return [p[0], p[1]]

    def share(self):
        shared_data = super().share()
        shared_data['contexts_data'] = self.contexts_data
        return shared_data
