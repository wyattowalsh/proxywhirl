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
  editors/
    features.md
    index.md
    migration.md
    settings.md
    setup.md
  formatter/
    black.md
  configuration.md
  faq.md
  formatter.md
  installation.md
  integrations.md
  linter.md
  preview.md
  requirements-insiders.txt
  requirements.txt
  tutorial.md
  versioning.md
```

# Files

## File: docs/editors/features.md
````markdown
# Features

This section provides a detailed overview of the features provided by the Ruff Language Server.

## Diagnostic Highlighting

Provide diagnostics for your Python code in real-time.

<img
src="https://astral.sh/static/GIF/v0.4.5/violation_hx.gif"
alt="Editing a file in Helix"
/>

## Dynamic Configuration

The server dynamically refreshes the diagnostics when a configuration file is changed in the
workspace, whether it's a `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file.

The server relies on the file watching capabilities of the editor to detect changes to these files.
If an editor does not support file watching, the server will not be able to detect
changes to the configuration file and thus will not refresh the diagnostics.

<img
src="https://astral.sh/static/GIF/v0.4.5/config_reload_vscode.gif"
alt="Editing a `pyproject.toml` configuration file in VS Code"
/>

## Formatting

Provide code formatting for your Python code. The server can format an entire document or a specific
range of lines.

The VS Code extension provides the `Ruff: Format Document` command to format an entire document.
In VS Code, the range formatting can be triggered by selecting a range of lines, right-clicking, and
selecting `Format Selection` from the context menu.

<img
src="https://astral.sh/static/GIF/v0.4.5/format_vscode.gif"
alt="Formatting a document in VS Code"
/>

## Code Actions

Code actions are context-sensitive suggestions that can help you fix issues in your code. They are
usually triggered by a shortcut or by clicking a light bulb icon in the editor. The Ruff Language
Server provides the following code actions:

- Apply a quick fix for a diagnostic that has a fix available (e.g., removing an unused import).
- Ignore a diagnostic with a `# noqa` comment.
- Apply all quick fixes available in the document.
- Organize imports in the document.

<img
src="https://astral.sh/static/GIF/v0.4.5/code_action_hx.gif"
alt="Applying a quick fix in Helix"
/>

You can even run these actions on-save. For example, to fix all issues and organize imports on save
in VS Code, add the following to your `settings.json`:

```json
{
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  }
}
```

### Fix Safety

Ruff's automatic fixes are labeled as "safe" and "unsafe". By default, the "Fix all" action will not
apply unsafe fixes. However, unsafe fixes can be applied manually with the "Quick fix" action.
Application of unsafe fixes when using "Fix all" can be enabled by setting `unsafe-fixes = true` in
your Ruff configuration file.

See the [Ruff fix documentation](https://docs.astral.sh/ruff/linter/#fix-safety) for more details on
how fix safety works.

## Hover

The server can provide the rule documentation when focusing over a NoQA code in the comment.
Focusing is usually hovering with a mouse, but can also be triggered with a shortcut.

<img
src="https://astral.sh/static/GIF/v0.4.5/hover_vscode.gif"
alt="Hovering over a noqa code in VS Code"
/>

## Jupyter Notebook

Similar to Ruff's CLI, the Ruff Language Server fully supports Jupyter Notebook files with all the
capabilities available to Python files.

!!! note

    Unlike [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) and similar to the Ruff's CLI, the
    native language server requires user to explicitly include the Jupyter Notebook files in the set
    of files to lint and format. Refer to the [Jupyter Notebook discovery](https://docs.astral.sh/ruff/configuration/#jupyter-notebook-discovery)
    section on how to do this.

<img
src="https://astral.sh/static/GIF/v0.4.5/ipynb_editing_vscode.gif"
alt="Editing multiple Jupyter Notebook cells in VS Code"
/>

<img
src="https://astral.sh/static/GIF/v0.4.5/ipynb_range_format_vscode.gif"
alt="Formatting a selection within a Jupyter Notebook cell in VS Code"
/>
````

## File: docs/editors/index.md
````markdown
# Editor Integrations

Ruff can be integrated with various editors and IDEs to provide a seamless development experience.
This section provides instructions on [how to set up Ruff with your editor](./setup.md) and [configure it to your
liking](./settings.md).

## Language Server Protocol

The editor integration is mainly powered by the Ruff Language Server which implements the
[Language Server Protocol](https://microsoft.github.io/language-server-protocol/). The server is
written in Rust and is available as part of the `ruff` CLI via `ruff server`. It is a single, common
backend built directly into Ruff, and a direct replacement for [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp),
our previous language server. You can read more about `ruff server` in the
[`v0.4.5` blog post](https://astral.sh/blog/ruff-v0.4.5).

The server supports surfacing Ruff diagnostics, providing Code Actions to fix them, and
formatting the code using Ruff's built-in formatter. Currently, the server is intended to be used
alongside another Python Language Server in order to support features like navigation and
autocompletion.

The Ruff Language Server was available first in Ruff [v0.4.5](https://astral.sh/blog/ruff-v0.4.5)
in beta and stabilized in Ruff [v0.5.3](https://github.com/astral-sh/ruff/releases/tag/0.5.3).

!!! note

    This is the documentation for Ruff's built-in language server written in Rust (`ruff server`).
    If you are looking for the documentation for the `ruff-lsp` language server, please refer to the
    [README](https://github.com/astral-sh/ruff-lsp) of the `ruff-lsp` repository.
````

## File: docs/editors/migration.md
````markdown
# Migrating from `ruff-lsp`

[`ruff-lsp`][ruff-lsp] is the [Language Server Protocol] implementation for Ruff to power the editor
integrations. It is written in Python and is a separate package from Ruff itself. The **native
server**, however, is the [Language Server Protocol] implementation which is **written in Rust** and
is available under the `ruff server` command. This guide is intended to help users migrate from
[`ruff-lsp`][ruff-lsp] to the native server.

!!! note

    The native server was first introduced in Ruff version `0.3.5`. It was marked as [beta in
    version `0.4.5`](https://astral.sh/blog/ruff-v0.4.5) and officially [stabilized in version
    `0.5.3`](https://github.com/astral-sh/ruff/releases/tag/0.5.3). It is recommended to use the
    latest version of Ruff to ensure the best experience.

The migration process involves any or all of the following:

1. Migrate [deprecated settings](#unsupported-settings) to the [new settings](#new-settings)
1. [Remove settings](#removed-settings) that are no longer supported
1. Update the `ruff` version

Read on to learn more about the unsupported or new settings, or jump to the [examples](#examples)
that enumerate some of the common settings and how to migrate them.

## Unsupported Settings

The following [`ruff-lsp`][ruff-lsp] settings are not supported by the native server:

- [`lint.run`](settings.md#lintrun): This setting is no longer relevant for the native language
    server, which runs on every keystroke by default.
- [`lint.args`](settings.md#lintargs), [`format.args`](settings.md#formatargs): These settings have
    been replaced by more granular settings in the native server like [`lint.select`](settings.md#select),
    [`format.preview`](settings.md#format_preview), etc. along with the ability to override any
    configuration using the [`configuration`](settings.md#configuration) setting.

The following settings are not accepted by the language server but are still used by the [VS Code extension].
Refer to their respective documentation for more information on how each is used by the extension:

- [`path`](settings.md#path)
- [`interpreter`](settings.md#interpreter)

## Removed Settings

Additionally, the following settings are not supported by the native server and should be removed:

- [`ignoreStandardLibrary`](settings.md#ignorestandardlibrary)
- [`showNotifications`](settings.md#shownotifications)

## New Settings

The native server introduces several new settings that [`ruff-lsp`][ruff-lsp] does not have:

- [`configuration`](settings.md#configuration)
- [`configurationPreference`](settings.md#configurationpreference)
- [`exclude`](settings.md#exclude)
- [`format.preview`](settings.md#format_preview)
- [`lineLength`](settings.md#linelength)
- [`lint.select`](settings.md#select)
- [`lint.extendSelect`](settings.md#extendselect)
- [`lint.ignore`](settings.md#ignore)
- [`lint.preview`](settings.md#lint_preview)

## Examples

All of the examples mentioned below are only valid for the [VS Code extension]. For other editors,
please refer to their respective documentation sections in the [settings](settings.md) page.

### Configuration file

If you've been providing a configuration file as shown below:

```json
{
    "ruff.lint.args": "--config ~/.config/custom_ruff_config.toml",
    "ruff.format.args": "--config ~/.config/custom_ruff_config.toml"
}
```

You can migrate to the new server by using the [`configuration`](settings.md#configuration) setting
like below which will apply the configuration to both the linter and the formatter:

```json
{
    "ruff.configuration": "~/.config/custom_ruff_config.toml"
}
```

### `lint.args`

If you're providing the linter flags by using `ruff.lint.args` like so:

```json
{
    "ruff.lint.args": "--select=E,F --unfixable=F401 --unsafe-fixes"
}
```

You can migrate to the new server by using the [`lint.select`](settings.md#select) and
[`configuration`](settings.md#configuration) setting like so:

```json
{
    "ruff.lint.select": ["E", "F"],
    "ruff.configuration": {
        "unsafe-fixes": true,
        "lint": {
            "unfixable": ["F401"]
        }
    }
}
```

The following options can be set directly in the editor settings:

- [`lint.select`](settings.md#select)
- [`lint.extendSelect`](settings.md#extendselect)
- [`lint.ignore`](settings.md#ignore)
- [`lint.preview`](settings.md#lint_preview)

The remaining options can be set using the [`configuration`](settings.md#configuration) setting.

### `format.args`

If you're also providing formatter flags by using `ruff.format.args` like so:

```json
{
    "ruff.format.args": "--line-length 80 --config='format.quote-style=double'"
}
```

You can migrate to the new server by using the [`lineLength`](settings.md#linelength) and
[`configuration`](settings.md#configuration) setting like so:

```json
{
    "ruff.lineLength": 80,
    "ruff.configuration": {
        "format": {
            "quote-style": "double"
        }
    }
}
```

The following options can be set directly in the editor settings:

- [`lineLength`](settings.md#linelength)
- [`format.preview`](settings.md#format_preview)

The remaining options can be set using the [`configuration`](settings.md#configuration) setting.

[language server protocol]: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
[ruff-lsp]: https://github.com/astral-sh/ruff-lsp
[vs code extension]: https://github.com/astral-sh/ruff-vscode
````

## File: docs/editors/settings.md
````markdown
# Settings

The Ruff Language Server provides a set of configuration options to customize its behavior
along with the ability to use an existing `pyproject.toml` or `ruff.toml` file to configure the
linter and formatter. This is done by providing these settings while initializing the server.
VS Code provides a UI to configure these settings, while other editors may require manual
configuration. The [setup](./setup.md) section provides instructions on where to place these settings
as per the editor.

## Top-level

### `configuration`

The `configuration` setting allows you to configure editor-specific Ruff behavior. This can be done
in one of the following ways:

1. **Configuration file path:** Specify the path to a `ruff.toml` or `pyproject.toml` file that
    contains the configuration. User home directory and environment variables will be expanded.
1. **Inline JSON configuration:** Directly provide the configuration as a JSON object.

!!! note "Added in Ruff `0.9.8`"

    The **Inline JSON configuration** option was introduced in Ruff `0.9.8`.

The default behavior, if `configuration` is unset, is to load the settings from the project's
configuration (a `ruff.toml` or `pyproject.toml` in the project's directory), consistent with when
running Ruff on the command-line.

The [`configurationPreference`](#configurationpreference) setting controls the precedence if both an
editor-provided configuration (`configuration`) and a project level configuration file are present.

#### Resolution order {: #configuration_resolution_order }

In an editor, Ruff supports three sources of configuration, prioritized as follows (from highest to
lowest):

1. **Specific settings:** Individual settings like [`lineLength`](#linelength) or
    [`lint.select`](#select) defined in the editor
1. [**`ruff.configuration`**](#configuration): Settings provided via the
    [`configuration`](#configuration) field (either a path to a configuration file or an inline
    configuration object)
1. **Configuration file:** Settings defined in a `ruff.toml` or `pyproject.toml` file in the
    project's directory (if present)

For example, if the line length is specified in all three sources, Ruff will use the value from the
[`lineLength`](#linelength) setting.

**Default value**: `null`

**Type**: `string`

**Example usage**:

_Using configuration file path:_

=== "VS Code"

    ```json
    {
        "ruff.configuration": "~/path/to/ruff.toml"
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          configuration = "~/path/to/ruff.toml"
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "configuration": "~/path/to/ruff.toml"
            }
          }
        }
      }
    }
    ```

_Using inline configuration:_

=== "VS Code"

    ```json
    {
        "ruff.configuration": {
            "lint": {
                "unfixable": ["F401"],
                "extend-select": ["TID251"],
                "flake8-tidy-imports": {
                    "banned-api": {
                        "typing.TypedDict": {
                            "msg": "Use `typing_extensions.TypedDict` instead",
                        }
                    }
                }
            },
            "format": {
                "quote-style": "single"
            }
        }
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          configuration = {
            lint = {
              unfixable = {"F401"},
              ["extend-select"] = {"TID251"},
              ["flake8-tidy-imports"] = {
                ["banned-api"] = {
                  ["typing.TypedDict"] = {
                    msg = "Use `typing_extensions.TypedDict` instead"
                  }
                }
              }
            },
            format = {
              ["quote-style"] = "single"
            }
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "configuration": {
                "lint": {
                  "unfixable": ["F401"],
                  "extend-select": ["TID251"],
                  "flake8-tidy-imports": {
                    "banned-api": {
                      "typing.TypedDict": {
                        "msg": "Use `typing_extensions.TypedDict` instead"
                      }
                    }
                  }
                },
                "format": {
                  "quote-style": "single"
                }
              }
            }
          }
        }
      }
    }
    ```

### `configurationPreference`

The strategy to use when resolving settings across VS Code and the filesystem. By default, editor
configuration is prioritized over `ruff.toml` and `pyproject.toml` files.

- `"editorFirst"`: Editor settings take priority over configuration files present in the workspace.
- `"filesystemFirst"`: Configuration files present in the workspace takes priority over editor
    settings.
- `"editorOnly"`: Ignore configuration files entirely i.e., only use editor settings.

**Default value**: `"editorFirst"`

**Type**: `"editorFirst" | "filesystemFirst" | "editorOnly"`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.configurationPreference": "filesystemFirst"
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          configurationPreference = "filesystemFirst"
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "configurationPreference": "filesystemFirst"
            }
          }
        }
      }
    }
    ```

### `exclude`

A list of file patterns to exclude from linting and formatting. See [the
documentation](https://docs.astral.sh/ruff/settings/#exclude) for more details.

**Default value**: `null`

**Type**: `string[]`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.exclude": ["**/tests/**"]
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          exclude = ["**/tests/**"]
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "exclude": ["**/tests/**"]
            }
          }
        }
      }
    }
    ```

### `lineLength`

The line length to use for the linter and formatter.

**Default value**: `null`

**Type**: `int`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.lineLength": 100
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          lineLength = 100
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "lineLength": 100
            }
          }
        }
      }
    }
    ```

### `fixAll`

Whether to register the server as capable of handling `source.fixAll` code actions.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.fixAll": false
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          fixAll = false
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "fixAll": false
            }
          }
        }
      }
    }
    ```

### `organizeImports`

Whether to register the server as capable of handling `source.organizeImports` code actions.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.organizeImports": false
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          organizeImports = false
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "organizeImports": false
            }
          }
        }
      }
    }
    ```

### `showSyntaxErrors`

_New in Ruff [v0.5.0](https://astral.sh/blog/ruff-v0.5.0#changes-to-e999-and-reporting-of-syntax-errors)_

Whether to show syntax error diagnostics.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.showSyntaxErrors": false
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          showSyntaxErrors = false
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "showSyntaxErrors": false
            }
          }
        }
      }
    }
    ```

### `logLevel`

The log level to use for the server.

**Default value**: `"info"`

**Type**: `"trace" | "debug" | "info" | "warn" | "error"`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.logLevel": "debug"
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          logLevel = "debug"
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "logLevel": "debug"
            }
          }
        }
      }
    }
    ```

### `logFile`

Path to the log file to use for the server.

If not set, logs will be written to stderr.

**Default value**: `null`

**Type**: `string`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.logFile": "~/path/to/ruff.log"
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          logFile = "~/path/to/ruff.log"
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "logFile": "~/path/to/ruff.log"
            }
          }
        }
      }
    }
    ```

## `codeAction`

Enable or disable code actions provided by the server.

### `disableRuleComment.enable`

Whether to display Quick Fix actions to disable rules via `noqa` suppression comments.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.codeAction.disableRuleComment.enable": false
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          codeAction = {
            disableRuleComment = {
              enable = false
            }
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "codeAction": {
                "disableRuleComment": {
                  "enable": false
                }
              }
            }
          }
        }
      }
    }
    ```

### `fixViolation.enable`

Whether to display Quick Fix actions to autofix violations.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.codeAction.fixViolation.enable": false
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          codeAction = {
            fixViolation = {
              enable = false
            }
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "codeAction": {
                "fixViolation": = {
                  "enable": false
                }
              }
            }
          }
        }
      }
    }
    ```

## `lint`

Settings specific to the Ruff linter.

### `enable` {: #lint_enable }

Whether to enable linting. Set to `false` to use Ruff exclusively as a formatter.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.lint.enable": false
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          lint = {
            enable = false
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "lint": {
                "enable": false
              }
            }
          }
        }
      }
    }
    ```

### `preview` {: #lint_preview }

Whether to enable Ruff's preview mode when linting.

**Default value**: `null`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.lint.preview": true
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          lint = {
            preview = true
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "lint": {
                "preview": true
              }
            }
          }
        }
      }
    }
    ```

### `select`

Rules to enable by default. See [the documentation](https://docs.astral.sh/ruff/settings/#lint_select).

**Default value**: `null`

**Type**: `string[]`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.lint.select": ["E", "F"]
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          lint = {
            select = {"E", "F"}
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "lint": {
                "select": ["E", "F"]
              }
            }
          }
        }
      }
    }
    ```

### `extendSelect`

Rules to enable in addition to those in [`lint.select`](#select).

**Default value**: `null`

**Type**: `string[]`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.lint.extendSelect": ["W"]
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          lint = {
            extendSelect = {"W"}
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "lint": {
                "extendSelect": ["W"]
              }
            }
          }
        }
      }
    }
    ```

### `ignore`

Rules to disable by default. See [the documentation](https://docs.astral.sh/ruff/settings/#lint_ignore).

**Default value**: `null`

**Type**: `string[]`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.lint.ignore": ["E4", "E7"]
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          lint = {
            ignore = {"E4", "E7"}
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "lint": {
                "ignore": ["E4", "E7"]
              }
            }
          }
        }
      }
    }
    ```

## `format`

Settings specific to the Ruff formatter.

### `preview` {: #format_preview }

Whether to enable Ruff's preview mode when formatting.

**Default value**: `null`

**Type**: `bool`

**Example usage**:

=== "VS Code"

    ```json
    {
        "ruff.format.preview": true
    }
    ```

=== "Neovim"

    ```lua
    require('lspconfig').ruff.setup {
      init_options = {
        settings = {
          format = {
            preview = true
          }
        }
      }
    }
    ```

=== "Zed"

    ```json
    {
      "lsp": {
        "ruff": {
          "initialization_options": {
            "settings": {
              "format": {
                "preview": true
              }
            }
          }
        }
      }
    }
    ```

## VS Code specific

Additionally, the Ruff extension provides the following settings specific to VS Code. These settings
are not used by the language server and are only relevant to the extension.

### `enable`

Whether to enable the Ruff extension. Modifying this setting requires restarting VS Code to take effect.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

```json
{
    "ruff.enable": false
}
```

### `format.args`

!!! warning "Deprecated"

    This setting is only used by [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) which is
    deprecated in favor of the native language server. Refer to the [migration
    guide](migration.md) for more information.

_**This setting is not used by the native language server.**_

Additional arguments to pass to the Ruff formatter.

**Default value**: `[]`

**Type**: `string[]`

**Example usage**:

```json
{
    "ruff.format.args": ["--line-length", "100"]
}
```

### `ignoreStandardLibrary`

!!! warning "Deprecated"

    This setting is only used by [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) which is
    deprecated in favor of the native language server. Refer to the [migration
    guide](migration.md) for more information.

_**This setting is not used by the native language server.**_

Whether to ignore files that are inferred to be part of the Python standard library.

**Default value**: `true`

**Type**: `bool`

**Example usage**:

```json
{
    "ruff.ignoreStandardLibrary": false
}
```

### `importStrategy`

Strategy for loading the `ruff` executable.

- `fromEnvironment` finds Ruff in the environment, falling back to the bundled version
- `useBundled` uses the version bundled with the extension

**Default value**: `"fromEnvironment"`

**Type**: `"fromEnvironment" | "useBundled"`

**Example usage**:

```json
{
    "ruff.importStrategy": "useBundled"
}
```

### `interpreter`

A list of paths to Python interpreters. Even though this is a list, only the first interpreter is
used.

This setting depends on the [`ruff.nativeServer`](#nativeserver) setting:

- If using the native server, the interpreter is used to find the `ruff` executable when
    [`ruff.importStrategy`](#importstrategy) is set to `fromEnvironment`.
- Otherwise, the interpreter is used to run the `ruff-lsp` server.

**Default value**: `[]`

**Type**: `string[]`

**Example usage**:

```json
{
    "ruff.interpreter": ["/home/user/.local/bin/python"]
}
```

### `lint.args`

!!! warning "Deprecated"

    This setting is only used by [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) which is
    deprecated in favor of the native language server. Refer to the [migration
    guide](migration.md) for more information.

_**This setting is not used by the native language server.**_

Additional arguments to pass to the Ruff linter.

**Default value**: `[]`

**Type**: `string[]`

**Example usage**:

```json
{
    "ruff.lint.args": ["--config", "/path/to/pyproject.toml"]
}
```

### `lint.run`

!!! warning "Deprecated"

    This setting is only used by [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) which is
    deprecated in favor of the native language server. Refer to the [migration
    guide](migration.md) for more information.

_**This setting is not used by the native language server.**_

Run Ruff on every keystroke (`onType`) or on save (`onSave`).

**Default value**: `"onType"`

**Type**: `"onType" | "onSave"`

**Example usage**:

```json
{
    "ruff.lint.run": "onSave"
}
```

### `nativeServer`

Whether to use the native language server, [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) or
automatically decide between the two based on the Ruff version and extension settings.

- `"on"`: Use the native language server. A warning will be displayed if deprecated settings are
    detected.
- `"off"`: Use [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp). A warning will be displayed if
    settings specific to the native server are detected.
- `"auto"`: Automatically select between the native language server and
    [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) based on the following conditions:
    1. If the Ruff version is >= `0.5.3`, use the native language server unless any deprecated
        settings are detected. In that case, show a warning and use
        [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) instead.
    1. If the Ruff version is < `0.5.3`, use [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp). A
        warning will be displayed if settings specific to the native server are detected.
- `true`: Same as `on`
- `false`: Same as `off`

**Default value**: `"auto"`

**Type**: `"on" | "off" | "auto" | true | false`

**Example usage**:

```json
{
    "ruff.nativeServer": "on"
}
```

### `path`

A list of path to `ruff` executables.

The first executable in the list which is exists is used. This setting takes precedence over the
[`ruff.importStrategy`](#importstrategy) setting.

**Default value**: `[]`

**Type**: `string[]`

**Example usage**:

```json
{
    "ruff.path": ["/home/user/.local/bin/ruff"]
}
```

### `showNotifications`

!!! warning "Deprecated"

    This setting is only used by [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp) which is
    deprecated in favor of the native language server. Refer to the [migration
    guide](migration.md) for more information.

Setting to control when a notification is shown.

**Default value**: `"off"`

**Type**: `"off" | "onError" | "onWarning" | "always"`

**Example usage**:

```json
{
    "ruff.showNotifications": "onWarning"
}
```

### `trace.server`

The trace level for the language server. Refer to the [LSP
specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#traceValue)
for more information.

**Default value**: `"off"`

**Type**: `"off" | "messages" | "verbose"`

**Example usage**:

```json
{
    "ruff.trace.server": "messages"
}
```
````

## File: docs/editors/setup.md
````markdown
# Setup

We have specific setup instructions depending on your editor of choice. If you don't see your editor on this
list and would like a setup guide, please open an issue.

If you're transferring your configuration from [`ruff-lsp`](https://github.com/astral-sh/ruff-lsp),
regardless of editor, there are several settings which have changed or are no longer available. See
the [migration guide](./migration.md) for more.

!!! note

    The setup instructions provided below are on a best-effort basis. If you encounter any issues
    while setting up the Ruff in an editor, please [open an issue](https://github.com/astral-sh/ruff/issues/new)
    for assistance and help in improving this documentation.

!!! tip

    Regardless of the editor, it is recommended to disable the older language server
    ([`ruff-lsp`](https://github.com/astral-sh/ruff-lsp)) to prevent any conflicts.

## VS Code

Install the Ruff extension from the [VS Code
Marketplace](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff). It is
recommended to have the Ruff extension version `2024.32.0` or later to get the best experience with
the Ruff Language Server.

For more documentation on the Ruff extension, refer to the
[README](https://github.com/astral-sh/ruff-vscode/blob/main/README.md) of the extension repository.

## Neovim

The [`nvim-lspconfig`](https://github.com/neovim/nvim-lspconfig) plugin can be used to configure the
Ruff Language Server in Neovim. To set it up, install
[`nvim-lspconfig`](https://github.com/neovim/nvim-lspconfig) plugin, set it up as per the
[configuration](https://github.com/neovim/nvim-lspconfig#configuration) documentation, and add the
following to your `init.lua`:

=== "Neovim 0.10 (with [`nvim-lspconfig`](https://github.com/neovim/nvim-lspconfig))"

    ```lua
    require('lspconfig').ruff.setup({
      init_options = {
        settings = {
          -- Ruff language server settings go here
        }
      }
    })
    ```

=== "Neovim 0.11+ (with [`vim.lsp.config`](https://neovim.io/doc/user/lsp.html#vim.lsp.config()))"

    ```lua
    vim.lsp.config('ruff', {
      init_options = {
        settings = {
          -- Ruff language server settings go here
        }
      }
    })

    vim.lsp.enable('ruff')
    ```

!!! note

    If the installed version of `nvim-lspconfig` includes the changes from
    [neovim/nvim-lspconfig@`70d1c2c`](https://github.com/neovim/nvim-lspconfig/commit/70d1c2c31a88af4b36019dc1551be16bffb8f9db),
    you will need to use Ruff version `0.5.3` or later.

If you're using Ruff alongside another language server (like Pyright), you may want to defer to that
language server for certain capabilities, like [`textDocument/hover`](./features.md#hover):

```lua
vim.api.nvim_create_autocmd("LspAttach", {
  group = vim.api.nvim_create_augroup('lsp_attach_disable_ruff_hover', { clear = true }),
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    if client == nil then
      return
    end
    if client.name == 'ruff' then
      -- Disable hover in favor of Pyright
      client.server_capabilities.hoverProvider = false
    end
  end,
  desc = 'LSP: Disable hover capability from Ruff',
})
```

If you'd like to use Ruff exclusively for linting, formatting, and organizing imports, you can disable those
capabilities for Pyright:

```lua
require('lspconfig').pyright.setup {
  settings = {
    pyright = {
      -- Using Ruff's import organizer
      disableOrganizeImports = true,
    },
    python = {
      analysis = {
        -- Ignore all files for analysis to exclusively use Ruff for linting
        ignore = { '*' },
      },
    },
  },
}
```

By default, the log level for Ruff is set to `info`. To change the log level, you can set the
[`logLevel`](./settings.md#loglevel) setting:

```lua
require('lspconfig').ruff.setup {
  init_options = {
    settings = {
      logLevel = 'debug',
    }
  }
}
```

By default, Ruff will write logs to stderr which will be available in Neovim's LSP client log file
(`:lua vim.print(vim.lsp.get_log_path())`). It's also possible to divert these logs to a separate
file with the [`logFile`](./settings.md#logfile) setting.

To view the trace logs between Neovim and Ruff, set the log level for Neovim's LSP client to `debug`:

```lua
vim.lsp.set_log_level('debug')
```

<details>
<summary>With the <a href="https://github.com/stevearc/conform.nvim"><code>conform.nvim</code></a> plugin for Neovim.</summary>

```lua
require("conform").setup({
    formatters_by_ft = {
        python = {
          -- To fix auto-fixable lint errors.
          "ruff_fix",
          -- To run the Ruff formatter.
          "ruff_format",
          -- To organize the imports.
          "ruff_organize_imports",
        },
    },
})
```

</details>

<details>
<summary>With the <a href="https://github.com/mfussenegger/nvim-lint"><code>nvim-lint</code></a> plugin for Neovim.</summary>

```lua
require("lint").linters_by_ft = {
  python = { "ruff" },
}
```

</details>

<details>
<summary>With the <a href="https://github.com/dense-analysis/ale">ALE</a> plugin for Neovim or Vim.</summary>

<i>Neovim (using Lua):</i>

```lua
-- Linters
vim.g.ale_linters = { python = { "ruff" } }
-- Fixers
vim.g.ale_fixers = { python = { "ruff", "ruff_format" } }
```

<i>Vim (using Vimscript):</i>

```vim
" Linters
let g:ale_linters = { "python": ["ruff"] }
" Fixers
let g:ale_fixers = { "python": ["ruff", "ruff_format"] }
```

For the fixers, <code>ruff</code> will run <code>ruff check --fix</code> (to fix all auto-fixable
problems) whereas <code>ruff_format</code> will run <code>ruff format</code>.

</details>

## Vim

The [`vim-lsp`](https://github.com/prabirshrestha/vim-lsp) plugin can be used to configure the Ruff Language Server in Vim.
To set it up, install [`vim-lsp`](https://github.com/prabirshrestha/vim-lsp) plugin and register the server using the following
in your `.vimrc`:

```vim
if executable('ruff')
    au User lsp_setup call lsp#register_server({
        \ 'name': 'ruff',
        \ 'cmd': {server_info->['ruff', 'server']},
        \ 'allowlist': ['python'],
        \ 'workspace_config': {},
        \ })
endif
```

See the `vim-lsp`
[documentation](https://github.com/prabirshrestha/vim-lsp/blob/master/doc/vim-lsp.txt) for more
details on how to configure the language server.

If you're using Ruff alongside another LSP (like Pyright), you may want to defer to that LSP for certain capabilities,
like [`textDocument/hover`](./features.md#hover) by adding the following to the function `s:on_lsp_buffer_enabled()`:

```vim
function! s:on_lsp_buffer_enabled() abort
    " add your keybindings here (see https://github.com/prabirshrestha/vim-lsp?tab=readme-ov-file#registering-servers)

    let l:capabilities = lsp#get_server_capabilities('ruff')
    if !empty(l:capabilities)
      let l:capabilities.hoverProvider = v:false
    endif
endfunction
```

Ruff is also available as part of the [coc-pyright](https://github.com/fannheyward/coc-pyright)
extension for [coc.nvim](https://github.com/neoclide/coc.nvim).

<details>
<summary>Ruff can also be integrated via <a href="https://github.com/mattn/efm-langserver">efm language server</a> in just a few lines.</summary>

Following is an example config for efm to use Ruff for linting and formatting Python files:

```yaml
tools:
  python-ruff:
    lint-command: "ruff check --stdin-filename ${INPUT} --output-format concise --quiet -"
    lint-stdin: true
    lint-formats:
      - "%f:%l:%c: %m"
    format-command: "ruff format --stdin-filename ${INPUT} --quiet -"
    format-stdin: true
```

</details>

## Helix

Open the [language configuration file](https://docs.helix-editor.com/languages.html#languagestoml-files) for
Helix and add the language server as follows:

```toml
[language-server.ruff]
command = "ruff"
args = ["server"]
```

Then, you'll register the language server as the one to use with Python. If you don't already have a
language server registered to use with Python, add this to `languages.toml`:

```toml
[[language]]
name = "python"
language-servers = ["ruff"]
```

Otherwise, if you already have `language-servers` defined, you can simply add `"ruff"` to the list. For example,
if you already have `pylsp` as a language server, you can modify the language entry as follows:

```toml
[[language]]
name = "python"
language-servers = ["ruff", "pylsp"]
```

!!! note

    Support for multiple language servers for a language is only available in Helix version
    [`23.10`](https://github.com/helix-editor/helix/blob/master/CHANGELOG.md#2310-2023-10-24) and later.

If you want to, as an example, turn on auto-formatting, add `auto-format = true`:

```toml
[[language]]
name = "python"
language-servers = ["ruff", "pylsp"]
auto-format = true
```

See the [Helix documentation](https://docs.helix-editor.com/languages.html) for more settings you can use here.

You can pass settings into `ruff server` using `[language-server.ruff.config.settings]`. For example:

```toml
[language-server.ruff.config.settings]
lineLength = 80

[language-server.ruff.config.settings.lint]
select = ["E4", "E7"]
preview = false

[language-server.ruff.config.settings.format]
preview = true
```

By default, the log level for Ruff is set to `info`. To change the log level, you can set the
[`logLevel`](./settings.md#loglevel) setting:

```toml
[language-server.ruff]
command = "ruff"
args = ["server"]

[language-server.ruff.config.settings]
logLevel = "debug"
```

You can also divert Ruff's logs to a separate file with the [`logFile`](./settings.md#logfile) setting.

To view the trace logs between Helix and Ruff, pass in the `-v` (verbose) flag when starting Helix:

```sh
hx -v path/to/file.py
```

## Kate

1. Activate the [LSP Client plugin](https://docs.kde.org/stable5/en/kate/kate/plugins.html#kate-application-plugins).
1. Setup LSP Client [as desired](https://docs.kde.org/stable5/en/kate/kate/kate-application-plugin-lspclient.html).
1. Finally, add this to `Settings` -> `Configure Kate` -> `LSP Client` -> `User Server Settings`:

```json
{
  "servers": {
    "python": {
      "command": ["ruff", "server"],
      "url": "https://github.com/astral-sh/ruff",
      "highlightingModeRegex": "^Python$",
      "settings": {}
    }
  }
}
```

See [LSP Client documentation](https://docs.kde.org/stable5/en/kate/kate/kate-application-plugin-lspclient.html) for more details
on how to configure the server from there.

!!! important

    Kate's LSP Client plugin does not support multiple servers for the same language. As a
    workaround, you can use the [`python-lsp-server`](https://github.com/python-lsp/python-lsp-server)
    along with the [`python-lsp-ruff`](https://github.com/python-lsp/python-lsp-ruff) plugin to
    use Ruff alongside another language server. Note that this setup won't use the [server settings](settings.md)
    because the [`python-lsp-ruff`](https://github.com/python-lsp/python-lsp-ruff) plugin uses the
    `ruff` executable and not the language server.

## Sublime Text

To use Ruff with Sublime Text, install Sublime Text's [LSP](https://github.com/sublimelsp/LSP)
and [LSP-ruff](https://github.com/sublimelsp/LSP-ruff) package.

## PyCharm

### Via External Tool

Ruff can be installed as an [External Tool](https://www.jetbrains.com/help/pycharm/configuring-third-party-tools.html)
in PyCharm. Open the Preferences pane, then navigate to "Tools", then "External Tools". From there,
add a new tool with the following configuration:

![Install Ruff as an External Tool](https://github.com/user-attachments/assets/2b7af3e4-8196-4c64-a721-5bc3d7564a72)

Ruff should then appear as a runnable action:

![Ruff as a runnable action](https://user-images.githubusercontent.com/1309177/193156026-732b0aaf-3dd9-4549-9b4d-2de6d2168a33.png)

### Via third-party plugin

Ruff is also available as the [Ruff](https://plugins.jetbrains.com/plugin/20574-ruff) plugin on the
IntelliJ Marketplace (maintained by [@koxudaxi](https://github.com/koxudaxi)).

## Emacs

Ruff can be utilized as a language server via [`Eglot`](https://github.com/joaotavora/eglot), which is in Emacs's core.
To enable Ruff with automatic formatting on save, use the following configuration:

```elisp
(add-hook 'python-mode-hook 'eglot-ensure)
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '(python-mode . ("ruff" "server")))
  (add-hook 'after-save-hook 'eglot-format))
```

Ruff is available as [`flymake-ruff`](https://melpa.org/#/flymake-ruff) on MELPA:

```elisp
(require 'flymake-ruff)
(add-hook 'python-mode-hook #'flymake-ruff-load)
```

Ruff is also available as [`emacs-ruff-format`](https://github.com/scop/emacs-ruff-format):

```elisp
(require 'ruff-format)
(add-hook 'python-mode-hook 'ruff-format-on-save-mode)
```

Alternatively, it can be used via the [Apheleia](https://github.com/radian-software/apheleia) formatter library, by setting this configuration:

```emacs-lisp
;; Replace default (black) to use ruff for sorting import and formatting.
(setf (alist-get 'python-mode apheleia-mode-alist)
      '(ruff-isort ruff))
(setf (alist-get 'python-ts-mode apheleia-mode-alist)
      '(ruff-isort ruff))
```

## TextMate

Ruff is also available via the [`textmate2-ruff-linter`](https://github.com/vigo/textmate2-ruff-linter)
bundle for TextMate.

## Zed

Ruff is available as an extension for the Zed editor. To install it:

1. Open the command palette with `Cmd+Shift+P`
1. Search for "zed: extensions"
1. Search for "ruff" in the extensions list and click "Install"

To configure Zed to use the Ruff language server for Python files, add the following
to your `settings.json` file:

```json
{
  "languages": {
    "Python": {
      "language_servers": ["ruff"]
      // Or, if there are other language servers you want to use with Python
      // "language_servers": ["pyright", "ruff"]
    }
  }
}
```

To configure the language server, you can provide the [server settings](settings.md)
under the [`lsp.ruff.initialization_options.settings`](https://zed.dev/docs/configuring-zed#lsp) key:

```json
{
  "lsp": {
    "ruff": {
      "initialization_options": {
        "settings": {
          // Ruff server settings goes here
          "lineLength": 80,
          "lint": {
            "extendSelect": ["I"],
          }
        }
      }
    }
  }
}
```

!!! note

    Support for multiple formatters for a given language is only available in Zed version
    `0.146.0` and later.

You can configure Ruff to format Python code on-save by registering the Ruff formatter
and enabling the [`format_on_save`](https://zed.dev/docs/configuring-zed#format-on-save) setting:

=== "Zed 0.146.0+"

    ```json
    {
      "languages": {
        "Python": {
          "language_servers": ["ruff"],
          "format_on_save": "on",
          "formatter": [
            {
              "language_server": {
                "name": "ruff"
              }
            }
          ]
        }
      }
    }
    ```

You can configure Ruff to fix lint violations and/or organize imports on-save by enabling the
`source.fixAll.ruff` and `source.organizeImports.ruff` code actions respectively:

=== "Zed 0.146.0+"

    ```json
    {
      "languages": {
        "Python": {
          "language_servers": ["ruff"],
          "format_on_save": "on",
          "formatter": [
            {
              "code_actions": {
                // Fix all auto-fixable lint violations
                "source.fixAll.ruff": true,
                // Organize imports
                "source.organizeImports.ruff": true
              }
            }
          ]
        }
      }
    }
    ```

Taken together, you can configure Ruff to format, fix, and organize imports on-save via the
following `settings.json`:

!!! note

    For this configuration, it is important to use the correct order of the code action and
    formatter language server settings. The code actions should be defined before the formatter to
    ensure that the formatter takes care of any remaining style issues after the code actions have
    been applied.

=== "Zed 0.146.0+"

    ```json
    {
      "languages": {
        "Python": {
          "language_servers": ["ruff"],
          "format_on_save": "on",
          "formatter": [
            {
              "code_actions": {
                "source.organizeImports.ruff": true,
                "source.fixAll.ruff": true
              }
            },
            {
              "language_server": {
                "name": "ruff"
              }
            }
          ]
        }
      }
    }
    ```
````

## File: docs/formatter/black.md
````markdown
---
title: "Known Deviations from Black"
hide:
  - navigation
---

This document enumerates the known, intentional differences in code style between Black and Ruff's
formatter.

For a list of unintentional deviations, see [issue tracker](https://github.com/astral-sh/ruff/issues?q=is%3Aopen+is%3Aissue+label%3Aformatter).

### Trailing end-of-line comments

Black's priority is to fit an entire statement on a line, even if it contains end-of-line comments.
In such cases, Black collapses the statement, and moves the comment to the end of the collapsed
statement:

```python
# Input
while (
    cond1  # almost always true
    and cond2  # almost never true
):
    print("Do something")

# Black
while cond1 and cond2:  # almost always true  # almost never true
    print("Do something")
```

Ruff, like [Prettier](https://prettier.io/), expands any statement that contains trailing
end-of-line comments. For example, Ruff would avoid collapsing the `while` test in the snippet
above. This ensures that the comments remain close to their original position and retain their
original intent, at the cost of retaining additional vertical space.

This deviation only impacts unformatted code, in that Ruff's output should not deviate for code that
has already been formatted by Black.

### Pragma comments are ignored when computing line width

Pragma comments (`# type`, `# noqa`, `# pyright`, `# pylint`, etc.) are ignored when computing the width of a line.
This prevents Ruff from moving pragma comments around, thereby modifying their meaning and behavior:

See Ruff's [pragma comment handling proposal](https://github.com/astral-sh/ruff/discussions/6670)
for details.

This is similar to [Pyink](https://github.com/google/pyink) but a deviation from Black. Black avoids
splitting any lines that contain a `# type` comment ([#997](https://github.com/psf/black/issues/997)),
but otherwise avoids special-casing pragma comments.

As Ruff expands trailing end-of-line comments, Ruff will also avoid moving pragma comments in cases
like the following, where moving the `# noqa` to the end of the line causes it to suppress errors
on both `first()` and `second()`:

```python
# Input
[
    first(),  # noqa
    second()
]

# Black
[first(), second()]  # noqa

# Ruff
[
    first(),  # noqa
    second(),
]
```

### Line width vs. line length

Ruff uses the Unicode width of a line to determine if a line fits. Black uses Unicode width for strings,
and character width for all other tokens. Ruff _also_ uses Unicode width for identifiers and comments.

### Parenthesizing long nested-expressions

Black 24 and newer parenthesizes long conditional expressions and type annotations in function parameters:

```python
# Black
[
    "____________________________",
    "foo",
    "bar",
    (
        "baz"
        if some_really_looooooooong_variable
        else "some other looooooooooooooong value"
    ),
]


def foo(
    i: int,
    x: (
        Loooooooooooooooooooooooong
        | Looooooooooooooooong
        | Looooooooooooooooooooong
        | Looooooong
    ),
    *,
    s: str,
) -> None:
    pass

# Ruff
[
    "____________________________",
    "foo",
    "bar",
    "baz"
    if some_really_looooooooong_variable
    else "some other looooooooooooooong value",
]


def foo(
    i: int,
    x: Loooooooooooooooooooooooong
    | Looooooooooooooooong
    | Looooooooooooooooooooong
    | Looooooong,
    *,
    s: str,
) -> None:
    pass
```

We agree that Ruff's formatting (that matches Black's 23) is hard to read and needs improvement. But we aren't convinced that parenthesizing long nested expressions is the best solution, especially when considering expression formatting holistically. That's why we want to defer the decision until we've explored alternative nested expression formatting styles. See [psf/Black#4123](https://github.com/psf/black/issues/4123) for an in-depth explanation of our concerns and an outline of possible alternatives.

### Call expressions with a single multiline string argument

Unlike Black, Ruff preserves the indentation of a single multiline-string argument in a call expression:

```python
# Input
call(
  """"
  A multiline
  string
  """
)

dedent(""""
    A multiline
    string
""")

# Black
call(
  """"
  A multiline
  string
  """
)

dedent(
  """"
  A multiline
  string
"""
)


# Ruff
call(
  """"
  A multiline
  string
  """
)

dedent(""""
    A multiline
    string
""")
```

Black intended to ship a similar style change as part of the 2024 style that always removes the indent. It turned out that this change was too disruptive to justify the cases where it improved formatting. Ruff introduced the new heuristic of preserving the indent. We believe it's a good compromise that improves formatting but minimizes disruption for users.

### Blank lines at the start of a block

Black 24 and newer allows blank lines at the start of a block, where Ruff always removes them:

```python
# Black
if x:

  a = 123

# Ruff
if x:
  a = 123
```

Currently, we are concerned that allowing blank lines at the start of a block leads [to unintentional blank lines when refactoring or moving code](https://github.com/astral-sh/ruff/issues/8893#issuecomment-1867259744). However, we will consider adopting Black's formatting at a later point with an improved heuristic. The style change is tracked in [#9745](https://github.com/astral-sh/ruff/issues/9745).


### F-strings

Ruff formats expression parts in f-strings whereas Black does not:

```python
# Input
f'test{inner   + "nested_string"} including math {5 ** 3 + 10}'

# Black
f'test{inner   + "nested_string"} including math {5 ** 3 + 10}'

# Ruff
f"test{inner + 'nested_string'} including math {5**3 + 10}"
```

For more details on the formatting style, refer to the [f-string
formatting](../formatter.md#f-string-formatting) section.

### Implicit concatenated strings

Ruff merges implicitly concatenated strings if the entire string fits on a single line:

```python
# Input
def test(max_history):
    raise argparse.ArgumentTypeError(
        f"The value of `--max-history {max_history}` " f"is not a positive integer."
    )

# Black
def test(max_history):
    raise argparse.ArgumentTypeError(
        f"The value of `--max-history {max_history}` " f"is not a positive integer."
    )

# Ruff
def test(max_history):
    raise argparse.ArgumentTypeError(
        f"The value of `--max-history {max_history}` is not a positive integer."
    )
```

Black's unstable style applies the same formatting.

There are few rare cases where Ruff can't merge the implicitly concatenated strings automatically.
In those cases, Ruff preserves if the implicit concatenated strings are formatted over multiple lines:

```python
# Input
a = (
    r"aaaaaaa"
    "bbbbbbbbbbbb"
)

# Black
a = r"aaaaaaa" "bbbbbbbbbbbb"

# Ruff
a = (
    r"aaaaaaa"
    "bbbbbbbbbbbb"
)
```

This ensures compatibility with `ISC001` ([#8272](https://github.com/astral-sh/ruff/issues/8272)).

### `assert` statements

Unlike Black, Ruff prefers breaking the message over breaking the assertion, similar to how both Ruff and Black prefer breaking the assignment value over breaking the assignment target:

```python
# Input
assert (
    len(policy_types) >= priority + num_duplicates
), f"This tests needs at least {priority+num_duplicates} many types."


# Black
assert (
    len(policy_types) >= priority + num_duplicates
), f"This tests needs at least {priority+num_duplicates} many types."

# Ruff
assert len(policy_types) >= priority + num_duplicates, (
    f"This tests needs at least {priority + num_duplicates} many types."
)
```

### `global` and `nonlocal` names are broken across multiple lines by continuations

If a `global` or `nonlocal` statement includes multiple names, and exceeds the configured line
width, Ruff will break them across multiple lines using continuations:

```python
# Input
global analyze_featuremap_layer, analyze_featuremapcompression_layer, analyze_latencies_post, analyze_motions_layer, analyze_size_model

# Ruff
global \
    analyze_featuremap_layer, \
    analyze_featuremapcompression_layer, \
    analyze_latencies_post, \
    analyze_motions_layer, \
    analyze_size_model
```

### Trailing own-line comments on imports are not moved to the next line

Black enforces a single empty line between an import and a trailing own-line comment. Ruff leaves
such comments in-place:

```python
# Input
import os
# comment

import sys

# Black
import os

# comment

import sys

# Ruff
import os
# comment

import sys
```

### Parentheses around awaited collections are not preserved

Black preserves parentheses around awaited collections:

```python
await ([1, 2, 3])
```

Ruff will instead remove them:

```python
await [1, 2, 3]
```

This is more consistent to the formatting of other awaited expressions: Ruff and Black both
remove parentheses around, e.g., `await (1)`, only retaining them when syntactically required,
as in, e.g., `await (x := 1)`.

### Implicit string concatenations in attribute accesses

Given the following unformatted code:

```python
print("aaaaaaaaaaaaaaaa" "aaaaaaaaaaaaaaaa".format(bbbbbbbbbbbbbbbbbb + bbbbbbbbbbbbbbbbbb))
```

Internally, Black's logic will first expand the outermost `print` call:

```python
print(
    "aaaaaaaaaaaaaaaa" "aaaaaaaaaaaaaaaa".format(bbbbbbbbbbbbbbbbbb + bbbbbbbbbbbbbbbbbb)
)
```

Since the argument is _still_ too long, Black will then split on the operator with the highest split
precedence. In this case, Black splits on the implicit string concatenation, to produce the
following Black-formatted code:

```python
print(
    "aaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaa".format(bbbbbbbbbbbbbbbbbb + bbbbbbbbbbbbbbbbbb)
)
```

Ruff gives implicit concatenations a "lower" priority when breaking lines. As a result, Ruff
would instead format the above as:

```python
print(
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa".format(bbbbbbbbbbbbbbbbbb + bbbbbbbbbbbbbbbbbb)
)
```

In general, Black splits implicit string concatenations over multiple lines more often than Ruff,
even if those concatenations _can_ fit on a single line. Ruff instead avoids splitting such
concatenations unless doing so is necessary to fit within the configured line width.

### Own-line comments on expressions don't cause the expression to expand

Given an expression like:

```python
(
    # A comment in the middle
    some_example_var and some_example_var not in some_example_var
)
```

Black associates the comment with `some_example_var`, thus splitting it over two lines:

```python
(
    # A comment in the middle
    some_example_var
    and some_example_var not in some_example_var
)
```

Ruff will instead associate the comment with the entire boolean expression, thus preserving the
initial formatting:

```python
(
    # A comment in the middle
    some_example_var and some_example_var not in some_example_var
)
```

### Tuples are parenthesized when expanded

Ruff tends towards parenthesizing tuples (with a few exceptions), while Black tends to remove tuple
parentheses more often.

In particular, Ruff will always insert parentheses around tuples that expand over multiple lines:

```python
# Input
(a, b), (c, d,)

# Black
(a, b), (
    c,
    d,
)

# Ruff
(
    (a, b),
    (
        c,
        d,
    ),
)
```

There's one exception here. In `for` loops, both Ruff and Black will avoid inserting unnecessary
parentheses:

```python
# Input
for a, [b, d,] in c:
    pass

# Black
for a, [
    b,
    d,
] in c:
    pass

# Ruff
for a, [
    b,
    d,
] in c:
    pass
```

### Single-element tuples are always parenthesized

Ruff always inserts parentheses around single-element tuples, while Black will omit them in some
cases:

```python
# Input
(a, b),

# Black
(a, b),

# Ruff
((a, b),)
```

Adding parentheses around single-element tuples adds visual distinction and helps avoid "accidental"
tuples created by extraneous trailing commas (see, e.g., [#17181](https://github.com/django/django/pull/17181)).


### Parentheses around call-chain assignment values are not preserved

Given:

```python
def update_emission_strength():
    (
        get_rgbw_emission_node_tree(self)
        .nodes["Emission"]
        .inputs["Strength"]
        .default_value
    ) = (self.emission_strength * 2)
```

Black will preserve the parentheses in `(self.emission_strength * 2)`, whereas Ruff will remove
them.

Both Black and Ruff remove such parentheses in simpler assignments, like:

```python
# Input
def update_emission_strength():
    value = (self.emission_strength * 2)

# Black
def update_emission_strength():
    value = self.emission_strength * 2

# Ruff
def update_emission_strength():
    value = self.emission_strength * 2
```

### Call chain calls break differently in some cases

Black occasionally breaks call chains differently than Ruff; in particular, Black occasionally
expands the arguments for the last call in the chain, as in:

```python
# Input
df.drop(
    columns=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
).drop_duplicates().rename(
    columns={
        "a": "a",
    }
).to_csv(path / "aaaaaa.csv", index=False)

# Black
df.drop(
    columns=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
).drop_duplicates().rename(
    columns={
        "a": "a",
    }
).to_csv(
    path / "aaaaaa.csv", index=False
)

# Ruff
df.drop(
    columns=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
).drop_duplicates().rename(
    columns={
        "a": "a",
    }
).to_csv(path / "aaaaaa.csv", index=False)
```

Ruff will only expand the arguments if doing so is necessary to fit within the configured line
width.

Note that Black does not apply this last-call argument breaking universally. For example, both
Black and Ruff will format the following identically:

```python
# Input
df.drop(
    columns=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
).drop_duplicates(a).rename(
    columns={
        "a": "a",
    }
).to_csv(
    path / "aaaaaa.csv", index=False
).other(a)

# Black
df.drop(columns=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]).drop_duplicates(a).rename(
    columns={
        "a": "a",
    }
).to_csv(path / "aaaaaa.csv", index=False).other(a)

# Ruff
df.drop(columns=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]).drop_duplicates(a).rename(
    columns={
        "a": "a",
    }
).to_csv(path / "aaaaaa.csv", index=False).other(a)
```

Similarly, in some cases, Ruff will collapse composite binary expressions more aggressively than
Black, if doing so allows the expression to fit within the configured line width:

```python
# Black
assert AAAAAAAAAAAAAAAAAAAAAA.bbbbbb.fooo(
    aaaaaaaaaaaa=aaaaaaaaaaaa
).ccccc() == (len(aaaaaaaaaa) + 1) * fooooooooooo * (
    foooooo + 1
) * foooooo * len(
    list(foo(bar(4, foo), foo))
)

# Ruff
assert AAAAAAAAAAAAAAAAAAAAAA.bbbbbb.fooo(
    aaaaaaaaaaaa=aaaaaaaaaaaa
).ccccc() == (len(aaaaaaaaaa) + 1) * fooooooooooo * (
    foooooo + 1
) * foooooo * len(list(foo(bar(4, foo), foo)))
```

### Single `with` item targeting Python 3.8 or older

Unlike Black, Ruff uses the same layout for `with` statements with a single context manager as it does for `while`, `if` and other compound statements:

```python
# Input
def run(data_path, model_uri):
    with pyspark.sql.SparkSession.builder.config(
        key="spark.python.worker.reuse", value=True
    ).config(key="spark.ui.enabled", value=False).master(
        "local-cluster[2, 1, 1024]"
    ).getOrCreate():
        # ignore spark log output
        spark.sparkContext.setLogLevel("OFF")
        print(score_model(spark, data_path, model_uri))

# Black
def run(data_path, model_uri):
    with pyspark.sql.SparkSession.builder.config(
        key="spark.python.worker.reuse", value=True
    ).config(key="spark.ui.enabled", value=False).master(
        "local-cluster[2, 1, 1024]"
    ).getOrCreate():
        # ignore spark log output
        spark.sparkContext.setLogLevel("OFF")
        print(score_model(spark, data_path, model_uri))

# Ruff
def run(data_path, model_uri):
    with (
        pyspark.sql.SparkSession.builder.config(
            key="spark.python.worker.reuse", value=True
        )
        .config(key="spark.ui.enabled", value=False)
        .master("local-cluster[2, 1, 1024]")
        .getOrCreate()
    ):
        # ignore spark log output
        spark.sparkContext.setLogLevel("OFF")
        print(score_model(spark, data_path, model_uri))
```

Ruff's formatting matches the formatting of other compound statements:

```python
def test():
    if (
        pyspark.sql.SparkSession.builder.config(
            key="spark.python.worker.reuse", value=True
        )
        .config(key="spark.ui.enabled", value=False)
        .master("local-cluster[2, 1, 1024]")
        .getOrCreate()
    ):
        # ignore spark log output
        spark.sparkContext.setLogLevel("OFF")
        print(score_model(spark, data_path, model_uri))
```

### The last context manager in a `with` statement may be collapsed onto a single line

When using a `with` statement with multiple unparenthesized context managers, Ruff may collapse the
last context manager onto a single line, if doing so allows the `with` statement to fit within the
configured line width.

Black, meanwhile, tends to break the last context manager slightly differently, as in the following
example:

```python
# Black
with tempfile.TemporaryDirectory() as d1:
    symlink_path = Path(d1).joinpath("testsymlink")
    with tempfile.TemporaryDirectory(dir=d1) as d2, tempfile.TemporaryDirectory(
        dir=d1
    ) as d4, tempfile.TemporaryDirectory(dir=d2) as d3, tempfile.NamedTemporaryFile(
        dir=d4
    ) as source_file, tempfile.NamedTemporaryFile(
        dir=d3
    ) as lock_file:
        pass

# Ruff
with tempfile.TemporaryDirectory() as d1:
    symlink_path = Path(d1).joinpath("testsymlink")
    with tempfile.TemporaryDirectory(dir=d1) as d2, tempfile.TemporaryDirectory(
        dir=d1
    ) as d4, tempfile.TemporaryDirectory(dir=d2) as d3, tempfile.NamedTemporaryFile(
        dir=d4
    ) as source_file, tempfile.NamedTemporaryFile(dir=d3) as lock_file:
        pass
```

When targeting Python 3.9 or newer, parentheses will be inserted around the
context managers to allow for clearer breaks across multiple lines, as in:

```python
with tempfile.TemporaryDirectory() as d1:
    symlink_path = Path(d1).joinpath("testsymlink")
    with (
        tempfile.TemporaryDirectory(dir=d1) as d2,
        tempfile.TemporaryDirectory(dir=d1) as d4,
        tempfile.TemporaryDirectory(dir=d2) as d3,
        tempfile.NamedTemporaryFile(dir=d4) as source_file,
        tempfile.NamedTemporaryFile(dir=d3) as lock_file,
    ):
        pass
```

### Preserving parentheses around single-element lists

Ruff preserves at least one parentheses around list elements, even if the list only contains a single element. The Black 2025 or newer, on the other hand, removes the parentheses 
for single-element lists if they aren't multiline and doing so does not change semantics:

```python
# Input
items = [(True)]
items = [(((((True)))))]
items = {(123)}

# Black
items = [True]
items = [True]
items = {123}

# Ruff
items = [(True)]
items = [(True)]
items = {(123)}

```
````

## File: docs/configuration.md
````markdown
# Configuring Ruff

Ruff can be configured through a `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file.

Whether you're using Ruff as a linter, formatter, or both, the underlying configuration strategy and
semantics are the same.

For a complete enumeration of the available configuration options, see [_Settings_](settings.md).

If left unspecified, Ruff's default configuration is equivalent to:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    # Exclude a variety of commonly ignored directories.
    exclude = [
        ".bzr",
        ".direnv",
        ".eggs",
        ".git",
        ".git-rewrite",
        ".hg",
        ".ipynb_checkpoints",
        ".mypy_cache",
        ".nox",
        ".pants.d",
        ".pyenv",
        ".pytest_cache",
        ".pytype",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        ".vscode",
        "__pypackages__",
        "_build",
        "buck-out",
        "build",
        "dist",
        "node_modules",
        "site-packages",
        "venv",
    ]

    # Same as Black.
    line-length = 88
    indent-width = 4

    # Assume Python 3.9
    target-version = "py39"

    [tool.ruff.lint]
    # Enable Pyflakes (`F`) and a subset of the pycodestyle (`E`) codes by default.
    # Unlike Flake8, Ruff doesn't enable pycodestyle warnings (`W`) or
    # McCabe complexity (`C901`) by default.
    select = ["E4", "E7", "E9", "F"]
    ignore = []

    # Allow fix for all enabled rules (when `--fix`) is provided.
    fixable = ["ALL"]
    unfixable = []

    # Allow unused variables when underscore-prefixed.
    dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

    [tool.ruff.format]
    # Like Black, use double quotes for strings.
    quote-style = "double"

    # Like Black, indent with spaces, rather than tabs.
    indent-style = "space"

    # Like Black, respect magic trailing commas.
    skip-magic-trailing-comma = false

    # Like Black, automatically detect the appropriate line ending.
    line-ending = "auto"

    # Enable auto-formatting of code examples in docstrings. Markdown,
    # reStructuredText code/literal blocks and doctests are all supported.
    #
    # This is currently disabled by default, but it is planned for this
    # to be opt-out in the future.
    docstring-code-format = false

    # Set the line length limit used when formatting code snippets in
    # docstrings.
    #
    # This only has an effect when the `docstring-code-format` setting is
    # enabled.
    docstring-code-line-length = "dynamic"
    ```

=== "ruff.toml"

    ```toml
    # Exclude a variety of commonly ignored directories.
    exclude = [
        ".bzr",
        ".direnv",
        ".eggs",
        ".git",
        ".git-rewrite",
        ".hg",
        ".ipynb_checkpoints",
        ".mypy_cache",
        ".nox",
        ".pants.d",
        ".pyenv",
        ".pytest_cache",
        ".pytype",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        ".vscode",
        "__pypackages__",
        "_build",
        "buck-out",
        "build",
        "dist",
        "node_modules",
        "site-packages",
        "venv",
    ]

    # Same as Black.
    line-length = 88
    indent-width = 4

    # Assume Python 3.9
    target-version = "py39"

    [lint]
    # Enable Pyflakes (`F`) and a subset of the pycodestyle (`E`) codes by default.
    # Unlike Flake8, Ruff doesn't enable pycodestyle warnings (`W`) or
    # McCabe complexity (`C901`) by default.
    select = ["E4", "E7", "E9", "F"]
    ignore = []

    # Allow fix for all enabled rules (when `--fix`) is provided.
    fixable = ["ALL"]
    unfixable = []

    # Allow unused variables when underscore-prefixed.
    dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

    [format]
    # Like Black, use double quotes for strings.
    quote-style = "double"

    # Like Black, indent with spaces, rather than tabs.
    indent-style = "space"

    # Like Black, respect magic trailing commas.
    skip-magic-trailing-comma = false

    # Like Black, automatically detect the appropriate line ending.
    line-ending = "auto"

    # Enable auto-formatting of code examples in docstrings. Markdown,
    # reStructuredText code/literal blocks and doctests are all supported.
    #
    # This is currently disabled by default, but it is planned for this
    # to be opt-out in the future.
    docstring-code-format = false

    # Set the line length limit used when formatting code snippets in
    # docstrings.
    #
    # This only has an effect when the `docstring-code-format` setting is
    # enabled.
    docstring-code-line-length = "dynamic"
    ```

As an example, the following would configure Ruff to:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    # 1. Enable flake8-bugbear (`B`) rules, in addition to the defaults.
    select = ["E4", "E7", "E9", "F", "B"]

    # 2. Avoid enforcing line-length violations (`E501`)
    ignore = ["E501"]

    # 3. Avoid trying to fix flake8-bugbear (`B`) violations.
    unfixable = ["B"]

    # 4. Ignore `E402` (import violations) in all `__init__.py` files, and in selected subdirectories.
    [tool.ruff.lint.per-file-ignores]
    "__init__.py" = ["E402"]
    "**/{tests,docs,tools}/*" = ["E402"]

    [tool.ruff.format]
    # 5. Use single quotes in `ruff format`.
    quote-style = "single"
    ```

=== "ruff.toml"

    ```toml
    [lint]
    # 1. Enable flake8-bugbear (`B`) rules, in addition to the defaults.
    select = ["E4", "E7", "E9", "F", "B"]

    # 2. Avoid enforcing line-length violations (`E501`)
    ignore = ["E501"]

    # 3. Avoid trying to fix flake8-bugbear (`B`) violations.
    unfixable = ["B"]

    # 4. Ignore `E402` (import violations) in all `__init__.py` files, and in selected subdirectories.
    [lint.per-file-ignores]
    "__init__.py" = ["E402"]
    "**/{tests,docs,tools}/*" = ["E402"]

    [format]
    # 5. Use single quotes in `ruff format`.
    quote-style = "single"
    ```

Linter plugin configurations are expressed as subsections, e.g.:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    # Add "Q" to the list of enabled codes.
    select = ["E4", "E7", "E9", "F", "Q"]

    [tool.ruff.lint.flake8-quotes]
    docstring-quotes = "double"
    ```

=== "ruff.toml"

    ```toml
    [lint]
    # Add "Q" to the list of enabled codes.
    select = ["E4", "E7", "E9", "F", "Q"]

    [lint.flake8-quotes]
    docstring-quotes = "double"
    ```

Ruff respects `pyproject.toml`, `ruff.toml`, and `.ruff.toml` files. All three implement an
equivalent schema (though in the `ruff.toml` and `.ruff.toml` versions, the `[tool.ruff]` header and
`tool.ruff` section prefix is omitted).

For a complete enumeration of the available configuration options, see [_Settings_](settings.md).

## Config file discovery

Similar to [ESLint](https://eslint.org/docs/latest/use/configure/configuration-files#cascading-configuration-objects),
Ruff supports hierarchical configuration, such that the "closest" config file in the
directory hierarchy is used for every individual file, with all paths in the config file
(e.g., `exclude` globs, `src` paths) being resolved relative to the directory containing that
config file.

There are a few exceptions to these rules:

1. In locating the "closest" `pyproject.toml` file for a given path, Ruff ignores any
    `pyproject.toml` files that lack a `[tool.ruff]` section.
1. If a configuration file is passed directly via `--config`, those settings are used for _all_
    analyzed files, and any relative paths in that configuration file (like `exclude` globs or
    `src` paths) are resolved relative to the _current_ working directory.
1. If no config file is found in the filesystem hierarchy, Ruff will fall back to using
    a default configuration. If a user-specific configuration file exists
    at `${config_dir}/ruff/pyproject.toml`, that file will be used instead of the default
    configuration, with `${config_dir}` being determined via [`etcetera`'s native strategy](https://docs.rs/etcetera/latest/etcetera/#native-strategy),
    and all relative paths being again resolved relative to the _current working directory_.
1. Any config-file-supported settings that are provided on the command-line (e.g., via
    `--select`) will override the settings in _every_ resolved configuration file.

Unlike [ESLint](https://eslint.org/docs/latest/use/configure/configuration-files#cascading-configuration-objects),
Ruff does not merge settings across configuration files; instead, the "closest" configuration file
is used, and any parent configuration files are ignored. In lieu of this implicit cascade, Ruff
supports an [`extend`](settings.md#extend) field, which allows you to inherit the settings from another
config file, like so:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    # Extend the `pyproject.toml` file in the parent directory...
    extend = "../pyproject.toml"

    # ...but use a different line length.
    line-length = 100
    ```

=== "ruff.toml"

    ```toml
    # Extend the `ruff.toml` file in the parent directory...
    extend = "../ruff.toml"

    # ...but use a different line length.
    line-length = 100
    ```

All of the above rules apply equivalently to `pyproject.toml`, `ruff.toml`, and `.ruff.toml` files.
If Ruff detects multiple configuration files in the same directory, the `.ruff.toml` file will take
precedence over the `ruff.toml` file, and the `ruff.toml` file will take precedence over
the `pyproject.toml` file.

### Inferring the Python version
When no discovered configuration specifies a [`target-version`](settings.md#target-version), Ruff will attempt to fall back to the minimum version compatible with the `requires-python` field in a nearby `pyproject.toml`.
The rules for this behavior are as follows:

1. If a configuration file is passed directly, Ruff does not attempt to infer a missing `target-version`.
1. If a configuration file is found in the filesystem hierarchy, Ruff will infer a missing `target-version` from the `requires-python` field in a `pyproject.toml` file in the same directory as the found configuration.
1. If we are using a user-level configuration from `${config_dir}/ruff/pyproject.toml`, the `requires-python` field in the first `pyproject.toml` file found in an ancestor of the current working directory takes precedence over the `target-version` in the user-level configuration.
1. If no configuration files are found, Ruff will infer the `target-version` from the `requires-python` field in the first `pyproject.toml` file found in an ancestor of the current working directory.

Note that in these last two cases, the behavior of Ruff may differ depending on the working directory from which it is invoked.

## Python file discovery

When passed a path on the command-line, Ruff will automatically discover all Python files in that
path, taking into account the [`exclude`](settings.md#exclude) and [`extend-exclude`](settings.md#extend-exclude)
settings in each directory's configuration file.

Files can also be selectively excluded from linting or formatting by scoping the `exclude` setting
to the tool-specific configuration tables. For example, the following would prevent `ruff` from
formatting `.pyi` files, but would continue to include them in linting:

=== "pyproject.toml"

    ```toml
    [tool.ruff.format]
    exclude = ["*.pyi"]
    ```

=== "ruff.toml"

    ```toml
    [format]
    exclude = ["*.pyi"]
    ```

By default, Ruff will also skip any files that are omitted via `.ignore`, `.gitignore`,
`.git/info/exclude`, and global `gitignore` files (see: [`respect-gitignore`](settings.md#respect-gitignore)).

Files that are passed to `ruff` directly are always analyzed, regardless of the above criteria.
For example, `ruff check /path/to/excluded/file.py` will always lint `file.py`.

### Default inclusions

By default, Ruff will discover files matching `*.py`, `*.pyi`, `*.ipynb`, or `pyproject.toml`.

To lint or format files with additional file extensions, use the [`extend-include`](settings.md#extend-include) setting.
You can also change the default selection using the [`include`](settings.md#include) setting.


=== "pyproject.toml"

    ```toml
    [tool.ruff]
    include = ["pyproject.toml", "src/**/*.py", "scripts/**/*.py"]
    ```

=== "ruff.toml"

    ```toml
    include = ["pyproject.toml", "src/**/*.py", "scripts/**/*.py"]
    ```

!!! warning
    Paths provided to `include` _must_ match files. For example, `include = ["src"]` will fail since it
    matches a directory.

## Jupyter Notebook discovery

Ruff has built-in support for linting and formatting [Jupyter Notebooks](https://jupyter.org/),
which are linted and formatted by default on version `0.6.0` and higher.

If you'd prefer to either only lint or only format Jupyter Notebook files, you can use the
section-specific `exclude` option to do so. For example, the following would only lint Jupyter
Notebook files and not format them:

=== "pyproject.toml"

    ```toml
    [tool.ruff.format]
    exclude = ["*.ipynb"]
    ```

=== "ruff.toml"

    ```toml
    [format]
    exclude = ["*.ipynb"]
    ```

And, conversely, the following would only format Jupyter Notebook files and not lint them:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    exclude = ["*.ipynb"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    exclude = ["*.ipynb"]
    ```

You can completely disable Jupyter Notebook support by updating the
[`extend-exclude`](settings.md#extend-exclude) setting:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    extend-exclude = ["*.ipynb"]
    ```

=== "ruff.toml"

    ```toml
    extend-exclude = ["*.ipynb"]
    ```

If you'd like to ignore certain rules specifically for Jupyter Notebook files, you can do so by
using the [`per-file-ignores`](settings.md#per-file-ignores) setting:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint.per-file-ignores]
    "*.ipynb" = ["T20"]
    ```

=== "ruff.toml"

    ```toml
    [lint.per-file-ignores]
    "*.ipynb" = ["T20"]
    ```

Some rules have different behavior when applied to Jupyter Notebook files. For
example, when applied to `.py` files the
[`module-import-not-at-top-of-file` (`E402`)](rules/module-import-not-at-top-of-file.md)
rule detect imports at the top of a file, but for notebooks it detects imports at the top of a
**cell**. For a given rule, the rule's documentation will always specify if it has different
behavior when applied to Jupyter Notebook files.

## Command-line interface

Some configuration options can be provided or overridden via dedicated flags on the command line.
This includes those related to rule enablement and disablement,
file discovery, logging level, and more:

```console
$ ruff check path/to/code/ --select F401 --select F403 --quiet
```

All other configuration options can be set via the command line
using the `--config` flag, detailed below.

### The `--config` CLI flag

The `--config` flag has two uses. It is most often used to point to the
configuration file that you would like Ruff to use, for example:

```console
$ ruff check path/to/directory --config path/to/ruff.toml
```

However, the `--config` flag can also be used to provide arbitrary
overrides of configuration settings using TOML `<KEY> = <VALUE>` pairs.
This is mostly useful in situations where you wish to override a configuration setting
that does not have a dedicated command-line flag.

In the below example, the `--config` flag is the only way of overriding the
`dummy-variable-rgx` configuration setting from the command line,
since this setting has no dedicated CLI flag. The `per-file-ignores` setting
could also have been overridden via the `--per-file-ignores` dedicated flag,
but using `--config` to override the setting is also fine:

```console
$ ruff check path/to/file --config path/to/ruff.toml --config "lint.dummy-variable-rgx = '__.*'" --config "lint.per-file-ignores = {'some_file.py' = ['F841']}"
```

Configuration options passed to `--config` are parsed in the same way
as configuration options in a `ruff.toml` file.
As such, options specific to the Ruff linter need to be prefixed with `lint.`
(`--config "lint.dummy-variable-rgx = '__.*'"` rather than simply
`--config "dummy-variable-rgx = '__.*'"`), and options specific to the Ruff formatter
need to be prefixed with `format.`.

If a specific configuration option is simultaneously overridden by
a dedicated flag and by the `--config` flag, the dedicated flag
takes priority. In this example, the maximum permitted line length
will be set to 90, not 100:

```console
$ ruff format path/to/file --line-length=90 --config "line-length=100"
```

Specifying `--config "line-length=90"` will override the `line-length`
setting from *all* configuration files detected by Ruff,
including configuration files discovered in subdirectories.
In this respect, specifying `--config "line-length=90"` has
the same effect as specifying `--line-length=90`,
which will similarly override the `line-length` setting from
all configuration files detected by Ruff, regardless of where
a specific configuration file is located.

### Full command-line interface

See `ruff help` for the full list of Ruff's top-level commands:

<!-- Begin auto-generated command help. -->

```text
Ruff: An extremely fast Python linter and code formatter.

Usage: ruff [OPTIONS] <COMMAND>

Commands:
  check    Run Ruff on the given files or directories
  rule     Explain a rule (or all rules)
  config   List or describe the available configuration options
  linter   List all supported upstream linters
  clean    Clear any caches in the current directory and any subdirectories
  format   Run the Ruff formatter on the given files or directories
  server   Run the language server
  analyze  Run analysis over Python source code
  version  Display Ruff's version
  help     Print this message or the help of the given subcommand(s)

Options:
  -h, --help     Print help
  -V, --version  Print version

Log levels:
  -v, --verbose  Enable verbose logging
  -q, --quiet    Print diagnostics, but nothing else
  -s, --silent   Disable all logging (but still exit with status code "1" upon
                 detecting diagnostics)

Global options:
      --config <CONFIG_OPTION>
          Either a path to a TOML configuration file (`pyproject.toml` or
          `ruff.toml`), or a TOML `<KEY> = <VALUE>` pair (such as you might
          find in a `ruff.toml` configuration file) overriding a specific
          configuration option. Overrides of individual settings using this
          option always take precedence over all configuration files, including
          configuration files that were also specified using `--config`
      --isolated
          Ignore all configuration files

For help with a specific command, see: `ruff help <command>`.
```

<!-- End auto-generated command help. -->

Or `ruff help check` for more on the linting command:

<!-- Begin auto-generated check help. -->

```text
Run Ruff on the given files or directories

Usage: ruff check [OPTIONS] [FILES]...

Arguments:
  [FILES]...  List of files or directories to check [default: .]

Options:
      --fix
          Apply fixes to resolve lint violations. Use `--no-fix` to disable or
          `--unsafe-fixes` to include unsafe fixes
      --unsafe-fixes
          Include fixes that may not retain the original intent of the code.
          Use `--no-unsafe-fixes` to disable
      --show-fixes
          Show an enumeration of all fixed lint violations. Use
          `--no-show-fixes` to disable
      --diff
          Avoid writing any fixed files back; instead, output a diff for each
          changed file to stdout, and exit 0 if there are no diffs. Implies
          `--fix-only`
  -w, --watch
          Run in watch mode by re-running whenever files change
      --fix-only
          Apply fixes to resolve lint violations, but don't report on, or exit
          non-zero for, leftover violations. Implies `--fix`. Use
          `--no-fix-only` to disable or `--unsafe-fixes` to include unsafe
          fixes
      --ignore-noqa
          Ignore any `# noqa` comments
      --output-format <OUTPUT_FORMAT>
          Output serialization format for violations. The default serialization
          format is "full" [env: RUFF_OUTPUT_FORMAT=] [possible values:
          concise, full, json, json-lines, junit, grouped, github, gitlab,
          pylint, rdjson, azure, sarif]
  -o, --output-file <OUTPUT_FILE>
          Specify file to write the linter output to (default: stdout) [env:
          RUFF_OUTPUT_FILE=]
      --target-version <TARGET_VERSION>
          The minimum Python version that should be supported [possible values:
          py37, py38, py39, py310, py311, py312, py313, py314]
      --preview
          Enable preview mode; checks will include unstable rules and fixes.
          Use `--no-preview` to disable
      --extension <EXTENSION>
          List of mappings from file extension to language (one of `python`,
          `ipynb`, `pyi`). For example, to treat `.ipy` files as IPython
          notebooks, use `--extension ipy:ipynb`
      --statistics
          Show counts for every rule with at least one violation
      --add-noqa
          Enable automatic additions of `noqa` directives to failing lines
      --show-files
          See the files Ruff will be run against with the current settings
      --show-settings
          See the settings Ruff will use to lint a given Python file
  -h, --help
          Print help

Rule selection:
      --select <RULE_CODE>
          Comma-separated list of rule codes to enable (or ALL, to enable all
          rules)
      --ignore <RULE_CODE>
          Comma-separated list of rule codes to disable
      --extend-select <RULE_CODE>
          Like --select, but adds additional rule codes on top of those already
          specified
      --per-file-ignores <PER_FILE_IGNORES>
          List of mappings from file pattern to code to exclude
      --extend-per-file-ignores <EXTEND_PER_FILE_IGNORES>
          Like `--per-file-ignores`, but adds additional ignores on top of
          those already specified
      --fixable <RULE_CODE>
          List of rule codes to treat as eligible for fix. Only applicable when
          fix itself is enabled (e.g., via `--fix`)
      --unfixable <RULE_CODE>
          List of rule codes to treat as ineligible for fix. Only applicable
          when fix itself is enabled (e.g., via `--fix`)
      --extend-fixable <RULE_CODE>
          Like --fixable, but adds additional rule codes on top of those
          already specified

File selection:
      --exclude <FILE_PATTERN>
          List of paths, used to omit files and/or directories from analysis
      --extend-exclude <FILE_PATTERN>
          Like --exclude, but adds additional files and directories on top of
          those already excluded
      --respect-gitignore
          Respect file exclusions via `.gitignore` and other standard ignore
          files. Use `--no-respect-gitignore` to disable
      --force-exclude
          Enforce exclusions, even for paths passed to Ruff directly on the
          command-line. Use `--no-force-exclude` to disable

Miscellaneous:
  -n, --no-cache
          Disable cache reads [env: RUFF_NO_CACHE=]
      --cache-dir <CACHE_DIR>
          Path to the cache directory [env: RUFF_CACHE_DIR=]
      --stdin-filename <STDIN_FILENAME>
          The name of the file when passing it through stdin
  -e, --exit-zero
          Exit with status code "0", even upon detecting lint violations
      --exit-non-zero-on-fix
          Exit with a non-zero status code if any files were modified via fix,
          even if no lint violations remain

Log levels:
  -v, --verbose  Enable verbose logging
  -q, --quiet    Print diagnostics, but nothing else
  -s, --silent   Disable all logging (but still exit with status code "1" upon
                 detecting diagnostics)

Global options:
      --config <CONFIG_OPTION>
          Either a path to a TOML configuration file (`pyproject.toml` or
          `ruff.toml`), or a TOML `<KEY> = <VALUE>` pair (such as you might
          find in a `ruff.toml` configuration file) overriding a specific
          configuration option. Overrides of individual settings using this
          option always take precedence over all configuration files, including
          configuration files that were also specified using `--config`
      --isolated
          Ignore all configuration files
```

<!-- End auto-generated check help. -->

Or `ruff help format` for more on the formatting command:

<!-- Begin auto-generated format help. -->

```text
Run the Ruff formatter on the given files or directories

Usage: ruff format [OPTIONS] [FILES]...

Arguments:
  [FILES]...  List of files or directories to format [default: .]

Options:
      --check
          Avoid writing any formatted files back; instead, exit with a non-zero
          status code if any files would have been modified, and zero otherwise
      --diff
          Avoid writing any formatted files back; instead, exit with a non-zero
          status code and the difference between the current file and how the
          formatted file would look like
      --extension <EXTENSION>
          List of mappings from file extension to language (one of `python`,
          `ipynb`, `pyi`). For example, to treat `.ipy` files as IPython
          notebooks, use `--extension ipy:ipynb`
      --target-version <TARGET_VERSION>
          The minimum Python version that should be supported [possible values:
          py37, py38, py39, py310, py311, py312, py313, py314]
      --preview
          Enable preview mode; enables unstable formatting. Use `--no-preview`
          to disable
  -h, --help
          Print help (see more with '--help')

Miscellaneous:
  -n, --no-cache
          Disable cache reads [env: RUFF_NO_CACHE=]
      --cache-dir <CACHE_DIR>
          Path to the cache directory [env: RUFF_CACHE_DIR=]
      --stdin-filename <STDIN_FILENAME>
          The name of the file when passing it through stdin
      --exit-non-zero-on-format
          Exit with a non-zero status code if any files were modified via
          format, even if all files were formatted successfully

File selection:
      --respect-gitignore
          Respect file exclusions via `.gitignore` and other standard ignore
          files. Use `--no-respect-gitignore` to disable
      --exclude <FILE_PATTERN>
          List of paths, used to omit files and/or directories from analysis
      --force-exclude
          Enforce exclusions, even for paths passed to Ruff directly on the
          command-line. Use `--no-force-exclude` to disable

Format configuration:
      --line-length <LINE_LENGTH>  Set the line-length

Editor options:
      --range <RANGE>  When specified, Ruff will try to only format the code in
                       the given range.
                       It might be necessary to extend the start backwards or
                       the end forwards, to fully enclose a logical line.
                       The `<RANGE>` uses the format
                       `<start_line>:<start_column>-<end_line>:<end_column>`.

Log levels:
  -v, --verbose  Enable verbose logging
  -q, --quiet    Print diagnostics, but nothing else
  -s, --silent   Disable all logging (but still exit with status code "1" upon
                 detecting diagnostics)

Global options:
      --config <CONFIG_OPTION>
          Either a path to a TOML configuration file (`pyproject.toml` or
          `ruff.toml`), or a TOML `<KEY> = <VALUE>` pair (such as you might
          find in a `ruff.toml` configuration file) overriding a specific
          configuration option. Overrides of individual settings using this
          option always take precedence over all configuration files, including
          configuration files that were also specified using `--config`
      --isolated
          Ignore all configuration files
```

<!-- End auto-generated format help. -->

## Shell autocompletion

Ruff supports autocompletion for most shells. A shell-specific completion script can be generated
by `ruff generate-shell-completion <SHELL>`, where `<SHELL>` is one of `bash`, `elvish`, `fig`, `fish`,
`powershell`, or `zsh`.

The exact steps required to enable autocompletion will vary by shell. For example instructions,
see the [Poetry](https://python-poetry.org/docs/#enable-tab-completion-for-bash-fish-or-zsh) or
[ripgrep](https://github.com/BurntSushi/ripgrep/blob/master/FAQ.md#complete) documentation.

As an example: to enable autocompletion for Zsh, run
`ruff generate-shell-completion zsh > ~/.zfunc/_ruff`. Then add the following line to your
`~/.zshrc` file, if they're not already present:

```zsh
fpath+=~/.zfunc
autoload -Uz compinit && compinit
```
````

## File: docs/faq.md
````markdown
# FAQ

## Is the Ruff linter compatible with Black?

Yes. The Ruff linter is compatible with [Black](https://github.com/psf/black) out-of-the-box, as
long as the [`line-length`](settings.md#line-length) setting is consistent between the two.

Ruff is designed to be used alongside a formatter (like Ruff's own formatter, or Black) and, as
such, will defer implementing stylistic rules that are obviated by automated formatting.

Note that Ruff's linter and Black treat line-length enforcement a little differently. Black, like
Ruff's formatter, makes a best-effort attempt to adhere to the
[`line-length`](settings.md#line-length), but avoids automatic line-wrapping in some cases (e.g.,
within comments). Ruff, on the other hand, will flag [`line-too-long`](rules/line-too-long.md)
(`E501`) for any line that exceeds the [`line-length`](settings.md#line-length) setting. As such, if
[`line-too-long`](rules/line-too-long.md) (`E501`) is enabled, Ruff can still trigger line-length
violations even when Black or `ruff format` is enabled.

## How does Ruff's formatter compare to Black?

The Ruff formatter is designed to be a drop-in replacement for [Black](https://github.com/psf/black).

Specifically, the formatter is intended to emit near-identical output when run over Black-formatted
code. When run over extensive Black-formatted projects like Django and Zulip, > 99.9% of lines
are formatted identically. When migrating an existing project from Black to Ruff, you should expect
to see a few differences on the margins, but the vast majority of your code should be unchanged.

When run over _non_-Black-formatted code, the formatter makes some different decisions than Black,
and so more deviations should be expected, especially around the treatment of end-of-line comments.

See [_Style Guide_](formatter.md#style-guide) for more.

## How does Ruff's linter compare to Flake8?

Ruff can be used as a drop-in replacement for Flake8 when used (1) without or with a small number of
plugins, (2) alongside Black, and (3) on Python 3 code.

Under those conditions, Ruff implements every rule in Flake8. In practice, that means Ruff
implements all of the `F` rules (which originate from Pyflakes), along with a subset of the `E` and
`W` rules (which originate from pycodestyle).

Ruff also re-implements some of the most popular Flake8 plugins and related code quality tools
natively, including:

- [autoflake](https://pypi.org/project/autoflake/)
- [eradicate](https://pypi.org/project/eradicate/)
- [flake8-2020](https://pypi.org/project/flake8-2020/)
- [flake8-annotations](https://pypi.org/project/flake8-annotations/)
- [flake8-async](https://pypi.org/project/flake8-async)
- [flake8-bandit](https://pypi.org/project/flake8-bandit/) ([#1646](https://github.com/astral-sh/ruff/issues/1646))
- [flake8-blind-except](https://pypi.org/project/flake8-blind-except/)
- [flake8-boolean-trap](https://pypi.org/project/flake8-boolean-trap/)
- [flake8-bugbear](https://pypi.org/project/flake8-bugbear/)
- [flake8-builtins](https://pypi.org/project/flake8-builtins/)
- [flake8-commas](https://pypi.org/project/flake8-commas/)
- [flake8-comprehensions](https://pypi.org/project/flake8-comprehensions/)
- [flake8-copyright](https://pypi.org/project/flake8-copyright/)
- [flake8-datetimez](https://pypi.org/project/flake8-datetimez/)
- [flake8-debugger](https://pypi.org/project/flake8-debugger/)
- [flake8-django](https://pypi.org/project/flake8-django/)
- [flake8-docstrings](https://pypi.org/project/flake8-docstrings/)
- [flake8-eradicate](https://pypi.org/project/flake8-eradicate/)
- [flake8-errmsg](https://pypi.org/project/flake8-errmsg/)
- [flake8-executable](https://pypi.org/project/flake8-executable/)
- [flake8-gettext](https://pypi.org/project/flake8-gettext/)
- [flake8-implicit-str-concat](https://pypi.org/project/flake8-implicit-str-concat/)
- [flake8-import-conventions](https://pypi.org/project/flake8-import-conventions/)
- [flake8-logging](https://pypi.org/project/flake8-logging-format/)
- [flake8-logging-format](https://pypi.org/project/flake8-logging-format/)
- [flake8-no-pep420](https://pypi.org/project/flake8-no-pep420)
- [flake8-pie](https://pypi.org/project/flake8-pie/)
- [flake8-print](https://pypi.org/project/flake8-print/)
- [flake8-pyi](https://pypi.org/project/flake8-pyi/)
- [flake8-pytest-style](https://pypi.org/project/flake8-pytest-style/)
- [flake8-quotes](https://pypi.org/project/flake8-quotes/)
- [flake8-raise](https://pypi.org/project/flake8-raise/)
- [flake8-return](https://pypi.org/project/flake8-return/)
- [flake8-self](https://pypi.org/project/flake8-self/)
- [flake8-simplify](https://pypi.org/project/flake8-simplify/)
- [flake8-slots](https://pypi.org/project/flake8-slots/)
- [flake8-super](https://pypi.org/project/flake8-super/)
- [flake8-tidy-imports](https://pypi.org/project/flake8-tidy-imports/)
- [flake8-todos](https://pypi.org/project/flake8-todos/)
- [flake8-type-checking](https://pypi.org/project/flake8-type-checking/)
- [flake8-use-pathlib](https://pypi.org/project/flake8-use-pathlib/)
- [flynt](https://pypi.org/project/flynt/) ([#2102](https://github.com/astral-sh/ruff/issues/2102))
- [isort](https://pypi.org/project/isort/)
- [mccabe](https://pypi.org/project/mccabe/)
- [pandas-vet](https://pypi.org/project/pandas-vet/)
- [pep8-naming](https://pypi.org/project/pep8-naming/)
- [perflint](https://pypi.org/project/perflint/) ([#4789](https://github.com/astral-sh/ruff/issues/4789))
- [pydocstyle](https://pypi.org/project/pydocstyle/)
- [pygrep-hooks](https://github.com/pre-commit/pygrep-hooks)
- [pyupgrade](https://pypi.org/project/pyupgrade/)
- [tryceratops](https://pypi.org/project/tryceratops/)
- [yesqa](https://pypi.org/project/yesqa/)

Note that, in some cases, Ruff uses different rule codes and prefixes than would be found in the
originating Flake8 plugins. For example, Ruff uses `TID252` to represent the `I252` rule from
flake8-tidy-imports. This helps minimize conflicts across plugins and allows any individual plugin
to be toggled on or off with a single (e.g.) `--select TID`, as opposed to `--select I2` (to avoid
conflicts with the isort rules, like `I001`).

Beyond the rule set, Ruff's primary limitation vis-à-vis Flake8 is that it does not support custom
lint rules. (Instead, popular Flake8 plugins are re-implemented in Rust as part of Ruff itself.)
One minor difference is that Ruff doesn't include all the 'opinionated' rules from flake8-bugbear.

## How does Ruff's linter compare to Pylint?

At time of writing, Pylint implements ~409 total rules, while Ruff implements over 800, of which at
least 209 overlap with the Pylint rule set (see: [#970](https://github.com/astral-sh/ruff/issues/970)).

Pylint implements many rules that Ruff does not, and vice versa. For example, Pylint does more type
inference than Ruff (e.g., Pylint can validate the number of arguments in a function call). As such,
Ruff is not a "pure" drop-in replacement for Pylint (and vice versa), as they enforce different sets
of rules.

Despite these differences, many users have successfully switched from Pylint to Ruff, especially
those using Ruff alongside a [type checker](faq.md#how-does-ruff-compare-to-mypy-or-pyright-or-pyre),
which can cover some of the functionality that Pylint provides.

Like Flake8, Pylint supports plugins (called "checkers"), while Ruff implements all rules natively
and does not support custom or third-party rules. Unlike Pylint, Ruff is capable of automatically
fixing its own lint violations.

In some cases, Ruff's rules may yield slightly different results than their Pylint counterparts. For
example, Ruff's [`too-many-branches`](rules/too-many-branches.md) does not count `try` blocks as
their own branches, unlike Pylint's `R0912`. Ruff's `PL` rule group also includes a small number of
rules from Pylint _extensions_ (like [`magic-value-comparison`](rules/magic-value-comparison.md)),
which need to be explicitly activated when using Pylint. By enabling Ruff's `PL` group, you may
see violations for rules that weren't previously enabled through your Pylint configuration.

Pylint parity is being tracked in [#970](https://github.com/astral-sh/ruff/issues/970).

## How does Ruff compare to Mypy, or Pyright, or Pyre?

Ruff is a linter, not a type checker. It can detect some of the same problems that a type checker
can, but a type checker will catch certain errors that Ruff would miss. The opposite is also true:
Ruff will catch certain errors that a type checker would typically ignore.

For example, unlike a type checker, Ruff will notify you if an import is unused, by looking for
references to that import in the source code; on the other hand, a type checker could flag that you
passed an integer argument to a function that expects a string, which Ruff would miss. The
tools are complementary.

It's recommended that you use Ruff in conjunction with a type checker, like Mypy, Pyright, or Pyre,
with Ruff providing faster feedback on lint violations and the type checker providing more detailed
feedback on type errors.

## Which tools does Ruff replace?

Today, Ruff can be used to replace Flake8 when used with any of the following plugins:

- [flake8-2020](https://pypi.org/project/flake8-2020/)
- [flake8-annotations](https://pypi.org/project/flake8-annotations/)
- [flake8-async](https://pypi.org/project/flake8-async)
- [flake8-bandit](https://pypi.org/project/flake8-bandit/) ([#1646](https://github.com/astral-sh/ruff/issues/1646))
- [flake8-blind-except](https://pypi.org/project/flake8-blind-except/)
- [flake8-boolean-trap](https://pypi.org/project/flake8-boolean-trap/)
- [flake8-bugbear](https://pypi.org/project/flake8-bugbear/)
- [flake8-builtins](https://pypi.org/project/flake8-builtins/)
- [flake8-commas](https://pypi.org/project/flake8-commas/)
- [flake8-comprehensions](https://pypi.org/project/flake8-comprehensions/)
- [flake8-copyright](https://pypi.org/project/flake8-copyright/)
- [flake8-datetimez](https://pypi.org/project/flake8-datetimez/)
- [flake8-debugger](https://pypi.org/project/flake8-debugger/)
- [flake8-django](https://pypi.org/project/flake8-django/)
- [flake8-docstrings](https://pypi.org/project/flake8-docstrings/)
- [flake8-eradicate](https://pypi.org/project/flake8-eradicate/)
- [flake8-errmsg](https://pypi.org/project/flake8-errmsg/)
- [flake8-executable](https://pypi.org/project/flake8-executable/)
- [flake8-gettext](https://pypi.org/project/flake8-gettext/)
- [flake8-implicit-str-concat](https://pypi.org/project/flake8-implicit-str-concat/)
- [flake8-import-conventions](https://pypi.org/project/flake8-import-conventions/)
- [flake8-logging](https://pypi.org/project/flake8-logging/)
- [flake8-logging-format](https://pypi.org/project/flake8-logging-format/)
- [flake8-no-pep420](https://pypi.org/project/flake8-no-pep420)
- [flake8-pie](https://pypi.org/project/flake8-pie/)
- [flake8-print](https://pypi.org/project/flake8-print/)
- [flake8-pytest-style](https://pypi.org/project/flake8-pytest-style/)
- [flake8-quotes](https://pypi.org/project/flake8-quotes/)
- [flake8-raise](https://pypi.org/project/flake8-raise/)
- [flake8-return](https://pypi.org/project/flake8-return/)
- [flake8-self](https://pypi.org/project/flake8-self/)
- [flake8-simplify](https://pypi.org/project/flake8-simplify/)
- [flake8-slots](https://pypi.org/project/flake8-slots/)
- [flake8-super](https://pypi.org/project/flake8-super/)
- [flake8-tidy-imports](https://pypi.org/project/flake8-tidy-imports/)
- [flake8-todos](https://pypi.org/project/flake8-todos/)
- [flake8-type-checking](https://pypi.org/project/flake8-type-checking/)
- [flake8-use-pathlib](https://pypi.org/project/flake8-use-pathlib/)
- [flynt](https://pypi.org/project/flynt/) ([#2102](https://github.com/astral-sh/ruff/issues/2102))
- [mccabe](https://pypi.org/project/mccabe/)
- [pandas-vet](https://pypi.org/project/pandas-vet/)
- [pep8-naming](https://pypi.org/project/pep8-naming/)
- [perflint](https://pypi.org/project/perflint/) ([#4789](https://github.com/astral-sh/ruff/issues/4789))
- [pydocstyle](https://pypi.org/project/pydocstyle/)
- [tryceratops](https://pypi.org/project/tryceratops/)

Ruff can also replace [Black](https://pypi.org/project/black/), [isort](https://pypi.org/project/isort/),
[yesqa](https://pypi.org/project/yesqa/), [eradicate](https://pypi.org/project/eradicate/), and
most of the rules implemented in [pyupgrade](https://pypi.org/project/pyupgrade/).

If you're looking to use Ruff, but rely on an unsupported Flake8 plugin, feel free to file an
[issue](https://github.com/astral-sh/ruff/issues/new).

## Do I have to use Ruff's linter and formatter together?

Nope! Ruff's linter and formatter can be used independently of one another -- you can use
Ruff as a formatter, but not a linter, or vice versa.

## What versions of Python does Ruff support?

Ruff can lint code for any Python version from 3.7 onwards, including Python 3.13.

Ruff does not support Python 2. Ruff _may_ run on pre-Python 3.7 code, although such versions
are not officially supported (e.g., Ruff does _not_ respect type comments).

Ruff is installable under any Python version from 3.7 onwards.

## Do I need to install Rust to use Ruff?

Nope! Ruff is available as [`ruff`](https://pypi.org/project/ruff/) on PyPI. We recommend installing Ruff with [uv](https://docs.astral.sh/uv/),
though it's also installable with `pip`, `pipx`, and a [variety of other package managers](installation.md):

```console
$ # Install Ruff globally.
$ uv tool install ruff@latest

$ # Or add Ruff to your project.
$ uv add --dev ruff

$ # With pip.
$ pip install ruff

$ # With pipx.
$ pipx install ruff
```

Starting with version `0.5.0`, Ruff can also be installed with our standalone installers:

```console
$ # On macOS and Linux.
$ curl -LsSf https://astral.sh/ruff/install.sh | sh

$ # On Windows.
$ powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"

$ # For a specific version.
$ curl -LsSf https://astral.sh/ruff/0.5.0/install.sh | sh
$ powershell -c "irm https://astral.sh/ruff/0.5.0/install.ps1 | iex"
```

Ruff ships with wheels for all major platforms, which enables `uv`, `pip`, and other tools to install Ruff without
relying on a Rust toolchain at all.

## Can I write my own linter plugins for Ruff?

Ruff does not yet support third-party plugins, though a plugin system is within-scope for the
project. See [#283](https://github.com/astral-sh/ruff/issues/283) for more.

## How does Ruff's import sorting compare to [isort](https://pypi.org/project/isort/)?

Ruff's import sorting is intended to be near-equivalent to isort's when using isort's
`profile = "black"`.

There are a few known differences in how Ruff and isort treat aliased imports, and in how Ruff and
isort treat inline comments in some cases (see: [#1381](https://github.com/astral-sh/ruff/issues/1381),
[#2104](https://github.com/astral-sh/ruff/issues/2104)).

For example, Ruff tends to group non-aliased imports from the same module:

```python
from numpy import cos, int8, int16, int32, int64, tan, uint8, uint16, uint32, uint64
from numpy import sin as np_sin
```

Whereas isort splits them into separate import statements at each aliased boundary:

```python
from numpy import cos, int8, int16, int32, int64
from numpy import sin as np_sin
from numpy import tan, uint8, uint16, uint32, uint64
```

Ruff also correctly classifies some modules as standard-library that aren't recognized
by isort, like `_string` and `idlelib`.

Like isort, Ruff's import sorting is compatible with Black.

## How does Ruff determine which of my imports are first-party, third-party, etc.?

Ruff accepts a `src` option that in your `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file,
specifies the directories that Ruff should consider when determining whether an import is
first-party.

For example, if you have a project with the following structure:

```tree
my_project
├── pyproject.toml
└── src
    └── foo
        ├── __init__.py
        └── bar
            ├── __init__.py
            └── baz.py
```

When Ruff sees an import like `import foo`, it will then iterate over the `src` directories,
looking for a corresponding Python module (in reality, a directory named `foo` or a file named
`foo.py`). For module paths with multiple components like `import foo.bar`,
the default behavior is to search only for a directory named `foo` or a file
named `foo.py`. However, if `preview` is enabled, Ruff will require that the full relative path `foo/bar` exists as a directory, or that `foo/bar.py` or `foo/bar.pyi` exist as files. Finally, imports of the form `from foo import bar`, Ruff will only use `foo` when determining whether a module is first-party or third-party. 

If there is a directory
whose name matches a third-party package, but does not contain Python code,
it could happen that the above algorithm incorrectly infers an import to be first-party.
To prevent this, you can modify the [`known-third-party`](settings.md#lint_isort_known-third-party) setting. For example, if you import
the package `wandb` but also have a subdirectory of your `src` with
the same name, you can add the following:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint.isort]
    known-third-party = ["wandb"]
    ```

=== "ruff.toml"

    ```toml
    [lint.isort]
    known-third-party = ["wandb"]
    ```


If the `src` field is omitted, Ruff will default to using the "project root", along with a `"src"`
subdirectory, as the first-party sources, to support both flat and nested project layouts.
The "project root" is typically the directory containing your `pyproject.toml`, `ruff.toml`, or
`.ruff.toml` file, unless a configuration file is provided on the command-line via the `--config`
option, in which case, the current working directory is used as the project root.

In this case, Ruff would check the `"src"` directory by default, but we can configure it as an
explicit, exclusive first-party source like so:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    # Ruff supports a top-level `src` option in lieu of isort's `src_paths` setting.
    # All paths are relative to the project root, which is the directory containing the pyproject.toml.
    src = ["src"]
    ```

=== "ruff.toml"

    ```toml
    # Ruff supports a top-level `src` option in lieu of isort's `src_paths` setting.
    # All paths are relative to the project root, which is the directory containing the pyproject.toml.
    src = ["src"]
    ```

If your `pyproject.toml`, `ruff.toml`, or `.ruff.toml` extends another configuration file, Ruff
will still use the directory containing your `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file as
the project root (as opposed to the directory of the file pointed to via the `extends` option).

For example, if you add a configuration file to the `tests` directory in the above example, you'll
want to explicitly set the `src` option in the extended configuration file:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    extend = "../pyproject.toml"
    src = ["../src"]
    ```

=== "ruff.toml"

    ```toml
    extend = "../pyproject.toml"
    src = ["../src"]
    ```

Beyond this `src`-based detection, Ruff will also attempt to determine the current Python package
for a given Python file, and mark imports from within the same package as first-party. For example,
above, `baz.py` would be identified as part of the Python package beginning at
`./my_project/src/foo`, and so any imports in `baz.py` that begin with `foo` (like `import foo.bar`)
would be considered first-party based on this same-package heuristic.

For a detailed explanation of `src` resolution, see the [contributing guide](contributing.md).

Ruff can also be configured to treat certain modules as (e.g.) always first-party, regardless of
their location on the filesystem. For example, you can set [`known-first-party`](settings.md#lint_isort_known-first-party)
like so:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    src = ["src", "tests"]

    [tool.ruff.lint]
    select = [
        # Pyflakes
        "F",
        # Pycodestyle
        "E",
        "W",
        # isort
        "I001"
    ]

    [tool.ruff.lint.isort]
    known-first-party = ["my_module1", "my_module2"]
    ```

=== "ruff.toml"

    ```toml
    src = ["src", "tests"]

    [lint]
    select = [
        # Pyflakes
        "F",
        # Pycodestyle
        "E",
        "W",
        # isort
        "I001"
    ]

    [lint.isort]
    known-first-party = ["my_module1", "my_module2"]
    ```

Ruff does not yet support all of isort's configuration options, though it does support many of
them. You can find the supported settings in the [API reference](settings.md#lintisort).

## Does Ruff support Jupyter Notebooks?

Ruff has built-in support for linting and formatting [Jupyter Notebooks](https://jupyter.org/). Refer to the
[Jupyter Notebook section](configuration.md#jupyter-notebook-discovery) for more details.

Ruff also integrates with [nbQA](https://github.com/nbQA-dev/nbQA), a tool for running linters and
code formatters over Jupyter Notebooks.

After installing `ruff` and `nbqa`, you can run Ruff over a notebook like so:

```console
$ nbqa ruff Untitled.ipynb
Untitled.ipynb:cell_1:2:5: F841 Local variable `x` is assigned to but never used
Untitled.ipynb:cell_2:1:1: E402 Module level import not at top of file
Untitled.ipynb:cell_2:1:8: F401 `os` imported but unused
Found 3 errors.
1 potentially fixable with the --fix option.
```

## Does Ruff support NumPy- or Google-style docstrings?

Yes! To enforce a docstring convention, add a [`convention`](settings.md#lint_pydocstyle_convention)
setting following to your configuration file:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint.pydocstyle]
    convention = "google"  # Accepts: "google", "numpy", or "pep257".
    ```

=== "ruff.toml"

    ```toml
    [lint.pydocstyle]
    convention = "google"  # Accepts: "google", "numpy", or "pep257".
    ```

For example, if you're coming from flake8-docstrings, and your originating configuration uses
`--docstring-convention=numpy`, you'd instead set `convention = "numpy"` in your `pyproject.toml`,
as above.

Alongside [`convention`](settings.md#lint_pydocstyle_convention), you'll want to
explicitly enable the `D` rule code prefix, since the `D` rules are not enabled by default:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    select = ["D"]

    [tool.ruff.lint.pydocstyle]
    convention = "google"
    ```

=== "ruff.toml"

    ```toml
    [lint]
    select = ["D"]

    [lint.pydocstyle]
    convention = "google"
    ```

Enabling a [`convention`](settings.md#lint_pydocstyle_convention) will disable any rules that are not
included in the specified convention. As such, the intended workflow is to enable a convention and
then selectively enable or disable any additional rules on top of it:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    select = [
        "D",
        # Augment the convention by requiring an imperative mood for all docstrings.
        "D401",
    ]

    ignore = [
        # Relax the convention by _not_ requiring documentation for every function parameter.
        "D417",
    ]

    [tool.ruff.lint.pydocstyle]
    convention = "google"
    ```

=== "ruff.toml"

    ```toml
    [lint]
    select = [
        "D",
        # Augment the convention by requiring an imperative mood for all docstrings.
        "D401",
    ]

    ignore = [
        # Relax the convention by _not_ requiring documentation for every function parameter.
        "D417",
    ]

    [lint.pydocstyle]
    convention = "google"
    ```

The PEP 257 convention includes all `D` errors apart from:
[`D203`](rules/incorrect-blank-line-before-class.md),
[`D212`](rules/multi-line-summary-first-line.md),
[`D213`](rules/multi-line-summary-second-line.md),
[`D214`](rules/overindented-section.md),
[`D215`](rules/overindented-section-underline.md),
[`D404`](rules/docstring-starts-with-this.md),
[`D405`](rules/non-capitalized-section-name.md),
[`D406`](rules/missing-new-line-after-section-name.md),
[`D407`](rules/missing-dashed-underline-after-section.md),
[`D408`](rules/missing-section-underline-after-name.md),
[`D409`](rules/mismatched-section-underline-length.md),
[`D410`](rules/no-blank-line-after-section.md),
[`D411`](rules/no-blank-line-before-section.md),
[`D413`](rules/no-blank-line-after-section.md),
[`D415`](rules/missing-terminal-punctuation.md),
[`D416`](rules/missing-section-name-colon.md), and
[`D417`](rules/undocumented-param.md).

The NumPy convention includes all `D` errors apart from:
[`D107`](rules/undocumented-public-init.md),
[`D203`](rules/incorrect-blank-line-before-class.md),
[`D212`](rules/multi-line-summary-first-line.md),
[`D213`](rules/multi-line-summary-second-line.md),
[`D402`](rules/signature-in-docstring.md),
[`D413`](rules/no-blank-line-after-section.md),
[`D415`](rules/missing-terminal-punctuation.md),
[`D416`](rules/missing-section-name-colon.md), and
[`D417`](rules/undocumented-param.md).

The Google convention includes all `D` errors apart from:
[`D203`](rules/incorrect-blank-line-before-class.md),
[`D204`](rules/incorrect-blank-line-after-class.md),
[`D213`](rules/multi-line-summary-second-line.md),
[`D215`](rules/overindented-section-underline.md),
[`D400`](rules/missing-trailing-period.md),
[`D401`](rules/non-imperative-mood.md),
[`D404`](rules/docstring-starts-with-this.md),
[`D406`](rules/missing-new-line-after-section-name.md),
[`D407`](rules/missing-dashed-underline-after-section.md),
[`D408`](rules/missing-section-underline-after-name.md),
[`D409`](rules/mismatched-section-underline-length.md), and
[`D413`](rules/no-blank-line-after-section.md).

By default, no [`convention`](settings.md#lint_pydocstyle_convention) is set, and so the enabled rules
are determined by the [`select`](settings.md#lint_select) setting alone.

## What is "preview"?

Preview enables a collection of newer rules and fixes that are considered experimental or unstable.
See the [preview documentation](preview.md) for more details; or, to see which rules are currently
in preview, visit the [rules reference](rules.md).

## How can I tell what settings Ruff is using to check my code?

Run `ruff check /path/to/code.py --show-settings` to view the resolved settings for a given file.

## I want to use Ruff, but I don't want to use `pyproject.toml`. What are my options?

In lieu of a `pyproject.toml` file, you can use a `ruff.toml` file for configuration. The two
files are functionally equivalent and have an identical schema, with the exception that a `ruff.toml`
file can omit the `[tool.ruff]` section header. For example:

=== "pyproject.toml"

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint.pydocstyle]
convention = "google"
```

=== "ruff.toml"

```toml
line-length = 88

[lint.pydocstyle]
convention = "google"
```

Ruff doesn't currently support INI files, like `setup.cfg` or `tox.ini`.

## How can I change Ruff's default configuration?

When no configuration file is found, Ruff will look for a user-specific `ruff.toml` file as a
last resort. This behavior is similar to Flake8's `~/.config/flake8`.

On macOS and Linux, Ruff expects that file to be located at `~/.config/ruff/ruff.toml`,
and respects the `XDG_CONFIG_HOME` specification.

On Windows, Ruff expects that file to be located at `~\AppData\Roaming\ruff\ruff.toml`.

!!! note
    Prior to `v0.5.0`, Ruff would read user-specific configuration from
    `~/Library/Application Support/ruff/ruff.toml` on macOS. While Ruff will still respect
    such configuration files, the use of `~/Library/Application Support` is considered deprecated.

For more, see the [`etcetera`](https://crates.io/crates/etcetera) crate.

## Ruff tried to fix something — but it broke my code. What's going on?

Ruff labels fixes as "safe" and "unsafe". By default, Ruff will fix all violations for which safe
fixes are available, while unsafe fixes can be enabled via the [`unsafe-fixes`](settings.md#unsafe-fixes)
setting, or passing the [`--unsafe-fixes`](settings.md#unsafe-fixes) flag to `ruff check`. For
more, see [the fix documentation](linter.md#fixes).

Even still, given the dynamic nature of Python, it's difficult to have _complete_ certainty when
making changes to code, even for seemingly trivial fixes. If a "safe" fix breaks your code, please
[file an Issue](https://github.com/astral-sh/ruff/issues/new).

## How can I disable/force Ruff's color output?

Ruff's color output is powered by the [`colored`](https://crates.io/crates/colored) crate, which
attempts to automatically detect whether the output stream supports color. However, you can force
colors off by setting the `NO_COLOR` environment variable to any value (e.g., `NO_COLOR=1`), or
force colors on by setting `FORCE_COLOR` to any non-empty value (e.g., `FORCE_COLOR=1`).

[`colored`](https://crates.io/crates/colored) also supports the `CLICOLOR` and `CLICOLOR_FORCE`
environment variables (see the [spec](https://bixense.com/clicolors/)).

## Ruff behaves unexpectedly when using `source.*` code actions in Notebooks. What's going on? {: #source-code-actions-in-notebooks }

Ruff does not support `source.organizeImports` and `source.fixAll` code actions in Jupyter Notebooks
(`notebook.codeActionsOnSave` in VS Code). It's recommended to use the `notebook` prefixed code
actions for the same such as `notebook.source.organizeImports` and `notebook.source.fixAll`
respectively.

Ruff requires to have a full view of the notebook to provide accurate diagnostics and fixes. For
example, if you have a cell that imports a module and another cell that uses that module, Ruff
needs to see both cells to mark the import as used. If Ruff were to only see one cell at a time,
it would incorrectly mark the import as unused.

When using the `source.*` code actions for a Notebook, Ruff will be asked to fix any issues for each
cell in parallel, which can lead to unexpected behavior. For example, if a user has configured to
run `source.organizeImports` code action on save for a Notebook, Ruff will attempt to fix the
imports for the entire notebook corresponding to each cell. This leads to the client making the same
changes to the notebook multiple times, which can lead to unexpected behavior
([astral-sh/ruff-vscode#680](https://github.com/astral-sh/ruff-vscode/issues/680),
[astral-sh/ruff-vscode#640](https://github.com/astral-sh/ruff-vscode/issues/640),
[astral-sh/ruff-vscode#391](https://github.com/astral-sh/ruff-vscode/issues/391)).
````

## File: docs/formatter.md
````markdown
# The Ruff Formatter

The Ruff formatter is an extremely fast Python code formatter designed as a drop-in replacement for
[Black](https://pypi.org/project/black/), available as part of the `ruff` CLI via `ruff format`.

## `ruff format`

`ruff format` is the primary entrypoint to the formatter. It accepts a list of files or
directories, and formats all discovered Python files:

```shell
ruff format                   # Format all files in the current directory.
ruff format path/to/code/     # Format all files in `path/to/code` (and any subdirectories).
ruff format path/to/file.py   # Format a single file.
```

Similar to Black, running `ruff format /path/to/file.py` will format the given file or directory
in-place, while `ruff format --check /path/to/file.py` will avoid writing any formatted files back,
and instead exit with a non-zero status code upon detecting any unformatted files.

For the full list of supported options, run `ruff format --help`.

## Philosophy

The initial goal of the Ruff formatter is _not_ to innovate on code style, but rather, to innovate
on performance, and provide a unified toolchain across Ruff's linter, formatter, and any and all
future tools.

As such, the formatter is designed as a drop-in replacement for [Black](https://github.com/psf/black),
but with an excessive focus on performance and direct integration with Ruff. Given Black's
popularity within the Python ecosystem, targeting Black compatibility ensures that formatter
adoption is minimally disruptive for the vast majority of projects.

Specifically, the formatter is intended to emit near-identical output when run over existing
Black-formatted code. When run over extensive Black-formatted projects like Django and Zulip, > 99.9%
of lines are formatted identically. (See: [_Style Guide_](#style-guide).)

Given this focus on Black compatibility, the formatter thus adheres to [Black's (stable) code style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html),
which aims for "consistency, generality, readability and reducing git diffs". To give you a sense
for the enforced code style, here's an example:

```python
# Input
def _make_ssl_transport(
    rawsock, protocol, sslcontext, waiter=None,
    *, server_side=False, server_hostname=None,
    extra=None, server=None,
    ssl_handshake_timeout=None,
    call_connection_made=True):
    '''Make an SSL transport.'''
    if waiter is None:
      waiter = Future(loop=loop)

    if extra is None:
      extra = {}

    ...

# Ruff
def _make_ssl_transport(
    rawsock,
    protocol,
    sslcontext,
    waiter=None,
    *,
    server_side=False,
    server_hostname=None,
    extra=None,
    server=None,
    ssl_handshake_timeout=None,
    call_connection_made=True,
):
    """Make an SSL transport."""
    if waiter is None:
        waiter = Future(loop=loop)

    if extra is None:
        extra = {}

    ...
```

Like Black, the Ruff formatter does _not_ support extensive code style configuration; however,
unlike Black, it _does_ support configuring the desired quote style, indent style, line endings,
and more. (See: [_Configuration_](#configuration).)

While the formatter is designed to be a drop-in replacement for Black, it is not intended to be
used interchangeably with Black on an ongoing basis, as the formatter _does_ differ from
Black in a few conscious ways (see: [_Known deviations_](formatter/black.md)). In general,
deviations are limited to cases in which Ruff's behavior was deemed more consistent, or
significantly simpler to support (with negligible end-user impact) given the differences in the
underlying implementations between Black and Ruff.

Going forward, the Ruff Formatter will support Black's preview style under Ruff's own
[preview](preview.md) mode.

## Configuration

The Ruff Formatter exposes a small set of configuration options, some of which are also supported
by Black (like line width), some of which are unique to Ruff (like quote, indentation style and
formatting code examples in docstrings).

For example, to configure the formatter to use single quotes, format code
examples in docstrings, a line width of 100, and tab indentation, add the
following to your configuration file:

=== "pyproject.toml"

    ```toml
    [tool.ruff]
    line-length = 100

    [tool.ruff.format]
    quote-style = "single"
    indent-style = "tab"
    docstring-code-format = true
    ```

=== "ruff.toml"

    ```toml
    line-length = 100

    [format]
    quote-style = "single"
    indent-style = "tab"
    docstring-code-format = true
    ```


For the full list of supported settings, see [_Settings_](settings.md#format). For more on
configuring Ruff via `pyproject.toml`, see [_Configuring Ruff_](configuration.md).

Given the focus on Black compatibility (and unlike formatters like [YAPF](https://github.com/google/yapf)),
Ruff does not currently expose any other configuration options.

## Docstring formatting

The Ruff formatter provides an opt-in feature for automatically formatting
Python code examples in docstrings. The Ruff formatter currently recognizes
code examples in the following formats:

* The Python [doctest] format.
* CommonMark [fenced code blocks] with the following info strings: `python`,
`py`, `python3`, or `py3`. Fenced code blocks without an info string are
assumed to be Python code examples and also formatted.
* reStructuredText [literal blocks]. While literal blocks may contain things
other than Python, this is meant to reflect a long-standing convention in the
Python ecosystem where literal blocks often contain Python code.
* reStructuredText [`code-block` and `sourcecode` directives]. As with
Markdown, the language names recognized for Python are `python`, `py`,
`python3`, or `py3`.

If a code example is recognized and treated as Python, the Ruff formatter will
automatically skip it if the code does not parse as valid Python or if the
reformatted code would produce an invalid Python program.

Users may also configure the line length limit used for reformatting Python
code examples in docstrings. The default is a special value, `dynamic`, which
instructs the formatter to respect the line length limit setting for the
surrounding Python code. The `dynamic` setting ensures that even when code
examples are found inside indented docstrings, the line length limit configured
for the surrounding Python code will not be exceeded. Users may also configure
a fixed line length limit for code examples in docstrings.

For example, this configuration shows how to enable docstring code formatting
with a fixed line length limit:

=== "pyproject.toml"

    ```toml
    [tool.ruff.format]
    docstring-code-format = true
    docstring-code-line-length = 20
    ```

=== "ruff.toml"

    ```toml
    [format]
    docstring-code-format = true
    docstring-code-line-length = 20
    ```

With the above configuration, this code:

```python
def f(x):
    '''
    Something about `f`. And an example:

    .. code-block:: python

        foo, bar, quux = this_is_a_long_line(lion, hippo, lemur, bear)
    '''
    pass
```

... will be reformatted (assuming the rest of the options are set
to their defaults) as:

```python
def f(x):
    """
    Something about `f`. And an example:

    .. code-block:: python

        (
            foo,
            bar,
            quux,
        ) = this_is_a_long_line(
            lion,
            hippo,
            lemur,
            bear,
        )
    """
    pass
```

[doctest]: https://docs.python.org/3/library/doctest.html
[fenced code blocks]: https://spec.commonmark.org/0.30/#fenced-code-blocks
[literal blocks]: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks
[`code-block` and `sourcecode` directives]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block

## Format suppression

Like Black, Ruff supports `# fmt: on`, `# fmt: off`, and `# fmt: skip` pragma comments, which can
be used to temporarily disable formatting for a given code block.

`# fmt: on` and `# fmt: off` comments are enforced at the statement level:

```python
# fmt: off
not_formatted=3
also_not_formatted=4
# fmt: on
```

As such, adding `# fmt: on` and `# fmt: off` comments within expressions will have no effect. In
the following example, both list entries will be formatted, despite the `# fmt: off`:

```python
[
    # fmt: off
    '1',
    # fmt: on
    '2',
]
```

Instead, apply the `# fmt: off` comment to the entire statement:

```python
# fmt: off
[
    '1',
    '2',
]
# fmt: on
```

Like Black, Ruff will _also_ recognize [YAPF](https://github.com/google/yapf)'s `# yapf: disable` and `# yapf: enable` pragma
comments, which are treated equivalently to `# fmt: off` and `# fmt: on`, respectively.

`# fmt: skip` comments suppress formatting for a preceding statement, case header, decorator,
function definition, or class definition:

```python
if True:
    pass
elif False: # fmt: skip
    pass

@Test
@Test2 # fmt: skip
def test(): ...

a = [1, 2, 3, 4, 5] # fmt: skip

def test(a, b, c, d, e, f) -> int: # fmt: skip
    pass
```

As such, adding an `# fmt: skip` comment at the end of an expression will have no effect. In
the following example, the list entry `'1'` will be formatted, despite the `# fmt: skip`:

```python
a = call(
    [
        '1',  # fmt: skip
        '2',
    ],
    b
)
```

Instead, apply the `# fmt: skip` comment to the entire statement:

```python
a = call(
  [
    '1',
    '2',
  ],
  b
)  # fmt: skip
```

## Conflicting lint rules

Ruff's formatter is designed to be used alongside the linter. However, the linter includes
some rules that, when enabled, can cause conflicts with the formatter, leading to unexpected
behavior. When configured appropriately, the goal of Ruff's formatter-linter compatibility is
such that running the formatter should never introduce new lint errors.

When using Ruff as a formatter, we recommend avoiding the following lint rules:

- [`tab-indentation`](rules/tab-indentation.md) (`W191`)
- [`indentation-with-invalid-multiple`](rules/indentation-with-invalid-multiple.md) (`E111`)
- [`indentation-with-invalid-multiple-comment`](rules/indentation-with-invalid-multiple-comment.md) (`E114`)
- [`over-indented`](rules/over-indented.md) (`E117`)
- [`docstring-tab-indentation`](rules/docstring-tab-indentation.md) (`D206`)
- [`triple-single-quotes`](rules/triple-single-quotes.md) (`D300`)
- [`bad-quotes-inline-string`](rules/bad-quotes-inline-string.md) (`Q000`)
- [`bad-quotes-multiline-string`](rules/bad-quotes-multiline-string.md) (`Q001`)
- [`bad-quotes-docstring`](rules/bad-quotes-docstring.md) (`Q002`)
- [`avoidable-escaped-quote`](rules/avoidable-escaped-quote.md) (`Q003`)
- [`missing-trailing-comma`](rules/missing-trailing-comma.md) (`COM812`)
- [`prohibited-trailing-comma`](rules/prohibited-trailing-comma.md) (`COM819`)
- [`multi-line-implicit-string-concatenation`](rules/multi-line-implicit-string-concatenation.md) (`ISC002`) if used without `ISC001` and `flake8-implicit-str-concat.allow-multiline = false`

While the [`line-too-long`](rules/line-too-long.md) (`E501`) rule _can_ be used alongside the
formatter, the formatter only makes a best-effort attempt to wrap lines at the configured
[`line-length`](settings.md#line-length). As such, formatted code _may_ exceed the line length,
leading to [`line-too-long`](rules/line-too-long.md) (`E501`) errors.

None of the above are included in Ruff's default configuration. However, if you've enabled
any of these rules or their parent categories (like `Q`), we recommend disabling them via the
linter's [`lint.ignore`](settings.md#lint_ignore) setting.

Similarly, we recommend avoiding the following isort settings, which are incompatible with the
formatter's treatment of import statements when set to non-default values:

- [`force-single-line`](settings.md#lint_isort_force-single-line)
- [`force-wrap-aliases`](settings.md#lint_isort_force-wrap-aliases)
- [`lines-after-imports`](settings.md#lint_isort_lines-after-imports)
- [`lines-between-types`](settings.md#lint_isort_lines-between-types)
- [`split-on-trailing-comma`](settings.md#lint_isort_split-on-trailing-comma)

If you've configured any of these settings to take on non-default values, we recommend removing
them from your Ruff configuration.

When an incompatible lint rule or setting is enabled, `ruff format` will emit a warning. If your
`ruff format` is free of warnings, you're good to go!

## Exit codes

`ruff format` exits with the following status codes:

- `0` if Ruff terminates successfully, regardless of whether any files were formatted.
- `2` if Ruff terminates abnormally due to invalid configuration, invalid CLI options, or an
    internal error.

Meanwhile, `ruff format --check` exits with the following status codes:

- `0` if Ruff terminates successfully, and no files would be formatted if `--check` were not
    specified.
- `1` if Ruff terminates successfully, and one or more files would be formatted if `--check` were
    not specified.
- `2` if Ruff terminates abnormally due to invalid configuration, invalid CLI options, or an
    internal error.

## Style Guide <span id="black-compatibility"></span>

The formatter is designed to be a drop-in replacement for [Black](https://github.com/psf/black).
This section documents the areas where the Ruff formatter goes beyond Black in terms of code style.

### Intentional deviations

While the Ruff formatter aims to be a drop-in replacement for Black, it does differ from Black
in a few known ways. Some of these differences emerge from conscious attempts to improve upon
Black's code style, while others fall out of differences in the underlying implementations.

For a complete enumeration of these intentional deviations, see [_Known deviations_](formatter/black.md).

Unintentional deviations from Black are tracked in the [issue tracker](https://github.com/astral-sh/ruff/issues?q=is%3Aopen+is%3Aissue+label%3Aformatter).
If you've identified a new deviation, please [file an issue](https://github.com/astral-sh/ruff/issues/new).

### Preview style

Similar to [Black](https://black.readthedocs.io/en/stable/the_black_code_style/future_style.html#preview-style), Ruff implements formatting changes
under the [`preview`](https://docs.astral.sh/ruff/settings/#format_preview) flag, promoting them to stable through minor releases, in accordance with our [versioning policy](https://github.com/astral-sh/ruff/discussions/6998#discussioncomment-7016766).

### F-string formatting

_Stabilized in Ruff 0.9.0_

Unlike Black, Ruff formats the expression parts of f-strings which are the parts inside the curly
braces `{...}`. This is a [known deviation](formatter/black.md#f-strings) from Black.

Ruff employs several heuristics to determine how an f-string should be formatted which are detailed
below.

#### Quotes

Ruff will use the [configured quote style] for the f-string expression unless doing so would result in
invalid syntax for the target Python version or requires more backslash escapes than the original
expression. Specifically, Ruff will preserve the original quote style for the following cases:

When the target Python version is < 3.12 and a [self-documenting f-string] contains a string
literal with the [configured quote style]:

```python
# format.quote-style = "double"

f'{10 + len("hello")=}'
# This f-string cannot be formatted as follows when targeting Python < 3.12
f"{10 + len("hello")=}"
```

When the target Python version is < 3.12 and an f-string contains any triple-quoted string, byte
or f-string literal that contains the [configured quote style]:

```python
# format.quote-style = "double"

f'{"""nested " """}'
# This f-string cannot be formatted as follows when targeting Python < 3.12
f"{'''nested " '''}"
```

For all target Python versions, when a [self-documenting f-string] contains an expression between
the curly braces (`{...}`) with a format specifier containing the [configured quote style]:

```python
# format.quote-style = "double"

f'{1=:"foo}'
# This f-string cannot be formatted as follows for all target Python versions
f"{1=:"foo}"
```

For nested f-strings, Ruff alternates quote styles, starting with the [configured quote style] for the
outermost f-string. For example, consider the following f-string:

```python
# format.quote-style = "double"

f"outer f-string {f"nested f-string {f"another nested f-string"} end"} end"
```

Ruff formats it as:

```python
f"outer f-string {f'nested f-string {f"another nested f-string"} end'} end"
```

#### Line breaks

Starting with Python 3.12 ([PEP 701](https://peps.python.org/pep-0701/)), the expression parts of an f-string can
span multiple lines. Ruff needs to decide when to introduce a line break in an f-string expression.
This depends on the semantic content of the expression parts of an f-string - for example,
introducing a line break in the middle of a natural-language sentence is undesirable. Since Ruff
doesn't have enough information to make that decision, it adopts a heuristic similar to [Prettier](https://prettier.io/docs/en/next/rationale.html#template-literals):
it will only split the expression parts of an f-string across multiple lines if there was already a line break
within any of the expression parts.

For example, the following code:

```python
f"this f-string has a multiline expression {
  ['red', 'green', 'blue', 'yellow',]} and does not fit within the line length"
```

... is formatted as:

```python
# The list expression is split across multiple lines because of the trailing comma
f"this f-string has a multiline expression {
    [
        'red',
        'green',
        'blue',
        'yellow',
    ]
} and does not fit within the line length"
```

But, the following will not be split across multiple lines even though it exceeds the line length:

```python
f"this f-string has a multiline expression {['red', 'green', 'blue', 'yellow']} and does not fit within the line length"
```

If you want Ruff to split an f-string across multiple lines, ensure there's a linebreak somewhere within the
`{...}` parts of an f-string.

[self-documenting f-string]: https://realpython.com/python-f-strings/#self-documenting-expressions-for-debugging
[configured quote style]: settings.md/#format_quote-style

## Sorting imports

Currently, the Ruff formatter does not sort imports. In order to both sort imports and format,
call the Ruff linter and then the formatter:

```shell
ruff check --select I --fix
ruff format
```

A unified command for both linting and formatting is [planned](https://github.com/astral-sh/ruff/issues/8232).
````

## File: docs/installation.md
````markdown
# Installing Ruff

Ruff is available as [`ruff`](https://pypi.org/project/ruff/) on PyPI.

Ruff can be invoked directly with [`uvx`](https://docs.astral.sh/uv/):

```shell
uvx ruff check   # Lint all files in the current directory.
uvx ruff format  # Format all files in the current directory.
```

Or installed with `uv` (recommended), `pip`, or `pipx`:

```console
$ # Install Ruff globally.
$ uv tool install ruff@latest

$ # Or add Ruff to your project.
$ uv add --dev ruff

$ # With pip.
$ pip install ruff

$ # With pipx.
$ pipx install ruff
```

Once installed, you can run Ruff from the command line:

```console
$ ruff check   # Lint all files in the current directory.
$ ruff format  # Format all files in the current directory.
```

Starting with version `0.5.0`, Ruff can also be installed with our standalone installers:

```console
$ # On macOS and Linux.
$ curl -LsSf https://astral.sh/ruff/install.sh | sh

$ # On Windows.
$ powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"

$ # For a specific version.
$ curl -LsSf https://astral.sh/ruff/0.5.0/install.sh | sh
$ powershell -c "irm https://astral.sh/ruff/0.5.0/install.ps1 | iex"
```

For **macOS Homebrew** and **Linuxbrew** users, Ruff is also available
as [`ruff`](https://formulae.brew.sh/formula/ruff) on Homebrew:

```console
$ brew install ruff
```

For **Conda** users, Ruff is also available as [`ruff`](https://anaconda.org/conda-forge/ruff) on
`conda-forge`:

```console
$ conda install -c conda-forge ruff
```

For **pkgx** users, Ruff is also available as [`ruff`](https://pkgx.dev/pkgs/github.com/charliermarsh/ruff/)
on the `pkgx` registry:

```console
$ pkgx install ruff
```

For **Arch Linux** users, Ruff is also available as [`ruff`](https://archlinux.org/packages/extra/x86_64/ruff/)
on the official repositories:

```console
$ pacman -S ruff
```

For **Alpine** users, Ruff is also available as [`ruff`](https://pkgs.alpinelinux.org/package/edge/testing/x86_64/ruff)
on the testing repositories:

```console
$ apk add ruff
```

For **openSUSE Tumbleweed** users, Ruff is also available in the distribution repository:

```console
$ sudo zypper install python3-ruff
```

On **Docker**, it is published as `ghcr.io/astral-sh/ruff`, tagged for each release and `latest` for
the latest release.

```console
$ docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
$ docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.3.0 check

$ # Or, for Podman on SELinux.
$ docker run -v .:/io:Z --rm ghcr.io/astral-sh/ruff check
```

[![Packaging status](https://repology.org/badge/vertical-allrepos/ruff-python-linter.svg?exclude_unsupported=1)](https://repology.org/project/ruff-python-linter/versions)
````

## File: docs/integrations.md
````markdown
# Integrations

## GitHub Actions

GitHub Actions has everything you need to run Ruff out-of-the-box:

```yaml
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff
      # Update output format to enable automatic inline annotations.
      - name: Run Ruff
        run: ruff check --output-format=github .
```

Ruff can also be used as a GitHub Action via [`ruff-action`](https://github.com/astral-sh/ruff-action).

By default, `ruff-action` runs as a pass-fail test to ensure that a given repository doesn't contain
any lint rule violations as per its [configuration](configuration.md).
However, under-the-hood, `ruff-action` installs and runs `ruff` directly, so it can be used to
execute any supported `ruff` command (e.g., `ruff check --fix`).

`ruff-action` supports all GitHub-hosted runners, and can be used with any published Ruff version
(i.e., any version available on [PyPI](https://pypi.org/project/ruff/)).

To use `ruff-action`, create a file (e.g., `.github/workflows/ruff.yml`) inside your repository
with:

```yaml
name: Ruff
on: [ push, pull_request ]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
```

Alternatively, you can include `ruff-action` as a step in any other workflow file:

```yaml
      - uses: astral-sh/ruff-action@v3
```

`ruff-action` accepts optional configuration parameters via `with:`, including:

- `version`: The Ruff version to install (default: latest).
- `args`: The command-line arguments to pass to Ruff (default: `"check"`).
- `src`: The source paths to pass to Ruff (default: `[".", "src"]`).

For example, to run `ruff check --select B ./src` using Ruff version `0.8.0`:

```yaml
- uses: astral-sh/ruff-action@v3
  with:
    version: 0.8.0
    args: check --select B
    src: "./src"
```

## GitLab CI/CD

You can add the following configuration to `.gitlab-ci.yml` to run a `ruff format` in parallel with a `ruff check` compatible with GitLab's codequality report.

```yaml
.base_ruff:
  stage: build
  interruptible: true
  image:
    name: ghcr.io/astral-sh/ruff:0.12.9-alpine
  before_script:
    - cd $CI_PROJECT_DIR
    - ruff --version

Ruff Check:
  extends: .base_ruff
  script:
    - ruff check --output-format=gitlab > code-quality-report.json
  artifacts:
    reports:
      codequality: $CI_PROJECT_DIR/code-quality-report.json

Ruff Format:
  extends: .base_ruff
  script:
    - ruff format --diff
```

## pre-commit

Ruff can be used as a [pre-commit](https://pre-commit.com) hook via [`ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit):

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Ruff version.
  rev: v0.12.9
  hooks:
    # Run the linter.
    - id: ruff-check
    # Run the formatter.
    - id: ruff-format
```

To enable lint fixes, add the `--fix` argument to the lint hook:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Ruff version.
  rev: v0.12.9
  hooks:
    # Run the linter.
    - id: ruff-check
      args: [ --fix ]
    # Run the formatter.
    - id: ruff-format
```

To avoid running on Jupyter Notebooks, remove `jupyter` from the list of allowed filetypes:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Ruff version.
  rev: v0.12.9
  hooks:
    # Run the linter.
    - id: ruff-check
      types_or: [ python, pyi ]
      args: [ --fix ]
    # Run the formatter.
    - id: ruff-format
      types_or: [ python, pyi ]
```

When running with `--fix`, Ruff's lint hook should be placed _before_ Ruff's formatter hook, and
_before_ Black, isort, and other formatting tools, as Ruff's fix behavior can output code changes
that require reformatting.

When running without `--fix`, Ruff's formatter hook can be placed before or after Ruff's lint hook.

(As long as your Ruff configuration avoids any [linter-formatter incompatibilities](formatter.md#conflicting-lint-rules),
`ruff format` should never introduce new lint errors, so it's safe to run Ruff's format hook _after_
`ruff check --fix`.)

## `mdformat`

[mdformat](https://mdformat.readthedocs.io/en/stable/users/plugins.html#code-formatter-plugins) is
capable of formatting code blocks within Markdown. The [`mdformat-ruff`](https://github.com/Freed-Wu/mdformat-ruff)
plugin enables mdformat to format Python code blocks with Ruff.


## Docker

Ruff provides a distroless Docker image including the `ruff` binary. The following tags are published:

- `ruff:latest`
- `ruff:{major}.{minor}.{patch}`, e.g., `ruff:0.6.6`
- `ruff:{major}.{minor}`, e.g., `ruff:0.6` (the latest patch version)

In addition, ruff publishes the following images:

<!-- prettier-ignore -->
- Based on `alpine:3.20`:
  - `ruff:alpine`
  - `ruff:alpine3.20`
- Based on `debian:bookworm-slim`:
  - `ruff:debian-slim`
  - `ruff:bookworm-slim`
- Based on `buildpack-deps:bookworm`:
  - `ruff:debian`
  - `ruff:bookworm`

As with the distroless image, each image is published with ruff version tags as
`ruff:{major}.{minor}.{patch}-{base}` and `ruff:{major}.{minor}-{base}`, e.g., `ruff:0.6.6-alpine`.
````

## File: docs/linter.md
````markdown
# The Ruff Linter

The Ruff Linter is an extremely fast Python linter designed as a drop-in replacement for [Flake8](https://pypi.org/project/flake8/)
(plus dozens of plugins), [isort](https://pypi.org/project/isort/), [pydocstyle](https://pypi.org/project/pydocstyle/),
[pyupgrade](https://pypi.org/project/pyupgrade/), [autoflake](https://pypi.org/project/autoflake/),
and more.

## `ruff check`

`ruff check` is the primary entrypoint to the Ruff linter. It accepts a list of files or
directories, and lints all discovered Python files, optionally fixing any fixable errors.
When linting a directory, Ruff searches for Python files recursively in that directory
and all its subdirectories:

```console
$ ruff check                  # Lint files in the current directory.
$ ruff check --fix            # Lint files in the current directory and fix any fixable errors.
$ ruff check --watch          # Lint files in the current directory and re-lint on change.
$ ruff check path/to/code/    # Lint files in `path/to/code`.
```

For the full list of supported options, run `ruff check --help`.

## Rule selection

The set of enabled rules is controlled via the [`lint.select`](settings.md#lint_select),
[`lint.extend-select`](settings.md#lint_extend-select), and [`lint.ignore`](settings.md#lint_ignore) settings.

Ruff's linter mirrors Flake8's rule code system, in which each rule code consists of a one-to-three
letter prefix, followed by three digits (e.g., `F401`). The prefix indicates that "source" of the rule
(e.g., `F` for Pyflakes, `E` for pycodestyle, `ANN` for flake8-annotations).

Rule selectors like [`lint.select`](settings.md#lint_select) and [`lint.ignore`](settings.md#lint_ignore) accept either
a full rule code (e.g., `F401`) or any valid prefix (e.g., `F`). For example, given the following
configuration file:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    select = ["E", "F"]
    ignore = ["F401"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    select = ["E", "F"]
    ignore = ["F401"]
    ```

Ruff would enable all rules with the `E` (pycodestyle) or `F` (Pyflakes) prefix, with the exception
of `F401`. For more on configuring Ruff via `pyproject.toml`, see [_Configuring Ruff_](configuration.md).

As a special-case, Ruff also supports the `ALL` code, which enables all rules. Note that some
pydocstyle rules conflict (e.g., `D203` and `D211`) as they represent alternative docstring
formats. Ruff will automatically disable any conflicting rules when `ALL` is enabled.

If you're wondering how to configure Ruff, here are some **recommended guidelines**:

- Prefer [`lint.select`](settings.md#lint_select) over [`lint.extend-select`](settings.md#lint_extend-select) to make your rule set explicit.
- Use `ALL` with discretion. Enabling `ALL` will implicitly enable new rules whenever you upgrade.
- Start with a small set of rules (`select = ["E", "F"]`) and add a category at-a-time. For example,
    you might consider expanding to `select = ["E", "F", "B"]` to enable the popular flake8-bugbear
    extension.

For example, a configuration that enables some of the most popular rules (without being too
pedantic) might look like the following:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    select = [
        # pycodestyle
        "E",
        # Pyflakes
        "F",
        # pyupgrade
        "UP",
        # flake8-bugbear
        "B",
        # flake8-simplify
        "SIM",
        # isort
        "I",
    ]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    select = [
        # pycodestyle
        "E",
        # Pyflakes
        "F",
        # pyupgrade
        "UP",
        # flake8-bugbear
        "B",
        # flake8-simplify
        "SIM",
        # isort
        "I",
    ]
    ```

To resolve the enabled rule set, Ruff may need to reconcile [`lint.select`](settings.md#lint_select) and
[`lint.ignore`](settings.md#lint_ignore) from a variety of sources, including the current `pyproject.toml`,
any inherited `pyproject.toml` files, and the CLI (e.g., [`--select`](settings.md#lint_select)).

In those scenarios, Ruff uses the "highest-priority" [`select`](settings.md#lint_select) as the basis for
the rule set, and then applies [`extend-select`](settings.md#lint_extend-select) and
[`ignore`](settings.md#lint_ignore) adjustments. CLI options are given higher priority than
`pyproject.toml` options, and the current `pyproject.toml` file is given higher priority than any
inherited `pyproject.toml` files.

For example, given the following configuration file:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    select = ["E", "F"]
    ignore = ["F401"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    select = ["E", "F"]
    ignore = ["F401"]
    ```

Running `ruff check --select F401` would result in Ruff enforcing `F401`, and no other rules.

Running `ruff check --extend-select B` would result in Ruff enforcing the `E`, `F`, and `B` rules,
with the exception of `F401`.

## Fixes

Ruff supports automatic fixes for a variety of lint errors. For example, Ruff can remove unused
imports, reformat docstrings, rewrite type annotations to use newer Python syntax, and more.

To enable fixes, pass the `--fix` flag to `ruff check`:

```console
$ ruff check --fix
```

By default, Ruff will fix all violations for which safe fixes are available; to determine
whether a rule supports fixing, see [_Rules_](rules.md).

### Fix safety

Ruff labels fixes as "safe" and "unsafe". The meaning and intent of your code will be retained when
applying safe fixes, but the meaning could change when applying unsafe fixes.

Specifically, an unsafe fix could lead to a change in runtime behavior, the removal of comments, or both,
while safe fixes are intended to preserve runtime behavior and will only remove comments when deleting
entire statements or expressions (e.g., removing unused imports).

For example, [`unnecessary-iterable-allocation-for-first-element`](rules/unnecessary-iterable-allocation-for-first-element.md)
(`RUF015`) is a rule which checks for potentially unperformant use of `list(...)[0]`. The fix
replaces this pattern with `next(iter(...))` which can result in a drastic speedup:

```console
$ python -m timeit "head = list(range(99999999))[0]"
1 loop, best of 5: 1.69 sec per loop
```

```console
$ python -m timeit "head = next(iter(range(99999999)))"
5000000 loops, best of 5: 70.8 nsec per loop
```

However, when the collection is empty, this raised exception changes from an `IndexError` to `StopIteration`:

```console
$ python -c 'list(range(0))[0]'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
IndexError: list index out of range
```

```console
$ python -c 'next(iter(range(0)))[0]'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
StopIteration
```

Since the change in exception type could break error handling upstream, this fix is categorized as unsafe.

Ruff only enables safe fixes by default. Unsafe fixes can be enabled by settings [`unsafe-fixes`](settings.md#unsafe-fixes) in your configuration file or passing the `--unsafe-fixes` flag to `ruff check`:

```console
# Show unsafe fixes
ruff check --unsafe-fixes

# Apply unsafe fixes
ruff check --fix --unsafe-fixes
```

By default, Ruff will display a hint when unsafe fixes are available but not enabled. The suggestion can be silenced
by setting the [`unsafe-fixes`](settings.md#unsafe-fixes) setting to `false` or using the `--no-unsafe-fixes` flag.

The safety of fixes can be adjusted per rule using the [`lint.extend-safe-fixes`](settings.md#lint_extend-safe-fixes) and [`lint.extend-unsafe-fixes`](settings.md#lint_extend-unsafe-fixes) settings.

For example, the following configuration would promote unsafe fixes for `F601` to safe fixes and demote safe fixes for `UP034` to unsafe fixes:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    extend-safe-fixes = ["F601"]
    extend-unsafe-fixes = ["UP034"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    extend-safe-fixes = ["F601"]
    extend-unsafe-fixes = ["UP034"]
    ```

You may use prefixes to select rules as well, e.g., `F` can be used to promote fixes for all rules in Pyflakes to safe.

!!! note
    All fixes will always be displayed by Ruff when using the `json` output format. The safety of each fix is available under the `applicability` field.

### Disabling fixes

To limit the set of rules that Ruff should fix, use the [`lint.fixable`](settings.md#lint_fixable)
or [`lint.extend-fixable`](settings.md#lint_extend-fixable), and [`lint.unfixable`](settings.md#lint_unfixable) settings.

For example, the following configuration would enable fixes for all rules except
[`unused-imports`](rules/unused-import.md) (`F401`):

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    fixable = ["ALL"]
    unfixable = ["F401"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    fixable = ["ALL"]
    unfixable = ["F401"]
    ```

Conversely, the following configuration would only enable fixes for `F401`:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    fixable = ["F401"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    fixable = ["F401"]
    ```

## Error suppression

Ruff supports several mechanisms for suppressing lint errors, be they false positives or
permissible violations.

To omit a lint rule entirely, add it to the "ignore" list via the [`lint.ignore`](settings.md#lint_ignore)
setting, either on the command-line or in your `pyproject.toml` or `ruff.toml` file.

To suppress a violation inline, Ruff uses a `noqa` system similar to [Flake8](https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html).
To ignore an individual violation, add `# noqa: {code}` to the end of the line, like so:

```python
# Ignore F841.
x = 1  # noqa: F841

# Ignore E741 and F841.
i = 1  # noqa: E741, F841

# Ignore _all_ violations.
x = 1  # noqa
```

For multi-line strings (like docstrings), the `noqa` directive should come at the end of the string
(after the closing triple quote), and will apply to the entire string, like so:

```python
"""Lorem ipsum dolor sit amet.

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.
"""  # noqa: E501
```

For import sorting, the `noqa` should come at the end of the first line in the import block, and
will apply to all imports in the block, like so:

```python
import os  # noqa: I001
import abc
```

To ignore all violations across an entire file, add the line `# ruff: noqa` anywhere in the file,
preferably towards the top, like so:

```python
# ruff: noqa
```

To ignore a specific rule across an entire file, add the line `# ruff: noqa: {code}` anywhere in the
file, preferably towards the top, like so:

```python
# ruff: noqa: F841
```

Or see the [`lint.per-file-ignores`](settings.md#lint_per-file-ignores) setting, which enables the same
functionality from within your `pyproject.toml` or `ruff.toml` file.

Global `noqa` comments must be on their own line to disambiguate from comments which ignore
violations on a single line.

Note that Ruff will also respect Flake8's `# flake8: noqa` directive, and will treat it as
equivalent to `# ruff: noqa`.

### Full suppression comment specification

The full specification is as follows:

- An inline blanket `noqa` comment is given by a case-insensitive match for
  `#noqa` with optional whitespace after the `#` symbol, followed by either: the
  end of the comment, the beginning of a new comment (`#`), or whitespace
  followed by any character other than `:`.
- An inline rule suppression is given by first finding a case-insensitive match
  for `#noqa` with optional whitespace after the `#` symbol, optional whitespace
  after `noqa`, and followed by the symbol `:`. After this we are expected to
  have a list of rule codes which is given by sequences of uppercase ASCII
  characters followed by ASCII digits, separated by whitespace or commas. The
  list ends at the last valid code. We will attempt to interpret rules with a
  missing delimiter (e.g. `F401F841`), though a warning will be emitted in this
  case.
- A file-level exemption comment is given by a case-sensitive match for `#ruff:`
  or `#flake8:`, with optional whitespace after `#` and before `:`, followed by
  optional whitespace and a case-insensitive match for `noqa`. After this, the
  specification is as in the inline case.

### Detecting unused suppression comments

Ruff implements a special rule, [`unused-noqa`](https://docs.astral.sh/ruff/rules/unused-noqa/),
under the `RUF100` code, to enforce that your `noqa` directives are "valid", in that the violations
they _say_ they ignore are actually being triggered on that line (and thus suppressed). To flag
unused `noqa` directives, run: `ruff check /path/to/file.py --extend-select RUF100`.

Ruff can also _remove_ any unused `noqa` directives via its fix functionality. To remove any
unused `noqa` directives, run: `ruff check /path/to/file.py --extend-select RUF100 --fix`.

### Inserting necessary suppression comments

Ruff can _automatically add_ `noqa` directives to all lines that contain violations, which is
useful when migrating a new codebase to Ruff. To automatically add `noqa` directives to all
relevant lines (with the appropriate rule codes), run: `ruff check /path/to/file.py --add-noqa`.

### Action comments

Ruff respects isort's [action comments](https://pycqa.github.io/isort/docs/configuration/action_comments.html)
(`# isort: skip_file`, `# isort: on`, `# isort: off`, `# isort: skip`, and `# isort: split`), which
enable selectively enabling and disabling import sorting for blocks of code and other inline
configuration.

Ruff will also respect variants of these action comments with a `# ruff:` prefix
(e.g., `# ruff: isort: skip_file`, `# ruff: isort: on`, and so on). These variants more clearly
convey that the action comment is intended for Ruff, but are functionally equivalent to the
isort variants.

Unlike isort, Ruff does not respect action comments within docstrings.

See the [isort documentation](https://pycqa.github.io/isort/docs/configuration/action_comments.html)
for more.

## Exit codes

By default, `ruff check` exits with the following status codes:

- `0` if no violations were found, or if all present violations were fixed automatically.
- `1` if violations were found.
- `2` if Ruff terminates abnormally due to invalid configuration, invalid CLI options, or an
    internal error.

This convention mirrors that of tools like ESLint, Prettier, and RuboCop.

`ruff check` supports two command-line flags that alter its exit code behavior:

- `--exit-zero` will cause Ruff to exit with a status code of `0` even if violations were found.
    Note that Ruff will still exit with a status code of `2` if it terminates abnormally.
- `--exit-non-zero-on-fix` will cause Ruff to exit with a status code of `1` if violations were
    found, _even if_ all such violations were fixed automatically. Note that the use of
    `--exit-non-zero-on-fix` can result in a non-zero exit code even if no violations remain after
    fixing.
````

## File: docs/preview.md
````markdown
# Preview

Ruff includes an opt-in preview mode to provide an opportunity for community feedback and increase confidence that
changes are a net-benefit before enabling them for everyone.

Preview mode enables a collection of unstable features such as new lint rules and fixes, formatter style changes, interface updates, and more. Warnings about deprecated features may turn into errors when using preview mode.

Enabling preview mode does not on its own enable all preview rules. See the [rules section](#using-rules-that-are-in-preview) for details on selecting preview rules.

## Enabling preview mode

Preview mode can be enabled with the `--preview` flag on the CLI or by setting `preview = true` in your Ruff
configuration file.

Preview mode can be configured separately for linting and formatting. To enable preview lint rules without preview style formatting:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    preview = true
    ```

=== "ruff.toml"

    ```toml
    [lint]
    preview = true
    ```

=== "CLI"

    ```console
    ruff check --preview
    ```


To enable preview style formatting without enabling any preview lint rules:

=== "pyproject.toml"

    ```toml
    [tool.ruff.format]
    preview = true
    ```

=== "ruff.toml"

    ```toml
    [format]
    preview = true
    ```

=== "CLI"

    ```console
    ruff format --preview
    ```

## Using rules that are in preview

If a rule is marked as preview, it can only be selected if preview mode is enabled. For example, consider a
hypothetical rule, `HYP001`. If `HYP001` were in preview, it would _not_ be enabled by adding it to the selected rule set.

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    extend-select = ["HYP001"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    extend-select = ["HYP001"]
    ```

=== "CLI"

    ```console
    ruff check --extend-select HYP001
    ```


It also would _not_ be enabled by selecting the `HYP` category, like so:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    extend-select = ["HYP"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    extend-select = ["HYP"]
    ```

=== "CLI"

    ```console
    ruff check --extend-select HYP
    ```


Similarly, it would _not_ be enabled via the `ALL` selector:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    select = ["ALL"]
    ```

=== "ruff.toml"

    ```toml
    [lint]
    select = ["ALL"]
    ```

=== "CLI"

    ```console
    ruff check --select ALL
    ```

However, it _would_ be enabled in any of the above cases if you enabled preview mode:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    extend-select = ["HYP"]
    preview = true
    ```

=== "ruff.toml"

    ```toml
    [lint]
    extend-select = ["HYP"]
    preview = true
    ```

=== "CLI"

    ```console
    ruff check --extend-select HYP --preview
    ```

To see which rules are currently in preview, visit the [rules reference](rules.md).

## Selecting single preview rules

When preview mode is enabled, selecting rule categories or prefixes will include all preview rules that match.
If you'd prefer to opt in to each preview rule individually, you can toggle the `explicit-preview-rules`
setting in your configuration file:

=== "pyproject.toml"

    ```toml
    [tool.ruff.lint]
    preview = true
    explicit-preview-rules = true
    ```

=== "ruff.toml"

    ```toml
    [lint]
    preview = true
    explicit-preview-rules = true
    ```

In our previous example, `--select` with `ALL` `HYP`, `HYP0`, or `HYP00` would not enable `HYP001`. Each preview
rule will need to be selected with its exact code: for example, `--select ALL,HYP001`.

If preview mode is not enabled, this setting has no effect.

## Deprecated rules

When preview mode is enabled, deprecated rules will be disabled. If a deprecated rule is selected explicitly, an
error will be raised. Deprecated rules will not be included if selected via a rule category or prefix.
````

## File: docs/requirements-insiders.txt
````
PyYAML==6.0.2
ruff==0.12.8
mkdocs==1.6.1
mkdocs-material @ git+ssh://git@github.com/astral-sh/mkdocs-material-insiders.git@39da7a5e761410349e9a1b8abf593b0cdd5453ff
mkdocs-redirects==1.2.2
mdformat==0.7.22
mdformat-mkdocs==4.3.0
mkdocs-github-admonitions-plugin @ git+https://github.com/PGijsbers/admonitions.git#7343d2f4a92e4d1491094530ef3d0d02d93afbb7
````

## File: docs/requirements.txt
````
PyYAML==6.0.2
ruff==0.12.8
mkdocs==1.6.1
mkdocs-material==9.5.38
mkdocs-redirects==1.2.2
mdformat==0.7.22
mdformat-mkdocs==4.3.0
mkdocs-github-admonitions-plugin @ git+https://github.com/PGijsbers/admonitions.git#7343d2f4a92e4d1491094530ef3d0d02d93afbb7
````

## File: docs/tutorial.md
````markdown
# Tutorial

This tutorial will walk you through the process of integrating Ruff's linter and formatter into
your project. For a more detailed overview, see [_Configuring Ruff_](configuration.md).

## Getting Started

To start, we'll initialize a project using [uv](https://docs.astral.sh/uv/):

```console
$ uv init --lib numbers
```

This command creates a Python project with the following structure:

```text
numbers
  ├── README.md
  ├── pyproject.toml
  └── src
      └── numbers
          ├── __init__.py
          └── py.typed
```

We'll then clear out the auto-generated content in `src/numbers/__init__.py`
and create `src/numbers/calculate.py` with the following code:

```python
from typing import Iterable

import os


def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(
        num for num in numbers
        if num % 2 == 0
    )
```

Next, we'll add Ruff to our project:

```console
$ uv add --dev ruff
```

We can then run the Ruff linter over our project via `uv run ruff check`:

```console
$ uv run ruff check
src/numbers/calculate.py:3:8: F401 [*] `os` imported but unused
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

!!! note

    As an alternative to `uv run`, you can also run Ruff by activating the project's virtual
    environment (`source .venv/bin/active` on Linux and macOS, or `.venv\Scripts\activate` on
    Windows) and running `ruff check` directly.

Ruff identified an unused import, which is a common error in Python code. Ruff considers this a
"fixable" error, so we can resolve the issue automatically by running `ruff check --fix`:

```console
$ uv run ruff check --fix
Found 1 error (1 fixed, 0 remaining).
```

Running `git diff` shows the following:

```diff
--- a/src/numbers/calculate.py
+++ b/src/numbers/calculate.py
@@ -1,7 +1,5 @@
 from typing import Iterable

-import os
-

def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(
        num for num in numbers
        if num % 2 == 0
    )
```

Note Ruff runs in the current directory by default, but you can pass specific paths to check:

```console
$ uv run ruff check src/numbers/calculate.py
```

Now that our project is passing `ruff check`, we can run the Ruff formatter via `ruff format`:

```console
$ uv run ruff format
1 file reformatted
```

Running `git diff` shows that the `sum` call was reformatted to fit within the default 88-character
line length limit:

```diff
--- a/src/numbers/calculate.py
+++ b/src/numbers/calculate.py
@@ -3,7 +3,4 @@ from typing import Iterable

 def sum_even_numbers(numbers: Iterable[int]) -> int:
     """Given an iterable of integers, return the sum of all even numbers in the iterable."""
-    return sum(
-        num for num in numbers
-        if num % 2 == 0
-    )
+    return sum(num for num in numbers if num % 2 == 0)
```

Thus far, we've been using Ruff's default configuration. Let's take a look at how we can customize
Ruff's behavior.

## Configuration

To determine the appropriate settings for each Python file, Ruff looks for the first
`pyproject.toml`, `ruff.toml`, or `.ruff.toml` file in the file's directory or any parent directory.

To configure Ruff, we'll add the following to the configuration file in our project's root directory:

=== "pyproject.toml"

     ```toml
     [tool.ruff]
     # Set the maximum line length to 79.
     line-length = 79

     [tool.ruff.lint]
     # Add the `line-too-long` rule to the enforced rule set. By default, Ruff omits rules that
     # overlap with the use of a formatter, like Black, but we can override this behavior by
     # explicitly adding the rule.
     extend-select = ["E501"]
     ```

=== "ruff.toml"

     ```toml
     # Set the maximum line length to 79.
     line-length = 79

     [lint]
     # Add the `line-too-long` rule to the enforced rule set. By default, Ruff omits rules that
     # overlap with the use of a formatter, like Black, but we can override this behavior by
     # explicitly adding the rule.
     extend-select = ["E501"]
     ```

Running Ruff again, we see that it now enforces a maximum line width, with a limit of 79:

```console
$ uv run ruff check
src/numbers/calculate.py:5:80: E501 Line too long (90 > 79)
Found 1 error.
```

For a full enumeration of the supported settings, see [_Settings_](settings.md). For our project
specifically, we'll want to make note of the minimum supported Python version:

=== "pyproject.toml"

     ```toml
     [project]
     # Support Python 3.10+.
     requires-python = ">=3.10"

     [tool.ruff]
     # Set the maximum line length to 79.
     line-length = 79

     [tool.ruff.lint]
     # Add the `line-too-long` rule to the enforced rule set.
     extend-select = ["E501"]
     ```

=== "ruff.toml"

     ```toml
     # Support Python 3.10+.
     target-version = "py310"
     # Set the maximum line length to 79.
     line-length = 79

     [lint]
     # Add the `line-too-long` rule to the enforced rule set.
     extend-select = ["E501"]
     ```

### Rule Selection

Ruff supports [over 800 lint rules](rules.md) split across over 50 built-in plugins, but
determining the right set of rules will depend on your project's needs: some rules may be too
strict, some are framework-specific, and so on.

By default, Ruff enables Flake8's `F` rules, along with a subset of the `E` rules, omitting any
stylistic rules that overlap with the use of a formatter, like `ruff format` or
[Black](https://github.com/psf/black).

If you're introducing a linter for the first time, **the default rule set is a great place to
start**: it's narrow and focused while catching a wide variety of common errors (like unused
imports) with zero configuration.

If you're migrating to Ruff from another linter, you can enable rules that are equivalent to
those enforced in your previous configuration. For example, if we want to enforce the pyupgrade
rules, we can set our configuration file to the following:

=== "pyproject.toml"

     ```toml
     [project]
     requires-python = ">=3.10"

     [tool.ruff.lint]
     extend-select = [
       "UP",  # pyupgrade
     ]
     ```

=== "ruff.toml"

     ```toml
     target-version = "py310"

     [lint]
     extend-select = [
       "UP",  # pyupgrade
     ]
     ```

If we run Ruff again, we'll see that it now enforces the pyupgrade rules. In particular, Ruff flags
the use of the deprecated `typing.Iterable` instead of `collections.abc.Iterable`:

```console
$ uv run ruff check
src/numbers/calculate.py:1:1: UP035 [*] Import from `collections.abc` instead: `Iterable`
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

Over time, we may choose to enforce additional rules. For example, we may want to enforce that
all functions have docstrings:

=== "pyproject.toml"

     ```toml
     [project]
     requires-python = ">=3.10"

     [tool.ruff.lint]
     extend-select = [
       "UP",  # pyupgrade
       "D",   # pydocstyle
     ]

     [tool.ruff.lint.pydocstyle]
     convention = "google"
     ```

=== "ruff.toml"

     ```toml
     target-version = "py310"

     [lint]
     extend-select = [
       "UP",  # pyupgrade
       "D",   # pydocstyle
     ]

     [lint.pydocstyle]
     convention = "google"
     ```

If we run Ruff again, we'll see that it now enforces the pydocstyle rules:

```console
$ uv run ruff check
src/numbers/__init__.py:1:1: D104 Missing docstring in public package
src/numbers/calculate.py:1:1: UP035 [*] Import from `collections.abc` instead: `Iterable`
  |
1 | from typing import Iterable
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^ UP035
  |
  = help: Import from `collections.abc`

src/numbers/calculate.py:1:1: D100 Missing docstring in public module
Found 3 errors.
[*] 1 fixable with the `--fix` option.
```

### Ignoring Errors

Any lint rule can be ignored by adding a `# noqa` comment to the line in question. For example,
let's ignore the `UP035` rule for the `Iterable` import:

```python
from typing import Iterable  # noqa: UP035


def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(num for num in numbers if num % 2 == 0)
```

Running `ruff check` again, we'll see that it no longer flags the `Iterable` import:

```console
$ uv run ruff check
src/numbers/__init__.py:1:1: D104 Missing docstring in public package
src/numbers/calculate.py:1:1: D100 Missing docstring in public module
Found 2 errors.
```

If we want to ignore a rule for an entire file, we can add the line `# ruff: noqa: {code}` anywhere
in the file, preferably towards the top, like so:

```python
# ruff: noqa: UP035
from typing import Iterable


def sum_even_numbers(numbers: Iterable[int]) -> int:
    """Given an iterable of integers, return the sum of all even numbers in the iterable."""
    return sum(num for num in numbers if num % 2 == 0)
```

For more in-depth instructions on ignoring errors, please see [_Error suppression_](linter.md#error-suppression).

### Adding Rules

When enabling a new rule on an existing codebase, you may want to ignore all _existing_
violations of that rule and instead focus on enforcing it going forward.

Ruff enables this workflow via the `--add-noqa` flag, which will add a `# noqa` directive to each
line based on its existing violations. We can combine `--add-noqa` with the `--select` command-line
flag to add `# noqa` directives to all existing `UP035` violations:

```console
$ uv run ruff check --select UP035 --add-noqa .
Added 1 noqa directive.
```

Running `git diff` shows the following:

```diff
diff --git a/numbers/src/numbers/calculate.py b/numbers/src/numbers/calculate.py
index 71fca60c8d..e92d839f1b 100644
--- a/numbers/src/numbers/calculate.py
+++ b/numbers/src/numbers/calculate.py
@@ -1,4 +1,4 @@
-from typing import Iterable
+from typing import Iterable  # noqa: UP035
```

## Integrations

This tutorial has focused on Ruff's command-line interface, but Ruff can also be used as a
[pre-commit](https://pre-commit.com) hook via [`ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit):

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Ruff version.
  rev: v0.12.9
  hooks:
    # Run the linter.
    - id: ruff
    # Run the formatter.
    - id: ruff-format
```

Ruff can also be integrated into your editor of choice. Refer to the [Editors](editors/index.md)
section for more information.

For other integrations, see the [Integrations](integrations.md) section.
````

## File: docs/versioning.md
````markdown
# Versioning

Ruff uses a custom versioning scheme that uses the **minor** version number for breaking changes and the **patch** version number for bug fixes. Ruff does not yet have a stable API; once Ruff's API is stable, the **major** version number and semantic versioning will be used.

## Version changes

**Minor** version increases will occur when:

- A deprecated option or feature is removed
- Configuration changes in a backwards incompatible way
    - This _may_ occur in minor version changes until `1.0.0`, however, it should generally be avoided.
- Support for a new file type is promoted to stable
- Support for an end-of-life Python version is dropped
- Linter:
    - A rule is promoted to stable
    - The behavior of a stable rule is changed
        - The scope of a stable rule is significantly increased
        - The intent of the rule changes
        - Does not include bug fixes that follow the original intent of the rule
    - Stable rules are added to the default set
    - Stable rules are removed from the default set
    - A safe fix for a rule is promoted to stable
- Formatter:
     - The stable style changed
- Language server:
    - An existing capability is removed
    - A deprecated server setting is removed

**Patch** version increases will occur when:

- Bugs are fixed, _including behavior changes that fix bugs_
- A new configuration option is added in a backwards compatible way (no formatting changes or new lint errors)
- Support for a new Python version is added
- Support for a new file type is added in preview
- An option or feature is deprecated
- Linter:
    - An unsafe fix for a rule is added
    - A safe fix for a rule is added in preview
    - The scope of a rule is increased in preview
    - A fix’s applicability is demoted
    - A rule is added in preview
    - The behavior of a preview rule is changed
- Formatter:
    - The stable style changed to prevent invalid syntax, changes to the program's semantics, or removal of comments
    - The preview style changed
- Language server:
    - Support for a new capability is added
    - A new server setting is added
    - A server setting is deprecated

## Minimum supported Rust version

The minimum supported Rust version required to compile Ruff is listed in the `rust-version` key of
the `[workspace.package]` section in `Cargo.toml`. It may change in any release (minor or patch). It
will never be newer than N-2 Rust versions, where N is the latest stable version. For example, if
the latest stable Rust version is 1.85, Ruff's minimum supported Rust version will be at most 1.83.

This is only relevant to users who build Ruff from source. Installing Ruff from the Python package
index usually installs a pre-built binary and does not require Rust compilation.

## Preview mode

A preview mode is available to enable new, unstable rules and features, e.g., support for a new file type.

The preview mode is intended to help us collect community feedback and gain confidence that changes are a net-benefit.

The preview mode is _not_ intended to gate access to work that is incomplete or features that we are _likely to remove._ However, **we reserve the right to make changes to _any_ behavior gated by the mode** including the removal of preview features or rules.

## Rule stabilization

When modifying or adding rules, we use the following guidelines:

- New rules should always be added in preview mode
- New rules will remain in preview mode for at least one minor release before being promoted to stable
    - If added in a patch release i.e. `0.6.1` then a rule will not be eligible for stability until `0.8.0`
- Stable rule behaviors are not changed significantly in patch versions
- Promotion of rules to stable may be delayed in order to “batch” them into a single minor release
- Not all rules in preview need to be promoted in a given minor release

## Fix stabilization

Fixes have three applicability levels:

- **Display**: Never applied, just displayed.
- **Unsafe**: Can be applied with explicit opt-in.
- **Safe**: Can be applied automatically.

Fixes for rules may be introduced at a lower applicability, then promoted to a higher applicability. Reducing the applicability of a fix is not a breaking change. The applicability of a given fix may change when the preview mode is enabled.

## Visual Studio Code Extension

Visual Studio Code [doesn't support pre-release
tags](https://code.visualstudio.com/api/working-with-extensions/publishing-extension#prerelease-extensions)
for extensions. Consequently, Ruff uses the following scheme to distinguish between stable and
preview releases:

Stable releases use even numbers in minor version component: `2024.30.0`, `2024.32.0`, `2024.34.0`, …
Preview releases use odd numbers in minor version component: `2024.31.0`, `2024.33.0`, `2024.35.0`, …
````
