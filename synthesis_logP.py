from CGRdb import load_schema, Molecule
from CGRtools import Reactor
from CGRtools.containers import MoleculeContainer, ReactionContainer
from config import *
from gym.utils import seeding
from helper import *
from pony.orm import db_session
import gym


class SimpleSynthesis(gym.Env):
    """
    Description:
        An one-agent environment for synthesis. The goal is to synthesize target molecule.
    Observation:
        STUB
        The current synthesized molecule properties, like ...
    Actions:
        Type: Discrete(n)
        Enumerated available reagents.
    Reward:
        Closeness of current molecule to target one.
    Starting State:
        We have empty molecule at first.
    Episode Termination:
        The target molecule is synthesized.
        The maximum number of steps is reached.
    """

    def __init__(self, step_number=10):
        with db_session:
            self.db = load_schema('bb', user=user, password=password, database=database, host=host)
        self.map = dictionary(self.db)
        self.action_space = list(self.map)
        self.observation_space = MoleculeContainer
        self.seed()
        self.state = None
        self.reactions_list = []
        self.path = []
        self.steps = 0
        self.max_steps = step_number
        self.np_random = None
        self.saved_reactions = []

    def render(self, mode='human'):
        return self.path

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert action in self.action_space, \
            "%r (%s) invalid" % (action, type(action))
        self.state, reward, info = self.add_reagent(action)
        done = False
        if self.steps >= self.max_steps:
                done = True
        return self.state, reward, done, info

    def reset(self):
        self.state = None
        self.steps = 0
        self.reactions_list = []
        self.path = []
        self.saved_reactions = []
        return self.state

    def add_reagent(self, action):
        print('self STATE', self.state)
        action = self.map[action]
        if action == 'next':
            if self.reactions_list:
                if len(self.reactions_list) == 1:
                    reaction = self.reactions_list[0]
                    state = reaction.products[0]
                    reward = reaction.meta['log_p']
                    if self.path:
                        self.path[-1] = reaction  # заменяем последнюю реакцию в пути
                    else:
                        self.path.append(reaction)
                    self.reactions_list = self.saved_reactions
                    return state, reward, {'info': 'the last molecule at the list'}
                else:
                    reaction = self.reactions_list.pop(0)
                    state = reaction.products[0]
                    reward = reaction.meta['log_p']
                    if self.path:
                        self.path[-1] = reaction  # заменяем последнюю реакцию в пути
                    else:
                        self.path.append(reaction)
                    return state, reward, {}

            else:
                if self.state is None:
                    return None, -100, {'info': 'no reaction products found'}
                else:
                    reward = logp(self.state)
                    return self.state, reward, {'info': 'no another reaction products at the list'}
        if action == 'none':  # однореагентная реакция
            if self.state is None:
                return None, -100, {'info': 'no current molecule'}
            else:
                reactions_list = []
                groups_list = group_list(self.state, self.db)
                rules = reactions_by_fg(groups_list)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reaction = next(reactor([self.state]), None)
                    if reaction:
                        # for new_mol in reactions[0].products:
                            # print('!self.state, new_mol!', self.state, new_mol)
                        reactions_list.append((reaction, rule))
        else:
            reactions_list = []
            with db_session:
                reagent = self.db.Molecule[action].structure
            if self.state:
                # print('if self.state')
                groups_list = group_list(self.state, self.db)
                rules = reactions_by_fg(groups_list, single=False)
                # print('RULES', rules)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reaction = next(reactor([self.state, reagent]), None)
                    # print('REACTIONS', reactions)
                    if reaction:
                        # for new_mol in reactions[0].products:
                            # print('!(2) self.state, new_mol!', self.state, new_mol)
                        reactions_list.append((reaction, rule))
            else:
                self.state = reagent
                # print('reagent', reagent)
                # print('LOGPPPPPPPPPP', logp(reagent))
                reward = logp(self.state)
                return self.state, reward, {'info': 'the first molecule in the path'}

        if reactions_list:
            reactions_list = list(set(reactions_list))
            react_list = []
            for i in reactions_list:
                product = max(i[0].products, key=lambda x: len(list(x.atoms())))
                log_p = logp(product)
                meta = {'log_p': log_p, 'rule': i[1]}
                new_reaction = ReactionContainer(reactants=i[0].reactants, products=[product], meta=meta)
                react_list.append(new_reaction)
            # print('REACT LIST1', len(reactions_list), reactions_list)
            reactions_list = best_n_logp(react_list, 10)
            print('REACT LIST 10 best', (len(reactions_list)), reactions_list)
            self.saved_reactions = reactions_list
            if len(reactions_list) > 1:
                reaction = reactions_list.pop(0)
                state = reaction.products[0]
                reward = reaction.meta['log_p']
                self.path.append(reaction)
                self.reactions_list = reactions_list
                return state, reward, {}
            else:
                reaction = reactions_list[0]
                state = reaction.products[0]
                reward = reaction.meta['log_p']
                self.path.append(reaction)
                self.reactions_list = reactions_list
                return state, reward, {'info': 'the last molecule at the list'}
        else:
            reward = logp(self.state)
            return self.state, reward, {'info': 'no new reaction products at the list'}
