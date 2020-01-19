"""
定义两个类

1. Vertex
2. Graph (无向图)
"""
import copy
import re
from collections import defaultdict
from typing import List, Tuple, Union

import pandas as pd
from geopy.distance import geodesic


class Vertex:
    """
    一个顶点，其属性包括：
    1. 名称
    2. 相邻其他点
    3. 发现时间 (从任一顶点出发，遍历经过该 Vertex 时，经过的 Vertex 计数)
    4. 结束时间 (遍历接受后， reverse 经过该 Vertex 时，经过的 Vertex 计数)
    5. 颜色 ('undiscovered', 'discovered', 'finished')
    """

    def __init__(self, name):
        self.name = name
        self.neighbors = list()

        self.discovered = 0
        self.finished = 0
        self.color = "black"

    def add_neighbor(self, vertex):
        if vertex not in self.neighbors:
            self.neighbors.append(vertex)
            self.neighbors.sort()


class Graph:
    """
    图的表示，就是 Vertex 以及连接 Vertex 之间的连线
    """

    def __init__(self):
        self.vertices = {}
        self.time = 0

    def add_vertex(self, vertex):
        if isinstance(vertex, Vertex) and vertex.name not in self.vertices:
            self.vertices[vertex.name] = vertex
            return True
        else:
            return False

    def add_edge(self, u, v):
        if u in self.vertices and v in self.vertices:
            for key, value in self.vertices.items():
                if key == u:
                    value.add_neighbor(v)
                if key == v:
                    value.add_neighbor(u)

                return True
        else:
            return False

    def print_graph(self):
        for key in sorted(list(self.vertices.keys())):
            print(
                key
                + str(self.vertices[key].neighbors)
                + " "
                + str(self.vertices[key].discovered)
                + "/"
                + str(self.vertices[key].finished)
            )

    def _dfs(self, vertex):
        # global time
        vertex.color = "red"
        vertex.discovered = self.time
        self.time += 1
        for v in vertex.neighbors:
            if self.vertices[v].color == "black":
                self._dfs(self.vertices[v])
        vertex.color = "blue"
        vertex.finish = self.time
        self.time += 1

    def dfs(self, vertex):
        # global time
        self.time = 1
        self._dfs(vertex)


class City(Vertex):
    """
    城市定义
    """

    def __init__(self, name: str, coords: Union[List, Tuple]):
        super(City, self).__init__(name)
        self.coords = coords


THRESHOLD = 700

coordination_source = """
{name:'兰州', geoCoord:[103.73, 36.03]},
{name:'嘉峪关', geoCoord:[98.17, 39.47]},
{name:'西宁', geoCoord:[101.74, 36.56]},
{name:'成都', geoCoord:[104.06, 30.67]},
{name:'石家庄', geoCoord:[114.48, 38.03]},
{name:'拉萨', geoCoord:[102.73, 25.04]},
{name:'贵阳', geoCoord:[106.71, 26.57]},
{name:'武汉', geoCoord:[114.31, 30.52]},
{name:'郑州', geoCoord:[113.65, 34.76]},
{name:'济南', geoCoord:[117, 36.65]},
{name:'南京', geoCoord:[118.78, 32.04]},
{name:'合肥', geoCoord:[117.27, 31.86]},
{name:'杭州', geoCoord:[120.19, 30.26]},
{name:'南昌', geoCoord:[115.89, 28.68]},
{name:'福州', geoCoord:[119.3, 26.08]},
{name:'广州', geoCoord:[113.23, 23.16]},
{name:'长沙', geoCoord:[113, 28.21]},
//{name:'海口', geoCoord:[110.35, 20.02]},
{name:'沈阳', geoCoord:[123.38, 41.8]},
{name:'长春', geoCoord:[125.35, 43.88]},
{name:'哈尔滨', geoCoord:[126.63, 45.75]},
{name:'太原', geoCoord:[112.53, 37.87]},
{name:'西安', geoCoord:[108.95, 34.27]},
//{name:'台湾', geoCoord:[121.30, 25.03]},
{name:'北京', geoCoord:[116.46, 39.92]},
{name:'上海', geoCoord:[121.48, 31.22]},
{name:'重庆', geoCoord:[106.54, 29.59]},
{name:'天津', geoCoord:[117.2, 39.13]},
{name:'呼和浩特', geoCoord:[111.65, 40.82]},
{name:'南宁', geoCoord:[108.33, 22.84]},
//{name:'西藏', geoCoord:[91.11, 29.97]},
{name:'银川', geoCoord:[106.27, 38.47]},
{name:'乌鲁木齐', geoCoord:[87.68, 43.77]},
{name:'香港', geoCoord:[114.17, 22.28]},
{name:'澳门', geoCoord:[113.54, 22.19]}
"""

graph = Graph()
city_tuple = []
for line in coordination_source.split("\n"):
    if not line.strip().rstrip():
        continue
    if line.startswith("//"):
        continue
    city_name, city_coords = re.findall(r"name:'(\w+)', geoCoord:\[(.*)\]", line)[0]
    city = City(city_name, tuple(map(float, city_coords.split(","))))
    city_tuple.append((city, city.coords))
    graph.add_vertex(city)


def get_city_distance(loc_1: Union[List, Tuple], loc_2: Union[List, Tuple]):
    """
    计算两个城市之间距离

    :param city_1: 城市 1
    :param city_2: 城市 2
    """
    return geodesic(loc_1, loc_2).km


for city_A in graph.vertices:
    for city_B in graph.vertices:
        if city_A == city_B:
            continue
        distance = get_city_distance(
            (graph.vertices[city_A].coords[1], graph.vertices[city_A].coords[0]),
            (graph.vertices[city_B].coords[1], graph.vertices[city_B].coords[0]),
        )
        if distance < THRESHOLD:
            graph.add_edge(city_A, city_B)

print(graph.dfs("兰州"))


## city_pair = []
## city_connection = defaultdict(list)
# for city_A, loc_A in city_tuple:
#     for city_B, loc_B in city_tuple:
#         if city_A == city_B:
#             continue
#         distance = get_city_distance((loc_A[1], loc_A[0]), (loc_B[1], loc_B[0]))
#         if distance < THRESHOLD:
#             city_pair.append((city_A, city_B))
#             city_connection[city_A].append(city_B)
