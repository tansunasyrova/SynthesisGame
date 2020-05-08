from CIMtools.preprocessing import FragmentorFingerprint
from config import *
from operator import itemgetter
from pony.orm import db_session


def dictionary(db):
    mol_dict = {}
    with db_session:
        mol_ids = [mol.id for mol in db.Molecule.select()]
    a = 0
    for n, id in enumerate(mol_ids):
        mol_dict[n] = id
        a += 1
    mol_dict[a] = 'none'
    mol_dict[a + 1] = 'next'
    return mol_dict


def evaluation(mol1, mol2):
    """
    оценка нод.
    возвращает танимото для пары запрос-результат.
    """
    f = FragmentorFingerprint(max_length=6, workpath='/tmp')
    mol1_fp = set(f.transform_bitset([mol1])[0])
    mol2_fp = set(f.transform_bitset([mol2])[0])
    mol1_c, mol2_c, common = len(mol1_fp), len(mol2_fp), len(mol1_fp.intersection(mol2_fp))
    return common / (mol1_c + mol2_c - common)


def best_n_molecules(reactions_list, target, n):
    tanimoto_list = []
    for reaction in reactions_list:
        # print('i am reaction from reactionlist', reaction)
        # print('!reaction.products!', reaction.products)
        for product in reaction.products:
            # print('PRODUCT', product)
            tanimoto_list.append((product, reaction, evaluation(product, target)))
    return sorted(tanimoto_list, key=itemgetter(2), reverse=True)[:n]


def reactions_by_fg(group_id_list, single=True):
    reactions_list = []
    rules = single_rules if single else double_rules
    for react in rules:
        reaction_groups = rules[react]
        if any(group in reaction_groups for group in group_id_list):
            reactions_list.append(react)
    return reactions_list


def group_list(structure, db):
    with db_session:
        molecule = db.Molecule.find_structure(structure)
    if molecule:
        with db_session:
            groups_list = [x.id for x in db.Molecule[molecule.id].classes]
    else:
        molecule = structure
        with db_session:
            groups_list = [i for i, fg in groups.items() if fg < molecule]
    return groups_list


__all__ = ['dictionary', 'evaluation', 'best_n_molecules', 'reactions_by_fg', 'group_list']
