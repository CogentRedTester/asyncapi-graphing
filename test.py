# diagram.py
# from diagrams import Diagram
# from diagrams.aws.compute import EC2
# from diagrams.aws.database import RDS
# from diagrams.aws.network import ELB

# with Diagram("Web Service", show=False):
#     ELB("lb") >> EC2("web") >> RDS("userdb")


import json
import sys
import graphviz
import yaml

configs = []
channels = {}

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

# Creates a directed graph for each microservice and channel
dot = graphviz.Digraph('Topology')

for config in configs:
    config["dot_name"] = "service_"+config["info"]["title"]
    dot.node(config["dot_name"], config["info"]["title"])

for name, channel in channels.items():
    channel["dot_name"] = "channel_"+name
    dot.node(channel["dot_name"], name, shape="plaintext")

    for api in channel["publishers"]:
        dot.edge(api["dot_name"], channel["dot_name"])

    for api in channel["subscribers"]:
        dot.edge(channel["dot_name"], api["dot_name"])

dot.render(view=True)