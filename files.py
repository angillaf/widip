import functools
import pathlib

import yaml
from discopy.frobenius import Ty, Diagram, Hypergraph as H, Box, Functor, Swap, Category, Id

from loader import HypergraphLoader
from composing import expand_name_functor, glue_diagrams, replace_id_ty


def path_diagram(path: pathlib.Path):
    # TODO during recursion some tags have relative references
    dir_d = None
    file_d = None
    if path.is_dir():
        dir_d = dir_diagram(path)
        file_path = path.with_suffix(".yaml")
        if file_path.exists():
            file_d = file_diagram(file_path)
    elif path.suffix == ".yaml":
        file_d = file_diagram(path)
        dir_path = path.with_suffix("")
        if dir_path.is_dir():
            dir_d = dir_diagram(dir_path)

    diagram = Id()
    if dir_d is not None and file_d is not None:
        diagram = glue_diagrams(file_d, dir_d)
    elif dir_d is not None:
        diagram = dir_d
    elif file_d is not None:
        diagram = file_d
    Diagram.to_gif(diagram, path=str(path.with_suffix('.gif')))
    return diagram

def dir_diagram(path: pathlib.Path):
    f = expand_name_functor(path.stem)
    dir_diagrams = (
        f(path_diagram(subpath))
        for subpath in path.iterdir())
    diagram = Id().tensor(*dir_diagrams)
    return diagram

def file_diagram(path: pathlib.Path):
    file_diagrams = yaml.compose_all(open(path), Loader=HypergraphLoader)
    i = 0
    diagram = None
    for d in file_diagrams:
        if i == 0:
            diagram = d
        else:
            diagram = glue_diagrams(diagram, d)
        i += 1
    if i == 0:
        return Id()
    return diagram