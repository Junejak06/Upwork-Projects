import matplotlib.pyplot as plt
import networkx as nx

# Creating a directed graph
G = nx.DiGraph()

# Adding nodes (components of the AWS architecture)
nodes = ["AWS Cloud9", "AWS CodeCommit/GitHub", "AWS Elastic Beanstalk",
         "Amazon S3", "Amazon DynamoDB/SQLite", "AWS Lambda", "Amazon SQS/SNS",
         "AWS CloudWatch"]
G.add_nodes_from(nodes)

# Adding edges (representing the interactions)
edges = [("AWS Cloud9", "AWS CodeCommit/GitHub"),
         ("AWS CodeCommit/GitHub", "AWS Elastic Beanstalk"),
         ("AWS Elastic Beanstalk", "Amazon S3"),
         ("AWS Elastic Beanstalk", "Amazon DynamoDB/SQLite"),
         ("Amazon S3", "AWS Lambda"),
         ("Amazon DynamoDB/SQLite", "AWS Lambda"),
         ("AWS Lambda", "Amazon SQS/SNS"),
         ("Amazon SQS/SNS", "AWS CloudWatch")]
G.add_edges_from(edges)

# Drawing the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42)  # For consistent layout
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=3000,
        font_size=10, font_weight="bold", arrowstyle="->", arrowsize=15)
plt.title("AWS Cloud Architecture Flow Diagram", size=15)
plt.show()
