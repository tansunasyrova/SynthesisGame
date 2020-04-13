from pony.orm import db_session
from operator import itemgetter
from CIMtools.preprocessing import FragmentorFingerprint


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


def best_n_molecules(self, reactions_list, n):
    tanimoto_list = []
    for reaction in reactions_list:
        for product in reaction.products:
            tanimoto_list.append((product, reaction, self.evaluation(product, self.target)))
    return sorted(tanimoto_list, key=itemgetter(2), reverse=True)[:n]


def reactions_by_fg(self, group_id_list, n):
    reactions_list = []
    if n == 1:
        for react in self.single_rules:
            reaction_groups = self.single_rules[react]
            if any(group in reaction_groups for group in group_id_list):
                reactions_list.append(react)
    if n == 2:
        for react in self.double_rules:
            reaction_groups = self.double_rules[react]
            if any(group in reaction_groups for group in group_id_list):
                reactions_list.append(react)
    return reactions_list


def group_list(self, structure):
    with db_session:
        molecule = self.db.Molecule.find_structure(structure)
    if molecule:
        with db_session:
            group_list = [x.id for x in self.db.Molecule[molecule.id].classes]
    else:
        group_list = []
        molecule = structure
        for i, fg in self.groups.items():
            if fg < molecule:
                group_list.append(i)
    return group_list


__all__ = ['dictionary', 'evaluation', 'best_n_molecules', 'reactions_by_fg', 'group_list']
