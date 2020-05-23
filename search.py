from CGRtools.files import SMILESread, SDFread
from io import StringIO
import random
import os
import math
from mcts import mcts
import synthesis
os.environ['PATH'] = '/home/tansu/game'
os.environ['PATH'] += ':/home/tansu/venv/bin'

# 736786, 'next'
target = SMILESread(StringIO("CCCOC")).read()[0]
# target = SDFread('serotonine.sdf').read()[0]
target.implicify_hydrogens()
print(target)
play = synthesis.SimpleSynthesis(target, step_number=100)


def temp(t0, i):
    t = t0*0.1/i
    return t


def probability(dE, t):
    p = math.exp(-dE/t)
    return p


def act(p):
    value = random.random()
    if value <= p:
        a = 1
    else:
        a = 0
    return a


def simulated(t0, tend):
    actions = play.action_space
    action = random.choice(actions)
    t = t0
    i = 0
    state, reward, done, info = play.step(action)
    while t > tend:
        naction = random.choice(actions)
        nstate, nreward, ndone, ninfo = play.step(naction)
        if nreward > reward:
            state = nstate
            reward = nreward
        else:
            p = probability(reward - nreward, t)
            if act(p) == 1:
                state = nstate
                reward = nreward
        i += 1
        t = temp(t, i)
        print('state-reward!', state, reward)
    print('PATH:', play.render())


simulated(10000000, 0.0001)
