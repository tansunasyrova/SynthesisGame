from CGRdb import load_schema
from CGRtools.containers import ReactionContainer
from CGRtools.files import RDFread, SDFwrite
from CGRtools.files.SDFrw import SDFread
from config import *
from datetime import datetime
import pickle
from pony.orm import db_session

db = load_schema('bb', user=user, password=password, database=database, host=host)
Reagents = db.Molecule


def fill_mol_mol_class():
    with open('group_dict_12.pickle', 'rb') as f:
        group_dict = pickle.load(f)
    with db_session:
        reagents = list(db.Molecule.select())
        id_mol_dict = {molecule.id: molecule.structure for molecule in reagents}
    for mol_id, molecule in id_mol_dict.items():
        id_list = []
        for i, fg in group_dict.items():
            if fg < molecule:
                with db_session:
                    id_list.append(i)
        with db_session:
            Reagents[mol_id].classes = [db.MoleculeClass[x] for x in id_list]


@db_session
def fill_the_reagents_base():
    """
    Fill the 'Molecule' table of 'new_reagents' database with Reagents without duplicates.
    """
    reagents = SDFread('/home/tansu/laba_proj/BB_ZINC/acbbb_p0.0.sdf').read()
    for mol in reagents:
        if not Reagents.structure_exists(mol):  # проверка есть ли это в базе или нет
            Reagents(mol, db.User[1])


@db_session
def fill_db_with_fg():
    with open('group_dict_12.pickle', 'rb') as f:
        group_dict = pickle.load(f)
    for n, group in group_dict.items():
        db.MoleculeClass(id=n, name=str(group), _type=0)


@db_session
def index_reagents():
    with open('group_dict.pickle', 'rb') as f:
        group_dict = pickle.load(f)
    for mol in Reagents.select():
        mol.structure.reset_query_marks()
        group_list = []
        for n, group in group_dict.items():
            if group < mol.structure:
                print('ura')
                group_list.append(n)
        mol.classes = [db.MoleculeClass[x] for x in group_list]


def fg_in_react():
    fg_in_react_dict = dict()
    with open('group_dict.pickle', 'rb') as f:
        group_dict = pickle.load(f)
    reactions = set(RDFread('rules.rdf'))
    for react in reactions:
        react.reset_query_marks()
        groups_list = [] # думаю, что здесь нужно его создавать
        if len(react.reactants) == 1:
            for i in group_dict:
                if group_dict[i] < react.reactants[0]:
                    groups_list.append(i)
            if groups_list:
                fg_in_react_dict[react] = groups_list
        else:
            for reactant in react.reactants:
                groups_list = []  # думаю, что здесь нужно его создавать
                for i in group_dict:
                    if group_dict[i] < reactant:
                        groups_list.append(i)
                fg_in_react_dict[react] = groups_list
    with open('fg_in_react_dict.pickle', 'wb') as f:
        pickle.dump(fg_in_react_dict, f)


def fg_structure_id():
    group_dict = {}
    groups = set(SDFread('groups.sdf'))
    for n, group in enumerate(groups):
        group_dict[n] = group
    with open('group_dict.pickle', 'wb') as f:
        pickle.dump(group_dict, f)


def mol_with_fg(group_id_list):
    fg_mol_dict = dict()
    mol_id_sets = []

    if len(group_id_list) == 1:
        return [x.id for x in db.MoleculeClass[group_id_list[0]].structures]
    else:
        for group_id in group_id_list:
            fg_mol_dict[group_id] = [x.id for x in db.MoleculeClass[group_id].structures]
            # добавляем в словарь ключ(id группы) и значение(список соответствующих этой группе молекул)

        for group_id in fg_mol_dict:
            mol_id_sets.append(set(fg_mol_dict[group_id]))
            # создаем список, в котором содержатся сеты id молекул (каждый такой сет соответствует одной группе из
            # group_id_list)

        common_molecules = mol_id_sets[0]
        for s in mol_id_sets[1:]:
            common_molecules.intersection_update(s)
        print(common_molecules)
        # получаем сет из id молекул, которые есть у каждой группы из group_id_list


def reactions_with_fg(group_id_list):
    reactions_list = []

    with open('fg_in_react_dict.pickle', 'rb') as f:
        fg_in_react_dict_new = pickle.load(f)
    for react in fg_in_react_dict_new:
        l = fg_in_react_dict_new[react]
        if any(group in l for group in group_id_list):
            reactions_list.append(react)
    return reactions_list


startTime = datetime.now()
fg_fg = {}


def group_search_and_pickles():
    with RDFread('/home/tansu/Documents/new_rules_1.rdf') as rule_file_1, \
         RDFread('/home/tansu/Documents/new_rules_2.rdf') as rule_file_2:
        fg_in_react_dict_1 = {}
        fg_in_react_dict_2 = {}
        group_dict = {}
        for n, rule in enumerate(rule_file_1, start=1):
            if len(rule.meta['id']) > 50:
                reactants_list = rule.reactants
                reactants = reactants_list[0].split()
                print('I am reaction - ', n)
                for group in reactants:
                    i = len(group_dict) + 1
                    i = group_dict.setdefault(group, i)
                    fg_in_react_dict_1.setdefault(rule, []).append(i)

        for n, rule in enumerate(rule_file_2, start=1):
            if len(rule.meta['id']) > 50:
                reactants_list = rule.reactants
                reactants = reactants_list[0].split()
                print('I am reaction - ', n)
                rule = ReactionContainer(reactants, rule.products[0].split())
                for group in reactants:
                    i = len(group_dict) + 1
                    i = group_dict.setdefault(group, i)
                    fg_in_react_dict_2.setdefault(rule, []).append(i)

    with SDFwrite('/home/tansu/Documents/groups_12.sdf') as group_file:
        for group in group_dict:
            group_file.write(group)

    with open('group_dict_12.pickle', 'wb') as f:
        pickle.dump({i: group for group, i in group_dict.items()}, f)

    with open('fg_in_react_dict_1.pickle', 'wb') as e:
        pickle.dump(fg_in_react_dict_1, e)

    with open('fg_in_react_dict_2.pickle', 'wb') as e:
        pickle.dump(fg_in_react_dict_2, e)
