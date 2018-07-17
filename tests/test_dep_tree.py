import unittest
from support.dep_tree import parse_dep_tree, export_to_table, read_back_sentence


class TestParse(unittest.TestCase):
    def test_parse(self):
        with open('../support/sampleDepTree.txt') as file:
            forest = parse_dep_tree('../data/pb_frames', file)
        correct_0 = [[1, 'In', 'IN', 43, 'LOC', '_', '_', '_', '_', '_', 'AM-LOC'],
                     [2, 'an', 'DT', 5, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [3, 'Oct.', 'NNP', 4, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [4, '19', 'CD', 5, 'NMOD', '_', 'AM-TMP', '_', '_', '_', '_'],
                     [5, 'review', 'NN', 1, 'PMOD', 'review.01', '_', '_', '_', '_', '_'],
                     [6, 'of', 'IN', 5, 'NMOD', '_', 'A1', '_', '_', '_', '_'],
                     [7, '``', '``', 9, 'P', '_', '_', '_', '_', '_', '_'],
                     [8, 'The', 'DT', 9, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [9, 'Misanthrope', 'NN', 6, 'PMOD', '_', '_', '_', '_', '_', '_'],
                     [10, "''", "''", 9, 'P', '_', '_', '_', '_', '_', '_'],
                     [11, 'at', 'IN', 9, 'LOC', '_', '_', '_', '_', '_', '_'],
                     [12, 'Chicago', 'NNP', 15, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [13, "'s", 'POS', 12, 'SUFFIX', '_', '_', '_', '_', '_', '_'],
                     [14, 'Goodman', 'NNP', 15, 'NAME', '_', '_', '_', '_', '_', '_'],
                     [15, 'Theatre', 'NNP', 11, 'PMOD', '_', '_', '_', '_', '_', '_'],
                     [16, '(', '(', 20, 'P', '_', '_', '_', '_', '_', '_'],
                     [17, '``', '``', 20, 'P', '_', '_', '_', '_', '_', '_'],
                     [18, 'Revitalized', 'VBN', 19, 'NMOD', 'revitalize.01', '_', '_', '_', '_', '_'],
                     [19, 'Classics', 'NNS', 20, 'SBJ', '_', '_', 'A1', 'A0', '_', '_'],
                     [20, 'Take', 'VB', 5, 'PRN', 'take.01', '_', '_', '_', '_', '_'],
                     [21, 'the', 'DT', 22, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [22, 'Stage', 'NNP', 20, 'OBJ', '_', '_', '_', 'A1', '_', '_'],
                     [23, 'in', 'IN', 20, 'LOC', '_', '_', '_', 'AM-LOC', '_', '_'],
                     [24, 'Windy', 'NNP', 25, 'NAME', '_', '_', '_', '_', '_', '_'],
                     [25, 'City', 'NNP', 23, 'PMOD', '_', '_', '_', '_', '_', '_'],
                     [26, ',', ',', 20, 'P', '_', '_', '_', '_', '_', '_'],
                     [27, "''", "''", 20, 'P', '_', '_', '_', '_', '_', '_'],
                     [28, 'Leisure', 'NNP', 30, 'NAME', '_', '_', '_', '_', '_', '_'],
                     [29, '&', 'CC', 30, 'NAME', '_', '_', '_', '_', '_', '_'],
                     [30, 'Arts', 'NNS', 20, 'TMP', '_', '_', '_', '_', '_', '_'],
                     [31, ')', ')', 20, 'P', '_', '_', '_', '_', '_', '_'],
                     [32, ',', ',', 43, 'P', '_', '_', '_', '_', '_', '_'],
                     [33, 'the', 'DT', 34, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [34, 'role', 'NN', 43, 'SBJ', '_', '_', '_', '_', 'A1', 'A1'],
                     [35, 'of', 'IN', 34, 'NMOD', '_', '_', '_', '_', '_', '_'],
                     [36, 'Celimene', 'NNP', 35, 'PMOD', '_', '_', '_', '_', '_', '_'],
                     [37, ',', ',', 34, 'P', '_', '_', '_', '_', '_', '_'],
                     [38, 'played', 'VBN', 34, 'APPO', 'play.02', '_', '_', '_', '_', '_'],
                     [39, 'by', 'IN', 38, 'LGS', '_', '_', '_', '_', 'A0', '_'],
                     [40, 'Kim', 'NNP', 41, 'NAME', '_', '_', '_', '_', '_', '_'],
                     [41, 'Cattrall', 'NNP', 39, 'PMOD', '_', '_', '_', '_', '_', '_'],
                     [42, ',', ',', 34, 'P', '_', '_', '_', '_', '_', '_'],
                     [43, 'was', 'VBD', 0, 'ROOT', '_', '_', '_', '_', '_', '_'],
                     [44, 'mistakenly', 'RB', 45, 'MNR', '_', '_', '_', '_', '_', 'AM-MNR'],
                     [45, 'attributed', 'VBN', 43, 'VC', 'attribute.01', '_', '_', '_', '_', '_'],
                     [46, 'to', 'TO', 45, 'ADV', '_', '_', '_', '_', '_', 'A2'],
                     [47, 'Christina', 'NNP', 48, 'NAME', '_', '_', '_', '_', '_', '_'],
                     [48, 'Haag', 'NNP', 46, 'PMOD', '_', '_', '_', '_', '_', '_'],
                     [49, '.', '.', 43, 'P', '_', '_', '_', '_', '_', '_']]
        correct_1 = [[1, 'Ms.', 'NNP', 2, 'TITLE', '_', '_'],
                     [2, 'Haag', 'NNP', 3, 'SBJ', '_', 'A0'],
                     [3, 'plays', 'VBZ', 0, 'ROOT', 'play.02', '_'],
                     [4, 'Elianti', 'NNP', 3, 'OBJ', '_', 'A1'],
                     [5, '.', '.', 3, 'P', '_', '_']]
        self.assertEqual(export_to_table(forest[0]), correct_0)
        self.assertEqual(export_to_table(forest[1]), correct_1)


class TestReadBack(unittest.TestCase):
    def test_read_back(self):
        with open('../support/sampleDepTree.txt') as file:
            forest = parse_dep_tree('../data/pb_frames', file)

        tree = forest[1]
        original_dump = export_to_table(tree)
        new_tree = read_back_sentence(original_dump)
        new_dump = export_to_table(new_tree)
        self.assertEqual(original_dump, new_dump)


if __name__ == '__main__':
    unittest.main()
