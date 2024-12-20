# databpy


[![codecov](https://codecov.io/gh/BradyAJohnston/nodepad/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/nodepad)
![PyPI - Version](https://img.shields.io/pypi/v/nodepad.png) ![Tests
Workflow](https://github.com/bradyajohnston/nodepad/actions/workflows/tests.yml/badge.svg)
![CD
Workflow](https://github.com/bradyajohnston/nodepad/actions/workflows/ci-cd.yml/badge.svg)

Early stages at the moment, currently used for generating and building
docs for [Molecular
Nodes](https://bradyajohnston.github.io/MolecularNodes)

https://github.com/user-attachments/assets/5e5411df-a5e8-42e1-bd44-8f87cfbe9584

## Installation

Available on PyPI, install with pip:

``` bash
pip install nodepad
```

> [!CAUTION]
>
> `bpy` (Blender as a python module) is listed as an optional
> dependency, so that if you install `nodepad` inside of Blender you
> won’t install a redundant version of `bpy`. If you are using this
> outside of Blender, you will need to specifically request `bpy` with
> any of these methods:
>
> ``` bash
> # install wtih bpy dependency
> pip install 'nodepad[bpy]'
>
> # install both packages
> pip install nodepad bpy
>
> # install with all optional dependencies
> pip install 'nodepad[all]'
> ```

## `Documenter` class

Generates documentation for a `bpy.types.GeometryNodeTree`. The
`.as_markdown()` returns a markdown formatted string for a table for
inputs and outputs, as well as title and description.

``` python
import nodepad
import bpy
nodepad.utils.append_default_asset_node('Blend Hair Curves')
tree = bpy.data.node_groups['Blend Hair Curves']
tree.description = "This node group blends hair curves together"
doc = nodepad.Documenter(tree)
print(doc.as_markdown())
```


    ## Blend Hair Curves

    This node group blends hair curves together


    ### Outputs

    |Description|Socket               |
    |-----------|--------------------:|
    |           |`Geometry::Geometry` |

    : {tbl-colwidths="[90, 10]"}

    ### Inputs

    |Socket                 |Default|Description                                    |
    |-----------------------|:-----:|-----------------------------------------------|
    |`Geometry::Geometry`   |_None_ |Input Geometry (may include other than curves) |
    |`Factor::Float`        |1.0    |Factor to blend overall effect                 |
    |`Blend Radius::Float`  |0.05   |Radius to select neighbors for blending        |
    |`Blend Neighbors::Int` |10     |Amount of neighbors used for blending          |
    |`Preserve Length::Bool`|False  |Preserve each curve's length during deformation|

    : {tbl-colwidths="[10, 15, 80]"}
