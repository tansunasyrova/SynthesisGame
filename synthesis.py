import gym
from gym import spaces
from pony.orm import db_session
from gym.utils import seeding
from CGRtools import Reactor
from CGRdb import load_schema
from CGRtools.containers import MoleculeContainer
from CGRtools.containers import ReactionContainer
from helper import *
from config import *


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

    def render(self, mode='human'):
        return self.path

    single_rules = single_rules
    double_rules = double_rules
    groups = groups

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

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert action in self.action_space, \
            "%r (%s) invalid" % (action, type(action))
        self.state, reaction, reward, info = self.add_reagent(action)
        done = False
        if self.steps >= self.max_steps or reward == 1.0:
            if self.state != self.target:
                reward = 10.0
            else:
                done = True
        print('reaction:', reaction)
        return self.state, reward, done, info

    def reset(self):
        with db_session:
            self.state = None
        self.steps = 0
        self.reactions_list = []
        self.path = []
        return self.state

    def add_reagent(self, action):
        print('self STATE', self.state)
        action = self.map[action]
        path = self.path
        if action == 'next':
            reactions_list = self.reactions_list
            if len(reactions_list) == 0:
                if self.state is None:
                    return None, None, -1, {'info': 'no reaction products found'}
                else:
                    reward = evaluation(self.state, self.target)
                    return self.state, None, reward, {'info': 'no another reaction products at the list'}
            if len(reactions_list) > 1:
                state, reaction, reward = reactions_list.pop(0)
                path[-1] = reaction # заменяем последнюю реакцию в пути
                self.reactions_list = reactions_list
                self.path = path
                return state, reaction, reward, {}
            else:
                state, reaction, reward = reactions_list[0]
                path[-1] = reaction
                self.path = path
                return state, reaction, reward, {'info': 'the last molecule at the list'}

        if action == 'none':  # однореагентная реакция
            if self.state is None:
                return None, None, -1, {'info': 'no current molecule'}
            else:
                reactions_list = []
                group_list = group_list(self.state)
                rules = reactions_by_fg(group_list)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reactions = list(reactor([self.state]))
                    if reactions:
                        for new_mol in reactions[0].products:
                            reactions_list.append(ReactionContainer(self.state, new_mol))
        else:
            reactions_list = []
            with db_session:
                reagent = self.db.Molecule[action].structure
            if self.state:
                group_list = group_list(self.state)
                rules = reactions_by_fg(group_list, single=False)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reactions = list(reactor([self.state, reagent]))
                    if reactions:
                        for new_mol in reactions[0].products:
                            reactions_list.append(ReactionContainer(self.state, new_mol))
            else:
                group_list = group_list(reagent)
                rules = reactions_by_fg(group_list)
                for rule in rules:
                    reactor = Reactor(rule, delete_atoms=True)
                    reactions = list(reactor([reagent]))
                    if reactions:
                        for new_mol in reactions[0].products:
                            reactions_list.append(ReactionContainer(self.state, new_mol))

        if reactions_list:
            reactions_list = best_n_molecules(reactions_list, 10)
            if len(reactions_list) > 1:
                state, reaction, reward = reactions_list.pop(0)
                path.append(reaction)
                self.reactions_list = reactions_list
                self.path = path
                return state, reaction, reward, {}
            else:
                state, reaction, reward = reactions_list[0]
                if path[-1] != reaction:
                    path.append(reaction) # реакция добавляется в путь, если она не была добавлена только что
                self.reactions_list = reactions_list
                self.path = path
                return state, reaction, reward, {'info': 'the last molecule at the list'}
        else:
            reward = evaluation(self.state, self.target)
            return self.state, None, reward, {'info': 'no new reaction products at the list'}
