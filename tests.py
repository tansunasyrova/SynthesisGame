from CGRtools.files import SMILESread, SDFread
from io import StringIO
import random
import os
import synthesis
from datetime import datetime


os.environ['PATH'] = '/home/tansu/game'
os.environ['PATH'] += ':/home/tansu/venv/bin'

# 736786, 'next'
# 736785, 'none' 'next'


def random_func(n):
    actions = play.action_space
    start_time = datetime.now()
    step = 0
    for i in range(n):
        action = random.choice(actions)
        print(action, ',', play.step(action))
        step += 1
        print(step)
    print('PATH:', play.render())
    print(datetime.now() - start_time)
    print('среднее', (datetime.now() - start_time)/n)


target = SMILESread(StringIO("CCCOC")).read()[0]
# target = SDFread('serotonine.sdf').read()[0]
target.implicify_hydrogens()
print(target)
play = synthesis.SimpleSynthesis(target, step_number=1000)

random_func(1000)


# a1 = play.step(736786)  # next - но там еще ничего нет, правильный отклик 'no reaction products found'
# print('0!', a1)
# a = play.step(736785)  # none - однореагентная реакция, но там ничего нет, правильный отклик 'no current molecule'
# print('1!', a)
# b = play.step(2)  # пытаюсь сделать 2-реагентную реакцию с этой молекулой, но там ничего нет =>
# # 1-реагентная реакция молекулы "2". 0+1 (количество реакций в пути, было 0, стало 1)
# print('2!', b)
# c = play.step(736785)  # none - однореагентная реакция 1+1
# print('3!', c)
# d = play.step(5)  # 2-реагентная реакция текущей молекулы с молекулой "5", но она не получилась, поэтому, state остается
# print('4!', d)
# e = play.step(736785)  # none - однореагентная реакция 2+1
# print('5!', e)
# f = play.step(736784)  # 2-реагентная реакция текущей молекулы с последней молекулой "736784" 3+1
# print('6!', f)  # получилась 1 новая реакция (не 2, как раньше)
# g = play.step(736786)  # next - просим следующую молекулу из листа молекул, но там нет, правильно пишет =>
# print('7!', g)  # 'the last molecule at the list'.
# j = play.step(736785)  # none - однореагентная реакция 4+1
# print('8!', j)
# k = play.step(736786)  # next - просим следующую молекулу 4+1(!)
# print('9!', k)
# print('PATH:', play.render())  # просим путь, в котором должно быть 5 реакций, но он пропустил одну
# m = play.step(736786)  # next - просим следующую молекулу 4+1(!!)
# print('11!', m)
# print('PATH:', play.render())  # просим путь, в котором должно быть 5 реакций, он верный
# n = play.step(5)  # 2-реагентная реакция текущей молекулы с молекулой "5", но она не получилась, поэтому, state остается
# print('12!', n)
# p = play.step(736786)  # next - просим следующую молекулу 4+1(!!!)
# print('13', p)  # выходит 4-ая молекула из списка после шага 8! - так и должно быть
# print('PATH:', play.render())  # проверяем путь - там всё правильно заменилось
# q = play.step(736786)  # next - просим следующую молекулу 4+1(!!!!)
# q1 = play.step(736786)  # next - просим следующую молекулу 4+1(5!)
# q2 = play.step(736786)  # next - просим следующую молекулу 4+1(6!)
# q3 = play.step(736786)  # next - просим следующую молекулу 4+1(7!)
# q4 = play.step(736786)  # next - просим следующую молекулу 4+1(8!)
# q5 = play.step(736786)  # next - просим следующую молекулу 4+1(9!) - это последняя молекула в том списке
# print('14!', q5)
# q6 = play.step(736786)  # тут он должен вернуть самый первый state из списка
# print('15!', q6)
# q7 = play.step(736786)  # продолжает возвращать тот же state - как и должен
# print('16!', q7)
# print('PATH:', play.render())
# print('\n'.join(map(str, play.render())))

a = play.step(736)  # none - однореагентная реакция, но там ничего нет, правильный отклик 'no current molecule'
print('1!', a)
b = play.step(736800)
print('2!', b)
c = play.step(920000)
print('3!', c)
d = play.step(9200000)
print('4!', d)
print('\n'.join(map(str, play.render())))