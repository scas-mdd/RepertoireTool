#!/usr/bin/env python

import pickle

from simple_model import SimpleModel
from path_builder import PathBuilder
from vcs_git import GitInterface
from vcs_hg import HgInterface
from vcs_types import VcsTypes
from db_generator import RepDBPopulator

model = pickle.load(open("model.pickle", "r"))
proj0 = model.getProj(PathBuilder.Proj0)
proj1 = model.getProj(PathBuilder.Proj1)
path_builder = model.getPathBuilder()

rep_populator = RepDBPopulator(path_builder)
db = rep_populator.generateDB(proj0, proj1)
