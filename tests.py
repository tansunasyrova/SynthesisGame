from CGRtools.files import SMILESread, SDFread
from io import StringIO
import random
import os
import synthesis

os.environ['PATH'] = '/home/tansu/game'
os.environ['PATH'] += ':/home/tansu/venv/bin'

# 736786, 'next'
# 736785, 'none'


def random_func(n):
    actions = play.action_space
    for i in range(n):
        action = random.choice(actions)
        print(action, ',', play.step(action))
    print('PATH:', play.render())


target = SMILESread(StringIO("CCCOC")).read()[0]
# target = SDFread('serotonine.sdf').read()[0]
target.implicify_hydrogens()
print(target)
play = synthesis.SimpleSynthesis(target, step_number=100)


# random_func(5)

a1 = play.step(736786)  # next - но там еще ничего нет, правильный отклик 'no reaction products found'
print('0!', a1)
a = play.step(736785)  # none - однореагентная реакция, но там ничего нет, правильный отклик 'no current molecule'
print('1!', a)
b = play.step(2)  # пытаюсь сделать 2-реагентную реакцию с этой молекулой, но там ничего нет =>
# 1-реагентная реакция молекулы "2". 0+1 (количество реакций в пути, было 0, стало 1)
print('2!', b)
c = play.step(736785)  # none - однореагентная реакция 1+1
print('3!', c)
d = play.step(5)  # 2-реагентная реакция текущей молекулы с молекулой "5", но она не получилась, поэтому, state остается
print('4!', d)
e = play.step(736785)  # none - однореагентная реакция 2+1
print('5!', e)
f = play.step(736784)  # 2-реагентная реакция текущей молекулы с последней молекулой "736784" 3+1
print('6!', f)  # получилось 2 новые реакции, почему-то ReactionContainer у них разные, но сами реакции одинаковые
g = play.step(736786)  # next - просим следующую (последнюю) молекулу из листа молекул, правильно пишет =>
print('7!', g)  # 'the last molecule at the list'. 3+1(!) (один "!" значит, что в пути была замена последней реакции, =>
# из-за того, что мы просили next
h = play.step(736786)  # next - снова просим следующую (ту же последнюю), результат снова правильный
print('8!', h)
j = play.step(736785)  # none - однореагентная реакция 4+1
print('9!', j)
k = play.step(736786)  # next - просим следующую молекулу 4+1(!), но получаем такую же молекулу, =>
#  тк там одинаковые реакции (ПОЧEМУ?)
print('10!', k)
print('PATH:', play.render())  # просим путь, в котором должно быть 5 реакций, он верный
m = play.step(736786)  # next - просим следующую молекулу 4+1(!!)
print('11!', m)  # next - просим следующую молекулу 4+1(!!)
print('PATH:', play.render())  # просим путь, в котором должно быть 5 реакций, он верный
