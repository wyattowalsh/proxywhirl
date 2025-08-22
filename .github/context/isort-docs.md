This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: docs/**/*.{md,markdown,mdx,rmd,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  configuration/
    action_comments.md
    add_or_remove_imports.md
    black_compatibility.md
    config_files.md
    custom_sections_and_ordering.md
    git_hook.md
    github_action.md
    multi_line_output_modes.md
    options.md
    pre-commit.md
    profiles.md
    setuptools_integration.md
  contributing/
    1.-contributing-guide.md
    2.-coding-standard.md
    3.-code-of-conduct.md
    4.-acknowledgements.md
  howto/
    shared_profiles.md
  major_releases/
    introducing_isort_5.md
    release_policy.md
  quick_start/
    0.-try.md
    1.-install.md
    2.-cli.md
    3.-api.md
  upgrade_guides/
    5.0.0.md
  warning_and_error_codes/
    W0500.md
```

# Files

## File: docs/configuration/action_comments.md
````markdown
# Action Comments

The most basic way to configure the flow of isort within a single file is action comments. These comments are picked up and interpreted by the isort parser during parsing.


## isort: skip_file

Tells isort to skip the entire file.

Example:

```python
# !/bin/python3
# isort: skip_file
import os
import sys

...
```

!!! warning
    This should be placed as high in the file as reasonably possible.
    Since isort uses a streaming architecture, it may have already completed some work before it reaches the comment. Usually, this is okay - but can be confusing if --diff or any interactive options are used from the command line.


## isort: skip

If placed on the same line as (or within the continuation of a) an import statement, isort will not sort this import.
More specifically, it prevents the import statement from being recognized by isort as an import. In consequence, this line will be treated as code and be pushed down to below the import section of the file.

Example:

```python
import b
import a # isort: skip <- this will now stay below b
```
!!! note
    It is recommended to where possible use `# isort: off` and `# isort: on` or `# isort: split` instead as the behavior is more explicit and predictable.

## isort: off

Turns isort parsing off. Every line after an `# isort: off` statement will be passed along unchanged until an `# isort: on` comment or the end of the file.

Example:

```python
import e
import f

# isort: off

import b
import a
```

## isort: on

Turns isort parsing back on. This only makes sense if an `# isort: off` comment exists higher in the file! This allows you to have blocks of unsorted imports, around otherwise sorted ones.

Example:

```python

import e
import f

# isort: off

import b
import a

# isort: on

import c
import d

```

## isort: split

Tells isort the current sort section is finished, and all future imports belong to a new sort grouping.

Example:

```python

import e
import f

# isort: split

import a
import b
import c
import d

```

You can also use it inline to keep an import from having imports above or below it swap position:

```python
import c
import b  # isort: split
import a
```

!!! tip
    isort split is exactly the same as placing an `# isort: on` immediately below an `# isort: off`


## isort: dont-add-imports

Tells isort to not automatically add imports to this file, even if --add-imports is set.

## isort: dont-add-import: [IMPORT_LINE]

Tells isort to not automatically add a particular import, even if --add-imports says to add it.
````

## File: docs/configuration/add_or_remove_imports.md
````markdown
## Adding an import to multiple files
isort makes it easy to add an import statement across multiple files,
while being assured it's correctly placed.

To add an import to all files:

```bash
isort -a "from __future__ import print_function" *.py
```

To add an import only to files that already have imports:

```bash
isort -a "from __future__ import print_function" --append-only *.py
```


## Removing an import from multiple files

isort also makes it easy to remove an import from multiple files,
without having to be concerned with how it was originally formatted.

From the command line:

```bash
isort --rm "os.system" *.py
```
````

## File: docs/configuration/black_compatibility.md
````markdown
![isort loves black](https://raw.githubusercontent.com/pycqa/isort/main/art/isort_loves_black.png)

# Compatibility with black

Compatibility with black is very important to the isort project and comes baked in starting with version 5.
All that's required to use isort alongside black is to set the isort profile to "black".

!!! tip
    Beyond the profile, it is common to set [skip_gitignore](https://pycqa.github.io/isort/docs/configuration/options.html#skip-gitignore) (which is not enabled by default for isort as it requires git to be installed) and [line_length](https://pycqa.github.io/isort/docs/configuration/options.html#line-length) as it is common to deviate from black's default of 88.


## Using a config file (such as .isort.cfg)

For projects that officially use both isort and black, we recommend setting the black profile in a config file at the root of your project's repository.
That way it's independent of how users call isort (pre-commit, CLI, or editor integration) the black profile will automatically be applied.

For instance, your _pyproject.toml_ file would look something like

```ini
[tool.isort]
profile = "black"
```

Read More about supported [config files](https://pycqa.github.io/isort/docs/configuration/config_files.html).

## CLI

To use the profile option when calling isort directly from the commandline simply add the --profile black argument: `isort --profile black`.

A demo of how this would look like in your _.travis.yml_

```yaml
language: python
python:
  - "3.10"
  - "3.9"

install:
  - pip install -r requirements-dev.txt
  - pip install isort black
  - pip install coveralls
script:
  - pytest my-package
  - isort --profile black my-package
  - black --check --diff my-package
after_success:
  - coveralls

```

See [built-in profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html) for more profiles.

## Integration with pre-commit

You can also set the profile directly when integrating isort within pre-commit.

```yaml
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black", "--filter-files"]
```
````

## File: docs/configuration/config_files.md
````markdown
Supported Config Files
========

isort supports various standard config formats to allow customizations to be integrated into any project quickly.
When applying configurations, isort looks for the closest supported config file, in the order files are listed below.
You can manually specify the settings file or path by setting `--settings-path` from the command-line. Otherwise, isort will
traverse up to 25 parent directories until it finds a suitable config file.
Note that isort will not leave a git or Mercurial repository (checking for a `.git` or `.hg` directory).
As soon as it finds a file, it stops looking. The config file search is done relative to the current directory if `isort .`
or a file stream is passed in, or relative to the first path passed in if multiple paths are passed in.
isort **never** merges config files together due to the confusion it can cause.

!!! tip
    You can always introspect the configuration settings isort determined, and find out which config file it picked up, by running `isort . --show-config`



## .isort.cfg **[preferred format]**

The first place isort will look for settings is in dedicated .isort.cfg files.
The advantage of using this kind of config file, is that it is explicitly for isort and follows a well understood format.
The downside, is that it means one more config file in your project when you may already have several polluting your file hierarchy.

An example a config from the isort project itself:

```ini
[settings]
profile=hug
src_paths=isort,test
```

## pyproject.toml **[preferred format]**

The second place isort will look, and an equally excellent choice to place your configuration, is within a pyproject.toml file.
The advantage of using this config file, is that it is quickly becoming a standard place to configure all Python tools.
This means other developers will know to look here and you will keep your projects root nice and tidy.
The only disadvantage is that other tools you use might not yet support this format, negating the cleanliness.

```toml
[tool.isort]
profile = "hug"
src_paths = ["isort", "test"]
```

## setup.cfg

`setup.cfg` can be thought of as the precursor to `pyproject.toml`. While isort and newer tools are increasingly moving to pyproject.toml, if you rely on many tools that
use this standard it can be a natural fit to put your isort config there as well.


```ini
[isort]
profile=hug
src_paths=isort,test
```

## tox.ini

[tox](https://tox.readthedocs.io/en/latest/) is a tool commonly used in the Python community to specify multiple testing environments.
Because isort verification is commonly ran as a testing step, some prefer to place the isort config inside of the tox.ini file.

```ini
[isort]
profile = black
multi_line_output = 3
```

## .editorconfig

Finally, isort will look for a `.editorconfig` configuration with settings for Python source files. [EditorConfig](https://editorconfig.org/) is a project to enable specifying a configuration for text editing behaviour once, allowing multiple command line tools and text editors to pick it up. Since isort cares about a lot of the same settings as a text-editor (like line-length) it makes sense for it to look within these files
as well.

```
root = true

[*.py]
profile = hug
indent_style = space
indent_size = 4
skip = build,.tox,venv
src_paths=isort,test
```

## Custom config files

Optionally, you can also create a config file with a custom name, or directly point isort to a config file that falls lower in the priority order, by using [--settings-file](https://pycqa.github.io/isort/docs/configuration/options.html#settings-path).
This can be useful, for instance, if you want to have one configuration for `.py` files and another for `.pyx` - while keeping the config files at the root of your repository.

!!! tip
    Custom config files should place their configuration options inside an `[isort]` section and never a generic `[settings]` section. This is because isort can't know for sure
    how other tools are utilizing the config file.


## Supporting multiple config files in single isort run

If you have a directory structure where different sub-directories may have their separate configuration settings and you want isort to respect these configurations, not just apply the same global configuration for the entire directory then you can do so with the `--resolve-all-configs` flag. Using the `--resolve-all-configs` along with providing the directory root as `--config-root` argument(if the config-root is not explicitly defined, then isort will consider the current directory `.` where the shell is running), isort will traverse and parse all the config files defined under the `--config-root` and dynamically decide what configurations should be applied to a specific file by choosing the nearest config file in the file's path. For instance, if your directory structure is

```
directory_root

    subdir1
        .isort.cfg
        file1.py

    subdir2
        pyproject.toml
        file2.py

    subdir3
        file3.py

    setup.cfg
```

isort will sort `subdir1/file1` according to the configurations defined in `subdir1/.isort.cfg`, `subdir2/file2` with configurations from `subdir2/pyproject.toml` and `subdir3/file3.py` based on the `setup.cfg` settings.

!!! tip
    You can always confirm exactly what config file was used for a file by running isort with the `--verbose` flag.
````

## File: docs/configuration/custom_sections_and_ordering.md
````markdown
# Custom Sections and Ordering

isort provides lots of features to enable configuring how it sections imports
and how it sorts imports within those sections.
You can change the section order with `sections` option from the default
of:

```ini
FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
```

to your preference (if defined, omitting a default section may cause errors):

```ini
sections=FUTURE,STDLIB,FIRSTPARTY,THIRDPARTY,LOCALFOLDER
```

You also can define your own sections and their order.

Example:

```ini
known_django=django
known_pandas=pandas,numpy
sections=FUTURE,STDLIB,DJANGO,THIRDPARTY,PANDAS,FIRSTPARTY,LOCALFOLDER
```

would create two new sections with the specified known modules.

The `no_lines_before` option will prevent the listed sections from being
split from the previous section by an empty line.

Example:

```ini
sections=FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
no_lines_before=LOCALFOLDER
```

would produce a section with both FIRSTPARTY and LOCALFOLDER modules
combined.

**IMPORTANT NOTE**: It is very important to know when setting `known` sections that the naming
does not directly map for historical reasons. For custom settings, the only difference is
capitalization (`known_custom=custom` VS `sections=CUSTOM,...`) for all others reference the
following mapping:

 - `known_standard_library` : `STANDARD_LIBRARY`
 - `extra_standard_library` : `STANDARD_LIBRARY` # Like known standard library but appends instead of replacing
 - `known_future_library` : `FUTURE`
 - `known_first_party`: `FIRSTPARTY`
 - `known_third_party`: `THIRDPARTY`
 - `known_local_folder`: `LOCALFOLDER`

This will likely be changed in isort 6.0.0+ in a backwards compatible way.


## Auto-comment import sections

Some projects prefer to have import sections uniquely titled to aid in
identifying the sections quickly when visually scanning. isort can
automate this as well. To do this simply set the
`import_heading_{section_name}` setting for each section you wish to
have auto commented - to the desired comment.

For Example:

```ini
import_heading_stdlib=Standard Library
import_heading_firstparty=My Stuff
```

Would lead to output looking like the following:

```python
# Standard Library
import os
import sys

import django.settings

# My Stuff
import myproject.test
```

## Ordering by import length

isort also makes it easy to sort your imports by length, simply by
setting the `length_sort` option to `True`. This will result in the
following output style:

```python
from evn.util import (
    Pool,
    Dict,
    Options,
    Constant,
    DecayDict,
    UnexpectedCodePath,
)
```

It is also possible to opt-in to sorting imports by length for only
specific sections by using `length_sort_` followed by the section name
as a configuration item, e.g.:

    length_sort_stdlib=1

## Controlling how isort sections `from` imports

By default isort places straight (`import y`) imports above from imports (`from x import y`):

```python
import b
from a import a  # This will always appear below because it is a from import.
```

However, if you prefer to keep strict alphabetical sorting you can set [force sort within sections](https://pycqa.github.io/isort/docs/configuration/options.html#force-sort-within-sections) to true. Resulting in:


```python
from a import a  # This will now appear at top because a appears in the alphabet before b
import b
```

You can even tell isort to always place from imports on top, instead of the default of placing them on bottom, using [from first](https://pycqa.github.io/isort/docs/configuration/options.html#from-first).

```python
from b import b # If from first is set to True, all from imports will be placed before non-from imports.
import a
```
````

## File: docs/configuration/git_hook.md
````markdown
# Git Hook

isort provides a hook function that can be integrated into your Git
pre-commit script to check Python code before committing.

To cause the commit to fail if there are isort errors (strict mode),
include the following in `.git/hooks/pre-commit`:

```python
#!/usr/bin/env python
import sys
from isort.hooks import git_hook

sys.exit(git_hook(strict=True, modify=True, lazy=True, settings_file=""))
```

If you just want to display warnings, but allow the commit to happen
anyway, call `git_hook` without the strict parameter. If you want to
display warnings, but not also fix the code, call `git_hook` without the
modify parameter.
The `lazy` argument is to support users who are "lazy" to add files
individually to the index and tend to use `git commit -a` instead.
Set it to `True` to ensure all tracked files are properly isorted,
leave it out or set it to `False` to check only files added to your
index.

If you want to use a specific configuration file for the hook, you can pass its
path to settings_file. If no path is specifically requested, `git_hook` will
search for the configuration file starting at the directory containing the first
staged file, as per `git diff-index` ordering, and going upward in the directory
structure until a valid configuration file is found or
[`MAX_CONFIG_SEARCH_DEPTH`](src/config.py:35) directories are checked.
The settings_file parameter is used to support users who keep their configuration
file in a directory that might not be a parent of all the other files.
````

## File: docs/configuration/github_action.md
````markdown
# Github Action

isort provides an official [Github Action][github-action-docs] that can be used as part of a CI/CD workflow to ensure a project's imports are properly sorted.
The action can be found on the [Github Actions Marketplace][python-isort].

## Usage

The `python-isort` plugin is designed to be run in combination with the [`checkout`][checkout-action] and [`setup-python`][setup-python] actions.
By default, it will run recursively from the root of the repository being linted and will exit with an error if the code is not properly sorted.

### Inputs

#### `isort-version`

Optional. Version of `isort` to use. Defaults to latest version of `isort`.

#### `sort-paths`

Optional. List of paths to sort, relative to your project root. Defaults to `.`

#### `configuration`

Optional. `isort` configuration options to pass to the `isort` CLI. Defaults to `--check-only --diff`.

#### `requirements-files`

Optional. Paths to python requirements files to install before running isort.
If multiple requirements files are provided, they should be separated by a space.
If custom package installation is required, dependencies should be installed in a separate step before using this action.

!!! tip
    It is important that the project's dependencies be installed before running isort so that third-party libraries are properly sorted.

### Outputs

#### `isort-result`

Output of the `isort` CLI.

### Example usage

```yaml
name: Run isort
on:
  - push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: 3.13
      - uses: isort/isort-action@v1
        with:
            requirementsFiles: "requirements.txt requirements-test.txt"
```

[github-action-docs]: https://docs.github.com/en/free-pro-team@latest/actions
[python-isort]: https://github.com/marketplace/actions/python-isort
[checkout-action]: https://github.com/actions/checkout
[setup-python]: https://github.com/actions/setup-python
````

## File: docs/configuration/multi_line_output_modes.md
````markdown
# Multi Line Output Modes

This [config option](https://pycqa.github.io/isort/docs/configuration/options.html#multi-line-output) defines how from imports wrap when they extend past the line\_length
limit and has 12 possible settings:

## 0 - Grid

```python
from third_party import (lib1, lib2, lib3,
                         lib4, lib5, ...)
```

## 1 - Vertical

```python
from third_party import (lib1,
                         lib2,
                         lib3
                         lib4,
                         lib5,
                         ...)
```

## 2 - Hanging Indent

```python
from third_party import \
    lib1, lib2, lib3, \
    lib4, lib5, lib6
```

## 3 - Vertical Hanging Indent

```python
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4
)
```

## 4 - Hanging Grid

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5, ...)
```

## 5 - Hanging Grid Grouped

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5, ...
)
```

## 6 - Hanging Grid Grouped

Same as Mode 5. Deprecated.

## 7 - NOQA

```python
from third_party import lib1, lib2, lib3, ...  # NOQA
```

Alternatively, you can set `force_single_line` to `True` (`-sl` on the
command line) and every import will appear on its own line:

```python
from third_party import lib1
from third_party import lib2
from third_party import lib3
...
```

## 8 - Vertical Hanging Indent Bracket

Same as Mode 3 - _Vertical Hanging Indent_ but the closing parentheses
on the last line is indented.

```python
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
    )
```

## 9 - Vertical Prefix From Module Import

Starts a new line with the same `from MODULE import` prefix when lines are longer than the line length limit.

```python
from third_party import lib1, lib2, lib3
from third_party import lib4, lib5, lib6
```

## 10 - Hanging Indent With Parentheses

Same as Mode 2 - _Hanging Indent_ but uses parentheses instead of backslash
for wrapping long lines.

```python
from third_party import (
    lib1, lib2, lib3,
    lib4, lib5, lib6)
```

## 11 - Backslash Grid

Same as Mode 0 - _Grid_ but uses backslashes instead of parentheses to group imports.

```python
from third_party import lib1, lib2, lib3, \
                        lib4, lib5
```
````

## File: docs/configuration/options.md
````markdown
# Configuration options for isort

As a code formatter isort has opinions. However, it also allows you to have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted, organized, and formatted.

Too busy to build your perfect isort configuration? For curated common configurations, see isort's [built-in
profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html).

## Python Version

Tells isort to set the known standard library based on the specified Python version. Default is to assume any Python 3 version could be the target, and use a union of all stdlib modules across versions. If auto is specified, the version of the interpreter used to run isort (currently: 39) will be used.

**Type:** String  
**Default:** `py3`  
**Config default:** `3`  
**Python & Config File Name:** py_version  
**CLI Flags:**

- --py
- --python-version

**Examples:**

### Example `.isort.cfg`

```
[settings]
py_version=39

```

### Example `pyproject.toml`

```
[tool.isort]
py_version=39

```

### Example cli usage

`isort --py 39`

## Force To Top

Force specific imports to the top of their appropriate section.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** force_to_top  
**CLI Flags:**

- -t
- --top

## Skip

Files that isort should skip over. If you want to skip multiple files you should specify twice: `--skip file1 --skip file2`. Values can be file names, directory names or file paths. To skip all files in a nested path, use [`--skip-glob`](#skip-glob). To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `('.bzr', '.direnv', '.eggs', '.git', '.hg', '.mypy_cache', '.nox', '.pants.d', '.pytype' '.svn', '.tox', '.venv', '__pypackages__', '_build', 'buck-out', 'build', 'dist', 'node_modules', 'venv')`  
**Config default:** `['.bzr', '.direnv', '.eggs', '.git', '.hg', '.mypy_cache', '.nox', '.pants.d', '.svn', '.tox', '.venv', '__pypackages__', '_build', 'buck-out', 'build', 'dist', 'node_modules', 'venv']`  
**Python & Config File Name:** skip  
**CLI Flags:**

- -s
- --skip

**Examples:**

### Example `.isort.cfg`

```
[settings]
skip=.gitignore,.dockerignore
```

### Example `pyproject.toml`

```
[tool.isort]
skip = [".gitignore", ".dockerignore"]

```

## Extend Skip

Extends --skip to add additional files that isort should skip over. If you want to skip multiple files you should specify twice: --skip file1 --skip file2. Values can be file names, directory names or file paths. To skip all files in a nested path, use [`--skip-glob`](#skip-glob). To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** extend_skip  
**CLI Flags:**

- --extend-skip

**Examples:**

### Example `.isort.cfg`

```
[settings]
extend_skip=.md,.json
```

### Example `pyproject.toml`

```
[tool.isort]
extend_skip = [".md", ".json"]

```

## Skip Glob

Files that isort should skip over. To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** skip_glob  
**CLI Flags:**

- --sg
- --skip-glob

**Examples:**

### Example `.isort.cfg`

```
[settings]
skip_glob=docs/*

```

### Example `pyproject.toml`

```
[tool.isort]
skip_glob = ["docs/*"]

```

## Extend Skip Glob

Additional files that isort should skip over (extending --skip-glob). To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** extend_skip_glob  
**CLI Flags:**

- --extend-skip-glob

**Examples:**

### Example `.isort.cfg`

```
[settings]
extend_skip_glob=my_*_module.py,test/*

```

### Example `pyproject.toml`

```
[tool.isort]
extend_skip_glob = ["my_*_module.py", "test/*"]

```

## Skip Gitignore

Treat project as a git repository and ignore files listed in .gitignore. To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

NOTE: This requires git to be installed and accessible from the same shell as isort.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** skip_gitignore  
**CLI Flags:**

- --gitignore
- --skip-gitignore

## Line Length

The max length of an import line (used for wrapping long imports).

**Type:** Int  
**Default:** `79`  
**Config default:** `79`  
**Python & Config File Name:** line_length  
**CLI Flags:**

- -l
- -w
- --line-length
- --line-width

## Wrap Length

Specifies how long lines that are wrapped should be, if not set line_length is used.
NOTE: wrap_length must be LOWER than or equal to line_length.

**Type:** Int  
**Default:** `0`  
**Config default:** `0`  
**Python & Config File Name:** wrap_length  
**CLI Flags:**

- --wl
- --wrap-length

## Line Ending

Forces line endings to the specified value. If not set, values will be guessed per-file.

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** line_ending  
**CLI Flags:**

- --le
- --line-ending

## Sort Re-exports

Specifies whether to sort re-exports (`__all__` collections) automatically.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** sort_reexports  
**CLI Flags:**

- --srx
- --sort-reexports

## Sections

What sections isort should display imports for and in what order

**Type:** List of Strings  
**Default:** `('FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER')`  
**Config default:** `['FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER']`  
**Python & Config File Name:** sections  
**CLI Flags:** **Not Supported**

## No Sections

Put all imports into the same section bucket

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** no_sections  
**CLI Flags:**

- --ds
- --no-sections

## Known Future Library

Force isort to recognize a module as part of Python's internal future compatibility libraries. WARNING: this overrides the behavior of __future__ handling and therefore can result in code that can't execute. If you're looking to add dependencies such as six, a better option is to create another section below --future using custom sections. See: https://github.com/PyCQA/isort#custom-sections-and-ordering and the discussion here: https://github.com/PyCQA/isort/issues/1463.

**Type:** List of Strings  
**Default:** `('__future__',)`  
**Config default:** `['__future__']`  
**Python & Config File Name:** known_future_library  
**CLI Flags:**

- -f
- --future

## Known Third Party

Force isort to recognize a module as being part of a third party library.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** known_third_party  
**CLI Flags:**

- -o
- --thirdparty

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_third_party=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_third_party = ["my_module1", "my_module2"]

```

## Known First Party

Force isort to recognize a module as being part of the current python project.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** known_first_party  
**CLI Flags:**

- -p
- --project

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_first_party=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_first_party = ["my_module1", "my_module2"]

```

## Known Local Folder

Force isort to recognize a module as being a local folder. Generally, this is reserved for relative imports (from . import module).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** known_local_folder  
**CLI Flags:**

- --known-local-folder

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_local_folder=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_local_folder = ["my_module1", "my_module2"]

```

## Known Standard Library

Force isort to recognize a module as part of Python's standard library.

**Type:** List of Strings  
**Default:** `('_ast', '_dummy_thread', '_thread', 'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'dummy_threading', 'email', 'encodings', 'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fpectl', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'macpath', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'ntpath', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'sre', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo')`  
**Config default:** `['_ast', '_dummy_thread', '_thread', 'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'dummy_threading', 'email', 'encodings', 'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fpectl', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'macpath', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'ntpath', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'sre', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo']`  
**Python & Config File Name:** known_standard_library  
**CLI Flags:**

- -b
- --builtin

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_standard_library=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_standard_library = ["my_module1", "my_module2"]

```

## Extra Standard Library

Extra modules to be included in the list of ones in Python's standard library.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** extra_standard_library  
**CLI Flags:**

- --extra-builtin

**Examples:**

### Example `.isort.cfg`

```
[settings]
extra_standard_library=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
extra_standard_library = ["my_module1", "my_module2"]

```

## Known Other

known_OTHER is how imports of custom sections are defined. OTHER is a placeholder for the custom section name.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** known_other  
**CLI Flags:** **Not Supported**

**Examples:**

### Example `.isort.cfg`

```
[settings]
sections=FUTURE,STDLIB,THIRDPARTY,AIRFLOW,FIRSTPARTY,LOCALFOLDER
known_airflow=airflow
```

### Example `pyproject.toml`

```
[tool.isort]
sections = ['FUTURE', 'STDLIB', 'THIRDPARTY', 'AIRFLOW', 'FIRSTPARTY', 'LOCALFOLDER']
known_airflow = ['airflow']
```

## Multi Line Output

Multi line output (0-grid, 1-vertical, 2-hanging, 3-vert-hanging, 4-vert-grid, 5-vert-grid-grouped, 6-deprecated-alias-for-5, 7-noqa, 8-vertical-hanging-indent-bracket, 9-vertical-prefix-from-module-import, 10-hanging-indent-with-parentheses).

**Type:** Wrapmodes  
**Default:** `WrapModes.GRID`  
**Config default:** `WrapModes.GRID`  
**Python & Config File Name:** multi_line_output  
**CLI Flags:**

- -m
- --multi-line

**Examples:**

### Example `.isort.cfg`

```
[settings]
multi_line_output=3
```

### Example `pyproject.toml`

```
[tool.isort]
multi_line_output = 3
```

## Forced Separate

Force certain sub modules to show separately

**Type:** List of Strings  
**Default:** `()`  
**Config default:** `[]`  
**Python & Config File Name:** forced_separate  
**CLI Flags:** **Not Supported**

**Examples:**

### Example `.isort.cfg`

```
[settings]
forced_separate=glob_exp1,glob_exp2

```

### Example `pyproject.toml`

```
[tool.isort]
forced_separate = ["glob_exp1", "glob_exp2"]

```

## Indent

String to place for indents defaults to "    " (4 spaces).

**Type:** String  
**Default:** `    `  
**Config default:** `    `  
**Python & Config File Name:** indent  
**CLI Flags:**

- -i
- --indent

## Comment Prefix

Allows customizing how isort prefixes comments that it adds or modifies on import linesGenerally `  #` (two spaces before a pound symbol) is use, though one space is also common.

**Type:** String  
**Default:** `  #`  
**Config default:** `  #`  
**Python & Config File Name:** comment_prefix  
**CLI Flags:** **Not Supported**

## Length Sort

Sort imports by their string length.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** length_sort  
**CLI Flags:**

- --ls
- --length-sort

## Length Sort Straight

Sort straight imports by their string length. Similar to `length_sort` but applies only to straight imports and doesn't affect from imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** length_sort_straight  
**CLI Flags:**

- --lss
- --length-sort-straight

## Length Sort Sections

Sort the given sections by length

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** length_sort_sections  
**CLI Flags:** **Not Supported**

**Examples:**

### Example `.isort.cfg`

```
[settings]
length_sort_sections=future,stdlib

```

### Example `pyproject.toml`

```
[tool.isort]
length_sort_sections = ["future", "stdlib"]

```

## Add Imports

Adds the specified import line to all files, automatically determining correct placement.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** add_imports  
**CLI Flags:**

- -a
- --add-import

**Examples:**

### Example `.isort.cfg`

```
[settings]
add_imports=import os,import json

```

### Example `pyproject.toml`

```
[tool.isort]
add_imports = ["import os", "import json"]

```

## Remove Imports

Removes the specified import from all files.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** remove_imports  
**CLI Flags:**

- --rm
- --remove-import

**Examples:**

### Example `.isort.cfg`

```
[settings]
remove_imports=os,json

```

### Example `pyproject.toml`

```
[tool.isort]
remove_imports = ["os", "json"]

```

## Append Only

Only adds the imports specified in --add-import if the file contains existing imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** append_only  
**CLI Flags:**

- --append
- --append-only

## Reverse Relative

Reverse order of relative imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** reverse_relative  
**CLI Flags:**

- --rr
- --reverse-relative

## Force Single Line

Forces all from imports to appear on their own line

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_single_line  
**CLI Flags:**

- --sl
- --force-single-line-imports

## Single Line Exclusions

One or more modules to exclude from the single line rule.

**Type:** List of Strings  
**Default:** `()`  
**Config default:** `[]`  
**Python & Config File Name:** single_line_exclusions  
**CLI Flags:**

- --nsl
- --single-line-exclusions

**Examples:**

### Example `.isort.cfg`

```
[settings]
single_line_exclusions=os,json

```

### Example `pyproject.toml`

```
[tool.isort]
single_line_exclusions = ["os", "json"]

```

## Default Section

Sets the default section for import options: ('FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER')

**Type:** String  
**Default:** `THIRDPARTY`  
**Config default:** `THIRDPARTY`  
**Python & Config File Name:** default_section  
**CLI Flags:**

- --sd
- --section-default

## Import Headings

A mapping of import sections to import heading comments that should show above them.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** import_headings  
**CLI Flags:** **Not Supported**

## Import Footers

A mapping of import sections to import footer comments that should show below them.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** import_footers  
**CLI Flags:** **Not Supported**

## Balanced Wrapping

Balances wrapping to produce the most consistent line length possible

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** balanced_wrapping  
**CLI Flags:**

- -e
- --balanced

## Use Parentheses

Use parentheses for line continuation on length limit instead of backslashes. **NOTE**: This is separate from wrap modes, and only affects how individual lines that  are too long get continued, not sections of multiple imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** use_parentheses  
**CLI Flags:**

- --up
- --use-parentheses

## Order By Type

Order imports by type, which is determined by case, in addition to alphabetically.

**NOTE**: type here refers to the implied type from the import name capitalization.
 isort does not do type introspection for the imports. These "types" are simply: CONSTANT_VARIABLE, CamelCaseClass, variable_or_function. If your project follows PEP8 or a related coding standard and has many imports this is a good default, otherwise you likely will want to turn it off. From the CLI the `--dont-order-by-type` option will turn this off.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** order_by_type  
**CLI Flags:**

- --ot
- --order-by-type

## Atomic

Ensures the output doesn't save if the resulting file contains syntax errors.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** atomic  
**CLI Flags:**

- --ac
- --atomic

## Lines Before Imports

The number of blank lines to place before imports. -1 for automatic determination

**Type:** Int  
**Default:** `-1`  
**Config default:** `-1`  
**Python & Config File Name:** lines_before_imports  
**CLI Flags:**

- --lbi
- --lines-before-imports

## Lines After Imports

The number of blank lines to place after imports. -1 for automatic determination

**Type:** Int  
**Default:** `-1`  
**Config default:** `-1`  
**Python & Config File Name:** lines_after_imports  
**CLI Flags:**

- --lai
- --lines-after-imports

## Lines Between Sections

The number of lines to place between sections

**Type:** Int  
**Default:** `1`  
**Config default:** `1`  
**Python & Config File Name:** lines_between_sections  
**CLI Flags:** **Not Supported**

## Lines Between Types

The number of lines to place between direct and from imports

**Type:** Int  
**Default:** `0`  
**Config default:** `0`  
**Python & Config File Name:** lines_between_types  
**CLI Flags:**

- --lbt
- --lines-between-types

## Combine As Imports

Combines as imports on the same line.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** combine_as_imports  
**CLI Flags:**

- --ca
- --combine-as

## Combine Star

Ensures that if a star import is present, nothing else is imported from that namespace.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** combine_star  
**CLI Flags:**

- --cs
- --combine-star

## Include Trailing Comma

Includes a trailing comma on multi line imports that include parentheses.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** include_trailing_comma  
**CLI Flags:**

- --tc
- --trailing-comma
## Split on Trailing Comma

Split imports list followed by a trailing comma into VERTICAL_HANGING_INDENT mode. This follows Black style magic comma.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** split_on_trailing_comma  
**CLI Flags:**

- --split-on-trailing-comma

## From First

Switches the typical ordering preference, showing from imports first then straight ones.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** from_first  
**CLI Flags:**

- --ff
- --from-first

## Verbose

Shows verbose output, such as when files are skipped or when a check is successful.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** verbose  
**CLI Flags:**

- -v
- --verbose

## Quiet

Shows extra quiet output, only errors are outputted.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** quiet  
**CLI Flags:**

- -q
- --quiet

## Force Adds

Forces import adds even if the original file is empty.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_adds  
**CLI Flags:**

- --af
- --force-adds

## Force Alphabetical Sort Within Sections

Force all imports to be sorted alphabetically within a section

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_alphabetical_sort_within_sections  
**CLI Flags:**

- --fass
- --force-alphabetical-sort-within-sections

## Force Alphabetical Sort

Force all imports to be sorted as a single section

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_alphabetical_sort  
**CLI Flags:**

- --fas
- --force-alphabetical-sort

## Force Grid Wrap

Force number of from imports (defaults to 2 when passed as CLI flag without value) to be grid wrapped regardless of line length. If 0 is passed in (the global default) only line length is considered.

**Type:** Int  
**Default:** `0`  
**Config default:** `0`  
**Python & Config File Name:** force_grid_wrap  
**CLI Flags:**

- --fgw
- --force-grid-wrap

## Force Sort Within Sections

Don't sort straight-style imports (like import sys) before from-style imports (like from itertools import groupby). Instead, sort the imports by module, independent of import style.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_sort_within_sections  
**CLI Flags:**

- --fss
- --force-sort-within-sections

## Lexicographical

Lexicographical order is strictly alphabetical order. For example by default isort will sort `1, 10, 2` into `1, 2, 10` - but with lexicographical sorting enabled it will remain `1, 10, 2`.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** lexicographical  
**CLI Flags:** **Not Supported**

## Group By Package

If `True` isort will automatically create section groups by the top-level package they come from.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** group_by_package  
**CLI Flags:** **Not Supported**

## Ignore Whitespace

Tells isort to ignore whitespace differences when --check-only is being used.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** ignore_whitespace  
**CLI Flags:**

- --ws
- --ignore-whitespace

## No Lines Before

Sections which should not be split with previous by empty lines

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** no_lines_before  
**CLI Flags:**

- --nlb
- --no-lines-before

**Examples:**

### Example `.isort.cfg`

```
[settings]
no_lines_before=future,stdlib

```

### Example `pyproject.toml`

```
[tool.isort]
no_lines_before = ["future", "stdlib"]

```

## No Inline Sort

Leaves `from` imports with multiple imports 'as-is' (e.g. `from foo import a, c ,b`).

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** no_inline_sort  
**CLI Flags:**

- --nis
- --no-inline-sort

## Ignore Comments

If enabled, isort will strip comments that exist within import lines.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** ignore_comments  
**CLI Flags:** **Not Supported**

## Case Sensitive

Tells isort to include casing when sorting module names

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** case_sensitive  
**CLI Flags:**

- --case-sensitive

## Virtual Env

Virtual environment to use for determining whether a package is third-party

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** virtual_env  
**CLI Flags:**

- --virtual-env

## Conda Env

Conda environment to use for determining whether a package is third-party

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** conda_env  
**CLI Flags:**

- --conda-env

## Ensure Newline Before Comments

Inserts a blank line before a comment following an import.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** ensure_newline_before_comments  
**CLI Flags:**

- -n
- --ensure-newline-before-comments

## Profile

Base profile type to use for configuration. Profiles include: black, django,
pycharm, google, open\_stack, plone, attrs, hug, wemake, appnexus. As well as
any [shared
profiles](https://pycqa.github.io/isort/docs/howto/shared_profiles.html).

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** profile  
**CLI Flags:**

- --profile

## Honor Noqa

Tells isort to honor noqa comments to enforce skipping those comments.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** honor_noqa  
**CLI Flags:**

- --honor-noqa

## Src Paths

Add an explicitly defined source path (modules within src paths have their imports automatically categorized as first_party). Glob expansion (`*` and `**`) is supported for this option.

**Type:** List of Strings  
**Default:** `()`  
**Config default:** `[]`  
**Python & Config File Name:** src_paths  
**CLI Flags:**

- --src
- --src-path

**Examples:**

### Example `.isort.cfg`

```
[settings]
src_paths = src,tests

```

### Example `pyproject.toml`

```
[tool.isort]
src_paths = ["src", "tests"]

```

## Old Finders

Use the old deprecated finder logic that relies on environment introspection magic.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** old_finders  
**CLI Flags:**

- --old-finders
- --magic-placement

## Remove Redundant Aliases

Tells isort to remove redundant aliases from imports, such as `import os as os`. This defaults to `False` simply because some projects use these seemingly useless  aliases to signify intent and change behaviour.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** remove_redundant_aliases  
**CLI Flags:**

- --remove-redundant-aliases

## Float To Top

Causes all non-indented imports to float to the top of the file having its imports sorted (immediately below the top of file comment).
This can be an excellent shortcut for collecting imports every once in a while when you place them in the middle of a file to avoid context switching.

*NOTE*: It currently doesn't work with cimports and introduces some extra over-head and a performance penalty.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** float_to_top  
**CLI Flags:**

- --float-to-top

## Filter Files

Tells isort to filter files even when they are explicitly passed in as part of the CLI command.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** filter_files  
**CLI Flags:**

- --filter-files

## Formatter

Specifies the name of a formatting plugin to use when producing output.

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** formatter  
**CLI Flags:**

- --formatter

## Formatting Function

The fully qualified Python path of a function to apply to format code sorted by isort.

**Type:** Nonetype  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** formatting_function  
**CLI Flags:** **Not Supported**

## Color Output

Tells isort to use color in terminal output.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** color_output  
**CLI Flags:**

- --color

## Treat Comments As Code

Tells isort to treat the specified single line comment(s) as if they are code.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** treat_comments_as_code  
**CLI Flags:**

- --treat-comment-as-code

**Examples:**

### Example `.isort.cfg`

```
[settings]
treat_comments_as_code = # my comment 1, # my other comment

```

### Example `pyproject.toml`

```
[tool.isort]
treat_comments_as_code = ["# my comment 1", "# my other comment"]

```

## Treat All Comments As Code

Tells isort to treat all single line comments as if they are code.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** treat_all_comments_as_code  
**CLI Flags:**

- --treat-all-comment-as-code

## Supported Extensions

Specifies what extensions isort can be run against.

**Type:** List of Strings  
**Default:** `('pxd', 'py', 'pyi', 'pyx')`  
**Config default:** `['pxd', 'py', 'pyi', 'pyx']`  
**Python & Config File Name:** supported_extensions  
**CLI Flags:**

- --ext
- --extension
- --supported-extension

**Examples:**

### Example `.isort.cfg`

```
[settings]
supported_extensions=pyw,ext

```

### Example `pyproject.toml`

```
[tool.isort]
supported_extensions = ["pyw", "ext"]

```

## Blocked Extensions

Specifies what extensions isort can never be run against.

**Type:** List of Strings  
**Default:** `('pex',)`  
**Config default:** `['pex']`  
**Python & Config File Name:** blocked_extensions  
**CLI Flags:**

- --blocked-extension

**Examples:**

### Example `.isort.cfg`

```
[settings]
blocked_extensions=pyw,pyc

```

### Example `pyproject.toml`

```
[tool.isort]
blocked_extensions = ["pyw", "pyc"]

```

## Constants

An override list of tokens to always recognize as a CONSTANT for order_by_type regardless of casing.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** constants  
**CLI Flags:** **Not Supported**

## Classes

An override list of tokens to always recognize as a Class for order_by_type regardless of casing.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** classes  
**CLI Flags:** **Not Supported**

## Variables

An override list of tokens to always recognize as a var for order_by_type regardless of casing.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** variables  
**CLI Flags:** **Not Supported**

## Dedup Headings

Tells isort to only show an identical custom import heading comment once, even if there are multiple sections with the comment set.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** dedup_headings  
**CLI Flags:**

- --dedup-headings

## Only Sections

Causes imports to be sorted based on their sections like STDLIB, THIRDPARTY, etc. Within sections, the imports are ordered by their import style and the imports with the same style maintain their relative positions.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** only_sections  
**CLI Flags:**

- --only-sections
- --os

## Only Modified

Suppresses verbose output for non-modified files.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** only_modified  
**CLI Flags:**

- --only-modified
- --om

## Combine Straight Imports

Combines all the bare straight imports of the same section in a single line. Won't work with sections which have 'as' imports

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** combine_straight_imports  
**CLI Flags:**

- --combine-straight-imports
- --csi

## Auto Identify Namespace Packages

Automatically determine local namespace packages, generally by lack of any src files before a src containing directory.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** auto_identify_namespace_packages  
**CLI Flags:** **Not Supported**

## Namespace Packages

Manually specify one or more namespace packages.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** namespace_packages  
**CLI Flags:** **Not Supported**

## Follow Links

If `True` isort will follow symbolic links when doing recursive sorting.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** follow_links  
**CLI Flags:** **Not Supported**

## Indented Import Headings

If `True` isort will apply import headings to indented imports the same way it does unindented ones.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** indented_import_headings  
**CLI Flags:** **Not Supported**

## Honor Case In Force Sorted Sections

Honor `--case-sensitive` when `--force-sort-within-sections` is being used. Without this option set, `--order-by-type` decides module name ordering too.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** honor_case_in_force_sorted_sections  
**CLI Flags:**

- --hcss
- --honor-case-in-force-sorted-sections

## Sort Relative In Force Sorted Sections

When using `--force-sort-within-sections`, sort relative imports the same way as they are sorted when not using that setting.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** sort_relative_in_force_sorted_sections  
**CLI Flags:**

- --srss
- --sort-relative-in-force-sorted-sections

## Overwrite In Place

Tells isort to overwrite in place using the same file handle. Comes at a performance and memory usage penalty over its standard approach but ensures all file flags and modes stay unchanged.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** overwrite_in_place  
**CLI Flags:**

- --overwrite-in-place

## Reverse Sort

Reverses the ordering of imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** reverse_sort  
**CLI Flags:**

- --reverse-sort

## Star First

Forces star imports above others to avoid overriding directly imported variables.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** star_first  
**CLI Flags:**

- --star-first

## Git Ignore

If `True` isort will honor ignores within locally defined .git_ignore files.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** git_ignore  
**CLI Flags:** **Not Supported**

## Format Error

Override the format used to print errors.

**Type:** String  
**Default:** `{error}: {message}`  
**Config default:** `{error}: {message}`  
**Python & Config File Name:** format_error  
**CLI Flags:**

- --format-error

## Format Success

Override the format used to print success.

**Type:** String  
**Default:** `{success}: {message}`  
**Config default:** `{success}: {message}`  
**Python & Config File Name:** format_success  
**CLI Flags:**

- --format-success

## Sort Order

Specify sorting function. Can be built in (natural[default] = force numbers to be sequential, native = Python's built-in sorted function) or an installable plugin.

**Type:** String  
**Default:** `natural`  
**Config default:** `natural`  
**Python & Config File Name:** sort_order  
**CLI Flags:**

- --sort-order

## Show Version

Displays the currently installed version of isort.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -V
- --version

**Examples:**

### Example cli usage

`isort --version`

## Version Number

Returns just the current version number without the logo

**Type:** String  
**Default:** `==SUPPRESS==`  
**Config default:** `==SUPPRESS==`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --vn
- --version-number

## Write To Stdout

Force resulting output to stdout, instead of in-place.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -d
- --stdout

## Show Config

See isort's determined config, as well as sources of config options.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --show-config

## Show Files

See the files isort will be run against with the current config options.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --show-files

## Show Diff

Prints a diff of all the changes isort would make to a file, instead of changing it in place

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --df
- --diff

## Check

Checks the file for unsorted / unformatted imports and prints them to the command line without modifying the file. Returns 0 when nothing would change and returns 1 when the file would be reformatted.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -c
- --check-only
- --check

## Settings Path

Explicitly set the settings path or file instead of auto determining based on file location.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --sp
- --settings-path
- --settings-file
- --settings

## Config Root

Explicitly set the config root for resolving all configs. When used with the --resolve-all-configs flag, isort will look at all sub-folders in this config root to resolve config files and sort files based on the closest available config(if any)

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --cr
- --config-root

## Resolve All Configs

Tells isort to resolve the configs for all sub-directories and sort files in terms of its closest config files.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --resolve-all-configs

## Jobs

Number of files to process in parallel. Negative value means use number of CPUs.

**Type:** Int  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -j
- --jobs

## Ask To Apply

Tells isort to apply changes interactively.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --interactive

## Files

One or more Python source files that need their imports sorted.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- 

## Dont Follow Links

Tells isort not to follow symlinks that are encountered when running recursively.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --dont-follow-links

## Filename

Provide the filename associated with a stream.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --filename

## Allow Root

Tells isort not to treat / specially, allowing it to be run against the root dir.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --allow-root

## Dont Float To Top

Forces --float-to-top setting off. See --float-to-top for more information.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --dont-float-to-top

## Dont Order By Type

Don't order imports by type, which is determined by case, in addition to alphabetically.

**NOTE**: type here refers to the implied type from the import name capitalization.
 isort does not do type introspection for the imports. These "types" are simply: CONSTANT_VARIABLE, CamelCaseClass, variable_or_function. If your project follows PEP8 or a related coding standard and has many imports this is a good default. You can turn this on from the CLI using `--order-by-type`.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --dt
- --dont-order-by-type

## Ext Format

Tells isort to format the given files according to an extensions formatting rules.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --ext-format

## Deprecated Flags

==SUPPRESS==

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -k
- --keep-direct-and-as
````

## File: docs/configuration/pre-commit.md
````markdown
Using isort with pre-commit
========

isort provides official support for [pre-commit](https://pre-commit.com/).

### isort pre-commit step

To use isort's official pre-commit integration add the following config:

```yaml
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        name: isort (python)
```

under the `repos` section of your projects `.pre-commit-config.yaml` file.  Optionally if you want to have different hooks
over different file types (ex: python vs cython vs pyi) you can do so with the following config:

```yaml
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        name: isort (python)
      - id: isort
        name: isort (cython)
        types: [cython]
      - id: isort
        name: isort (pyi)
        types: [pyi]
```

### seed-isort-config

Older versions of isort used a lot of magic to determine import placement, that could easily break when running on CI/CD.
To fix this, a utility called `seed-isort-config` was created. Since isort 5 however, the project has drastically improved its placement
logic and ensured a good level of consistency across environments.
If you have a step in your pre-commit config called `seed-isort-config` or similar, it is highly recommend that you remove this.
It is guaranteed to slow things down, and can conflict with isort's own module placement logic.
````

## File: docs/configuration/profiles.md
````markdown
Built-in Profile for isort
========

The following profiles are built into isort to allow easy interoperability with
common projects and code styles.

To use any of the listed profiles, use `isort --profile PROFILE_NAME` from the command line, or `profile=PROFILE_NAME` in your configuration file.


#black


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **split_on_trailing_comma**: `True`
 - **force_grid_wrap**: `0`
 - **use_parentheses**: `True`
 - **ensure_newline_before_comments**: `True`
 - **line_length**: `88`

#django


 - **combine_as_imports**: `True`
 - **include_trailing_comma**: `True`
 - **multi_line_output**: `5`
 - **line_length**: `79`

#pycharm


 - **multi_line_output**: `3`
 - **force_grid_wrap**: `2`
 - **lines_after_imports**: `2`

#google


 - **force_single_line**: `True`
 - **force_sort_within_sections**: `True`
 - **lexicographical**: `True`
 - **single_line_exclusions**: `('typing',)`
 - **order_by_type**: `False`
 - **group_by_package**: `True`

#open_stack


 - **force_single_line**: `True`
 - **force_sort_within_sections**: `True`
 - **lexicographical**: `True`

#plone


 - **force_alphabetical_sort**: `True`
 - **force_single_line**: `True`
 - **lines_after_imports**: `2`
 - **line_length**: `200`

#attrs


 - **atomic**: `True`
 - **force_grid_wrap**: `0`
 - **include_trailing_comma**: `True`
 - **lines_after_imports**: `2`
 - **lines_between_types**: `1`
 - **multi_line_output**: `3`
 - **use_parentheses**: `True`

#hug


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **force_grid_wrap**: `0`
 - **use_parentheses**: `True`
 - **line_length**: `100`

#wemake


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **use_parentheses**: `True`
 - **line_length**: `80`

#appnexus


 - **multi_line_output**: `3`
 - **include_trailing_comma**: `True`
 - **force_grid_wrap**: `0`
 - **use_parentheses**: `True`
 - **ensure_newline_before_comments**: `True`
 - **line_length**: `88`
 - **force_sort_within_sections**: `True`
 - **order_by_type**: `False`
 - **case_sensitive**: `False`
 - **reverse_relative**: `True`
 - **sort_relative_in_force_sorted_sections**: `True`
 - **sections**: `['FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'APPLICATION', 'LOCALFOLDER']`
 - **no_lines_before**: `'LOCALFOLDER'`
````

## File: docs/configuration/setuptools_integration.md
````markdown
# Setuptools integration

Upon installation, isort enables a `setuptools` command that checks
Python files declared by your project.

Running `python setup.py isort` on the command line will check the files
listed in your `py_modules` and `packages`. If any warning is found, the
command will exit with an error code:

```bash
$ python setup.py isort
```

Also, to allow users to be able to use the command without having to
install isort themselves, add isort to the setup\_requires of your
`setup()` like so:

```python
setup(
    name="project",
    packages=["project"],

    setup_requires=[
        "isort"
    ]
)
```
````

## File: docs/contributing/1.-contributing-guide.md
````markdown
Contributing to isort
========

Looking for a useful open source project to contribute to?
Want your contributions to be warmly welcomed and acknowledged?
Welcome! You have found the right place.

## Getting isort set up for local development
The first step when contributing to any project is getting it set up on your local machine. isort aims to make this as simple as possible.

Account Requirements:

- [A valid GitHub account](https://github.com/join)

Base System Requirements:

- Python3.9+
- uv
- bash or a bash compatible shell (should be auto-installed on Linux / Mac)
  - WSL users running Ubuntu may need to install Python's venv module even after installing Python.

Once you have verified that your system matches the base requirements you can start to get the project working by following these steps:

1. [Fork the project on GitHub](https://github.com/pycqa/isort/fork).
1. Clone your fork to your local file system:
    `git clone https://github.com/$GITHUB_ACCOUNT/isort.git`
1. `cd isort`
1. `uv sync --all-extras --frozen`
   * Optionally, isolate uv's installation from the rest of your system using the instructions on the uv site here: https://docs.astral.sh/uv/ 
1. `./scripts/test.sh` should yield Success: no issues found
1. `./scripts/clean.sh` should yield a report checking packages

**TIP**: `./scripts/done.sh` will run both clean and test in one step.

### Docker development

If you would instead like to develop using Docker, the only local requirement is docker.
See the [docker docs](https://docs.docker.com/get-started/) if you have not used docker before.

Once you have the docker daemon running and have cloned the repository, you can get started by following these steps:

1. `cd isort`
2. `./scripts/docker.sh`

A local test cycle might look like the following:

1. `docker build ./ -t isort:latest`
2. `docker run isort`
3. if #2 fails, debug, save, and goto #1
    * `docker run -it isort bash` will get you into the failed environment
    * `docker run -v $(git rev-parse --show-toplevel):/isort` will make changes made in the docker environment persist on your local checkout.
      **TIP**: combine both to get an interactive docker shell that loads changes made locally, even after build, to quickly rerun that pesky failing test
4. `./scripts/docker.sh`
5. if #4 fails, debug, save and goto #1; you may need to specify a different `--build-arg VERSION=$VER`
6. congrats! you are probably ready to push a contribution

## Making a contribution
Congrats! You're now ready to make a contribution! Use the following as a guide to help you reach a successful pull-request:

1. Check the [issues page](https://github.com/pycqa/isort/issues) on GitHub to see if the task you want to complete is listed there.
    - If it's listed there, write a comment letting others know you are working on it.
    - If it's not listed in GitHub issues, go ahead and log a new issue. Then add a comment letting everyone know you have it under control.
        - If you're not sure if it's something that is good for the main isort project and want immediate feedback, you can discuss it [here](https://gitter.im/timothycrosley/isort).
2. Create an issue branch for your local work `git checkout -b issue/$ISSUE-NUMBER`.
3. Do your magic here.
4. Ensure your code matches the [HOPE-8 Coding Standard](https://github.com/hugapi/HOPE/blob/master/all/HOPE-8--Style-Guide-for-Hug-Code.md#hope-8----style-guide-for-hug-code) used by the project.
5. Run tests locally to make sure everything is still working
	`./scripts/done.sh`
	_Or if you are using Docker_
	`docker run isort:latest`
6. Submit a pull request to the main project repository via GitHub.

Thanks for the contribution! It will quickly get reviewed, and, once accepted, will result in your name being added to the acknowledgments list :).

## Thank you!
I can not tell you how thankful I am for the hard work done by isort contributors like *you*.

Thank you!

~Timothy Crosley
````

## File: docs/contributing/2.-coding-standard.md
````markdown
# HOPE 8 -- Style Guide for Hug Code

|             |                                             |
| ------------| ------------------------------------------- |
| HOPE:       | 8                                           |
| Title:      | Style Guide for Hug Code                    |
| Author(s):  | Timothy Crosley <timothy.crosley@gmail.com> |
| Status:     | Active                                      |
| Type:       | Process                                     |
| Created:    | 19-May-2019                                 |
| Updated:    | 17-August-2019                                 |

## Introduction

This document gives coding conventions for the Hug code comprising the Hug core as well as all official interfaces, extensions, and plugins for the framework.
Optionally, projects that use Hug are encouraged to follow this HOPE and link to it as a reference.

## PEP 8 Foundation

All guidelines in this document are in addition to those defined in Python's [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP 257](https://www.python.org/dev/peps/pep-0257/) guidelines.

## Line Length

Too short of lines discourage descriptive variable names where they otherwise make sense.
Too long of lines reduce overall readability and make it hard to compare 2 files side by side.
There is no perfect number: but for Hug, we've decided to cap the lines at 100 characters.

## Descriptive Variable names

Naming things is hard. Hug has a few strict guidelines on the usage of variable names, which hopefully will reduce some of the guesswork:
- No one character variable names.
    - Except for x, y, and z as coordinates.
- It's not okay to override built-in functions.
    - Except for `id`. Guido himself thought that shouldn't have been moved to the system module. It's too commonly used, and alternatives feel very artificial.
- Avoid Acronyms, Abbreviations, or any other short forms - unless they are almost universally understand.

## Adding new modules

New modules added to the a project that follows the HOPE-8 standard should all live directly within the base `PROJECT_NAME/` directory without nesting. If the modules are meant only for internal use within the project, they should be prefixed with a leading underscore. For example, def _internal_function. Modules should contain a docstring at the top that gives a general explanation of the purpose and then restates the project's use of the MIT license.
There should be a `tests/test_$MODULE_NAME.py` file created to correspond to every new module that contains test coverage for the module. Ideally, tests should be 1:1 (one test object per code object, one test method per code method) to the extent cleanly possible.

## Automated Code Cleaners

All code submitted to Hug should be formatted using Black and isort.
Black should be run with the line length set to 100, and isort with Black compatible settings in place.

## Automated Code Linting

All code submitted to hug should run through the following tools:

- Black and isort verification.
- Flake8
   - flake8-bugbear
- Bandit
- ruff
- pep8-naming
- vulture
````

## File: docs/contributing/3.-code-of-conduct.md
````markdown
# HOPE 11 -- Code of Conduct

|             |                                             |
| ------------| ------------------------------------------- |
| HOPE:       | 11                                          |
| Title:      | Code of Conduct                             |
| Author(s):  | Timothy Crosley <timothy.crosley@gmail.com> |
| Status:     | Active                                      |
| Type:       | Process                                     |
| Created:    | 17-August-2019                              |
| Updated:    | 17-August-2019                              |

## Abstract

Defines the Code of Conduct for Hug and all related projects.

## Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, sex characteristics, gender identity and expression,
level of experience, education, socio-economic status, nationality, personal
appearance, race, religion, or sexual identity and orientation.

## Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
 advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
 address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
 professional setting

## Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

## Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting [timothy.crosley@gmail.com](mailto:timothy.crosley@gmail.com). All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. Confidentiality will be maintained
with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][https://www.contributor-covenant.org], version 1.4,
available at https://www.contributor-covenant.org/version/1/4/code-of-conduct.html

For answers to common questions about this code of conduct, see
https://www.contributor-covenant.org/faq
````

## File: docs/contributing/4.-acknowledgements.md
````markdown
Core Developers
===================
- Aniruddha Bhattacharjee (@anirudnits)
- Jon Dufresne (@jdufresne)
- Tamas Szabo (@sztamas)
- Thiago A. (@staticdev)
- Timothy Edmund Crosley (@timothycrosley)

Plugin Writers
===================
- *VIM* - Juan Pedro Fisanotti (@fisadev)
- *Emacs* - Friedrich Paetzke (@paetzke)
- *Sublime* - Thijs de Zoute (@thijsdezoete)

Notable Bug Reporters
===================
- Bengt Lüers (@Bengt)
- Chris Adams (@acdha)
- @OddBloke
- Martin Geisler (@mgeisleinr)
- Tim Heap (@timheap)
- Matěj Nikl (@MatejNikl)

Code Contributors
===================
- Aaron Gallagher (@habnabit)
- Thomas Grainger (@graingert)
- Thijs de Zoute (@thijsdezoete)
- Marc Abramowitz (@msabramo)
- Daniel Cowgill (@dcowgill)
- Francois Lebel (@flebel)
- Antoni Segura Puimedon (@celebdor)
- Pablo (@oubiga)
- Oskar Hahn (@ostcar)
- Wim Glenn (@wimglenn)
- Matt Caldwell (@mattcaldwell)
- Dwayne Bailey (@dwaynebailey)
- Ionel Cristian Mărieș (@ionelmc)
- Chris Adams (@acdha)
- GuoJing (@GuoJing)
- George Hickman (@ghickman)
- Dan Davison (@dandavison)
- Maciej Wolff (@maciejwo)
- Elliott Sales de Andrade (@qulogic)
- Kasper Jacobsen (@dinoshauer)
- Sebastian Pipping (@hartwork)
- Helen Sherwood-Taylor (@helenst)
- Mocker (@Zuckonit)
- Tim Graham (@timgraham)
- Adam (@NorthIsUp)
- Norman Jäckel (@normanjaeckel)
- Derrick Petzold (@dpetzold)
- Michael van Tellingen (@mvantellingen)
- Patrick Yevsukov (@patrickyevsukov)
- Christer van der Meeren (@cmeeren)
- Timon Wong/NHNCN (@timonwong)
- Jeremy Dunck (@jdunck)
- Benjamin ABEL (@benjaminabel)
- Dan Baragan (@danbaragan)
- Rob Cowie (@robcowie)
- Amit Shah (@Amwam)
- Patrick Gerken (@do3cc)
- @dein0s
- David Stensland (@terite)
- Ankur Dedania (@AbsoluteMSTR)
- Lee Packham (@leepa)
- Jesse Mullan (@jmullan)
- Kwok-kuen Cheung (@cheungpat)
- Johan Bloemberg (@aequitas)
- Dan Watson (@dcwatson)
- Éric Araujo (@merwok)
- Dan Palmer (@danpalmer)
- Andy Boot (@bootandy)
- @m7v8
- John Vandenberg (@jayvdb)
- Adam Chainz (@adamchainz)
- @Brightcells
- Jonas Trappenberg (@teeberg)
- Andrew Konstantaras (@akonsta)
- Jason Brackman (@jasonbrackman)
- Kathryn Lingel (@katlings)
- Andrew Gaul (@gaul)
- John Chadwick (@jchv)
- Jon Dufresne (@jdufresne)
- Brian F. Baron (@briabar)
- Madison Caldwell (@madirey)
- Matt Yule-Bennett (@mattbennett)
- Jaswanth Kumar (@jaswanth098)
- Dario Navin (@Zarathustra2)
- Danny Weinberg (@FuegoFro)
- Gram (@orsinium)
- Hugo van Kemenade (@hugovk)
- Géry Ogam (@maggyero)
- Cody Scott (@Siecje)
- Pedro Algarvio (@s0undt3ch)
- Chris St. Pierre (@stpierre)
- Sebastian Rittau (@srittau)
- João M.C. Teixeira (@joaomcteixeira)
- Honnix (@honnix)
- Anders Kaseorg (@andersk)
- @r-richmond
- Sebastian (@sebix)
- Kosei Kitahara (@Surgo)
- Seung Hyeon, Kim (@hyeonjames)
- Gerard Dalmau (@gdalmau)
- Robert Tasarz (@rtasarz)
- Ryo Miyajima (@sergeant-wizard)
- @mdagaro
- Maksim Kurnikov (@mkurnikov)
- Daniel Hahler (@blueyed)
- @ucodery
- Aarni Koskela (@akx)
- Alex Chan (@alexwlchan)
- Rick Thomas (@richardlthomas)
- Jeppe Fihl-Pearson (@Tenzer)
- Jonas Lundberg (@lundberg)
- Neil (@NeilGirdhar)
- @dmanikowski-reef
- Stephen Brown II (@StephenBrown2)
- Ankur Dedania (@AnkurDedania)
- Anthony Sottile (@asottile)
- Bendik Samseth (@bsamseth)
- Dan W Anderson (@anderson-dan-w)
- DeepSource Bot (@deepsourcebot)
- Mitar (@mitar)
- Omer Katz (@thedrow)
- Santiago Castro (@bryant1410)
- Sergey Fursov (@GeyseR)
- Thomas Robitaille (@astrofrog)
- Ville Skyttä (@scop)
- Hakan Çelik (@hakancelik96)
- Dylan Katz (@Plazmaz)
- Linus Lewandowski (@LEW21)
- Bastien Gérard (@bagerard)
- Brian Dombrowski (@bdombro)
- Ed Morley (@edmorley)
- Graeme Coupar (@obmarg)
- Jerome Leclanche (@jleclanche)
- Joshu Coats (@rhwlo)
- Mansour Behabadi (@oxplot)
- Sam Lai (@slai)
- Tamas Szabo (@sztamas)
- Yedidyah Bar David (@didib)
- Hidetoshi Hirokawa (@h-hirokawa)
- Aaron Chong (@acjh)
- Harai Akihiro (@harai)
- Andy Freeland (@rouge8)
- @ethifus
- Joachim Brandon LeBlanc (@demosdemon)
- Brian May (@brianmay)
- Bruno Oliveira (@nicoddemus)
- Bruno Renié (@brutasse)
- Bryce Guinta (@brycepg)
- David Chan (@dchanm)
- David Smith (@smithdc1)
- Irv Lustig (@Dr-Irv)
- Dylan Richardson (@dylrich)
- Emil Melnikov (@emilmelnikov)
- Eric Johnson (@metrizable)
- @ryabtsev
- Felix Yan (@felixonmars)
- Gil Forcada Codinachs (@gforcada)
- Ilya Konstantinov (@ikonst)
- Jace Browning (@jacebrowning)
- Jin Suk Park (@jinmel)
- Jürgen Gmach (@jugmac00)
- Maciej Gawinecki (@dzieciou)
- Minn Soe (@MinnSoe)
- Nikolaus Wittenstein (@adzenith)
- Norman J. Harman Jr. (@njharman)
- P R Gurunath (@gurunath-p)
- Patrick Hayes (@pfhayes)
- Pete Grayson (@jpgrayson)
- Philip Jenvey (@pjenvey)
- Rajiv Bakulesh Shah (@brainix)
- Reid D McKenzie (@arrdem)
- Robert DeRose (@RobertDeRose)
- Roey Darwish Dror (@r-darwish)
- Rudinei Goi Roecker (@rudineirk)
- Wagner (@wagner-certat)
- Nikita Sobolev (@sobolevn)
- Terence Honles (@terencehonles)
- The Gitter Badger (@gitter-badger)
- Tim Gates (@timgates42)
- Tim Staley (@timstaley)
- Vincent Hatakeyama (@vincent-hatakeyama)
- Yaron de Leeuw (@jarondl)
- @jwg4
- @nicolelodeon
- Łukasz Langa (@ambv)
- Grzegorz Pstrucha (@Gricha)
- Zac Hatfield-Dodds (@Zac-HD)
- Jiří Škorpil (@JiriSko)
- James Winegar (@jameswinegar)
- Abdullah Dursun (@adursun)
- Guillaume Lostis (@glostis)
- Krzysztof Jagiełło (@kjagiello)
- Nicholas Devenish (@ndevenish)
- Aniruddha Bhattacharjee (@anirudnits)
- Alexandre Yang (@AlexandreYang)
- Andrew Howe (@howeaj)
- Sang-Heon Jeon (@lntuition)
- Denis Veselov (@saippuakauppias)
- James Curtin (@jamescurtin)
- Marco Gorelli (@MarcoGorelli)
- Louis Sautier (@sbraz)
- Timur Kushukov (@timqsh)
- Bhupesh Varshney (@Bhupesh-V)
- Rohan Khanna (@rohankhanna)
- Vasilis Gerakaris (@vgerak)
- @tonci-bw
- @jaydesl
- Tamara (@infinityxxx)
- Akihiro Nitta (@akihironitta)
- Samuel Gaist (@sgaist)
- @dwanderson-intel
- Quentin Santos (@qsantos)
- @gofr
- Pavel Savchenko (@asfaltboy)
- @dongfangtianyu
- Christian Clauss (@cclauss)
- Jon Banafato (@jonafato)
- ruro (@RuRo)
- Léni (@legau)
- keno (Ken Okada) (@kenoss)
- Shota Terashita (@shotat)
- Luca Di sera (@diseraluca)
- Tonye Jack (@jackton1)
- Yusuke Hayashi (@yhay81)
- Arthur Rio (@arthurio)
- Bob (@bobwalker99)
- Martijn Pieters (@mjpieters)
- Asiel Díaz Benítez (@adbenitez)
- Almaz (@monosans)
- Mathieu Kniewallner (@mkniewallner)
- Christian Decker (@chrisdecker1201)
- Adam Parkin (@pzelnip)
- @MapleCCC
- @Parnassius
- @SaucyGames05
- Tim Heap (@mx-moth)

Documenters
===================
- Reinout van Rees (@reinout)
- Helen Sherwood-Taylor (@helenst)
- Elliott Sales de Andrade (@QuLogic)
- Brian Peiris (@brianpeiris)
- Tim Graham (@timgraham)
- Josh Soref (@jsoref)
- Teg Khanna (@tegkhanna)
- Sarah Beth Tracy (@sbtries)
- Aaron Brown (@aaronvbrown)
- Harutaka Kawamura (@harupy)
- Brad Solomon (@bsolomon1124)
- Martynas Mickevičius (@2m)
- Taneli Hukkinen (@hukkinj1)
- @r-richmond
- John Villalovos (@JohnVillalovos)
- Kosei Kitahara (@Surgo)
- Marat Sharafutdinov (@decaz)
- Abtin (@abtinmo)
- @scottwedge
- Hasan Ramezani (@hramezani)
- @hirosassa
- David Poznik (@dpoznik)
- Mike Frysinger (@vapier)
- @DanielFEvans
- Giuseppe Lumia (@glumia)
- John Brock (@JohnHBrock)
- Sergey Fedoseev (@sir-sigurd)

--------------------------------------------

A sincere thanks to everyone who has helped isort be the great utility it is today!
It would not be one-hundredth as useful and consistent as it is now without the help of your bug reports,
commits, and suggestions. You guys rock!

~Timothy Crosley
````

## File: docs/howto/shared_profiles.md
````markdown
# Shared Profiles

As well as the [built in
profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html), you
can define and share your own profiles.

All that's required is to create a Python package that exposes an entry point to
a dictionary exposing profile settings under `isort.profiles`. An example is
available [within the `isort`
repo](https://github.com/PyCQA/isort/tree/main/example_shared_isort_profile)

### Example `.isort.cfg`

```
[options.entry_points]
isort.profiles =
    shared_profile=my_module:PROFILE
```
````

## File: docs/major_releases/introducing_isort_5.md
````markdown
# Introducing isort 5

[![isort 5 - the best version of isort yet](https://raw.githubusercontent.com/pycqa/isort/main/art/logo_5.png)](https://pycqa.github.io/isort/)

isort 5.0.0 is the first major release of isort in over five years and the first significant refactoring of isort since it was conceived more than ten years ago.
It's also the first version to require Python 3 (Python 3.6+ at that!) to run - though it can still be run on source files from any version of Python.
This does mean that there may be some pain with the upgrade process, but we believe the improvements will be well worth it.

[Click here for an attempt at full changelog with a list of breaking changes.](https://pycqa.github.io/isort/CHANGELOG.html)

[Using isort 4.x.x? Click here for the isort 5.0.0 upgrade guide.](https://pycqa.github.io/isort/docs/upgrade_guides/5.0.0.html)

[Try isort 5 right now from your browser!](https://pycqa.github.io/isort/docs/quick_start/0.-try.html)

So why the massive change?

# Profile support
```
isort --profile black .
isort --profile django .
isort --profile pycharm .
isort --profile google .
isort --profile open_stack .
isort --profile plone .
isort --profile attrs .
isort --profile hug .
```

isort is very configurable. That's great, but it can be overwhelming, both for users and for the isort project. isort now comes with profiles for the most common isort configurations,
so you likely will not need to configure anything at all. This also means that as a project, isort can run extensive tests against these specific profiles to ensure nothing breaks over time.

# Sort imports **anywhere**

```python3
import a  # <- These are sorted
import b

b.install(a)

import os  # <- And these are sorted
import sys


def my_function():
    import x  # <- Even these are sorted!
    import z
```

isort 5 will find and sort contiguous section of imports no matter where they are.
It also allows you to place code in-between imports without any hacks required.

# Streaming architecture

```python3
import a
import b
...
∞
```
isort has been refactored to use a streaming architecture. This means it can sort files of *any* size (even larger than the Python interpreter supports!) without breaking a sweat.
It also means that even when sorting imports in smaller files, it is faster and more resource-efficient.

# Consistent behavior across **all** environments

Sorting the same file with the same configuration should give you the same output no matter what computer or OS you are running. Extensive effort has been placed around refactoring
how modules are placed and how configuration files are loaded to ensure this is the case.


# Cython support

```python3
cimport ctime
from cpython cimport PyLong_FromVoidPtr
from cpython cimport bool as py_bool
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from libc.stdint cimport uint64_t, uintptr_t
from libc.stdlib cimport atoi, calloc, free, malloc
from libc.string cimport memcpy, strlen
from libcpp cimport bool as cpp_bool
from libcpp.map cimport map as cpp_map
from libcpp.pair cimport pair as cpp_pair
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from multimap cimport multimap as cpp_multimap
from wstring cimport wstring as cpp_wstring
```

isort 5 adds seamless support for Cython (`.pyx`) files.

# Action Comments

```python3
import e
import f

# isort: off  <- Turns isort parsing off

import b
import a

# isort: on  <- Turns isort parsing back on

import c
import d
```

isort 5 adds support for [Action Comments](https://pycqa.github.io/isort/docs/configuration/action_comments.html) which provide a quick and convenient way to control the flow of parsing within single source files.


# First class Python API

```python3
import isort

isort.code("""
import b
import a
""") == """
import a
import b
"""
```

isort now exposes its programmatic API as a first-class citizen. This API makes it easy to extend or use isort in your own Python project. You can see the full documentation for this new API [here](https://pycqa.github.io/isort/reference/isort/api.html).

# Solid base for the future

A major focus for the release was to give isort a solid foundation for the next 5-10 years of the project's life.
isort has been refactored into functional components that are easily testable. The project now has 100% code coverage.
It utilizes tools like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) to reduce the number of unexpected errors.
It went from fully dynamic to fully static typing using mypy. Finally, it utilizes the latest linters both on (like [DeepSource](https://deepsource.io/gh/pycqa/isort/)) and offline (like [Flake8](https://flake8.pycqa.org/en/latest/)) to help ensure a higher bar for all code contributions into the future.

# Give 5.0.0 a try!

[Try isort 5 right now from your browser!](https://pycqa.github.io/isort/docs/quick_start/0.-try.html)

OR

Install isort locally using `pip3 install isort`.

[Click here for full installation instructions.](https://pycqa.github.io/isort/docs/quick_start/1.-install.html)
````

## File: docs/major_releases/release_policy.md
````markdown
# isort Project Official Release Policy

isort has moved from being a simple hobby project for individuals to sort imports in their Python files
to an essential part of the CI/CD pipeline for large companies and significant Open Source projects.
Due to this evolution, it is now of increased importance that isort maintains a level of quality, predictability, and consistency
that gives projects big and small confidence to depend on it.

## Formatting guarantees

With isort 5.1.0, the isort Project guarantees that formatting will stay the same for the options given in accordance to its test suite for the duration of all major releases. This means projects can safely use isort > 5.1.0 < 6.0.0
without worrying about major formatting changes disrupting their Project.

## Packaging guarantees

Starting with the 5.0.0 release isort includes the following project guarantees to help guide development:

- isort will never have dependencies, optional, required, or otherwise.
- isort will always act the same independent to the Python environment it is installed in.

## Versioning

isort follows the [Semantic Versioning 2.0.0 specification](https://semver.org/spec/v2.0.0.html) meaning it has three numerical version parts with distinct rules
`MAJOR.MINOR.PATCH`.

### Patch Releases x.x.1

Within the isort Project, patch releases are really meant solely to fix bugs and minor oversights.
Patch releases should *never* drastically change formatting, even if it's for the better.

### Minor Releases x.1.x

Minor changes can contain new backward-incompatible features, and of particular note can include bug fixes
that result in intentional formatting changes - but they should still never be too large in scope.
API backward compatibility should strictly be maintained.

### Major Releases 1.x.x

Major releases are the only place where backward-incompatible changes or substantial formatting changes can occur.
Because these kind of changes are likely to break projects that utilize isort, either as a formatter or library,
isort must do the following:

- Release a release candidate with at least 2 weeks for bugs to be reported and fixed.
- Keep releasing follow up release candidates until there are no or few bugs reported.
- Provide an upgrade guide that helps users work around any backward-incompatible changes.
- Provide a detailed changelog of all changes.
- Where possible, warn and point to the upgrade guide instead of breaking when options are removed.
````

## File: docs/quick_start/0.-try.md
````markdown
Try isort from your browser!
========

Use our live isort editor to see how isort can help improve the formatting of your Python imports.

!!! important - "Safe to use. No code is transmitted."
    The below live isort tester doesn't transmit any of the code you paste to our server or anyone else's. Instead, this page runs a complete Python3 installation with isort installed entirely within your browser. To accomplish this, it utilizes the [pyodide](https://github.com/iodide-project/pyodide) project.

<head>
<script type="text/javascript">
    // set the pyodide files URL (packages.json, pyodide.asm.data etc)
    window.languagePluginUrl = 'https://cdn.jsdelivr.net/pyodide/v0.15.0/full/';
</script>
<script src="https://cdn.jsdelivr.net/pyodide/v0.15.0/full/pyodide.js" integrity="sha256-W+0Mr+EvJb1qJx9UZ9wuvd/uWrXCzeaEu6OzEEHMCik=" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/ace-builds@1.4.5/src-min-noconflict/ace.min.js"></script>
<link rel="stylesheet" type="text/css" href="https://pycqa.github.io/isort/docs/quick_start/interactive.css">
</head>


<div id="liveTester">
<div id="sideBySide">
<div id="inputEditor" class="editor">from future import braces
import b
import b
import os
import a
from future import braces
import b
import a
import b, a
</div>
<div id="outputEditor" class="editor">Loading...</div>
<div>

&nbsp;Configuration (Note: the below must follow JSON format). Full configuration guide is <a href="https://pycqa.github.io/isort/docs/configuration/options">here</a>:

<div id="configEditor" class="configurator">{"line_length": 80,
 "profile": "black",
 "atomic": true
}
</div>
</div>
</div>
</div>

<script src="https://pycqa.github.io/isort/docs/quick_start/interactive.js"></script>
<div style="clear:both;"></div>
Like what you saw? Installing isort to use locally is as simple as `pip3 install isort`.

[Click here for full installation instructions.](https://pycqa.github.io/isort/docs/quick_start/1.-install)
````

## File: docs/quick_start/1.-install.md
````markdown
Install `isort` using your preferred Python package manager:

`pip3 install isort`

OR

`uv add isort`

OR

`poetry add isort`

OR

`pipenv install isort`

OR

For a fully isolated user installation you can use [pipx](https://github.com/pipxproject/pipx)

`pipx install isort`

<script id="asciicast-qZglwdh3YdoRHjtpxuNmQJehj" src="https://asciinema.org/a/qZglwdh3YdoRHjtpxuNmQJehj.js" async></script>

!!!tip
    If you want isort to act as a linter for projects, it probably makes sense to add isort as an explicit development dependency for each project that uses it. If, on the other hand, you are an individual developer simply using isort as a personal tool to clean up your own commits, a global or user level installation makes sense. Both are seamlessly supported on a single machine.
````

## File: docs/quick_start/2.-cli.md
````markdown
# Command Line Usage

Once installed, `isort` exposes a command line utility for sorting, organizing, and formatting imports within Python and Cython source files.

To verify the tool is installed correctly, run `isort` from the command line and you should be given the available commands and the version of isort installed.
For a list of all CLI options type `isort --help` or view [the online configuration reference](https://pycqa.github.io/isort/docs/configuration/options):

<script id="asciicast-346599" src="https://asciinema.org/a/346599.js" async></script>

## Formatting a Project

In general, isort is most commonly utilized across an entire projects source at once. The simplest way to do this is `isort .` or if using a `src` directory `isort src`. isort will automatically find all Python source files recursively and pick-up a configuration file placed at the root of your project if present. This can be combined with any command line configuration customizations such as specifying a profile to use (`isort . --profile black`).

<script id="asciicast-346600" src="https://asciinema.org/a/346600.js" async></script>

## Verifying a Project

The second most common usage of isort is verifying that imports within a project are formatted correctly (often within the context of a CI/CD system). The simplest way to accomplish this is using the check command line option: `isort --check .`. To improve the usefulness of errors when they do occur, this can be combined with the diff option: `isort --check --diff .`.

<script id="asciicast-346601" src="https://asciinema.org/a/346601.js" async></script>

## Single Source Files

Finally, isort can just as easily be ran against individual source files. Simply pass in a single or multiple source files to sort or validate (Example: `isort setup.py`).

<script id="asciicast-346602" src="https://asciinema.org/a/346602.js" async></script>

## Multiple Projects

Running a single isort command across multiple projects, or source files spanning multiple projects, is highly discouraged. Instead it is recommended that an isort process (or command) is ran for each project independently. This is because isort creates an immutable config for each CLI instance.

```
# YES
isort project1
isort project2

# Also YES
isort project1/src project1/test
isort project2/src project2/test

# NO
isort project1 project2
```
````

## File: docs/quick_start/3.-api.md
````markdown
# Programmatic Python API Usage

In addition to the powerful command line interface, isort exposes a complete Python API.

To use the Python API, `import isort` and then call the desired function call:

<script id="asciicast-346604" src="https://asciinema.org/a/346604.js" async></script>

Every function is fully type hinted and requires and returns only builtin Python objects.

Highlights include:

- `isort.code` - Takes a string containing code, and returns it with imports sorted.
- `isort.check_code` - Takes a string containing code, and returns `True` if all imports are sorted correctly, otherwise, `False`.
- `isort.stream` - Takes an input stream containing Python code and an output stream. Outputs code to output stream with all imports sorted.
- `isort.check_stream` - Takes an input stream containing Python code and returns `True` if all imports in the stream are sorted correctly, otherwise, `False`.
- `isort.file` - Takes the path of a Python source file and sorts the imports in-place.
- `isort.check_file` - Takes the path of a Python source file and returns `True` if all imports contained within are sorted correctly, otherwise, `False`.
- `isort.place_module` - Takes the name of a module as a string and returns the categorization determined for it.
- `isort.place_module_with_reason` - Takes the name of a module as a string and returns the categorization determined for it and why that categorization was given.

For a full definition of the API see the [API reference documentation](https://pycqa.github.io/isort/reference/isort/api) or try `help(isort)` from an interactive interpreter.
````

## File: docs/upgrade_guides/5.0.0.md
````markdown
# Upgrading to 5.0.0

isort 5.0.0 is the first major release of isort in 5 years, and as such it does introduce some breaking changes.
This guide is meant to help migrate projects from using isort 4.x.x unto the 5.0.0 release.

Related documentation:

* [isort 5.0.0 changelog](https://pycqa.github.io/isort/CHANGELOG#500-penny-july-4-2020)
* [isort 5 release document](https://pycqa.github.io/isort/docs/major_releases/introducing_isort_5.html)

!!! important - "If you use pre-commit remove seed-isort-config."
    If you currently use pre-commit, make sure to see the pre-commit section of this document. In particular, make sure to remove any `seed-isort-config` pre-step.

## Imports no Longer Moved to Top

One of the most immediately evident changes when upgrading to isort 5, is it now avoids moving imports around code by default.
The great thing about this is that it means that isort can safely run against complex code bases that need to place side effects between import sections without needing any comments, flags, or configs. It's also part of the rearchitecting that allows it to sort within type checking conditionals and functions. However, it can be a jarring change
for those of us who have gotten used to placing imports right above their usage in code to avoid context switching. No need to worry! isort still supports this work mode.

If you want to move all imports to the top, you can use the new`--float-to-top` flag in the CLI or `float_to_top=true` option in your config file.

See: [https://pycqa.github.io/isort/docs/configuration/options.html#float-to-top](https://pycqa.github.io/isort/docs/configuration/options.html#float-to-top)

## Migrating CLI options

### `--dont-skip` or `-ns`
In an earlier version isort had a default skip of `__init__.py`. To get around that many projects wanted a way to not skip `__init__.py` or any other files that were automatically skipped in the future by isort. isort no longer has any default skips, so if the value here is `__init__.py` you can simply remove the command line option. If it is something else, just make sure you aren't specifying to skip that file somewhere else in your config.

### `--recursive` or `-rc`
Prior to version 5.0.0, isort wouldn't automatically traverse directories. The --recursive option was necessary to tell it to do so. In 5.0.0 directories are automatically traversed for all Python files, and as such this option is no longer necessary and should simply be removed.

### `--apply` or `-y`
Prior to version 5.0.0, depending on how isort was executed, it would ask you before making every file change. In isort 5.0.0 file changes happen by default inline with other formatters. `--interactive` is available to restore the previous behavior. If encountered this option can simply be removed.

### `--keep-direct-and-as` or `-k`
Many versions ago, by default isort would remove imports such as `from datetime import datetime` if an alias for the same import also existed such as `from datetime import datetime as dt` - never allowing both to exist.
The option was originally added to allow working around this, and was then turned on as the default. Now the option for the old behaviour has been removed. Simply remove the option from your config file.

### `-ac`, `-wl`, `-ws`, `-tc`, `-sp`, `-sp`, `-sl`, `-sg`, `-sd`, `-rr`, `-ot`, `-nlb`, `-nis`, `-ls`, `-le`, `-lbt`, `-lai`, `-fss`, `-fgw`, `-ff`, `-fass`, `-fas`, `-dt`, `-ds`, `-df`, `-cs`, `-ca`, `-af`, `-ac`
Two-letter shortened setting names (like `ac` for `atomic`) now require two dashes to avoid ambiguity. Simply add another dash before the option, or switch to the long form option to fix (example: `--ac` or `--atomic`).

### `-v` and `-V`
The `-v` (previously for version now for verbose) and `-V` (previously for verbose and now for version) options have been swapped to be more consistent with tools across the CLI and in particular Python ecosystem.

## Migrating Config options

The first thing to keep in mind is how isort loads config options has changed in isort 5. It will no longer merge multiple config files, instead you must have 1 isort config per a project.
If you have multiple configs, they will need to be merged into 1 single one. You can see the priority order of configuration files and the manner in which they are loaded on the
[config files documentation page](https://pycqa.github.io/isort/docs/configuration/config_files.html).

!!! tip - "Config options are loaded relative to the file, not the isort instance."
    isort looks for a config file based on the path of the file you request to sort. If you have your config placed outside of the project, you can use `--settings-path` to manually specify the config location instead. Full information about how config files are loaded is in the linked config files documentation page.


### `not_skip`
This is the same as the `--dont-skip` CLI option above. In an earlier version isort had a default skip of `__init__.py`. To get around that many projects wanted a way to not skip `__init__.py` or any other files that were automatically skipped in the future by isort. isort no longer has any default skips, so if the value here is `__init__.py` you can simply remove the setting. If it is something else, just make sure you aren't specifying to skip that file somewhere else in your config.

### `keep_direct_and_as_imports`
This is the same as `keep-direct-and-as` from CLI. Many versions ago, by default isort would remove imports such as `from datetime import datetime` if an alias for the same import also existed such as `from datetime import datetime as dt` - never allowing both to exist.
The option was originally added to allow working around this, and was then turned on as the default. Now the option for the old behaviour has been removed. Simply remove the option from your config file.

### `known_standard_library`
isort settings no longer merge together, instead they override. The old behavior of merging together caused many hard to
track down errors, but the one place it was very convenient was for adding a few additional standard library modules.
In isort 5, you can still get this behavior by moving your extra modules from the `known_standard_library` setting to [`extra_standard_library`](https://pycqa.github.io/isort/docs/configuration/options.html#extra-standard-library).

### module placement changes: `known_third_party`, `known_first_party`, `default_section`, etc...
isort has completely rewritten its logic for placing modules in 5.0.0 to ensure the same behavior across environments. You can see the details of this change [here](https://github.com/pycqa/isort/issues/1147).
The TL;DR of which is that isort has now changed from `default_section=FIRSTPARTY` to `default_section=THIRDPARTY`. If you all already setting the default section to third party, your config is probably in good shape.
If not, you can either use the old finding approach with `--magic-placement` in the CLI or `old_finders=True` in your config, or preferably, you are able to remove all placement options and isort will determine it correctly.
If it doesn't, you should be able to just specify your projects modules with `known_first_party` and be done with it.

## Migrating pre-commit

### seed-isort-config

If you have a step in your precommit called `seed-isort-config` or similar, it is highly recommend that you remove this. It is unnecessary in 5.x.x, is guaranteed to slow things down, and worse can conflict with isort's own module placement logic.

### isort pre-commit step

isort now includes an optimized precommit configuration in the repo itself. To use it you can replace any existing isort precommit step with:

```
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        name: isort (python)
      - id: isort
        name: isort (cython)
        types: [cython]
      - id: isort
        name: isort (pyi)
        types: [pyi]
```

under the `repos` section of your projects `.pre-commit-config.yaml` config.
````

## File: docs/warning_and_error_codes/W0500.md
````markdown
# W0500 Warning Codes

The W0500 error codes are reserved for warnings related to a major release of the isort project.
Generally, the existence of any of these will trigger one additional warning listing the upgrade guide.

For the most recent upgrade guide, see: [The 5.0.0 Upgrade Guide.](https://pycqa.github.io/isort/docs/upgrade_guides/5.0.0.html).

## W0501: Deprecated CLI flags were included that will be ignored.

This warning will be shown if a CLI flag is passed into the isort command that is no longer supported but can safely be ignored.
Often, this happens because an argument used to be required to turn on a feature that then became the default. An example of this
is `--recursive` which became the default behavior for all folders passed-in starting with 5.0.0.

## W0502: Deprecated CLI flags were included that will safely be remapped.

This warning will be shown if a CLI flag is passed into the isort command that is no longer supported but can safely be remapped to the new version of the flag. If you encounter this warning, you must update the argument to match the new flag
before the next major release.

## W0503: Deprecated config options were ignored.

This warning will be shown if a deprecated config option is defined in the Project's isort config file, but can safely be ignored.
This is similar to `W0500` but dealing with config files rather than CLI flags.
````
