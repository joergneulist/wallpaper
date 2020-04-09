# wallpaper
Python project to automate wallpaper retrieval from multiple online sources and applying them.

## Basic structure

`wallpaper.py` is the central executable (there is no module setup yet).
`get`, `modify`, `apply` are subdirectories where individual plugins can be located. These should be extending the `wpPlugin` class, defining a class of exactly the same name as the python file basename (i.e. `class bing` in `bing.py`).

