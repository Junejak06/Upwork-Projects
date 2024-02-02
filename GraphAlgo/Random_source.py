import random
import math
import heapq
from collections import deque
import matplotlib.pyplot as plt

# Define the function to check if a path from start to end exists using BFS
def is_reachable(graph, start, end):
    visited = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            return True
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                queue.append(neighbour)
    return False

# Define the function to generate a random graph
def generate_sink_source_graph(n, r, upper_cap):
    coordinates = {i: (random.random(), random.random()) for i in range(n)}
    graph = {i: {} for i in range(n)}
    for u in graph:
        for v in graph:
            if u != v:
                dist = math.sqrt((coordinates[u][0] - coordinates[v][0])**2 +
                                 (coordinates[u][1] - coordinates[v][1])**2)
                if dist <= r:
                    rand = random.random()
                    if rand < 0.5:
                        if (v, u) not in graph[u] and (u, v) not in graph[v]:
                            graph[u][v] = random.randint(1, upper_cap)
                    else:
                        if (u, v) not in graph[u]:
                            graph[u][v] = random.randint(1, upper_cap)
                        if (v, u) in graph[v]:
                            del graph[v][u]
    source = random.randint(0, n - 1)
    sink = source
    while sink == source or not is_reachable(graph, source, sink):
        sink = random.randint(0, n - 1)
    return graph, coordinates, (source, sink)


def dijkstra_sap(residual_graph, source, sink):
    pq = []
    heapq.heappush(pq, (0, source))
    dist = {node: float('inf') for node in residual_graph}
    dist[source] = 0
    parent = {node: None for node in residual_graph}

    while pq:
        current_dist, u = heapq.heappop(pq)
        if u == sink:
            break
        for v in residual_graph[u]:
            if residual_graph[u][v]['capacity'] > 0 and dist[v] > current_dist + 1:
                dist[v] = current_dist + 1
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    path = []
    u = sink
    while u is not None:
        path.append(u)
        u = parent[u]
    path.reverse()
    return path if dist[sink] != float('inf') else None


def dijkstra_dfs_like(residual_graph, source, sink):
    pq = []
    counter = float('inf')
    heapq.heappush(pq, (counter, source))
    visited = {node: False for node in residual_graph}
    parent = {node: None for node in residual_graph}

    while pq:
        _, u = heapq.heappop(pq)
        if u == sink:
            break
        if not visited[u]:
            visited[u] = True
            for v in residual_graph[u]:
                if not visited[v] and residual_graph[u][v]['capacity'] > 0:
                    counter -= 1
                    heapq.heappush(pq, (counter, v))
                    parent[v] = u

    path = []
    u = sink
    while u is not None:
        path.append(u)
        u = parent[u]
    path.reverse()
    return path if visited[sink] else None



def dijkstra_maxcap(residual_graph, source, sink):
    pq = []
    heapq.heappush(pq, (-float('inf'), source))
    max_cap = {node: 0 for node in residual_graph}
    max_cap[source] = float('inf')
    parent = {node: None for node in residual_graph}

    while pq:
        current_cap, u = heapq.heappop(pq)
        current_cap = -current_cap
        if u == sink:
            break
        for v in residual_graph[u]:
            cap = min(current_cap, residual_graph[u][v]['capacity'])
            if cap > max_cap[v]:
                max_cap[v] = cap
                parent[v] = u
                heapq.heappush(pq, (-cap, v))

    path = []
    u = sink
    while u is not None:
        path.append(u)
        u = parent[u]
    path.reverse()
    return path if max_cap[sink] > 0 else None

def dijkstra_random(residual_graph, source, sink):
    pq = []
    heapq.heappush(pq, (0, source))
    visited = {node: False for node in residual_graph}
    parent = {node: None for node in residual_graph}

    while pq:
        _, u = heapq.heappop(pq)
        if u == sink:
            break
        if not visited[u]:
            visited[u] = True
            for v in residual_graph[u]:
                if not visited[v] and residual_graph[u][v]['capacity'] > 0:
                    random_priority = random.random()
                    heapq.heappush(pq, (random_priority, v))
                    parent[v] = u

    path = []
    u = sink
    while u is not None:
        path.append(u)
        u = parent[u]
    path.reverse()
    return path if visited[sink] else None


def create_residual_graph(graph):
    residual_graph = {u: {} for u in graph}
    for u in graph:
        for v, cap in graph[u].items():
            residual_graph[u][v] = {'capacity': cap}
            residual_graph[v][u] = {'capacity': 0}  # Add reverse edge with 0 capacity
    return residual_graph


# Ford-Fulkerson algorithm using the residual graph and path-finding algorithms
def ford_fulkerson(graph, source, sink, find_path):
    max_flow = 0
    residual_graph = create_residual_graph(graph)
    paths_count = 0
    total_path_length = 0

    path = find_path(residual_graph, source, sink)
    while path:
        path_flow = min(residual_graph[u][v]['capacity'] for u, v in zip(path, path[1:]))
        for u, v in zip(path, path[1:]):
            residual_graph[u][v]['capacity'] -= path_flow
            residual_graph[v][u]['capacity'] += path_flow
        max_flow += path_flow
        paths_count += 1
        total_path_length += len(path) - 1  # Subtract one to count edges, not nodes
        path = find_path(residual_graph, source, sink)

    mean_length = total_path_length / paths_count if paths_count > 0 else 0
    return max_flow, paths_count, mean_length
n = 100
r = 0.2
upperCap = 2


graph, coordinates, source_sink_pair = generate_sink_source_graph(n, r, upperCap)
sap_path = dijkstra_sap(graph, source_sink_pair[0], source_sink_pair[1])
dfs_like_path = dijkstra_dfs_like(graph, source_sink_pair[0], source_sink_pair[1])
maxcap_path = dijkstra_maxcap(graph, source_sink_pair[0], source_sink_pair[1])
random_path = dijkstra_random(graph, source_sink_pair[0], source_sink_pair[1])

results = {}
for algorithm in [dijkstra_sap, dijkstra_dfs_like, dijkstra_maxcap, dijkstra_random]:
    max_flow, paths_count, mean_length = ford_fulkerson(graph, source_sink_pair[0], source_sink_pair[1], algorithm)
    results[algorithm.__name__] = {
        'max_flow': max_flow,
        'paths_count': paths_count,
        'mean_length': mean_length
    }

# Print results
for algorithm_name, data in results.items():
    print(f"Algorithm: {algorithm_name}")
    for key, value in data.items():
        print(f"{key}: {value}")
    print()
    print()


def visualize_graph(graph, coordinates, path=None, title="Graph Visualization"):
    plt.figure(figsize=(12, 7))
    # Draw all nodes
    for node, (x, y) in coordinates.items():
        plt.scatter(x, y, c='red' if path and node in path else 'blue', s=100, zorder=5)
        plt.text(x, y, str(node), fontsize=12, ha='center', va='center', zorder=5)

    # Draw all edges
    for u in graph:
        for v in graph[u]:
            if path and u in path and v in path and path.index(u) + 1 == path.index(v):
                plt.plot([coordinates[u][0], coordinates[v][0]], [coordinates[u][1], coordinates[v][1]], 'r-', lw=2, zorder=4)
            else:
                plt.plot([coordinates[u][0], coordinates[v][0]], [coordinates[u][1], coordinates[v][1]], 'k-', alpha=0.5, zorder=3)

    plt.title(title)
    plt.axis('off')
    plt.show()


if sap_path:
    visualize_graph(graph, coordinates, sap_path, title="SAP Path Visualization")
if dfs_like_path:
    visualize_graph(graph, coordinates, dfs_like_path, title="DFS-like Path Visualization")
if maxcap_path:
    visualize_graph(graph, coordinates, maxcap_path, title="MaxCap Path Visualization")
if random_path:
    visualize_graph(graph, coordinates, random_path, title="Random Path Visualization")