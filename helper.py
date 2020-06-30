from CGRtools.containers import MoleculeContainer
from CIMtools.preprocessing import FragmentorFingerprint
from config import *
from operator import itemgetter
from pmapper.customize import load_factory
from pony.orm import db_session
from rdkit import Chem, DataStructs
from rdkit.Chem import Crippen
from rdkit.Chem.Pharm2D import Generate
from rdkit.Chem.Pharm2D.SigFactory import SigFactory


def dictionary(db):
    mol_dict = {}
    with db_session:
        mol_ids = [mol.id for mol in db.Molecule.select()]
    a = 0
    for n, id in enumerate(mol_ids):
        mol_dict[n] = id
        a += 1
    mol_dict[a] = 'next'
    for i in range(a+1, a+184196):
        mol_dict[i] = 'none'
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


def best_n_molecules(reactions_list, n):
    return sorted(reactions_list, key=lambda x: x.meta.get('tanimoto'), reverse=True)[:n]


def best_n_logp(reactions_list, n):
    return sorted(reactions_list, key=lambda x: x.meta.get('log_p'), reverse=True)[:n]


def best_pharm(reactions_list, n):
    return sorted(reactions_list, key=lambda x: x.meta.get('pharm'), reverse=True)[:n]


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


def logp(mol):
    print('mol', mol)
    #a = mol.depict()
    mol = str(mol)
    mol = mol.replace('N(=O)O', '[N+](=O)[O-]')
    mol = mol.replace('N(O)=O', '[N+]([O-])=O')
    mol = mol.replace('n(O)', '[n+]([O-])')
    print('mol!!', mol)
    #mol.kekule()
    m = Chem.MolFromSmiles(mol, sanitize=True)
    try:
        logp = Chem.Crippen.MolLogP(m)
        return logp
    except:
        return -101


def pharmacophore(mol, target):
    i = 0
    print('mol/target', mol, target)
    mol.standardize()
    target.standardize()
    mol = str(mol)
    mol = mol.replace('N(=O)O', '[N+](=O)[O-]')
    mol = mol.replace('N(O)=O', '[N+]([O-])=O')
    mol = mol.replace('n(O)', '[n+]([O-])')
    target = str(target)
    target = target.replace('N(=O)O', '[N+](=O)[O-]')
    target = target.replace('N(O)=O', '[N+]([O-])=O')
    target = target.replace('n(O)', '[n+]([O-])')
    featfactory = load_factory()
    sigfactory = SigFactory(featfactory, minPointCount=2, maxPointCount=3, trianglePruneBins=False)
    sigfactory.SetBins([(0, 2), (2, 5), (5, 8)])
    sigfactory.Init()
    mol1 =Chem.MolFromSmiles(mol)
    mol2 =Chem.MolFromSmiles(target)
    if mol1 and mol2:
        fp1 = Generate.Gen2DFingerprint(mol1, sigfactory)
        fp2 = Generate.Gen2DFingerprint(mol2, sigfactory)
        sims = DataStructs.TanimotoSimilarity(fp1, fp2)
        return sims
    else:
        i = i + 1
        print('ошибка', i, mol)
        return -100


__all__ = ['dictionary', 'evaluation', 'best_n_molecules', 'reactions_by_fg', 'group_list', 'logp', 'best_n_logp', 'best_pharm', 'pharmacophore']
