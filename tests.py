import synthesis
from CGRtools.files import SMILESread, SDFread
from io import StringIO
import random
from CGRdb import load_schema
from pony.orm import db_session
import os
os.environ['PATH'] = '/home/tansu/rnn'
os.environ['PATH'] = '/home/tansu/env/bin'
# 736785, 'next'
# 736784, 'none'


def random_func(n):
    actions = play.action_space
    for i in range(n):
        action = random.choice(actions)
        print(action, ',', play.step(action))


target = SMILESread(StringIO("CCCOC")).read()[0]
#target = SDFread('serotonine.sdf').read()[0]
target.implicify_hydrogens()
print(target)
play = synthesis.SimpleSynthesis(target, step_number=100)


random_func(100)

# c = play.reset()
# d = play.step(736784)
# print('1!!!!!!!!!', d)
# e = play.step(19)
# print('2!!!!!!!!!', e)
# f = play.step(0)
# print('3!!!!!!!!!', f)
# # g = play.step(25)
# # print('4!!!!!!!!!', str(g[0]), g[1])
# print('mol list', play.products)
# h = play.step(0)
# print('4!!!!!!!!!', str(h[0]), h[1])
# print('mol list', play.products)
# j = play.step(0)
# print('5!!!!!!!!!', str(j[0]), j[1])
