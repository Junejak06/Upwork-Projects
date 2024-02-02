import random
import heapq

# Graph generation function
def generate_random_graph(n, r, upper_cap):
    vertices = [(random.uniform(0, 1), random.uniform(0, 1)) for _ in range(n)]
    edges = {}
    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i != j:
                distance = ((v[0] - w[0]) ** 2 + (v[1] - w[1]) ** 2) ** 0.5
                if distance <= r:
                    rand = random.uniform(0, 1)
                    if (j, i) not in edges and rand <= 0.5:
                        edges[(i, j)] = random.randint(1, upper_cap)
                    elif (j, i) not in edges:
                        edges[(j, i)] = random.randint(1, upper_cap)
    return vertices, edges

# Initialize the graph for algorithms
def initialize_graph(vertices, edges):
    graph = {i: [] for i in range(len(vertices))}
    for (u, v), w in edges.items():
        graph[u].append((w, v))
        graph[v].append((w, u))  # Since the graph is undirected
    return graph

# SAP algorithm
def dijkstra_sap(graph, start, end):
    queue = [(0, start)]
    distances = {vertex: float('infinity') for vertex in graph}
    previous = {vertex: None for vertex in graph}
    distances[start] = 0
    while queue:
        current_distance, current_vertex = heapq.heappop(queue)
        if current_vertex == end:
            break
        for edge_weight, neighbor in graph[current_vertex]:
            distance = current_distance + edge_weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(queue, (distance, neighbor))
    path = []
    while previous[end] is not None:
        path.insert(0, end)
        end = previous[end]
    path.insert(0, start)
    return path, distances[path[-1]]

# DFS-like algorithm
def dfs_like_dijkstra(graph, start, end):
    stack = [(0, start, [])]
    visited = set()
    best_path = []
    best_cost = float('infinity')
    while stack:
        cost, vertex, path = stack.pop()
        if vertex in visited:
            continue
        visited.add(vertex)
        path = path + [vertex]
        if vertex == end:
            if cost < best_cost:
                best_path = path
                best_cost = cost
            continue
        for edge_weight, neighbor in graph[vertex]:
            if neighbor not in visited:
                stack.append((cost + edge_weight, neighbor, path))
    return best_path, best_cost

# MaxCap algorithm
def maxcap_dijkstra_corrected(graph, start, end):
    queue = [(float('infinity'), start, [])]
    visited = set()
    best_path = []
    best_capacity = -float('infinity')
    while queue:
        current_capacity, current_vertex, path = heapq.heappop(queue)
        visited.add(current_vertex)
        path = path + [current_vertex]
        if current_vertex == end:
            if current_capacity > best_capacity:
                best_capacity = current_capacity
                best_path = path
            continue
        for edge_weight, neighbor in graph[current_vertex]:
            if neighbor not in visited:
                heapq.heappush(queue, (min(current_capacity, edge_weight), neighbor, path))
    return best_path, best_capacity

# Random algorithm
def random_dijkstra(graph, start, end):
    queue = [(random.random(), start, [])]
    visited = set()
    path = None
    while queue:
        _, current_vertex, current_path = heapq.heappop(queue)
        if current_vertex in visited:
            continue
        visited.add(current_vertex)
        current_path = current_path + [current_vertex]
        if current_vertex == end:
            path = current_path
            break
        for edge_weight, neighbor in graph[current_vertex]:
            if neighbor not in visited:
                heapq.heappush(queue, (random.random(), neighbor, current_path))
    return path


def update_graph(graph, u, v, flow, add_reverse=False):
    # Update forward edge
    for edge in graph[u]:
        if edge[1] == v:
            # Decrease the flow from the forward edge
            updated_capacity = edge[0] - flow
            graph[u].remove(edge)
            if updated_capacity > 0:
                graph[u].append((updated_capacity, v))
            break
    else:
        # This should not happen if the graph was initialized correctly
        raise ValueError(f"No edge found from {u} to {v} to update")

    # Update reverse edge
    if add_reverse:
        for edge in graph[v]:
            if edge[1] == u:
                # Increase the flow to the reverse edge
                updated_capacity = edge[0] + flow
                graph[v].remove(edge)
                graph[v].append((updated_capacity, u))
                break
        else:
            # If the reverse edge does not exist, create it
            graph[v].append((flow, u))


# Ford-Fulkerson method to find maximum flow in the graph
def ford_fulkerson(graph, start, end):
    max_flow = 0
    iteration = 0
    while True:
        iteration += 1
        print(f"Iteration: {iteration}")
        path, path_flow = dijkstra_sap(graph, start, end)  # Use the SAP algorithm to find the augmenting path

        if path_flow == float('infinity'):  # No augmenting path found
            print("No more augmenting paths found. Terminating.")
            break

        print(f"Augmenting path found: {path} with flow: {path_flow}")

        # Update the residual capacities of the graph along the path
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            print(f"Updating edge from {u} to {v}")
            update_graph(graph, u, v, path_flow, add_reverse=True)

        # Add the path flow to the total flow
        max_flow += path_flow
        print(f"Updated total flow: {max_flow}")

    return max_flow


# Function to record the simulation results
def record_simulation_results(simulation_results):
    print("Algorithm\t n\t r\t upperCap\t paths\t ML\t MPL\t total edges")
    for result in simulation_results:
        algorithm = result['algorithm']
        n = result['n']
        r = result['r']
        upper_cap = result['upper_cap']
        paths = len(result['path'])
        ml = result['distance']
        mpl = ml / n  # Mean Proportional Length is the Mean Length divided by the number of nodes
        total_edges = result['total_edges']
        print(f"{algorithm}\t {n}\t {r}\t {upper_cap}\t {paths}\t {ml}\t {mpl:.2f}\t {total_edges}")

# Function to run the full simulation with the Ford-Fulkerson method
def run_full_simulation(n, r, upper_cap):
    vertices, edges = generate_random_graph(n, r, upper_cap)
    graph = initialize_graph(vertices, edges)
    start, end = 0, len(vertices) - 1
    max_flow = ford_fulkerson(graph, start, end)
    return max_flow

# Parameters for the simulation
simulation_parameters = [(100, 0.2, 2), (200, 0.2, 2), (100, 0.3, 2), (200, 0.3, 2),
                         (100, 0.2, 50), (200, 0.2, 50), (100, 0.3, 50), (200, 0.3, 50)]

# Running the simulation
simulation_results = []
for params in simulation_parameters:
    n, r, upper_cap = params
    max_flow = run_full_simulation(n, r, upper_cap)
    # You can add the code to record the paths, mean length, and total edges here
    result = {'algorithm': 'Ford-Fulkerson', 'n': n, 'r': r, 'upper_cap': upper_cap, 'flow': max_flow}
    simulation_results.append(result)

# Record the simulation results
record_simulation_results(simulation_results)
print(simulation_results)
