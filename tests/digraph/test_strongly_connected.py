# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest

import rustworkx


class TestStronglyConnected(unittest.TestCase):
    def test_number_strongly_connected_all_strong(self):
        G = rustworkx.PyDiGraph()
        node_a = G.add_node(1)
        node_b = G.add_child(node_a, 2, {})
        node_c = G.add_child(node_b, 3, {})
        self.assertEqual(
            rustworkx.strongly_connected_components(G),
            [[node_c], [node_b], [node_a]],
        )

    def test_number_strongly_connected(self):
        G = rustworkx.PyDiGraph()
        node_a = G.add_node(1)
        node_b = G.add_child(node_a, 2, {})
        node_c = G.add_node(3)
        self.assertEqual(
            rustworkx.strongly_connected_components(G),
            [[node_c], [node_b], [node_a]],
        )

    def test_stongly_connected_no_linear(self):
        G = rustworkx.PyDiGraph()
        G.add_nodes_from(list(range(8)))
        G.add_edges_from_no_data(
            [
                (0, 1),
                (1, 2),
                (1, 7),
                (2, 3),
                (2, 6),
                (3, 4),
                (4, 2),
                (4, 5),
                (6, 3),
                (6, 5),
                (7, 0),
                (7, 6),
            ]
        )
        expected = [[5], [2, 3, 4, 6], [0, 1, 7]]
        components = rustworkx.strongly_connected_components(G)
        self.assertEqual(components, expected)

    def test_number_strongly_connected_big(self):
        G = rustworkx.PyDiGraph()
        for i in range(100000):
            node = G.add_node(i)
            G.add_child(node, str(i), {})
        self.assertEqual(len(rustworkx.strongly_connected_components(G)), 200000)


class TestCondensation(unittest.TestCase):
    def setUp(self):
        # グラフをセットアップ
        self.graph = rustworkx.PyDiGraph()
        self.node_a = self.graph.add_node("a")
        self.node_b = self.graph.add_node("b")
        self.node_c = self.graph.add_node("c")
        self.node_d = self.graph.add_node("d")
        self.node_e = self.graph.add_node("e")
        self.node_f = self.graph.add_node("f")
        self.node_g = self.graph.add_node("g")
        self.node_h = self.graph.add_node("h")

        # エッジを追加
        self.graph.add_edge(self.node_a, self.node_b, "a->b")
        self.graph.add_edge(self.node_b, self.node_c, "b->c")
        self.graph.add_edge(self.node_c, self.node_d, "c->d")
        self.graph.add_edge(self.node_d, self.node_a, "d->a")  # サイクル: a -> b -> c -> d -> a

        self.graph.add_edge(self.node_b, self.node_e, "b->e")
        self.graph.add_edge(self.node_e, self.node_f, "e->f")
        self.graph.add_edge(self.node_f, self.node_g, "f->g")
        self.graph.add_edge(self.node_g, self.node_h, "g->h")
        self.graph.add_edge(self.node_h, self.node_e, "h->e")  # サイクル: e -> f -> g -> h -> e

    def test_condensation(self):
        # condensation関数を呼び出し
        condensed_graph = rustworkx.condensation(self.graph)

        # ノード数を確認（2つのサイクルが1つずつのノードに縮約される）
        self.assertEqual(condensed_graph.node_count(), 2)  # [SCC(a, b, c, d), SCC(e, f, g, h)]

        # エッジ数を確認
        self.assertEqual(
            condensed_graph.edge_count(), 1
        )  # Edge: [SCC(a, b, c, d)] -> [SCC(e, f, g, h)]

        # 縮約されたノードの内容を確認
        nodes = list(condensed_graph.nodes())
        scc1 = nodes[0]
        scc2 = nodes[1]
        self.assertTrue(set(scc1) == {"a", "b", "c", "d"} or set(scc2) == {"a", "b", "c", "d"})
        self.assertTrue(set(scc1) == {"e", "f", "g", "h"} or set(scc2) == {"e", "f", "g", "h"})

        # エッジの内容を確認
        edges = list(condensed_graph.edges())
        self.assertEqual(len(edges), 1)
        source, target, weight = edges[0]
        self.assertIn("b->e", weight)  # 縮約後のグラフにおいて、正しいエッジが残っていることを確認
