# -*- coding: utf-8 -*-
# Python version: 3
#
# Bash format Code loader
# Simon Fraser University
# Ruoyi Wang
#
#
from bashlex.ast import node as BashAst
import sys
import os

from natlang.format.astTree import AstNode as BaseNode


class AstNode(BaseNode):
    def find_literal_nodes(self):
        if self.value[0] == 'LITERAL':
            return [self]
        else:
            nodes = []
            node = self.child
            while node is not None:
                nodes.extend(node.find_literal_nodes())
                node = node.sibling
            return nodes

    def export(self):
        pass


class _TmpNode:
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value
        self.children = []

    def __repr__(self):
        return 'TmpNode({}, {})'.format(repr(self.tag), repr(self.value))


def tree2ast(root):
    if root is None:
        return None
    elif root.value[0] == 'LITERAL':
        return root.value[1]
    elif root.value[0] == 'DUMMY':
        return None
    elif root.value[0] == 'ROOT':
        return tree2ast(root.child)
    elif root.value[0].endswith('_vec'):
        children = []
        n = root.child
        while n is not None:
            ast_node = tree2ast(n)
            n = n.sibling
            if ast_node is not None:
                children.append(ast_node)
        return children
    elif root.value[0].endswith('_optional'):
        return tree2ast(root.child)
    else:
        children = []
        n = root.child
        while n is not None:
            ast_node = tree2ast(n)
            n = n.sibling
            children.append(ast_node)
        root_ast_node = BashAst(kind=root.value[0], children=children)  # todo: fix
        return root_ast_node


def iter_fields(bash_ast):
    return [(k, v) for k, v in bash_ast.__dict__.items() if k != 'kind']


def _translate(bash_ast):
    """translate bash ast into custom class TmpNode"""

    if isinstance(bash_ast, _TmpNode):
        for i, child in enumerate(bash_ast.children):
            bash_ast.children[i] = _translate(child)
        return bash_ast
    elif not isinstance(bash_ast, BashAst):
        # literal
        return _TmpNode('LITERAL', bash_ast)
    else:
        node = _TmpNode(bash_ast.kind, None)
        for field, value in iter_fields(bash_ast):
            if isinstance(value, list):
                # star-production
                # this child is a list
                # transform into a standalone node
                vec_child = _TmpNode(field + '_vec', None)
                vec_child.children = list(value)
                node.children.append(vec_child)
            elif value is None:
                # optional-production
                vec_child = _TmpNode(field + '_optional', None)
                node.children.append(vec_child)
            else:
                node.children.append(value)

        for i, child in enumerate(node.children):
            node.children[i] = _translate(child)

        return node


def _restructure_rec(node, orig_children):
    """
    `node` is the already transformed node (type=tree.Node)
    `orig_children` is a list of the children corresponds to `node`
        (type=[TmpNode])
    """
    # edge case
    tag = node.value[0]
    if (tag.endswith('_vec') or tag.endswith('_optional')) and \
            not orig_children:
        # transformed grammar with no children
        dummy = AstNode()
        dummy.value = ('DUMMY', None)
        node.child = dummy
        dummy.parent = node

    # transform each child node
    child_nodes = []
    for orig_child in orig_children:
        child_node = AstNode()
        if orig_child.value is None:
            # internal node
            child_node.value = (orig_child.tag,)
        else:
            # leaf node
            child_node.value = (orig_child.tag, orig_child.value)
        child_nodes.append(child_node)

    # link child nodes
    for i, child_node in enumerate(child_nodes):
        child_node.parent = node
        if i == 0:
            node.child = child_node
        if i + 1 < len(child_nodes):
            # not last node
            child_node.sibling = child_nodes[i + 1]

    # recurse
    for child_node, orig_child in zip(child_nodes, orig_children):
        _restructure_rec(child_node, orig_child.children)


def _restructure(tmp_node, node_cls=AstNode):
    """transform the structure of TmpNode into Custom node class
    node_cls should be a subclass of AstNode"""
    node = node_cls()
    if tmp_node.value is None:
        node.value = (tmp_node.tag,)
    else:
        node.value = (tmp_node.tag, tmp_node.value)

    _restructure_rec(node, tmp_node.children)

    # append topmost root node
    root = node_cls()
    root.value = ('ROOT',)
    root.child = node
    node.parent = root
    return root


def bashAst2astTree(bash_ast, node_cls=AstNode):
    root = _translate(bash_ast)
    res_root = _restructure(root, node_cls)
    res_root.refresh()
    return res_root


def load(fileName, linesToLoad=sys.maxsize, verbose=True, option=None,
         no_process=False):
    """
    WARNING: this function assumes `[PREFIX].token_maps.pkl` is in the same
    directory as the code file
    `token_maps.pkl` should be a {int->[str]} mapping of copied words
    """
    import progressbar
    import pickle
    import itertools
    orig_name = os.path.basename(fileName)
    fileName = os.path.expanduser(fileName)

    if option == {}:
        option = None

    if option is None:
        option = {}
        option['mapping_path'] = \
            os.path.dirname(os.path.abspath(fileName)) + \
            '/{}.token_maps.pkl'.format(orig_name[:-13])
    # print(option['mapping_path'])

    if no_process:
        token_maps = []
    else:
        with open(option['mapping_path']) as mapping_f:
            token_maps = pickle.load(mapping_f)

    roots = []
    i = 0
    widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(),
               progressbar.FormatLabel(
                   '; Total: %(value)d sents (in: %(elapsed)s)')]
    if verbose is True:
        loadProgressBar = \
            progressbar.ProgressBar(widgets=widgets,
                                    maxval=min(
                                        sum(1 for line in open(fileName)),
                                        linesToLoad)).start()
    for line in open(fileName):
        i += 1
        if verbose is True:
            loadProgressBar.update(i)
        code = eval(line)
        roots.append(python2astTree(code))
        if i == linesToLoad:
            break

    for root, tokens_map in itertools.izip_longest(roots, token_maps,
                                                   fillvalue={}):
        literal_nodes = root.find_literal_nodes()
        for node in literal_nodes:
            if node.value[1] in tokens_map.values():
                node.value = node.value[0], '<COPIED>'

    if verbose is True:
        loadProgressBar.finish()

    return roots


def draw_tmp_tree(root, name='tmp'):
    from graphviz import Graph
    import os
    import errno
    try:
        os.makedirs('figures')
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

    fname = 'figures/{}'.format(name + '.gv')
    g = Graph(format='png', filename=fname)

    fringe = [root]
    while fringe:
        node = fringe.pop()
        g.node(str(id(node)), repr(node))
        for child in node.children:
            fringe.append(child)
            g.node(str(id(child)), repr(node))
            g.edge(str(id(node)), str(id(child)))

    return g.render()


def repr_n(node):
    return 'Node{}'.format(repr(node.value))


def draw_res_tree(root, name='res'):
    from graphviz import Graph
    import os
    import errno
    try:
        os.makedirs('figures')
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

    fname = 'figures/{}'.format(name + '.gv')
    g = Graph(format='png', filename=fname)
    g.attr(rankdir='BT')

    fringe = [root]
    while fringe:
        node = fringe.pop()
        g.node(str(id(node)), repr_n(node))
        if node.child is not None:
            child = node.child
            fringe.append(child)
            g.node(str(id(child)), repr_n(node))
            # g.edge(str(id(node)), str(id(child)), color='red')

        if node.sibling is not None:
            sibling = node.sibling
            fringe.append(sibling)
            # g.node(str(id(sibling)), repr_n(node))
            # g.edge(str(id(node)), str(id(sibling)), color='blue')

        if node.parent is not None:
            g.edge(str(id(node)), str(id(node.parent)), color='green')

    return g.render()


if __name__ == '__main__':
    import pickle

    with open('/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/train.cm.filtered.ast.pkl', 'rb') as f:
        l = pickle.load(f)

    for t in l:
        if t is None:
            print('found None')
            continue
        bash_ast = t
        root = _translate(bash_ast)
        res_root = _restructure(root)
