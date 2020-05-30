from CGRtools.files import SMILESread, SDFread, SMILESRead
from io import StringIO
import random
import os
import math
from mcts import mcts
import synthesis
from datetime import datetime
os.environ['PATH'] = '/home/tansu/game'
os.environ['PATH'] += ':/home/tansu/venv/bin'

# 736786, 'next'
target = SMILESRead(StringIO("CCN1CCN(CC2=CC=C(NC3=NC=C(F)C(=N3)C3=CC(F)=C4N=C(C)N(C(C)C)C4=C3)N=C2)CC1"), ignore=True).read()[0]
# target = SDFread('serotonine.sdf').read()[0]
#target.implicify_hydrogens()
print(target)
play = synthesis.SimpleSynthesis(target, step_number=1000000)


def probability(delta, t):
    p = math.exp(-delta/t)
    return p


def act(p):
    value = random.random()
    if value <= p:
        a = 1
    else:
        a = 0
    return a


def simulated_random(t0, tend):
    t = t0
    reward = 0
    step = 0
    actions = play.action_space
    action = random.choice(actions)
    while t > tend:
        play.reset()
        action = random.choice(actions)
        nstate, nreward, ndone, ninfo = play.step(action)
        if nreward >= 0.3:
            reward = nreward
            t = tend
        else:
            p = probability(0.3 - nreward, t)
            if act(p) == 0: # чтобы сначала была маленькая вероятность, а потом - большая
                reward = nreward
                t = tend
            else:
                t = t * 0.8
    while step != 10:
        naction = random.choice(actions)
        nstate, nreward, ndone, ninfo = play.step(naction)
        if nreward > reward:
            reward = nreward
            step += 1
        else:
            play.reset()
            state, reward, done, info = play.step(action)
    print('PATH:', play.render())
    return reward


simulated_random(10, 0.1)


def vector(t_start):
    start_time = datetime.now()
    t = t_start
    state = None
    new_state = None
    reward = 0
    new_reward = 0
    step_num = 0
    st = 0
    actions = play.action_space
    current_av = random.choices(actions, k=10)
    print('current_av', current_av)
    for action in current_av:
        state, reward, done, info = play.step(action)
    path = play.render()
    best_vector = (state, reward, path)
    print('best_vector', best_vector)
    print('\n'.join(map(str, path)))
    action_vector = current_av
    action_vector[random.randint(0, 9)] = random.choice(actions)
    while st < 1000:
        play.reset()
        print('action_vector', action_vector)
        for action in action_vector:
            new_state, new_reward, new_done, new_info = play.step(action)
        if new_reward > reward:
            current_av = action_vector
            state = new_state
            reward = new_reward
            print('new is better')
        else:
            p = probability(reward - new_reward, t)
            if act(p) == 1:
                current_av = action_vector
                reward = new_reward
                state = new_state
                print('new is NOT better, but accepted')
            else:
                print('NOT ACCEPT')
        current_av[random.randint(0, 9)] = random.choice(actions)
        action_vector = current_av
        print('best_vector', best_vector)
        if best_vector[1] < reward:
            path = play.render()
            best_vector = (state, reward, path)
        print('best_vector', best_vector)
        print('\n'.join(map(str, path)))
        print('_____________________________________________________________')
        if step_num < 50:
            t = 0.8 * t
            step_num += 1
        else:
            t = t_start
            step_num = 0
        st += 1
        print(st)
    print(datetime.now() - start_time)
    print(best_vector)


vector(1000)
