#!/usr/bin/env python3
import copy
import re
from collections import defaultdict
from typing import List, Tuple, Union

import pandas as pd
from geopy.distance import geodesic
from pyecharts import options as opts
from pyecharts.charts import Geo, Page
from pyecharts.faker import Collector, Faker
from pyecharts.globals import ChartType, SymbolType

THRESHOLD = 700

C = Collector()

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

city_info = {}
city_tuple = []
for line in coordination_source.split("\n"):
    if not line.strip().rstrip():
        continue
    if line.startswith("//"):
        continue
    city, coords = re.findall(r"name:'(\w+)', geoCoord:\[(.*)\]", line)[0]
    city_info[city] = tuple(map(float, coords.split(",")))
    city_tuple.append((city, city_info[city]))


def get_city_distance(loc_1: Union[List, Tuple], loc_2: Union[List, Tuple]):
    """
    计算两个城市之间距离

    :param city_1: 城市 1
    :param city_2: 城市 2
    """
    return geodesic(loc_1, loc_2).km


city_pair = []
city_connection = defaultdict(list)
for city_A, loc_A in city_tuple:
    for city_B, loc_B in city_tuple:
        if city_A == city_B:
            continue
        distance = get_city_distance((loc_A[1], loc_A[0]), (loc_B[1], loc_B[0]))
        if distance < THRESHOLD:
            city_pair.append((city_A, city_B))
            city_connection[city_A].append(city_B)


@C.funcs
def geo_background() -> Geo:
    c = (
        Geo()
        .add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111"),
        )
        .add("", city_tuple, type_=ChartType.EFFECT_SCATTER, color="red")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Geo-background"))
    )
    return c


@C.funcs
def geo_line_background() -> Geo:
    c = (
        Geo()
        .add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111"),
        )
        .add("", city_tuple, type_=ChartType.EFFECT_SCATTER, color="red")
        .add(
            "geo",
            city_pair,
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW, symbol_size=6, color="blue"
            ),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Geo-Line-background"))
    )
    return c


Page().add(*[fn() for fn, _ in C.charts]).render("path.html")


def bfs_search(graph: dict, start: str, target: str):
    """
    根据 graph 实现路径搜索，广度优先

    :param graph: 以 dict 形式保存的路径信息
    :param start: 起始点
    :param target: 终点
    :param search_strategy: 搜索方式
    """
    pathes = [[start]]  # 保存从起点开始所有的路径信息
    visited = set()

    while pathes:  # 对所有路径进行遍历
        path = pathes.pop()
        frontier = path[-1]  # 当前路径最后一个点为前点
        successors = graph[frontier]  # 前点连接的所有次级点
        for successor in successors:  # 对所有后点进行循环
            if successor in visited:  # 为了避免出现 loop, 即类似 A -> B, B -> A 的情形
                continue
            new_path = path + [successor]
            pathes.append(new_path)
            if successor == target:
                return new_path
        visited.add(frontier)


def dfs(
    start: str,
    end: str,
    visited: defaultdict(set),
    level: int = 0,
    path: list = [],
    stop_flag: bool = False,
):
    """
    深度优先搜索算法

    :param start: 起点
    :param end: 终点
    :param visited: 已访问结点记录
    :param level: 当前层级
    :param path: 路径记录
    :param stop_flag: 递归停止标记
    """
    if start == end:
        path = [start]
        return path
    if not city_connection[start]:  # 孤立结点
        raise ValueError("错误，孤立结点，无可达路径")

    def _dfs(start, end, level, visited, path, stop_flag):
        path.append(start)
        visited[level].add(start)
        successors = city_connection[start]
        for i, successor in enumerate(successors):
            if successor in visited[level]:
                continue
            if successor == end:
                path.append(successor)
                level += 1
                print(f"找到路径, {path}, 长度为 {level}")
                stop_flag = True
                return stop_flag, path
            else:
                if i == len(successors) - 1:
                    print(f"lenghth of successors is {i+1}")
                    # visited[level].add(successor)
                    # visited.pop(level)
                    # level -= 1
                    print(f"当前搜索路径为 {path}")
                    path.pop()
                    if level == 0:
                        print("找不到可行路径")
                        stop_flag = True
                        path = []
                        return stop_flag, path
                    return stop_flag, path
                if not stop_flag:
                    level += 1
                    visited[level] = visited[level - 1].copy()
                    visited[level].add(successor)
                    stop_flag, path = _dfs(
                        successor, end, level, visited, path, stop_flag
                    )
                if stop_flag:
                    return stop_flag, path
            if stop_flag:
                return stop_flag, path

    _dfs(start, end, level, visited, path, stop_flag)


visited = defaultdict(set)
dfs("兰州", "武汉", visited)
