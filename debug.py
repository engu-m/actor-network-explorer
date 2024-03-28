from dash import dcc, html


def mySwitch(id, value=True):
    return dcc.RadioItems(
        options=[
            {"label": "True", "value": True},
            {"label": "False", "value": False},
        ],
        value=value,
        id=id,
        inline=True,
    )


def myDropdown(id, options, value=None, clearable=False):
    if value is None:
        value = options[0]
    return dcc.Dropdown(
        options=options,
        value=value,
        id=id,
        clearable=clearable,
    )


def mySlider(id, value, min=0, max=None, nsteps=4):
    if value < 0:
        slider_min = 2 * value
        slider_max = min
    else:
        slider_min = min
        slider_max = 2 * value if max is None else max
    step = (slider_max - min) / nsteps
    return dcc.Slider(
        min=slider_min,
        max=slider_max,
        step=step,
        id=id,
        value=value,
    )


def myPre(id, clipboard_text):
    clipboard = html.Div(
        [
            dcc.Clipboard(id=f"{id}-clipboard", target_id=id),
            clipboard_text,
        ],
        style={"display": "inline-flex"},
    )

    return html.Div(
        [
            clipboard,
            html.Pre(
                "",
                id=id,
            ),
        ],
        style={
            "height": "calc(30% - 8px)",
            "border": "thin lightgrey solid",
        },
        className="overflow-auto my-0",
    )


layout_filters = {
    "cose": {
        "animate": {"type": mySwitch, "parameters": {"value": True}},
        # The duration of the animation for animate:'end'
        "animationDuration": {"type": mySlider, "parameters": {"value": 500}},
        # The layout animates only after this many milliseconds for animate:True
        # (prevents flashing on fast runs)
        "animationThreshold": {"type": mySlider, "parameters": {"value": 250}},
        # Number of iterations between consecutive screen positions update
        "refresh": {"type": mySlider, "parameters": {"value": 20}},
        # Whether to fit the network view after when done
        "fit": {"type": mySwitch, "parameters": {"value": True}},
        # Padding on fit
        "padding": {"type": mySlider, "parameters": {"value": 30}},
        # Excludes the label when calculating node bounding boxes for the layout algorithm
        "nodeDimensionsIncludeLabels": {"type": mySwitch, "parameters": {"value": False}},
        # Randomize the initial positions of the nodes (True) or use existing positions (False)
        "randomize": {"type": mySwitch, "parameters": {"value": False}},
        # Extra spacing between components in non-compound graphs
        "componentSpacing": {"type": mySlider, "parameters": {"value": 40}},
        # Node repulsion (non overlapping) multiplier
        "nodeRepulsion": {"type": mySlider, "parameters": {"value": 2048}},
        # Node repulsion (overlapping) multiplier
        "nodeOverlap": {"type": mySlider, "parameters": {"value": 4}},
        # Ideal edge (non nested) length
        "idealEdgeLength": {"type": mySlider, "parameters": {"value": 32}},
        # Divisor to compute edge forces
        "edgeElasticity": {"type": mySlider, "parameters": {"value": 32}},
        # Nesting factor (multiplier) to compute ideal edge length for nested edges
        "nestingFactor": {"type": mySlider, "parameters": {"value": 1.2}},
        # Gravity force (constant)
        "gravity": {"type": mySlider, "parameters": {"value": 1}},
        # Maximum number of iterations to perform
        "numIter": {"type": mySlider, "parameters": {"value": 1000}},
        # Initial temperature (maximum node displacement)
        "initialTemp": {"type": mySlider, "parameters": {"value": 1000}},
        # Cooling factor (how the temperature is reduced between consecutive iterations
        "coolingFactor": {"type": mySlider, "parameters": {"value": 0.99}},
        # Lower temperature threshold (below this point the layout will end)
        "minTemp": {"type": mySlider, "parameters": {"value": 1.0}},
    },
    "cose-blikent": {
        # 'draft', 'default' or 'proof"
        # - 'draft' fast cooling rate
        # - 'default' moderate cooling rate
        # - "proof" slow cooling rate
        "quality": {
            "type": myDropdown,
            "parameters": {"value": "default", "options": ["default", "draft", "proof"]},
        },
        # Whether to include labels in node dimensions. Useful for avoiding label overlap
        "nodeDimensionsIncludeLabels": {"type": mySwitch, "parameters": {"value": False}},
        # number of ticks per frame; higher is faster but more jerky
        "refresh": {"type": mySlider, "parameters": {"value": 30}},
        # Whether to fit the network view after when done
        "fit": {"type": mySwitch, "parameters": {"value": True}},
        # Padding on fit
        "padding": {"type": mySlider, "parameters": {"value": 10}},
        # Whether to enable incremental mode
        "randomize": {"type": mySwitch, "parameters": {"value": True}},
        # Node repulsion (non overlapping) multiplier
        "nodeRepulsion": {"type": mySlider, "parameters": {"value": 4500}},
        # Ideal (intra-graph) edge length
        "idealEdgeLength": {"type": mySlider, "parameters": {"value": 50}},
        # Divisor to compute edge forces
        "edgeElasticity": {"type": mySlider, "parameters": {"value": 0.45}},
        # Nesting factor (multiplier) to compute ideal edge length for inter-graph edges
        "nestingFactor": {"type": mySlider, "parameters": {"value": 0.1}},
        # Gravity force (constant)
        "gravity": {"type": mySlider, "parameters": {"value": 0.25}},
        # Maximum number of iterations to perform
        "numIter": {"type": mySlider, "parameters": {"value": 2500}},
        # Whether to tile disconnected nodes
        "tile": {"type": mySwitch, "parameters": {"value": True}},
        # # Type of layout animation. The option set is {'during', 'end', False}
        # "animate": {
        #     "type": myDropdown,
        #     "parameters": {"value": "end", "options": ["during", "end", False]},
        # },
        # Duration for animate:end
        "animationDuration": {"type": mySlider, "parameters": {"value": 500}},
        # Amount of vertical space to put between degree zero nodes during tiling (can also be a function)
        "tilingPaddingVertical": {"type": mySlider, "parameters": {"value": 10}},
        # Amount of horizontal space to put between degree zero nodes during tiling (can also be a function)
        "tilingPaddingHorizontal": {"type": mySlider, "parameters": {"value": 10}},
        # Gravity range (constant) for compounds
        "gravityRangeCompound": {"type": mySlider, "parameters": {"value": 1.5}},
        # Gravity force (constant) for compounds
        "gravityCompound": {"type": mySlider, "parameters": {"value": 1.0}},
        # Gravity range (constant)
        "gravityRange": {"type": mySlider, "parameters": {"value": 3.8}},
        # Initial cooling factor for incremental layout
        "initialEnergyOnIncremental": {"type": mySlider, "parameters": {"value": 0.5}},
    },
    "fcose": {
        # 'draft', 'default' or 'proof'
        # - "draft" only applies spectral layout
        # - "default" improves the quality with incremental layout (fast cooling rate)
        # - "proof" improves the quality with incremental layout (slow cooling rate)
        "quality": {
            "type": myDropdown,
            "parameters": {
                "options": [
                    "draft",
                    "default",
                    "proof",
                ],
                "value": "default",
                # "clearable": False,
            },
        },
        # Use random node positions at beginning of layout
        # if this is set to False, then quality option must be "proof"
        "randomize": {
            "type": mySwitch,
            "parameters": {
                "value": True,
            },
        },
        # False for random, True for greedy sampling
        "samplingType": {
            "type": mySwitch,
            "parameters": {
                "value": True,
            },
        },
        # Whether to include labels in node dimensions. Valid in "proof" quality
        "nodeDimensionsIncludeLabels": {
            "type": mySwitch,
            "parameters": {
                "value": False,
            },
        },
        # Whether or not simple nodes (non-compound nodes) are of uniform dimensions
        "uniformNodeDimensions": {
            "type": mySwitch,
            "parameters": {
                "value": False,
            },
        },
        "packComponents": {
            "type": mySwitch,
            "parameters": {
                "value": True,
            },
        },
        # Sample size to construct distance matrix
        "sampleSize": {"type": mySlider, "parameters": {"value": 25}},
        "animationThreshold": {"type": mySlider, "parameters": {"value": 250}},
        # Separation amount between nodes
        "nodeSeparation": {"type": mySlider, "parameters": {"value": 75}},
        # Power iteration tolerance
        "piTol": {"type": mySlider, "parameters": {"value": 0.0000001}},
        # /* incremental layout options */
        # Nesting factor (multiplier) to compute ideal edge length for nested edges
        "nestingFactor": {"type": mySlider, "parameters": {"value": 0.1}},
        # Maximum number of iterations to perform - this is a suggested value and might be adjusted by the algorithm as required
        "numIter": {"type": mySlider, "parameters": {"value": 2500}},
        "nodeRepulsion": {"type": mySlider, "parameters": {"value": 4500}},
        "idealEdgeLength": {"type": mySlider, "parameters": {"value": 50}},
        "edgeElasticity": {"type": mySlider, "parameters": {"value": 0.45}},
        # For enabling tiling
        "tile": {
            "type": mySwitch,
            "parameters": {
                "value": True,
            },
        },
        # Represents the amount of the vertical space to put between the zero degree members during the tiling operation(can also be a function)
        "tilingPaddingVertical": {"type": mySlider, "parameters": {"value": 10}},
        # Represents the amount of the horizontal space to put between the zero degree members during the tiling operation(can also be a function)
        "tilingPaddingHorizontal": {"type": mySlider, "parameters": {"value": 10}},
        # Gravity force (constant)
        "gravity": {"type": mySlider, "parameters": {"value": 0.25}},
        # Gravity range (constant)
        "gravityRange": {"type": mySlider, "parameters": {"value": 3.8}},
        # Initial cooling factor for incremental layout
        "initialEnergyOnIncremental": {"type": mySlider, "parameters": {"value": 0.3}},
    },
    "cola": {
        "animate": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # whether to show the layout as it's running
        "refresh": {
            "type": mySlider,
            "parameters": {"value": 1},
        },  # number of ticks per frame; higher is faster but more jerky
        "maxSimulationTime": {
            "type": mySlider,
            "parameters": {"value": 4000},
        },  # max length in ms to run the layout
        "ungrabifyWhileSimulating": {
            "type": mySwitch,
            "parameters": {"value": False},
        },  # so you can't drag nodes during layout
        "fit": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # on every layout reposition of nodes, fit the viewport
        "padding": {"type": mySlider, "parameters": {"value": 30}},  # padding around the simulation
        "nodeDimensionsIncludeLabels": {
            "type": mySwitch,
            "parameters": {"value": False},
        },  # whether labels should be included in determining the space used by a node
        # positioning options
        "randomize": {
            "type": mySwitch,
            "parameters": {"value": False},
        },  # use random node positions at beginning of layout
        "avoidOverlap": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # if True, prevents overlap of node bounding boxes
        "handleDisconnected": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # if True, avoids disconnected components from overlapping
        "convergenceThreshold": {
            "type": mySlider,
            "parameters": {"value": 0.01},
        },  # when the alpha value (system energy) falls below this value, the layout stops
        "nodeSpacing": {
            "type": mySlider,
            "parameters": {"value": 10},
        },  # extra spacing around nodes
        "centerGraph": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # adjusts the node positions initially to center the graph (pass False if you want to start the layout from the current position)
        # different methods of specifying edge length
        # each can be a constant numerical value or a function like `function( edge ){ return 2; }`
        "edgeLength": {
            "type": mySlider,
            "parameters": {"value": 2},
        },  # sets edge length directly in simulation
        "edgeSymDiffLength": {
            "type": mySlider,
            "parameters": {"value": 1},
        },  # symmetric diff edge length in simulation
        "edgeJaccardLength": {
            "type": mySlider,
            "parameters": {"value": 1},
        },  # jaccard edge length in simulation
    },
    "euler": {
        # The ideal length of a spring
        # - This acts as a hint for the edge length
        # - The edge length can be longer or shorter if the forces are set to extreme values
        "springLength": {"type": mySlider, "parameters": {"value": 80}},
        # Hooke's law coefficient
        # - The value ranges on [0, 1]
        # - Lower values give looser springs
        # - Higher values give tighter springs
        "springCoeff": {"type": mySlider, "parameters": {"value": 0.0008}},
        # The mass of the node in the physics simulation
        # - The mass affects the gravity node repulsion/attraction
        "mass": {"type": mySlider, "parameters": {"value": 4}},
        # Coulomb's law coefficient
        # - Makes the nodes repel each other for negative values
        # - Makes the nodes attract each other for positive values
        "gravity": {"type": mySlider, "parameters": {"value": -1.2}},
        # A force that pulls nodes towards the origin (0, 0)
        # Higher values keep the components less spread out
        "pull": {"type": mySlider, "parameters": {"value": 0.001}},
        # Theta coefficient from Barnes-Hut simulation
        # - Value ranges on [0, 1]
        # - Performance is better with smaller values
        # - Very small values may not create enough force to give a good result
        "theta": {"type": mySlider, "parameters": {"value": 0.666}},
        # Friction / drag coefficient to make the system stabilise over time
        "dragCoeff": {"type": mySlider, "parameters": {"value": 0.02}},
        # When the total of the squared position deltas is less than this value, the simulation ends
        "movementThreshold": {"type": mySlider, "parameters": {"value": 1}},
        # The amount of time passed per tick
        # - Larger values result in faster runtimes but might spread things out too far
        # - Smaller values produce more accurate results
        "timeStep": {"type": mySlider, "parameters": {"value": 20}},
        # The number of ticks per frame for animate:True
        # - A larger value reduces rendering cost but can be jerky
        # - A smaller value increases rendering cost but is smoother
        "refresh": {"type": mySlider, "parameters": {"value": 10}},
        # Whether to animate the layout
        # - True : Animate while the layout is running
        # - False : Just show the end result
        # - 'end' : Animate directly to the end result
        "animate": {"type": mySwitch, "parameters": {"value": True}},
        # Maximum iterations and time (in ms) before the layout will bail out
        # - A large value may allow for a better result
        # - A small value may make the layout end prematurely
        # - The layout may stop before this if it has settled
        "maxIterations": {"type": mySlider, "parameters": {"value": 1000}},
        "maxSimulationTime": {"type": mySlider, "parameters": {"value": 4000}},
        # Prevent the user grabbing nodes during the layout (usually with animate:True)
        "ungrabifyWhileSimulating": {"type": mySwitch, "parameters": {"value": False}},
        # Whether to fit the viewport to the repositioned graph
        # True : Fits at end of layout for animate:False or animate:'end'; fits on each frame for animate:True
        "fit": {"type": mySwitch, "parameters": {"value": True}},
        # Padding in rendered co-ordinates around the layout
        "padding": {"type": mySlider, "parameters": {"value": 30}},
        # Whether to randomize the initial positions of the nodes
        # True : Use random positions within the bounding box
        # False : Use the current node positions as the initial positions
        "randomize": {"type": mySwitch, "parameters": {"value": False}},
    },
    "spread": {
        "animate": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # Whether to show the layout as it's running
        "fit": {
            "type": mySwitch,
            "parameters": {"value": True},
        },  # Reset viewport to fit default simulationBounds
        "minDist": {
            "type": mySlider,
            "parameters": {"value": 20},
        },  # Minimum distance between nodes
        "padding": {"type": mySlider, "parameters": {"value": 20}},  # Padding
        "expandingFactor": {
            "type": mySlider,
            "parameters": {"value": -1.0},
        },  # If the network does not satisfy the minDist
        # criterium then it expands the network of this amount
        # If it is set to -1.0 the amount of expansion is automatically
        # calculated based on the minDist, the aspect ratio and the
        # number of nodes
        "maxExpandIterations": {
            "type": mySlider,
            "parameters": {"value": 4},
        },  # Maximum number of expanding iterations
        "randomize": {
            "type": mySwitch,
            "parameters": {"value": False},
        },  # Uses random initial node positions on True
    },
}

built_layouts = {
    layout_type: html.Div(
        [
            html.Div(
                [
                    layout_parameter,
                    info["type"](
                        id=f"layout-{layout_type}-{layout_parameter}", **info["parameters"]
                    ),
                ]
            )
            for layout_parameter, info in layout_type_specific_params.items()
        ],
        style={"scrollable": "y-overflow"},
    )
    for layout_type, layout_type_specific_params in layout_filters.items()
}


def tabs(prod_panels, debug):
    if debug:
        return dcc.Tabs(
            [
                dcc.Tab(
                    html.Div(prod_panels),
                    label="Main",
                    value="tab-1",
                ),
                dcc.Tab(
                    html.Div(
                        [
                            myPre("debug-info", "Full graph"),
                            myPre("debug-info-node", "Node info"),
                            myPre("debug-info-edge", "Edge info"),
                        ],
                        style={"height": "500px"},
                    ),
                    label="Elements",
                    value="tab-2",
                ),
                dcc.Tab(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Clipboard(id="copy_paste_layout"),
                                            "animate",
                                            mySwitch("layout-generic-animate"),
                                            "animationDuration",
                                            dcc.Slider(
                                                min=0,
                                                max=5000,
                                                step=500,
                                                value=2500,
                                                id="layout-generic-animationDuration",
                                            ),
                                            "fit",
                                            mySwitch("layout-generic-fit"),
                                            "padding",
                                            dcc.Slider(
                                                min=0,
                                                max=100,
                                                step=20,
                                                value=20,
                                                id="layout-generic-padding",
                                            ),
                                            html.Hr(),
                                            "LAYOUT",
                                            dcc.Dropdown(
                                                id="layout-generic-name",
                                                options=[
                                                    "cose",
                                                    "cose-blikent",
                                                    "fcose",
                                                    "cola",
                                                    "euler",
                                                    "spread",
                                                ],
                                                value="fcose",
                                                clearable=False,
                                            ),
                                        ],
                                        id="layout_generic_parameters",
                                    ),
                                    html.Div(id="layout_specific_parameters"),
                                ],
                                id="layout_parameters",
                            ),
                        ],
                        style={"height": "500px"},
                    ),
                    label="Layout",
                    value="tab-3",
                ),
            ],
            value="tab-3",
        )
    return html.Div(prod_panels)
