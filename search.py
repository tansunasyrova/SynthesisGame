from datetime import datetime
from CGRtools.files import SMILESRead
from io import StringIO
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import random
from rdkit import Chem
from rdkit.Chem import Crippen
from rdkit.Chem import Descriptors
from rdkit.Chem.QED import QEDproperties
import synthesis
import synthesis_pharm
import synthesis_logP

os.environ['PATH'] = '/home/tansu/game'
os.environ['PATH'] += ':/home/tansu/venv/bin'

# 736786, 'next'
target = SMILESRead(StringIO("CC(CCC1=CC=C(O)C=C1)NCCC1=CC(O)=C(O)C=C1"), ignore=True).read()[0]
# target = SDFread('serotonine.sdf').read()[0]
#target.implicify_hydrogens()
print(target)
#play = synthesis.SimpleSynthesis(target, step_number=1000000)
#play = synthesis_logP.SimpleSynthesis(step_number=1000000)
play = synthesis_pharm.SimpleSynthesis(target, step_number=1000000)


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


# def simulated_random(n, i):
#     start_time = datetime.now()
#     step = 0
#     actions = play.action_space
#     best = [(None, -1000)]
#     while n != 0:
#         play.reset()
#         action = random.choice(actions)
#         print('action1', action)
#         nstate, nreward, ndone, ninfo = play.step(action)
#         if nreward:
#             if best[0][1] < nreward:
#                 best[0] = (action, nreward)
#                 print('best', best)
#         print('nresults', nstate, nreward, ndone, ninfo)
#         if nreward >= 0.3:
#             continue
#         else:
#             n -= 1
#             print(n)
#     print('best!', best)
#     play.reset()
#     action = best[0][0]
#     state, reward, done, info = play.step(action)
#     path = []
#     max_step = 0
#     while step != 5 or max_step < 10000:
#         print('ШАААААААГГ', i)
#         max_step += 1
#         naction = random.choice(actions)
#         nstate, nreward, ndone, ninfo = play.step(naction)
#         print('nresults-2', naction, nstate, nreward, ndone, ninfo)
#         print('path?????', play.state, path)
#         if nreward > reward:
#             reward = nreward
#             state = nstate
#             path.append(play.render()[-1])
#             step += 1
#             print('step', step)
#         else:
#             play.state = state
#             print('path?', play.state, path)
#     time = datetime.now() - start_time
#     print('len path', len(path), path)
#     print('\n'.join(map(str, path)))
#     print(time)
#     print(reward)
#     return reward, path, time
#
#
# def repeat_random(n):
#     best_reward = 0.0
#     best_path = []
#     best_time = None
#     plt.axis([0, 100, 0, 1])
#     x = list()
#     y = list()
#     for i in range(0, n):
#         print('ШАГ', i)
#         reward, path, time = simulated_random(1000, i)
#         if reward > best_reward:
#             best_reward = reward
#             best_path = path
#             best_time = time
#             x.append(i)
#             y.append(best_reward)
#     fig, ax = plt.subplots()
#     ax.plot(x, y)
#     ax.yaxis.set_label_position('left')
#     ax.set_ylabel(u'Лучший коэффициент Танимото')
#     ax.xaxis.set_label_position('bottom')
#     ax.set_xlabel(u'Шаг')
#     plt.grid(True)
#     pwd = os.getcwd()
#     iPath = './{}'.format('png')
#     if not os.path.exists(iPath):
#         os.mkdir(iPath)
#     os.chdir(iPath)
#     fig.savefig('{}.{}'.format('pharm_Atenolol_random', 'png'), fmt='png')
#     os.chdir(pwd)
#     print('best reward', best_reward)
#     print('time', best_time)
#     print('\n'.join(map(str, best_path)))


def repeat_random_2(n):
    m = 1000
    actions = play.action_space
    best = [(None, -1000)]
    while m != 0:
        play.reset()
        action = random.choice(actions)
        print('action1', action)
        nstate, nreward, ndone, ninfo = play.step(action)
        if nreward < 0.4:
            if nreward:
                if best[0][1] < nreward:
                    best[0] = (action, nreward)
                    print('best action, nreward', best)
            print('nresults', nstate, nreward, ndone, ninfo)
        m -= 1
        print('m', m)
    print('итоговый best! начальной мол-лы', best)
    play.reset()
    action = best[0][0]
    best_reward = 0.0
    best_reward_path = []
    best_reward_time = None
    plt.axis([0, 10, 0, 1])
    x = list()
    y = list()
    for i in range(0, n):
        reward, path, time = simulated_random_2(i, action)
        if reward > best_reward:
            best_reward = reward
            best_reward_path = path
            best_reward_time = time
        x.append(i)
        y.append(reward)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.yaxis.set_label_position('left')
    ax.set_ylabel(u'Фармакофорное сходство') #Фармакофорное сходство #Kоэффициент Танимото
    ax.xaxis.set_label_position('bottom')
    ax.set_xlabel(u'Шаг')
    plt.grid(True)
    pwd = os.getcwd()
    iPath = './{}'.format('png')
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    os.chdir(iPath)
    fig.savefig('{}.{}'.format('Pharm_Фармакофорное сходство_random10_v3', 'png'), fmt='png') #Pharm_Dobutamine_new_random10__
    os.chdir(pwd)
    print('best reward', best_reward)
    print('time', best_reward_time)
    print('\n'.join(map(str, best_reward_path)))


def simulated_random_2(i, action):
    start_time = datetime.now()
    step = 0
    max_step = 0
    path = []
    actions = play.action_space
    state, reward, done, info = play.step(action)
    while step != 5 and max_step < 1000:
        max_step += 1
        print('ШАААААААГГ', i, 'max_step', max_step)
        naction = random.choice(actions)
        nstate, nreward, ndone, ninfo = play.step(naction)
        print('nresults_in_simulated_random', naction, nstate, nreward, ndone, ninfo)
        print('path_in_simulated_random', play.state, path)
        if nreward > reward:
            reward = nreward
            state = nstate
            path.append(play.render()[-1])
            step += 1
            print('step', step)
        else:
            play.state = state
            print('лучше не стало')
    time = datetime.now() - start_time
    print('len path', len(path), path)
    print('\n'.join(map(str, path)))
    print(time)
    print(reward)
    return reward, path, time


def vector(t_start):
    start_time = datetime.now()
    t = t_start
    state = None
    new_state = None
    reward = 0
    new_reward = 0
    step_num = 0
    st = 0
    plt.axis([0, 10000, -100, 50])
    x = list()
    y = list()
    actions = play.action_space
    current_av = random.choices(actions, k=5)
    print('current_av', current_av)
    for action in current_av:
        state, reward, done, info = play.step(action)
    path = play.render()
    best_vector = (state, reward, path)
    print('best_vector', best_vector)
    print('\n'.join(map(str, path)))
    action_vector = current_av
    action_vector[random.randint(0, 4)] = random.choice(actions)
    while st < 10001:
        play.reset()
        print('action_vector', action_vector)
        for action in action_vector:
            new_state, new_reward, new_done, new_info = play.step(action)
        if new_reward > reward:
            current_av = action_vector
            state = new_state
            reward = new_reward
            print('new is better', reward)
            if best_vector[1] < reward:
                path = play.render()
                best_vector = (state, reward, path)
        else:
            p = math.exp(- (reward - new_reward) / t)
            value = random.random()
            if value <= p:
                current_av = action_vector
                reward = new_reward
                print('new is NOT better, but accepted', reward)
            else:
                print('NOT ACCEPT')
        current_av[random.randint(0, 4)] = random.choice(actions)
        action_vector = current_av
        print('best_vector', best_vector)
        print('\n'.join(map(str, path)))
        print('_____________________________________________________________')
        if step_num < 100:
            t = 0.9 * t
            step_num += 1
        else:
            t = t_start
            step_num = 0
        st += 1
        x.append(st)
        y.append(best_vector[1])
        print(st)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.yaxis.set_label_position('left')
    ax.set_ylabel(u'Лучшее фармакофорное сходство')  #Фармакофорное сходство  #Kоэффициент Танимото
    ax.xaxis.set_label_position('bottom')
    ax.set_xlabel(u'Шаг')
    plt.grid(True)
    pwd = os.getcwd()
    iPath = './{}'.format('png')
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    os.chdir(iPath)
    fig.savefig('{}.{}'.format('PV_Dobutamine ', 'png'), fmt='png') #pharm_Atenolol_vector_v2
    os.chdir(pwd)
    print(datetime.now() - start_time)
    print(best_vector)
    print('\n'.join(map(str, best_vector[2])))


repeat_random_2(10)

#simulated_random(1000)
#vector(10000)
#repeat_random(9)
# m = Chem.MolFromSmiles('CCOCC')
# print(m)
# a = Chem.Crippen.MolLogP(m)
# b = Crippen.MolLogP(m)
# #s = Chem.QED.QEDproperties.ALOGP
# print(a)
# print(b)
# #print(s)
# Chem.MolToSmiles()
