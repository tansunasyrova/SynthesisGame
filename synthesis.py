from CGRdb import load_schema
from CGRtools import Reactor
from CGRtools.containers import MoleculeContainer
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

    def __init__(self, target, step_number=10):
        self.target = target
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
        self.first_step = None

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
        if self.steps >= self.max_steps or reward == 1.0:
            if self.state != self.target:
                reward = 10.0
            else:
                done = True
        return self.state, reward, done, info

    def reset(self):
        self.state = None
        self.steps = 0
        self.reactions_list = []
        self.path = []
        return self.state

    def add_reagent(self, action):
        print('self STATE', self.state)
        action = self.map[action]
        if action == 'next':
            if self.reactions_list:
                if len(self.reactions_list) == 1:
                    reaction = self.reactions_list[0]
                    state = reaction.products[0]
                    reward = reaction.meta['tanimoto']
                    if self.path:
                        self.path[-1] = reaction  # заменяем последнюю реакцию в пути
                    else:
                        self.path.append(reaction)
                    self.reactions_list[0] = self.first_step
                    return state, reward, {'info': 'the last molecule at the list'}
                else:
                    reaction = self.reactions_list.pop(0)
                    state = reaction.products[0]
                    reward = reaction.meta['tanimoto']
                    if self.path:
                        self.path[-1] = reaction  # заменяем последнюю реакцию в пути
                    else:
                        self.path.append(reaction)
                    return state, reward, {}

            else:
                if self.state is None:
                    return None, -1, {'info': 'no reaction products found'}
                else:
                    reward = evaluation(self.state, self.target)
                    return self.state, reward, {'info': 'no another reaction products at the list'}
        if action == 'none':  # однореагентная реакция
            if self.state is None:
                return None, -1, {'info': 'no current molecule'}
            else:
                reactions_list = []
                groups_list = group_list(self.state, self.db)
                rules = reactions_by_fg(groups_list)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reactions = next(reactor([self.state]))
                    if reactions:
                        # for new_mol in reactions[0].products:
                            # print('!self.state, new_mol!', self.state, new_mol)
                        reactions_list.append(reactions)
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
                    reactions = next(reactor([self.state, reagent]), None)
                    # print('REACTIONS', reactions)
                    if reactions:
                        # for new_mol in reactions[0].products:
                            # print('!(2) self.state, new_mol!', self.state, new_mol)
                        reactions_list.append(reactions)
            else:
                groups_list = group_list(reagent, self.db)
                rules = reactions_by_fg(groups_list)
                # print('RULES', rules)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reactions = list(reactor([reagent]))
                    # print('REACTIONS', reactions)
                    if reactions:
                        # for new_mol in reactions[0].products:
                            # print('!(1) new_mol!', new_mol)
                        reactions_list.append(reactions[0])

        if reactions_list:
            # print('REACT LIST1', len(reactions_list), reactions_list)
            reactions_list = best_n_molecules(reactions_list, self.target, 10)
            print('REACT LIST 10 best', (len(reactions_list)), reactions_list)
            self.first_step = reactions_list[0]
            if len(reactions_list) > 1:
                reaction = reactions_list.pop(0)
                state = reaction.products[0]
                reward = reaction.meta['tanimoto']
                self.path.append(reaction)
                self.reactions_list = reactions_list
                return state, reward, {}
            else:
                reaction = reactions_list.pop(0)
                state = reaction.products[0]
                reward = reaction.meta['tanimoto']
                self.path.append(reaction)
                self.reactions_list = reactions_list
                return state, reward, {'info': 'the last molecule at the list'}
        else:
            reward = evaluation(self.state, self.target)
            return self.state, reward, {'info': 'no new reaction products at the list'}
