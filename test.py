import json
import yaml
import sys

import graphviz

from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.generic.network import Router

import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt

configs = []
channels = {}
edges = []

# loads the API specifications from the commandline arguments
def load_configs():
    for file in sys.argv[1:]:
        api = None
        if file.endswith(".yaml"):
            with open(file, "r") as stream:
                try:
                    api = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        if file.endswith(".json"):
            api = json.load(open(file, "r"))
        
        if api is not None:
            configs.append(api)
            print("loaded file "+file+" - "+api['info']['title'])
            if "topics" in api and not "channels" in api:
                api["channels"] = api["topics"]

# extracts the channels from the API configs
def parse_config(config):
    if not "channels" in config: return
    for name, channel in config["channels"].items():
        if not name in channels:
            channels[name] = {
                "publishers": [],
                "subscribers": []
            }
        if "publish" in channel:
            channels[name]["publishers"].append(config)
        if "subscribe" in channel:
            channels[name]["subscribers"].append(config)

# prints the discovered channels and their services
def print_channels():
    for name, channel in channels.items():
        print()
        print("-----------------------------")
        print("Channel: \t"+name)
        print("Publishers:")
        for api in channel["publishers"]:
            print("\t\t", api["info"]["title"])
        print("Subscribers:")
        for api in channel["subscribers"]:
            print("\t\t", api["info"]["title"])

load_configs()

for config in configs:
    parse_config(config)
# print_channels()

def setup_nodes():
    for config in configs:
        config["dot_name"] = "service_"+config["info"]["title"]

    for name, channel in channels.items():
        channel["dot_name"] = "channel_"+name
        for api in channel["publishers"]:
            edges.append([api["dot_name"], channel["dot_name"]])

        for api in channel["subscribers"]:
            edges.append([channel["dot_name"], api["dot_name"]])

# Creates a directed graph for each microservice and channel using graphviz
def do_graphviz():
    dot = graphviz.Digraph('Topology_graphviz', engine="neato")
    # sub_services = graphviz.Digraph("Microservices")
    # sub_channels = graphviz.Digraph("Channels")
    # sub_services.attr(rank="max")
    # sub_channels.attr(rank="source")

    edge_attr = {
        "color": "gray",
        "arrowsize": "0.5"
    }

    for config in configs:
        dot.node(config["dot_name"], config["info"]["title"])

    for name, channel in channels.items():
        dot.node(channel["dot_name"], name, shape="plain")

    for edge in edges:
        dot.edge(*edge, **edge_attr)

    # dot.subgraph(sub_services)
    # dot.subgraph(sub_channels)
    dot.render(view=True)

# creates a directed graph for each microservice and channel using diagrams (uses graphviz internally)
def do_diagrams():
    with Diagram("Topology_diagrams", show=False):
        nodes = {}
        for config in configs:
            nodes[config["dot_name"]] = EC2(config["info"]["title"])

        for name, channel in channels.items():
            nodes[channel["dot_name"]] = Router(name)

        for edge in edges:
            nodes[edge[0]] >> nodes[edge[1]]


def do_networkx():
    G = nx.DiGraph()

    for config in configs:
        G.add_node(config["dot_name"])
    
    for name, channel in channels.items():
        G.add_node(channel["dot_name"])
    
    for edge in edges:
        G.add_edge(*edge)
    
    G = nx.complete_graph(5)
    nx.draw(G)
    
def do_cytoscape():
    v = {}

setup_nodes()
do_graphviz()
do_diagrams()
# do_cytoscape()
# do_networkx()
# do_plotly()