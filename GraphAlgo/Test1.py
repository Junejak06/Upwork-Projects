import random
import math
import heapq
from collections import deque
import matplotlib.pyplot as plt
import copy


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


def dijkstra_sap(graph, source, sink):
    pq = []  # Priority queue
    heapq.heappush(pq, (0, source))

    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    parent = {node: None for node in graph}

    while pq:
        current_dist, u = heapq.heappop(pq)
        if u == sink:
            break
        for v in graph[u]:
            if dist[v] > current_dist + 1:
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


def dijkstra_dfs_like(graph, source, sink):
    pq = []  # Priority queue
    counter = float('inf')  # Infinite distance for all nodes initially
    heapq.heappush(pq, (counter, source))

    visited = {node: False for node in graph}
    parent = {node: None for node in graph}

    while pq:
        current_counter, u = heapq.heappop(pq)
        if u == sink:
            break
        if not visited[u]:
            visited[u] = True
            for v in graph[u]:
                if not visited[v]:
                    counter -= 1  # Decrease counter for DFS-like behavior
                    heapq.heappush(pq, (counter, v))
                    parent[v] = u

    path = []
    u = sink
    while u is not None:
        path.append(u)
        u = parent[u]
    path.reverse()

    return path if visited[sink] else None


def dijkstra_maxcap(graph, source, sink):
    pq = []  # Priority queue
    heapq.heappush(pq, (-float('inf'), source))  # Negative infinity for max capacity

    max_cap = {node: 0 for node in graph}
    max_cap[source] = float('inf')
    parent = {node: None for node in graph}

    while pq:
        current_cap, u = heapq.heappop(pq)
        current_cap = -current_cap
        if u == sink:
            break
        for v, weight in graph[u].items():
            cap = min(current_cap, weight)
            if cap > max_cap[v]:
                max_cap[v] = cap
                parent[v] = u
                heapq.heappush(pq, (-cap, v))  # Push negative for max heap
    path = []
    u = sink
    while u is not None:
        path.append(u)
        u = parent[u]
    path.reverse()
    return path if max_cap[sink] > 0 else None
def dijkstra_random(graph, source, sink):
    pq = []  # Priority queue
    heapq.heappush(pq, (0, source))
    visited = {node: False for node in graph}
    parent = {node: None for node in graph}
    while pq:
        _, u = heapq.heappop(pq)
        if u == sink:
            break
        if not visited[u]:
            visited[u] = True
            for v in graph[u]:
                if not visited[v]:
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


def ford_fulkerson_metrics(orig_graph, source, sink, path_finder_func):
    graph = copy.deepcopy(orig_graph)  # Create a deep copy of the graph
    flow = 0
    paths = []
    while True:
        path = path_finder_func(graph, source, sink)
        if not path:
            break
        # Find the minimum capacity on the found path
        min_capacity = min(graph[u][v] for u, v in zip(path, path[1:]))
        flow += min_capacity
        paths.append(path)
        # Update the capacities and reverse edges along the path
        for u, v in zip(path, path[1:]):
            graph[u][v] -= min_capacity
            graph[v][u] = graph.get(v, {}).get(u, 0) + min_capacity
    # Calculate metrics
    ml = sum(len(p) for p in paths) / len(paths) if paths else 0
    mpl = sum(len(p) / max(len(p) for p in paths) for p in paths) / len(paths) if paths else 0
    return len(paths), ml, mpl, flow

def run_simulation(n, r, upper_cap):
    # Generate the graph
    graph, coordinates, source_sink_pair = generate_sink_source_graph(n, r, upper_cap)

    # Initialize a list to store the results for this simulation
    simulation_results = []

    # Run Ford-Fulkerson with each path-finding algorithm and collect metrics
    for path_finder_func in [dijkstra_sap, dijkstra_dfs_like, dijkstra_maxcap, dijkstra_random]:
        num_paths, ml, mpl, _ = ford_fulkerson_metrics(graph, source_sink_pair[0], source_sink_pair[1], path_finder_func)
        total_edges = sum(len(edges) for edges in graph.values())

        simulation_results.append({
            'Algorithm': path_finder_func.__name__,
            'n': n,
            'r': r,
            'upperCap': upper_cap,
            'paths': num_paths,
            'ML': ml,
            'MPL': mpl,
            'total_edges': total_edges
        })

    return simulation_results



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



# Simulation parameters
simulation_parameters = [
    (100, 0.2, 2),
    (200, 0.2, 2),
    (100, 0.3, 2),
    (200, 0.3, 2),
    (100, 0.2, 50),
    (200, 0.2, 50),
    (100, 0.3, 50),
    (200, 0.3, 50)
]

# Run all simulations
all_results = []
for params in simulation_parameters:
    results = run_simulation(*params)
    all_results.extend(results)

print(f"{'Algorithm':<10} {'n':<3} {'r':<4} {'upperCap':<9} {'Paths':<6} {'ML':<4} {'MPL':<5} {'Total Edges':<11}")
for result in all_results:
    print(f"{result['Algorithm']:10} {result['n']:3} {result['r']:4.1f} {result['upperCap']:9} "
          f"{result['paths']:6} {result['ML']:4.2f} {result['MPL']:5.2f} "
          f"{result['total_edges']:11}")

