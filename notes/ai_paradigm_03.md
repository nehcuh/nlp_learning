# 基于搜索的 AI 范例

## 场景描述

给定不同城市的经纬度

1. 计算城市之间距离
2. 假定在 700 公里以内的城市可以直接到达，超过 700 公里的城市需要进行换乘，对输入的两个城市，规划可行路线
3. 基于 “换乘最少” 或 “总路径最短” 进行路线规划。

## 原始输入: 城市经纬度

1.  原始数据

    这里直接给出了不同的城市的经纬度，实际在处理过程中，可以通过百度或高德地图
    API 获取不同城市的经纬度，或者直接通过爬取百度百科，并通过正则处理，获取相应城市的经纬度。

    ```python
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
    ```

2.  数据结构转换
    这里保存了两种数据结构，第一种数据结构为 `dict`, 利用 `dict` 可以方便地表示树状结构，
    使用 `list` 表示城市名称与城市经纬度的 `tuple`, 以方便之后画图处理。

    ```python
    import re

    city_info = {}
    city_tuple = []

    for line in coordination_source.split("\n"):
        if not line.strip().rstrip():
            continue
        if line.startswith("//"):
            continue
        city, coords = re.findall(r"name:'(\w+)', geoCoord:\[(.*)\]", line)[0]
        city_info[city] = list(map(float, coords.split(",")))
        city_tuple.append((city, city_info[city]))
    ```

## 距离计算与不同城市的拓扑结构展示

1. 距离计算

   考虑地球是一个球体，根据经纬度可以利用几何关系计算两个城市之间距离，这里简单起见，直接使用相应
   的根据经纬度计算距离的包

   ```python
   from geopy.distance import deodestic
   from typing import Union, Tuple, List
   def get_city_distance(loc_1: Union[Tuple, List], loc_2: Union[Tuple, List]):
       """
       计算两个城市之间距离

       :param loc_1: 城市 1 的纬度，经度
       :param loc_2: 城市 2 的纬度，经度
       """
       return geodestick(loc_1, loc_2).km
   ```

2. 城市拓扑结构展示

- 使用 `networkx` 显示拓扑结构 (-太丑，弃用-)

  ```python
  import matplotlib.pyplot as plt
  import networkx as nx
  cities = list(city_info.keys())
  city_graph = nx.Graph()
  city_graph.add_nodes_from(cities)
  nx.draw(city_graph, city_info, with_labels=True, node_size=10)
  ```

- 使用 `pyecharts` 展示拓扑结构

  ```python
  from pyecharts import options as opts
  from pyecharts.charts import Geo, Page
  from pyecharts.faker import Collector, Faker
  from pyecharts.globals import ChartType, SymbolType

  @C.funcs
  def geo_background() -> Geo:
      c = (
          Geo()
          .add_schema(
              maptype="china",
              itemstyle_opts=opts.ItemStyleOpts(
                  color="#323c48", border_color="#111"),
          )
          .add(
              "",
              city_tuple,
              type_=ChartType.EFFECT_SCATTER,
              color="red",
          )
          .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
          .set_global_opts(title_opts=opts.TitleOpts(title="Geo-background"))
      )
      return c
  ```

  !()[search_based_03.png]

3. 不同城市间的连接信息与相应拓扑结构展示

- 对每个城市进行遍历，计算两个城市的距离，需要两层循环
- 对每个城市所有可以去的城市，可以用 `dict` 来表示

```python
from collections import defaultdict
THRESHOLD = 700

city_pair = []
city_connection = defaultdict(list) # 保留路径的树形结构
for city_A, loc_A in city_tuple:
    for city_B, loc_B in city_tuple:
        if city_A == city_B:
            continue
        distance = get_city_distance((loc_A[1], loc_A[0]), (loc_B[1], loc_B[0]))
        if distance < THRESHOLD:
            city_pair.append((city_A, city_B))
            city_connection[city_A].append(city_B)

 @C.funcs
def geo_line_background() -> Geo:
    c = (
        Geo()
        .add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(
                color="#323c48", border_color="#111"),
        )
        .add("", city_tuple, type_=ChartType.EFFECT_SCATTER, color="red")
        .add("geo", city_pair, type_=ChartType.LINES, effect_opts=opts.EffectOpts(
            symbol=SymbolType.ARROW, symbol_size=6, color="blue"
        ))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Geo-Line-background"))
    )
    return c


Page().add(*[fn() for fn, _ in C.charts]).render()
```

!()[search_based_04.png]

## 路径搜索

对于搜索，其实本质上依然是树搜索，给定起点后，沿起点的所有次级点依次搜索，如果所有次级点没有终点时，
则再往次次级点进行搜索即可，一直到找到终点，或者所有可能的路径搜索结束。

按照遍历层次不同，搜索方式可以分为 “深度优先” 和 “广度优先”， 简单而言，“深度优先” 优先对某条分支
一路遍历到叶结点，如果没有发现终点，再尝试第二条线路；而 “广度优先” 的策略每次都先对同一层次的所有
结点进行遍历，当没有找到终点时，继续下一个级别的所有结点遍历。

1.  深度优先的搜索方案

    > 深度优先算法应用到路径搜索上，理解上可以看下面两幅图，图 1 是几个结点的简单的连接示意，当我们选择
    > 从某个点出发 (譬如 A 点)，想要达到另外一个点 (譬如 D 点), 就可以抽象为图 2. 图 2 中，不同颜色代
    > 表不同路径，虚线表示路径不可行。深度优先算法首先对 A 的子结点 B (level 1) 判断是否符合 D 点，不
    > 符合，继续搜索 B 点的子结点 C 点 (level 2), C 不符合 D 点，继续对 C 点子结点 F (level = 3) 进
    > 行判断，依然不符合，此时 F 点已经是该分支下最末的一个结点，搜索返回到上一级，即 C 点的另外一个子
    > 结点 D 点 (level =3), 发现符合条件，返回路径 [A, B，C，D]

2.  广度优先的搜索方案

    > 广度优先算法首先对同一层级的所有结点进行判断，如果都不符合，则继续对下一层级的结点进行判断，依然以
    > 图 2 为例，此时，从 A (level = 0) 出发，对其所有子结点 [B, D] 进行判断，结果发现 D
    > 符合查找的点, 返回路径 [A, D]

!()[search_based_01.png]
!()[search_based_02.png]

3.  算法实现

    - 深度优先算法：可以使用递归的方式进行路径搜索，但是对于递归，有个问题必须要考虑，即，如果在内部
      层次中，得到最终结果，如何跳出所有函数。笔者这里使用了一个 flag, 在递归函数调用之后，对 flag
      进行判断，当 flag 为 `True` 就接着返回，如此就实现了跳出深层递归。

      ```python
      def dfs(start: str, end: str, visited: defaultdict(set), level: int = 0, path: list = [], stop_flag: bool = False):
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
                       if i == len(successors) - 1: # 当前层级搜索结束
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
                           visited[level] = visited[level-1].copy()
                           visited[level].add(successor)
                           stop_flag, path = _dfs(
                               successor, end, level, visited, path, stop_flag)
                       if stop_flag:
                           return stop_flag, path
                   if stop_flag:
                       return stop_flag, path
           _dfs(start, end, level, visited, path, stop_flag)
      ```

    - 广度优先算法：相比深度优先算法，广度优先算法实现就简单了很多，只需要用一个 while 循环，对所有
      当前层级所有结点进行判断，如果不满足条件继续往下一层级进行搜索，循环 break 条件，要不是找到了
      终点，要不就是搜索完了树的所有结点。

      ```python
      def dfs_search(graph: dict, start: str, target: str):
          """
          根据 graph 实现路径搜索，深度优先
          """
          record_path = []
          visited = set()  # 已访问的结点
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
      ```
