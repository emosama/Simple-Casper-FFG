from pyecharts.charts import Tab
import time
import requests
from pyecharts.globals import ThemeType
import json
from pyecharts import options as opts
from pyecharts.charts import Graph

'''
description: check whether blocks got same height and fixed it's y_axis
input: json file
'''
def same_height(file_):
    with open(file_, 'r') as file:
        data = json.load(file)
        seen = {}
        for node in data["block"]:
            height = node["height"]
            if height in seen:
                node["x"] = (100 * seen[height] + node["x"])
                seen[height] += 1
            else:
                seen[height] = 1
    with open(file_, 'w') as file:
        json.dump(data, file, indent=2)

'''
description: collect data for pyechart graph
input: json file data
output: node(name, height, category, value data), edge(link between nodes), categories(node attributes)
'''
def plot(data):
    nodes = []
    for node in data["block"]:
        node = {
            "name": node["hash"],
            "height": node["height"],
            "x": node["x"],
            "y": 800 - node["height"] * 100,
            "category": node["attribute"],
            "prev": node["previous_hash"],
            "dynasty": node["dynasty"],
            "receive": node["receive"],
            "penalty": node["penalty"],
            "connection": node["connection"],
            "value": node["value"]
        }
        nodes.append(node)
    edges = []
    for node in data["block"]:
        edge = {"source": node["previous_hash"], "target": node["hash"]}
        edges.append(edge)
    text = ["receive: " + str(node["receive"]) + "\n"
            "penalty: " + str(node["penalty"]) ]
    # text = []
    return nodes, edges, text

'''
description: plot graph and adjust the zoom slider to fit small windows
input: node(name, height, category, value data), edge(link between nodes), categories(node attributes)
output: pyechart graph
'''
def datazoom_slider(nodes, edges, categories, text):
    c = (
        Graph(init_opts=opts.InitOpts(width="1000px", height="1500px", theme=ThemeType.DARK)).add(
            series_name='',
            nodes=nodes,
            links=edges,
            categories=categories,
            label_opts=opts.LabelOpts(position="right"),
            symbol_size=25,
            layout="none",
            edge_label=None,
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{c}"),
            is_focusnode=False,
            symbol='rect',
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=text),
            # datazoom_opts=[opts.DataZoomOpts()],
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"),
        )
    )
    return c

'''
description: read data from website('http://127.0.0.1:5000/blocktree'), 
        for each miner, plot a pyechart graph
'''
def main():
    r = requests.get('http://127.0.0.1:5000/blocktree')
    print(r)
    data = r.json()
    with open("new_all_blocks.json", 'w') as file:
        json.dump(data, file, indent=2)
    file_ = "new_all_blocks.json"
    with open(file_, 'r') as file:
        file_data = json.load(file)
        blocks = file_data.values()
        num = 1
        for block in blocks:
            block_info = block.values()
            for info in block_info:
                data = {}
                for i in info:
                    if info[i]["attribute"] == "head":
                        info[i]["attribute"] = 0
                    elif info[i]["attribute"] == "block":
                        info[i]["attribute"] = 1
                    elif info[i]["attribute"] == "NORMAL":
                        info[i]["attribute"] = 2
                    elif info[i]["attribute"] == "JUSTIFIED":
                        info[i]["attribute"] = 3
                    elif info[i]["attribute"] == "FINALIZED":
                        info[i]["attribute"] = 4
                    info[i].update({'x': 100, 'y': 800})
                data['block'] = list(info.values())
                with open("block%s.json" % num, 'w') as file1:
                    json.dump(data, file1, indent=2)
                num += 1
    tab = Tab()
    for i in range(1, num):
        same_height('block%s.json' % i)
        f = open('block%s.json' % i, )
        data = json.load(f)
        nodes, edges, text = plot(data)
        categories = [
            {
                "name": "head"
            },
            {
                "name": "block"
            },
            {
                "name": "normal checkpoint"
            },
            {
                "name": "justified checkpoint"
            },
            {
                "name": "finalized checkpoint"
            }]

        tab.add(datazoom_slider(nodes, edges, categories, text), "graph%s" % i)

    tab.render('blockchain.html')


if __name__ == '__main__':
    while True:
        main()
        time.sleep(10)
