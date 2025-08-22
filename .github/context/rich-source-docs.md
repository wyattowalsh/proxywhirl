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
- Only files matching these patterns are included: docs/source/**/*.{md,markdown,rmd,mdx,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  source/
    appendix/
      box.rst
      colors.rst
    reference/
      abc.rst
      align.rst
      bar.rst
      color.rst
      columns.rst
      console.rst
      control.rst
      emoji.rst
      highlighter.rst
      init.rst
      json.rst
      layout.rst
      live.rst
      logging.rst
      markdown.rst
      markup.rst
      measure.rst
      padding.rst
      panel.rst
      pretty.rst
      progress_bar.rst
      progress.rst
      prompt.rst
      protocol.rst
      rule.rst
      segment.rst
      spinner.rst
      status.rst
      style.rst
      styled.rst
      syntax.rst
      table.rst
      text.rst
      theme.rst
      traceback.rst
      tree.rst
    appendix.rst
    columns.rst
    console.rst
    group.rst
    highlighting.rst
    index.rst
    introduction.rst
    layout.rst
    live.rst
    logging.rst
    markdown.rst
    markup.rst
    padding.rst
    panel.rst
    pretty.rst
    progress.rst
    prompt.rst
    protocol.rst
    reference.rst
    style.rst
    syntax.rst
    tables.rst
    text.rst
    traceback.rst
    tree.rst
```

# Files

## File: docs/source/appendix/box.rst
```
.. _appendix_box:

Box
===

Rich has a number of constants that set the box characters used to draw tables and panels. To select a box style import one of the constants below from ``rich.box``. For example::

    from rich import box
    table = Table(box=box.SQUARE)


.. note::
    Some of the box drawing characters will not display correctly on Windows legacy terminal (cmd.exe) with *raster* fonts, and are disabled by default. If you want the full range of box options on Windows legacy terminal, use a *truetype* font and set the ``safe_box`` parameter on the Table class to ``False``.


The following table is generated with this command::

    python -m rich.box

.. image:: ../../images/box.svg
```

## File: docs/source/appendix/colors.rst
```
.. _appendix-colors:

Standard Colors
===============

The following is a list of the standard 8-bit colors supported in terminals.

Note that the first 16 colors are generally defined by the system or your terminal software, and may not display exactly as rendered here.

.. raw:: html

        
            <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">╔════════════╤════════╤═══════════════════════╤═════════╤══════════════════╗
    ║<span style="font-weight: bold"> Color      </span>│<span style="font-weight: bold"> Number </span>│<span style="font-weight: bold"> Name                  </span>│<span style="font-weight: bold"> Hex     </span>│<span style="font-weight: bold"> RGB              </span>║
    ╟────────────┼────────┼───────────────────────┼─────────┼──────────────────╢
    ║ <span style="background-color: #000000">          </span> │<span style="color: #808000">      0 </span>│<span style="color: #008000"> "black"               </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #800000">          </span> │<span style="color: #808000">      1 </span>│<span style="color: #008000"> "red"                 </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #008000">          </span> │<span style="color: #808000">      2 </span>│<span style="color: #008000"> "green"               </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #808000">          </span> │<span style="color: #808000">      3 </span>│<span style="color: #008000"> "yellow"              </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #000080">          </span> │<span style="color: #808000">      4 </span>│<span style="color: #008000"> "blue"                </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #800080">          </span> │<span style="color: #808000">      5 </span>│<span style="color: #008000"> "magenta"             </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #008080">          </span> │<span style="color: #808000">      6 </span>│<span style="color: #008000"> "cyan"                </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #c0c0c0">          </span> │<span style="color: #808000">      7 </span>│<span style="color: #008000"> "white"               </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #808080">          </span> │<span style="color: #808000">      8 </span>│<span style="color: #008000"> "bright_black"        </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #ff0000">          </span> │<span style="color: #808000">      9 </span>│<span style="color: #008000"> "bright_red"          </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #00ff00">          </span> │<span style="color: #808000">     10 </span>│<span style="color: #008000"> "bright_green"        </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #ffff00">          </span> │<span style="color: #808000">     11 </span>│<span style="color: #008000"> "bright_yellow"       </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #0000ff">          </span> │<span style="color: #808000">     12 </span>│<span style="color: #008000"> "bright_blue"         </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #ff00ff">          </span> │<span style="color: #808000">     13 </span>│<span style="color: #008000"> "bright_magenta"      </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #00ffff">          </span> │<span style="color: #808000">     14 </span>│<span style="color: #008000"> "bright_cyan"         </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #ffffff">          </span> │<span style="color: #808000">     15 </span>│<span style="color: #008000"> "bright_white"        </span>│<span style="color: #000080">         </span>│<span style="color: #800080">                  </span>║
    ║ <span style="background-color: #000000">          </span> │<span style="color: #808000">     16 </span>│<span style="color: #008000"> "grey0"               </span>│<span style="color: #000080"> #000000 </span>│<span style="color: #800080"> rgb(0,0,0)       </span>║
    ║ <span style="background-color: #00005f">          </span> │<span style="color: #808000">     17 </span>│<span style="color: #008000"> "navy_blue"           </span>│<span style="color: #000080"> #00005f </span>│<span style="color: #800080"> rgb(0,0,95)      </span>║
    ║ <span style="background-color: #000087">          </span> │<span style="color: #808000">     18 </span>│<span style="color: #008000"> "dark_blue"           </span>│<span style="color: #000080"> #000087 </span>│<span style="color: #800080"> rgb(0,0,135)     </span>║
    ║ <span style="background-color: #0000d7">          </span> │<span style="color: #808000">     20 </span>│<span style="color: #008000"> "blue3"               </span>│<span style="color: #000080"> #0000d7 </span>│<span style="color: #800080"> rgb(0,0,215)     </span>║
    ║ <span style="background-color: #0000ff">          </span> │<span style="color: #808000">     21 </span>│<span style="color: #008000"> "blue1"               </span>│<span style="color: #000080"> #0000ff </span>│<span style="color: #800080"> rgb(0,0,255)     </span>║
    ║ <span style="background-color: #005f00">          </span> │<span style="color: #808000">     22 </span>│<span style="color: #008000"> "dark_green"          </span>│<span style="color: #000080"> #005f00 </span>│<span style="color: #800080"> rgb(0,95,0)      </span>║
    ║ <span style="background-color: #005faf">          </span> │<span style="color: #808000">     25 </span>│<span style="color: #008000"> "deep_sky_blue4"      </span>│<span style="color: #000080"> #005faf </span>│<span style="color: #800080"> rgb(0,95,175)    </span>║
    ║ <span style="background-color: #005fd7">          </span> │<span style="color: #808000">     26 </span>│<span style="color: #008000"> "dodger_blue3"        </span>│<span style="color: #000080"> #005fd7 </span>│<span style="color: #800080"> rgb(0,95,215)    </span>║
    ║ <span style="background-color: #005fff">          </span> │<span style="color: #808000">     27 </span>│<span style="color: #008000"> "dodger_blue2"        </span>│<span style="color: #000080"> #005fff </span>│<span style="color: #800080"> rgb(0,95,255)    </span>║
    ║ <span style="background-color: #008700">          </span> │<span style="color: #808000">     28 </span>│<span style="color: #008000"> "green4"              </span>│<span style="color: #000080"> #008700 </span>│<span style="color: #800080"> rgb(0,135,0)     </span>║
    ║ <span style="background-color: #00875f">          </span> │<span style="color: #808000">     29 </span>│<span style="color: #008000"> "spring_green4"       </span>│<span style="color: #000080"> #00875f </span>│<span style="color: #800080"> rgb(0,135,95)    </span>║
    ║ <span style="background-color: #008787">          </span> │<span style="color: #808000">     30 </span>│<span style="color: #008000"> "turquoise4"          </span>│<span style="color: #000080"> #008787 </span>│<span style="color: #800080"> rgb(0,135,135)   </span>║
    ║ <span style="background-color: #0087d7">          </span> │<span style="color: #808000">     32 </span>│<span style="color: #008000"> "deep_sky_blue3"      </span>│<span style="color: #000080"> #0087d7 </span>│<span style="color: #800080"> rgb(0,135,215)   </span>║
    ║ <span style="background-color: #0087ff">          </span> │<span style="color: #808000">     33 </span>│<span style="color: #008000"> "dodger_blue1"        </span>│<span style="color: #000080"> #0087ff </span>│<span style="color: #800080"> rgb(0,135,255)   </span>║
    ║ <span style="background-color: #00af87">          </span> │<span style="color: #808000">     36 </span>│<span style="color: #008000"> "dark_cyan"           </span>│<span style="color: #000080"> #00af87 </span>│<span style="color: #800080"> rgb(0,175,135)   </span>║
    ║ <span style="background-color: #00afaf">          </span> │<span style="color: #808000">     37 </span>│<span style="color: #008000"> "light_sea_green"     </span>│<span style="color: #000080"> #00afaf </span>│<span style="color: #800080"> rgb(0,175,175)   </span>║
    ║ <span style="background-color: #00afd7">          </span> │<span style="color: #808000">     38 </span>│<span style="color: #008000"> "deep_sky_blue2"      </span>│<span style="color: #000080"> #00afd7 </span>│<span style="color: #800080"> rgb(0,175,215)   </span>║
    ║ <span style="background-color: #00afff">          </span> │<span style="color: #808000">     39 </span>│<span style="color: #008000"> "deep_sky_blue1"      </span>│<span style="color: #000080"> #00afff </span>│<span style="color: #800080"> rgb(0,175,255)   </span>║
    ║ <span style="background-color: #00d700">          </span> │<span style="color: #808000">     40 </span>│<span style="color: #008000"> "green3"              </span>│<span style="color: #000080"> #00d700 </span>│<span style="color: #800080"> rgb(0,215,0)     </span>║
    ║ <span style="background-color: #00d75f">          </span> │<span style="color: #808000">     41 </span>│<span style="color: #008000"> "spring_green3"       </span>│<span style="color: #000080"> #00d75f </span>│<span style="color: #800080"> rgb(0,215,95)    </span>║
    ║ <span style="background-color: #00d7af">          </span> │<span style="color: #808000">     43 </span>│<span style="color: #008000"> "cyan3"               </span>│<span style="color: #000080"> #00d7af </span>│<span style="color: #800080"> rgb(0,215,175)   </span>║
    ║ <span style="background-color: #00d7d7">          </span> │<span style="color: #808000">     44 </span>│<span style="color: #008000"> "dark_turquoise"      </span>│<span style="color: #000080"> #00d7d7 </span>│<span style="color: #800080"> rgb(0,215,215)   </span>║
    ║ <span style="background-color: #00d7ff">          </span> │<span style="color: #808000">     45 </span>│<span style="color: #008000"> "turquoise2"          </span>│<span style="color: #000080"> #00d7ff </span>│<span style="color: #800080"> rgb(0,215,255)   </span>║
    ║ <span style="background-color: #00ff00">          </span> │<span style="color: #808000">     46 </span>│<span style="color: #008000"> "green1"              </span>│<span style="color: #000080"> #00ff00 </span>│<span style="color: #800080"> rgb(0,255,0)     </span>║
    ║ <span style="background-color: #00ff5f">          </span> │<span style="color: #808000">     47 </span>│<span style="color: #008000"> "spring_green2"       </span>│<span style="color: #000080"> #00ff5f </span>│<span style="color: #800080"> rgb(0,255,95)    </span>║
    ║ <span style="background-color: #00ff87">          </span> │<span style="color: #808000">     48 </span>│<span style="color: #008000"> "spring_green1"       </span>│<span style="color: #000080"> #00ff87 </span>│<span style="color: #800080"> rgb(0,255,135)   </span>║
    ║ <span style="background-color: #00ffaf">          </span> │<span style="color: #808000">     49 </span>│<span style="color: #008000"> "medium_spring_green" </span>│<span style="color: #000080"> #00ffaf </span>│<span style="color: #800080"> rgb(0,255,175)   </span>║
    ║ <span style="background-color: #00ffd7">          </span> │<span style="color: #808000">     50 </span>│<span style="color: #008000"> "cyan2"               </span>│<span style="color: #000080"> #00ffd7 </span>│<span style="color: #800080"> rgb(0,255,215)   </span>║
    ║ <span style="background-color: #00ffff">          </span> │<span style="color: #808000">     51 </span>│<span style="color: #008000"> "cyan1"               </span>│<span style="color: #000080"> #00ffff </span>│<span style="color: #800080"> rgb(0,255,255)   </span>║
    ║ <span style="background-color: #5f00af">          </span> │<span style="color: #808000">     55 </span>│<span style="color: #008000"> "purple4"             </span>│<span style="color: #000080"> #5f00af </span>│<span style="color: #800080"> rgb(95,0,175)    </span>║
    ║ <span style="background-color: #5f00d7">          </span> │<span style="color: #808000">     56 </span>│<span style="color: #008000"> "purple3"             </span>│<span style="color: #000080"> #5f00d7 </span>│<span style="color: #800080"> rgb(95,0,215)    </span>║
    ║ <span style="background-color: #5f00ff">          </span> │<span style="color: #808000">     57 </span>│<span style="color: #008000"> "blue_violet"         </span>│<span style="color: #000080"> #5f00ff </span>│<span style="color: #800080"> rgb(95,0,255)    </span>║
    ║ <span style="background-color: #5f5f5f">          </span> │<span style="color: #808000">     59 </span>│<span style="color: #008000"> "grey37"              </span>│<span style="color: #000080"> #5f5f5f </span>│<span style="color: #800080"> rgb(95,95,95)    </span>║
    ║ <span style="background-color: #5f5f87">          </span> │<span style="color: #808000">     60 </span>│<span style="color: #008000"> "medium_purple4"      </span>│<span style="color: #000080"> #5f5f87 </span>│<span style="color: #800080"> rgb(95,95,135)   </span>║
    ║ <span style="background-color: #5f5fd7">          </span> │<span style="color: #808000">     62 </span>│<span style="color: #008000"> "slate_blue3"         </span>│<span style="color: #000080"> #5f5fd7 </span>│<span style="color: #800080"> rgb(95,95,215)   </span>║
    ║ <span style="background-color: #5f5fff">          </span> │<span style="color: #808000">     63 </span>│<span style="color: #008000"> "royal_blue1"         </span>│<span style="color: #000080"> #5f5fff </span>│<span style="color: #800080"> rgb(95,95,255)   </span>║
    ║ <span style="background-color: #5f8700">          </span> │<span style="color: #808000">     64 </span>│<span style="color: #008000"> "chartreuse4"         </span>│<span style="color: #000080"> #5f8700 </span>│<span style="color: #800080"> rgb(95,135,0)    </span>║
    ║ <span style="background-color: #5f8787">          </span> │<span style="color: #808000">     66 </span>│<span style="color: #008000"> "pale_turquoise4"     </span>│<span style="color: #000080"> #5f8787 </span>│<span style="color: #800080"> rgb(95,135,135)  </span>║
    ║ <span style="background-color: #5f87af">          </span> │<span style="color: #808000">     67 </span>│<span style="color: #008000"> "steel_blue"          </span>│<span style="color: #000080"> #5f87af </span>│<span style="color: #800080"> rgb(95,135,175)  </span>║
    ║ <span style="background-color: #5f87d7">          </span> │<span style="color: #808000">     68 </span>│<span style="color: #008000"> "steel_blue3"         </span>│<span style="color: #000080"> #5f87d7 </span>│<span style="color: #800080"> rgb(95,135,215)  </span>║
    ║ <span style="background-color: #5f87ff">          </span> │<span style="color: #808000">     69 </span>│<span style="color: #008000"> "cornflower_blue"     </span>│<span style="color: #000080"> #5f87ff </span>│<span style="color: #800080"> rgb(95,135,255)  </span>║
    ║ <span style="background-color: #5faf5f">          </span> │<span style="color: #808000">     71 </span>│<span style="color: #008000"> "dark_sea_green4"     </span>│<span style="color: #000080"> #5faf5f </span>│<span style="color: #800080"> rgb(95,175,95)   </span>║
    ║ <span style="background-color: #5fafaf">          </span> │<span style="color: #808000">     73 </span>│<span style="color: #008000"> "cadet_blue"          </span>│<span style="color: #000080"> #5fafaf </span>│<span style="color: #800080"> rgb(95,175,175)  </span>║
    ║ <span style="background-color: #5fafd7">          </span> │<span style="color: #808000">     74 </span>│<span style="color: #008000"> "sky_blue3"           </span>│<span style="color: #000080"> #5fafd7 </span>│<span style="color: #800080"> rgb(95,175,215)  </span>║
    ║ <span style="background-color: #5fd700">          </span> │<span style="color: #808000">     76 </span>│<span style="color: #008000"> "chartreuse3"         </span>│<span style="color: #000080"> #5fd700 </span>│<span style="color: #800080"> rgb(95,215,0)    </span>║
    ║ <span style="background-color: #5fd787">          </span> │<span style="color: #808000">     78 </span>│<span style="color: #008000"> "sea_green3"          </span>│<span style="color: #000080"> #5fd787 </span>│<span style="color: #800080"> rgb(95,215,135)  </span>║
    ║ <span style="background-color: #5fd7af">          </span> │<span style="color: #808000">     79 </span>│<span style="color: #008000"> "aquamarine3"         </span>│<span style="color: #000080"> #5fd7af </span>│<span style="color: #800080"> rgb(95,215,175)  </span>║
    ║ <span style="background-color: #5fd7d7">          </span> │<span style="color: #808000">     80 </span>│<span style="color: #008000"> "medium_turquoise"    </span>│<span style="color: #000080"> #5fd7d7 </span>│<span style="color: #800080"> rgb(95,215,215)  </span>║
    ║ <span style="background-color: #5fd7ff">          </span> │<span style="color: #808000">     81 </span>│<span style="color: #008000"> "steel_blue1"         </span>│<span style="color: #000080"> #5fd7ff </span>│<span style="color: #800080"> rgb(95,215,255)  </span>║
    ║ <span style="background-color: #5fff5f">          </span> │<span style="color: #808000">     83 </span>│<span style="color: #008000"> "sea_green2"          </span>│<span style="color: #000080"> #5fff5f </span>│<span style="color: #800080"> rgb(95,255,95)   </span>║
    ║ <span style="background-color: #5fffaf">          </span> │<span style="color: #808000">     85 </span>│<span style="color: #008000"> "sea_green1"          </span>│<span style="color: #000080"> #5fffaf </span>│<span style="color: #800080"> rgb(95,255,175)  </span>║
    ║ <span style="background-color: #5fffff">          </span> │<span style="color: #808000">     87 </span>│<span style="color: #008000"> "dark_slate_gray2"    </span>│<span style="color: #000080"> #5fffff </span>│<span style="color: #800080"> rgb(95,255,255)  </span>║
    ║ <span style="background-color: #870000">          </span> │<span style="color: #808000">     88 </span>│<span style="color: #008000"> "dark_red"            </span>│<span style="color: #000080"> #870000 </span>│<span style="color: #800080"> rgb(135,0,0)     </span>║
    ║ <span style="background-color: #8700af">          </span> │<span style="color: #808000">     91 </span>│<span style="color: #008000"> "dark_magenta"        </span>│<span style="color: #000080"> #8700af </span>│<span style="color: #800080"> rgb(135,0,175)   </span>║
    ║ <span style="background-color: #875f00">          </span> │<span style="color: #808000">     94 </span>│<span style="color: #008000"> "orange4"             </span>│<span style="color: #000080"> #875f00 </span>│<span style="color: #800080"> rgb(135,95,0)    </span>║
    ║ <span style="background-color: #875f5f">          </span> │<span style="color: #808000">     95 </span>│<span style="color: #008000"> "light_pink4"         </span>│<span style="color: #000080"> #875f5f </span>│<span style="color: #800080"> rgb(135,95,95)   </span>║
    ║ <span style="background-color: #875f87">          </span> │<span style="color: #808000">     96 </span>│<span style="color: #008000"> "plum4"               </span>│<span style="color: #000080"> #875f87 </span>│<span style="color: #800080"> rgb(135,95,135)  </span>║
    ║ <span style="background-color: #875fd7">          </span> │<span style="color: #808000">     98 </span>│<span style="color: #008000"> "medium_purple3"      </span>│<span style="color: #000080"> #875fd7 </span>│<span style="color: #800080"> rgb(135,95,215)  </span>║
    ║ <span style="background-color: #875fff">          </span> │<span style="color: #808000">     99 </span>│<span style="color: #008000"> "slate_blue1"         </span>│<span style="color: #000080"> #875fff </span>│<span style="color: #800080"> rgb(135,95,255)  </span>║
    ║ <span style="background-color: #87875f">          </span> │<span style="color: #808000">    101 </span>│<span style="color: #008000"> "wheat4"              </span>│<span style="color: #000080"> #87875f </span>│<span style="color: #800080"> rgb(135,135,95)  </span>║
    ║ <span style="background-color: #878787">          </span> │<span style="color: #808000">    102 </span>│<span style="color: #008000"> "grey53"              </span>│<span style="color: #000080"> #878787 </span>│<span style="color: #800080"> rgb(135,135,135) </span>║
    ║ <span style="background-color: #8787af">          </span> │<span style="color: #808000">    103 </span>│<span style="color: #008000"> "light_slate_grey"    </span>│<span style="color: #000080"> #8787af </span>│<span style="color: #800080"> rgb(135,135,175) </span>║
    ║ <span style="background-color: #8787d7">          </span> │<span style="color: #808000">    104 </span>│<span style="color: #008000"> "medium_purple"       </span>│<span style="color: #000080"> #8787d7 </span>│<span style="color: #800080"> rgb(135,135,215) </span>║
    ║ <span style="background-color: #8787ff">          </span> │<span style="color: #808000">    105 </span>│<span style="color: #008000"> "light_slate_blue"    </span>│<span style="color: #000080"> #8787ff </span>│<span style="color: #800080"> rgb(135,135,255) </span>║
    ║ <span style="background-color: #87af00">          </span> │<span style="color: #808000">    106 </span>│<span style="color: #008000"> "yellow4"             </span>│<span style="color: #000080"> #87af00 </span>│<span style="color: #800080"> rgb(135,175,0)   </span>║
    ║ <span style="background-color: #87af87">          </span> │<span style="color: #808000">    108 </span>│<span style="color: #008000"> "dark_sea_green"      </span>│<span style="color: #000080"> #87af87 </span>│<span style="color: #800080"> rgb(135,175,135) </span>║
    ║ <span style="background-color: #87afd7">          </span> │<span style="color: #808000">    110 </span>│<span style="color: #008000"> "light_sky_blue3"     </span>│<span style="color: #000080"> #87afd7 </span>│<span style="color: #800080"> rgb(135,175,215) </span>║
    ║ <span style="background-color: #87afff">          </span> │<span style="color: #808000">    111 </span>│<span style="color: #008000"> "sky_blue2"           </span>│<span style="color: #000080"> #87afff </span>│<span style="color: #800080"> rgb(135,175,255) </span>║
    ║ <span style="background-color: #87d700">          </span> │<span style="color: #808000">    112 </span>│<span style="color: #008000"> "chartreuse2"         </span>│<span style="color: #000080"> #87d700 </span>│<span style="color: #800080"> rgb(135,215,0)   </span>║
    ║ <span style="background-color: #87d787">          </span> │<span style="color: #808000">    114 </span>│<span style="color: #008000"> "pale_green3"         </span>│<span style="color: #000080"> #87d787 </span>│<span style="color: #800080"> rgb(135,215,135) </span>║
    ║ <span style="background-color: #87d7d7">          </span> │<span style="color: #808000">    116 </span>│<span style="color: #008000"> "dark_slate_gray3"    </span>│<span style="color: #000080"> #87d7d7 </span>│<span style="color: #800080"> rgb(135,215,215) </span>║
    ║ <span style="background-color: #87d7ff">          </span> │<span style="color: #808000">    117 </span>│<span style="color: #008000"> "sky_blue1"           </span>│<span style="color: #000080"> #87d7ff </span>│<span style="color: #800080"> rgb(135,215,255) </span>║
    ║ <span style="background-color: #87ff00">          </span> │<span style="color: #808000">    118 </span>│<span style="color: #008000"> "chartreuse1"         </span>│<span style="color: #000080"> #87ff00 </span>│<span style="color: #800080"> rgb(135,255,0)   </span>║
    ║ <span style="background-color: #87ff87">          </span> │<span style="color: #808000">    120 </span>│<span style="color: #008000"> "light_green"         </span>│<span style="color: #000080"> #87ff87 </span>│<span style="color: #800080"> rgb(135,255,135) </span>║
    ║ <span style="background-color: #87ffd7">          </span> │<span style="color: #808000">    122 </span>│<span style="color: #008000"> "aquamarine1"         </span>│<span style="color: #000080"> #87ffd7 </span>│<span style="color: #800080"> rgb(135,255,215) </span>║
    ║ <span style="background-color: #87ffff">          </span> │<span style="color: #808000">    123 </span>│<span style="color: #008000"> "dark_slate_gray1"    </span>│<span style="color: #000080"> #87ffff </span>│<span style="color: #800080"> rgb(135,255,255) </span>║
    ║ <span style="background-color: #af005f">          </span> │<span style="color: #808000">    125 </span>│<span style="color: #008000"> "deep_pink4"          </span>│<span style="color: #000080"> #af005f </span>│<span style="color: #800080"> rgb(175,0,95)    </span>║
    ║ <span style="background-color: #af0087">          </span> │<span style="color: #808000">    126 </span>│<span style="color: #008000"> "medium_violet_red"   </span>│<span style="color: #000080"> #af0087 </span>│<span style="color: #800080"> rgb(175,0,135)   </span>║
    ║ <span style="background-color: #af00d7">          </span> │<span style="color: #808000">    128 </span>│<span style="color: #008000"> "dark_violet"         </span>│<span style="color: #000080"> #af00d7 </span>│<span style="color: #800080"> rgb(175,0,215)   </span>║
    ║ <span style="background-color: #af00ff">          </span> │<span style="color: #808000">    129 </span>│<span style="color: #008000"> "purple"              </span>│<span style="color: #000080"> #af00ff </span>│<span style="color: #800080"> rgb(175,0,255)   </span>║
    ║ <span style="background-color: #af5faf">          </span> │<span style="color: #808000">    133 </span>│<span style="color: #008000"> "medium_orchid3"      </span>│<span style="color: #000080"> #af5faf </span>│<span style="color: #800080"> rgb(175,95,175)  </span>║
    ║ <span style="background-color: #af5fd7">          </span> │<span style="color: #808000">    134 </span>│<span style="color: #008000"> "medium_orchid"       </span>│<span style="color: #000080"> #af5fd7 </span>│<span style="color: #800080"> rgb(175,95,215)  </span>║
    ║ <span style="background-color: #af8700">          </span> │<span style="color: #808000">    136 </span>│<span style="color: #008000"> "dark_goldenrod"      </span>│<span style="color: #000080"> #af8700 </span>│<span style="color: #800080"> rgb(175,135,0)   </span>║
    ║ <span style="background-color: #af8787">          </span> │<span style="color: #808000">    138 </span>│<span style="color: #008000"> "rosy_brown"          </span>│<span style="color: #000080"> #af8787 </span>│<span style="color: #800080"> rgb(175,135,135) </span>║
    ║ <span style="background-color: #af87af">          </span> │<span style="color: #808000">    139 </span>│<span style="color: #008000"> "grey63"              </span>│<span style="color: #000080"> #af87af </span>│<span style="color: #800080"> rgb(175,135,175) </span>║
    ║ <span style="background-color: #af87d7">          </span> │<span style="color: #808000">    140 </span>│<span style="color: #008000"> "medium_purple2"      </span>│<span style="color: #000080"> #af87d7 </span>│<span style="color: #800080"> rgb(175,135,215) </span>║
    ║ <span style="background-color: #af87ff">          </span> │<span style="color: #808000">    141 </span>│<span style="color: #008000"> "medium_purple1"      </span>│<span style="color: #000080"> #af87ff </span>│<span style="color: #800080"> rgb(175,135,255) </span>║
    ║ <span style="background-color: #afaf5f">          </span> │<span style="color: #808000">    143 </span>│<span style="color: #008000"> "dark_khaki"          </span>│<span style="color: #000080"> #afaf5f </span>│<span style="color: #800080"> rgb(175,175,95)  </span>║
    ║ <span style="background-color: #afaf87">          </span> │<span style="color: #808000">    144 </span>│<span style="color: #008000"> "navajo_white3"       </span>│<span style="color: #000080"> #afaf87 </span>│<span style="color: #800080"> rgb(175,175,135) </span>║
    ║ <span style="background-color: #afafaf">          </span> │<span style="color: #808000">    145 </span>│<span style="color: #008000"> "grey69"              </span>│<span style="color: #000080"> #afafaf </span>│<span style="color: #800080"> rgb(175,175,175) </span>║
    ║ <span style="background-color: #afafd7">          </span> │<span style="color: #808000">    146 </span>│<span style="color: #008000"> "light_steel_blue3"   </span>│<span style="color: #000080"> #afafd7 </span>│<span style="color: #800080"> rgb(175,175,215) </span>║
    ║ <span style="background-color: #afafff">          </span> │<span style="color: #808000">    147 </span>│<span style="color: #008000"> "light_steel_blue"    </span>│<span style="color: #000080"> #afafff </span>│<span style="color: #800080"> rgb(175,175,255) </span>║
    ║ <span style="background-color: #afd75f">          </span> │<span style="color: #808000">    149 </span>│<span style="color: #008000"> "dark_olive_green3"   </span>│<span style="color: #000080"> #afd75f </span>│<span style="color: #800080"> rgb(175,215,95)  </span>║
    ║ <span style="background-color: #afd787">          </span> │<span style="color: #808000">    150 </span>│<span style="color: #008000"> "dark_sea_green3"     </span>│<span style="color: #000080"> #afd787 </span>│<span style="color: #800080"> rgb(175,215,135) </span>║
    ║ <span style="background-color: #afd7d7">          </span> │<span style="color: #808000">    152 </span>│<span style="color: #008000"> "light_cyan3"         </span>│<span style="color: #000080"> #afd7d7 </span>│<span style="color: #800080"> rgb(175,215,215) </span>║
    ║ <span style="background-color: #afd7ff">          </span> │<span style="color: #808000">    153 </span>│<span style="color: #008000"> "light_sky_blue1"     </span>│<span style="color: #000080"> #afd7ff </span>│<span style="color: #800080"> rgb(175,215,255) </span>║
    ║ <span style="background-color: #afff00">          </span> │<span style="color: #808000">    154 </span>│<span style="color: #008000"> "green_yellow"        </span>│<span style="color: #000080"> #afff00 </span>│<span style="color: #800080"> rgb(175,255,0)   </span>║
    ║ <span style="background-color: #afff5f">          </span> │<span style="color: #808000">    155 </span>│<span style="color: #008000"> "dark_olive_green2"   </span>│<span style="color: #000080"> #afff5f </span>│<span style="color: #800080"> rgb(175,255,95)  </span>║
    ║ <span style="background-color: #afff87">          </span> │<span style="color: #808000">    156 </span>│<span style="color: #008000"> "pale_green1"         </span>│<span style="color: #000080"> #afff87 </span>│<span style="color: #800080"> rgb(175,255,135) </span>║
    ║ <span style="background-color: #afffaf">          </span> │<span style="color: #808000">    157 </span>│<span style="color: #008000"> "dark_sea_green2"     </span>│<span style="color: #000080"> #afffaf </span>│<span style="color: #800080"> rgb(175,255,175) </span>║
    ║ <span style="background-color: #afffff">          </span> │<span style="color: #808000">    159 </span>│<span style="color: #008000"> "pale_turquoise1"     </span>│<span style="color: #000080"> #afffff </span>│<span style="color: #800080"> rgb(175,255,255) </span>║
    ║ <span style="background-color: #d70000">          </span> │<span style="color: #808000">    160 </span>│<span style="color: #008000"> "red3"                </span>│<span style="color: #000080"> #d70000 </span>│<span style="color: #800080"> rgb(215,0,0)     </span>║
    ║ <span style="background-color: #d70087">          </span> │<span style="color: #808000">    162 </span>│<span style="color: #008000"> "deep_pink3"          </span>│<span style="color: #000080"> #d70087 </span>│<span style="color: #800080"> rgb(215,0,135)   </span>║
    ║ <span style="background-color: #d700d7">          </span> │<span style="color: #808000">    164 </span>│<span style="color: #008000"> "magenta3"            </span>│<span style="color: #000080"> #d700d7 </span>│<span style="color: #800080"> rgb(215,0,215)   </span>║
    ║ <span style="background-color: #d75f00">          </span> │<span style="color: #808000">    166 </span>│<span style="color: #008000"> "dark_orange3"        </span>│<span style="color: #000080"> #d75f00 </span>│<span style="color: #800080"> rgb(215,95,0)    </span>║
    ║ <span style="background-color: #d75f5f">          </span> │<span style="color: #808000">    167 </span>│<span style="color: #008000"> "indian_red"          </span>│<span style="color: #000080"> #d75f5f </span>│<span style="color: #800080"> rgb(215,95,95)   </span>║
    ║ <span style="background-color: #d75f87">          </span> │<span style="color: #808000">    168 </span>│<span style="color: #008000"> "hot_pink3"           </span>│<span style="color: #000080"> #d75f87 </span>│<span style="color: #800080"> rgb(215,95,135)  </span>║
    ║ <span style="background-color: #d75faf">          </span> │<span style="color: #808000">    169 </span>│<span style="color: #008000"> "hot_pink2"           </span>│<span style="color: #000080"> #d75faf </span>│<span style="color: #800080"> rgb(215,95,175)  </span>║
    ║ <span style="background-color: #d75fd7">          </span> │<span style="color: #808000">    170 </span>│<span style="color: #008000"> "orchid"              </span>│<span style="color: #000080"> #d75fd7 </span>│<span style="color: #800080"> rgb(215,95,215)  </span>║
    ║ <span style="background-color: #d78700">          </span> │<span style="color: #808000">    172 </span>│<span style="color: #008000"> "orange3"             </span>│<span style="color: #000080"> #d78700 </span>│<span style="color: #800080"> rgb(215,135,0)   </span>║
    ║ <span style="background-color: #d7875f">          </span> │<span style="color: #808000">    173 </span>│<span style="color: #008000"> "light_salmon3"       </span>│<span style="color: #000080"> #d7875f </span>│<span style="color: #800080"> rgb(215,135,95)  </span>║
    ║ <span style="background-color: #d78787">          </span> │<span style="color: #808000">    174 </span>│<span style="color: #008000"> "light_pink3"         </span>│<span style="color: #000080"> #d78787 </span>│<span style="color: #800080"> rgb(215,135,135) </span>║
    ║ <span style="background-color: #d787af">          </span> │<span style="color: #808000">    175 </span>│<span style="color: #008000"> "pink3"               </span>│<span style="color: #000080"> #d787af </span>│<span style="color: #800080"> rgb(215,135,175) </span>║
    ║ <span style="background-color: #d787d7">          </span> │<span style="color: #808000">    176 </span>│<span style="color: #008000"> "plum3"               </span>│<span style="color: #000080"> #d787d7 </span>│<span style="color: #800080"> rgb(215,135,215) </span>║
    ║ <span style="background-color: #d787ff">          </span> │<span style="color: #808000">    177 </span>│<span style="color: #008000"> "violet"              </span>│<span style="color: #000080"> #d787ff </span>│<span style="color: #800080"> rgb(215,135,255) </span>║
    ║ <span style="background-color: #d7af00">          </span> │<span style="color: #808000">    178 </span>│<span style="color: #008000"> "gold3"               </span>│<span style="color: #000080"> #d7af00 </span>│<span style="color: #800080"> rgb(215,175,0)   </span>║
    ║ <span style="background-color: #d7af5f">          </span> │<span style="color: #808000">    179 </span>│<span style="color: #008000"> "light_goldenrod3"    </span>│<span style="color: #000080"> #d7af5f </span>│<span style="color: #800080"> rgb(215,175,95)  </span>║
    ║ <span style="background-color: #d7af87">          </span> │<span style="color: #808000">    180 </span>│<span style="color: #008000"> "tan"                 </span>│<span style="color: #000080"> #d7af87 </span>│<span style="color: #800080"> rgb(215,175,135) </span>║
    ║ <span style="background-color: #d7afaf">          </span> │<span style="color: #808000">    181 </span>│<span style="color: #008000"> "misty_rose3"         </span>│<span style="color: #000080"> #d7afaf </span>│<span style="color: #800080"> rgb(215,175,175) </span>║
    ║ <span style="background-color: #d7afd7">          </span> │<span style="color: #808000">    182 </span>│<span style="color: #008000"> "thistle3"            </span>│<span style="color: #000080"> #d7afd7 </span>│<span style="color: #800080"> rgb(215,175,215) </span>║
    ║ <span style="background-color: #d7afff">          </span> │<span style="color: #808000">    183 </span>│<span style="color: #008000"> "plum2"               </span>│<span style="color: #000080"> #d7afff </span>│<span style="color: #800080"> rgb(215,175,255) </span>║
    ║ <span style="background-color: #d7d700">          </span> │<span style="color: #808000">    184 </span>│<span style="color: #008000"> "yellow3"             </span>│<span style="color: #000080"> #d7d700 </span>│<span style="color: #800080"> rgb(215,215,0)   </span>║
    ║ <span style="background-color: #d7d75f">          </span> │<span style="color: #808000">    185 </span>│<span style="color: #008000"> "khaki3"              </span>│<span style="color: #000080"> #d7d75f </span>│<span style="color: #800080"> rgb(215,215,95)  </span>║
    ║ <span style="background-color: #d7d7af">          </span> │<span style="color: #808000">    187 </span>│<span style="color: #008000"> "light_yellow3"       </span>│<span style="color: #000080"> #d7d7af </span>│<span style="color: #800080"> rgb(215,215,175) </span>║
    ║ <span style="background-color: #d7d7d7">          </span> │<span style="color: #808000">    188 </span>│<span style="color: #008000"> "grey84"              </span>│<span style="color: #000080"> #d7d7d7 </span>│<span style="color: #800080"> rgb(215,215,215) </span>║
    ║ <span style="background-color: #d7d7ff">          </span> │<span style="color: #808000">    189 </span>│<span style="color: #008000"> "light_steel_blue1"   </span>│<span style="color: #000080"> #d7d7ff </span>│<span style="color: #800080"> rgb(215,215,255) </span>║
    ║ <span style="background-color: #d7ff00">          </span> │<span style="color: #808000">    190 </span>│<span style="color: #008000"> "yellow2"             </span>│<span style="color: #000080"> #d7ff00 </span>│<span style="color: #800080"> rgb(215,255,0)   </span>║
    ║ <span style="background-color: #d7ff87">          </span> │<span style="color: #808000">    192 </span>│<span style="color: #008000"> "dark_olive_green1"   </span>│<span style="color: #000080"> #d7ff87 </span>│<span style="color: #800080"> rgb(215,255,135) </span>║
    ║ <span style="background-color: #d7ffaf">          </span> │<span style="color: #808000">    193 </span>│<span style="color: #008000"> "dark_sea_green1"     </span>│<span style="color: #000080"> #d7ffaf </span>│<span style="color: #800080"> rgb(215,255,175) </span>║
    ║ <span style="background-color: #d7ffd7">          </span> │<span style="color: #808000">    194 </span>│<span style="color: #008000"> "honeydew2"           </span>│<span style="color: #000080"> #d7ffd7 </span>│<span style="color: #800080"> rgb(215,255,215) </span>║
    ║ <span style="background-color: #d7ffff">          </span> │<span style="color: #808000">    195 </span>│<span style="color: #008000"> "light_cyan1"         </span>│<span style="color: #000080"> #d7ffff </span>│<span style="color: #800080"> rgb(215,255,255) </span>║
    ║ <span style="background-color: #ff0000">          </span> │<span style="color: #808000">    196 </span>│<span style="color: #008000"> "red1"                </span>│<span style="color: #000080"> #ff0000 </span>│<span style="color: #800080"> rgb(255,0,0)     </span>║
    ║ <span style="background-color: #ff005f">          </span> │<span style="color: #808000">    197 </span>│<span style="color: #008000"> "deep_pink2"          </span>│<span style="color: #000080"> #ff005f </span>│<span style="color: #800080"> rgb(255,0,95)    </span>║
    ║ <span style="background-color: #ff00af">          </span> │<span style="color: #808000">    199 </span>│<span style="color: #008000"> "deep_pink1"          </span>│<span style="color: #000080"> #ff00af </span>│<span style="color: #800080"> rgb(255,0,175)   </span>║
    ║ <span style="background-color: #ff00d7">          </span> │<span style="color: #808000">    200 </span>│<span style="color: #008000"> "magenta2"            </span>│<span style="color: #000080"> #ff00d7 </span>│<span style="color: #800080"> rgb(255,0,215)   </span>║
    ║ <span style="background-color: #ff00ff">          </span> │<span style="color: #808000">    201 </span>│<span style="color: #008000"> "magenta1"            </span>│<span style="color: #000080"> #ff00ff </span>│<span style="color: #800080"> rgb(255,0,255)   </span>║
    ║ <span style="background-color: #ff5f00">          </span> │<span style="color: #808000">    202 </span>│<span style="color: #008000"> "orange_red1"         </span>│<span style="color: #000080"> #ff5f00 </span>│<span style="color: #800080"> rgb(255,95,0)    </span>║
    ║ <span style="background-color: #ff5f87">          </span> │<span style="color: #808000">    204 </span>│<span style="color: #008000"> "indian_red1"         </span>│<span style="color: #000080"> #ff5f87 </span>│<span style="color: #800080"> rgb(255,95,135)  </span>║
    ║ <span style="background-color: #ff5fd7">          </span> │<span style="color: #808000">    206 </span>│<span style="color: #008000"> "hot_pink"            </span>│<span style="color: #000080"> #ff5fd7 </span>│<span style="color: #800080"> rgb(255,95,215)  </span>║
    ║ <span style="background-color: #ff5fff">          </span> │<span style="color: #808000">    207 </span>│<span style="color: #008000"> "medium_orchid1"      </span>│<span style="color: #000080"> #ff5fff </span>│<span style="color: #800080"> rgb(255,95,255)  </span>║
    ║ <span style="background-color: #ff8700">          </span> │<span style="color: #808000">    208 </span>│<span style="color: #008000"> "dark_orange"         </span>│<span style="color: #000080"> #ff8700 </span>│<span style="color: #800080"> rgb(255,135,0)   </span>║
    ║ <span style="background-color: #ff875f">          </span> │<span style="color: #808000">    209 </span>│<span style="color: #008000"> "salmon1"             </span>│<span style="color: #000080"> #ff875f </span>│<span style="color: #800080"> rgb(255,135,95)  </span>║
    ║ <span style="background-color: #ff8787">          </span> │<span style="color: #808000">    210 </span>│<span style="color: #008000"> "light_coral"         </span>│<span style="color: #000080"> #ff8787 </span>│<span style="color: #800080"> rgb(255,135,135) </span>║
    ║ <span style="background-color: #ff87af">          </span> │<span style="color: #808000">    211 </span>│<span style="color: #008000"> "pale_violet_red1"    </span>│<span style="color: #000080"> #ff87af </span>│<span style="color: #800080"> rgb(255,135,175) </span>║
    ║ <span style="background-color: #ff87d7">          </span> │<span style="color: #808000">    212 </span>│<span style="color: #008000"> "orchid2"             </span>│<span style="color: #000080"> #ff87d7 </span>│<span style="color: #800080"> rgb(255,135,215) </span>║
    ║ <span style="background-color: #ff87ff">          </span> │<span style="color: #808000">    213 </span>│<span style="color: #008000"> "orchid1"             </span>│<span style="color: #000080"> #ff87ff </span>│<span style="color: #800080"> rgb(255,135,255) </span>║
    ║ <span style="background-color: #ffaf00">          </span> │<span style="color: #808000">    214 </span>│<span style="color: #008000"> "orange1"             </span>│<span style="color: #000080"> #ffaf00 </span>│<span style="color: #800080"> rgb(255,175,0)   </span>║
    ║ <span style="background-color: #ffaf5f">          </span> │<span style="color: #808000">    215 </span>│<span style="color: #008000"> "sandy_brown"         </span>│<span style="color: #000080"> #ffaf5f </span>│<span style="color: #800080"> rgb(255,175,95)  </span>║
    ║ <span style="background-color: #ffaf87">          </span> │<span style="color: #808000">    216 </span>│<span style="color: #008000"> "light_salmon1"       </span>│<span style="color: #000080"> #ffaf87 </span>│<span style="color: #800080"> rgb(255,175,135) </span>║
    ║ <span style="background-color: #ffafaf">          </span> │<span style="color: #808000">    217 </span>│<span style="color: #008000"> "light_pink1"         </span>│<span style="color: #000080"> #ffafaf </span>│<span style="color: #800080"> rgb(255,175,175) </span>║
    ║ <span style="background-color: #ffafd7">          </span> │<span style="color: #808000">    218 </span>│<span style="color: #008000"> "pink1"               </span>│<span style="color: #000080"> #ffafd7 </span>│<span style="color: #800080"> rgb(255,175,215) </span>║
    ║ <span style="background-color: #ffafff">          </span> │<span style="color: #808000">    219 </span>│<span style="color: #008000"> "plum1"               </span>│<span style="color: #000080"> #ffafff </span>│<span style="color: #800080"> rgb(255,175,255) </span>║
    ║ <span style="background-color: #ffd700">          </span> │<span style="color: #808000">    220 </span>│<span style="color: #008000"> "gold1"               </span>│<span style="color: #000080"> #ffd700 </span>│<span style="color: #800080"> rgb(255,215,0)   </span>║
    ║ <span style="background-color: #ffd787">          </span> │<span style="color: #808000">    222 </span>│<span style="color: #008000"> "light_goldenrod2"    </span>│<span style="color: #000080"> #ffd787 </span>│<span style="color: #800080"> rgb(255,215,135) </span>║
    ║ <span style="background-color: #ffd7af">          </span> │<span style="color: #808000">    223 </span>│<span style="color: #008000"> "navajo_white1"       </span>│<span style="color: #000080"> #ffd7af </span>│<span style="color: #800080"> rgb(255,215,175) </span>║
    ║ <span style="background-color: #ffd7d7">          </span> │<span style="color: #808000">    224 </span>│<span style="color: #008000"> "misty_rose1"         </span>│<span style="color: #000080"> #ffd7d7 </span>│<span style="color: #800080"> rgb(255,215,215) </span>║
    ║ <span style="background-color: #ffd7ff">          </span> │<span style="color: #808000">    225 </span>│<span style="color: #008000"> "thistle1"            </span>│<span style="color: #000080"> #ffd7ff </span>│<span style="color: #800080"> rgb(255,215,255) </span>║
    ║ <span style="background-color: #ffff00">          </span> │<span style="color: #808000">    226 </span>│<span style="color: #008000"> "yellow1"             </span>│<span style="color: #000080"> #ffff00 </span>│<span style="color: #800080"> rgb(255,255,0)   </span>║
    ║ <span style="background-color: #ffff5f">          </span> │<span style="color: #808000">    227 </span>│<span style="color: #008000"> "light_goldenrod1"    </span>│<span style="color: #000080"> #ffff5f </span>│<span style="color: #800080"> rgb(255,255,95)  </span>║
    ║ <span style="background-color: #ffff87">          </span> │<span style="color: #808000">    228 </span>│<span style="color: #008000"> "khaki1"              </span>│<span style="color: #000080"> #ffff87 </span>│<span style="color: #800080"> rgb(255,255,135) </span>║
    ║ <span style="background-color: #ffffaf">          </span> │<span style="color: #808000">    229 </span>│<span style="color: #008000"> "wheat1"              </span>│<span style="color: #000080"> #ffffaf </span>│<span style="color: #800080"> rgb(255,255,175) </span>║
    ║ <span style="background-color: #ffffd7">          </span> │<span style="color: #808000">    230 </span>│<span style="color: #008000"> "cornsilk1"           </span>│<span style="color: #000080"> #ffffd7 </span>│<span style="color: #800080"> rgb(255,255,215) </span>║
    ║ <span style="background-color: #ffffff">          </span> │<span style="color: #808000">    231 </span>│<span style="color: #008000"> "grey100"             </span>│<span style="color: #000080"> #ffffff </span>│<span style="color: #800080"> rgb(255,255,255) </span>║
    ║ <span style="background-color: #080808">          </span> │<span style="color: #808000">    232 </span>│<span style="color: #008000"> "grey3"               </span>│<span style="color: #000080"> #080808 </span>│<span style="color: #800080"> rgb(8,8,8)       </span>║
    ║ <span style="background-color: #121212">          </span> │<span style="color: #808000">    233 </span>│<span style="color: #008000"> "grey7"               </span>│<span style="color: #000080"> #121212 </span>│<span style="color: #800080"> rgb(18,18,18)    </span>║
    ║ <span style="background-color: #1c1c1c">          </span> │<span style="color: #808000">    234 </span>│<span style="color: #008000"> "grey11"              </span>│<span style="color: #000080"> #1c1c1c </span>│<span style="color: #800080"> rgb(28,28,28)    </span>║
    ║ <span style="background-color: #262626">          </span> │<span style="color: #808000">    235 </span>│<span style="color: #008000"> "grey15"              </span>│<span style="color: #000080"> #262626 </span>│<span style="color: #800080"> rgb(38,38,38)    </span>║
    ║ <span style="background-color: #303030">          </span> │<span style="color: #808000">    236 </span>│<span style="color: #008000"> "grey19"              </span>│<span style="color: #000080"> #303030 </span>│<span style="color: #800080"> rgb(48,48,48)    </span>║
    ║ <span style="background-color: #3a3a3a">          </span> │<span style="color: #808000">    237 </span>│<span style="color: #008000"> "grey23"              </span>│<span style="color: #000080"> #3a3a3a </span>│<span style="color: #800080"> rgb(58,58,58)    </span>║
    ║ <span style="background-color: #444444">          </span> │<span style="color: #808000">    238 </span>│<span style="color: #008000"> "grey27"              </span>│<span style="color: #000080"> #444444 </span>│<span style="color: #800080"> rgb(68,68,68)    </span>║
    ║ <span style="background-color: #4e4e4e">          </span> │<span style="color: #808000">    239 </span>│<span style="color: #008000"> "grey30"              </span>│<span style="color: #000080"> #4e4e4e </span>│<span style="color: #800080"> rgb(78,78,78)    </span>║
    ║ <span style="background-color: #585858">          </span> │<span style="color: #808000">    240 </span>│<span style="color: #008000"> "grey35"              </span>│<span style="color: #000080"> #585858 </span>│<span style="color: #800080"> rgb(88,88,88)    </span>║
    ║ <span style="background-color: #626262">          </span> │<span style="color: #808000">    241 </span>│<span style="color: #008000"> "grey39"              </span>│<span style="color: #000080"> #626262 </span>│<span style="color: #800080"> rgb(98,98,98)    </span>║
    ║ <span style="background-color: #6c6c6c">          </span> │<span style="color: #808000">    242 </span>│<span style="color: #008000"> "grey42"              </span>│<span style="color: #000080"> #6c6c6c </span>│<span style="color: #800080"> rgb(108,108,108) </span>║
    ║ <span style="background-color: #767676">          </span> │<span style="color: #808000">    243 </span>│<span style="color: #008000"> "grey46"              </span>│<span style="color: #000080"> #767676 </span>│<span style="color: #800080"> rgb(118,118,118) </span>║
    ║ <span style="background-color: #808080">          </span> │<span style="color: #808000">    244 </span>│<span style="color: #008000"> "grey50"              </span>│<span style="color: #000080"> #808080 </span>│<span style="color: #800080"> rgb(128,128,128) </span>║
    ║ <span style="background-color: #8a8a8a">          </span> │<span style="color: #808000">    245 </span>│<span style="color: #008000"> "grey54"              </span>│<span style="color: #000080"> #8a8a8a </span>│<span style="color: #800080"> rgb(138,138,138) </span>║
    ║ <span style="background-color: #949494">          </span> │<span style="color: #808000">    246 </span>│<span style="color: #008000"> "grey58"              </span>│<span style="color: #000080"> #949494 </span>│<span style="color: #800080"> rgb(148,148,148) </span>║
    ║ <span style="background-color: #9e9e9e">          </span> │<span style="color: #808000">    247 </span>│<span style="color: #008000"> "grey62"              </span>│<span style="color: #000080"> #9e9e9e </span>│<span style="color: #800080"> rgb(158,158,158) </span>║
    ║ <span style="background-color: #a8a8a8">          </span> │<span style="color: #808000">    248 </span>│<span style="color: #008000"> "grey66"              </span>│<span style="color: #000080"> #a8a8a8 </span>│<span style="color: #800080"> rgb(168,168,168) </span>║
    ║ <span style="background-color: #b2b2b2">          </span> │<span style="color: #808000">    249 </span>│<span style="color: #008000"> "grey70"              </span>│<span style="color: #000080"> #b2b2b2 </span>│<span style="color: #800080"> rgb(178,178,178) </span>║
    ║ <span style="background-color: #bcbcbc">          </span> │<span style="color: #808000">    250 </span>│<span style="color: #008000"> "grey74"              </span>│<span style="color: #000080"> #bcbcbc </span>│<span style="color: #800080"> rgb(188,188,188) </span>║
    ║ <span style="background-color: #c6c6c6">          </span> │<span style="color: #808000">    251 </span>│<span style="color: #008000"> "grey78"              </span>│<span style="color: #000080"> #c6c6c6 </span>│<span style="color: #800080"> rgb(198,198,198) </span>║
    ║ <span style="background-color: #d0d0d0">          </span> │<span style="color: #808000">    252 </span>│<span style="color: #008000"> "grey82"              </span>│<span style="color: #000080"> #d0d0d0 </span>│<span style="color: #800080"> rgb(208,208,208) </span>║
    ║ <span style="background-color: #dadada">          </span> │<span style="color: #808000">    253 </span>│<span style="color: #008000"> "grey85"              </span>│<span style="color: #000080"> #dadada </span>│<span style="color: #800080"> rgb(218,218,218) </span>║
    ║ <span style="background-color: #e4e4e4">          </span> │<span style="color: #808000">    254 </span>│<span style="color: #008000"> "grey89"              </span>│<span style="color: #000080"> #e4e4e4 </span>│<span style="color: #800080"> rgb(228,228,228) </span>║
    ║ <span style="background-color: #eeeeee">          </span> │<span style="color: #808000">    255 </span>│<span style="color: #008000"> "grey93"              </span>│<span style="color: #000080"> #eeeeee </span>│<span style="color: #800080"> rgb(238,238,238) </span>║
    ╚════════════╧════════╧═══════════════════════╧═════════╧══════════════════╝
    </pre>
```

## File: docs/source/reference/abc.rst
```
rich.abc
========

.. automodule:: rich.abc
    :members:
```

## File: docs/source/reference/align.rst
```
rich.align
==========

.. automodule:: rich.align
    :members:
```

## File: docs/source/reference/bar.rst
```
rich.bar
========

.. automodule:: rich.bar
    :members:
```

## File: docs/source/reference/color.rst
```
rich.color
==========

.. automodule:: rich.color
    :members:
```

## File: docs/source/reference/columns.rst
```
rich.columns
============

.. automodule:: rich.columns
    :members:
```

## File: docs/source/reference/console.rst
```
rich.console
============

.. automodule:: rich.console
    :members:
```

## File: docs/source/reference/control.rst
```
rich.control
============

.. automodule:: rich.control
    :members:
```

## File: docs/source/reference/emoji.rst
```
rich.emoji
==========

.. automodule:: rich.emoji
    :members: Emoji
```

## File: docs/source/reference/highlighter.rst
```
rich.highlighter
================

.. automodule:: rich.highlighter
    :members:
    :special-members: __call__
```

## File: docs/source/reference/init.rst
```
rich
====

.. automodule:: rich
    :members:
```

## File: docs/source/reference/json.rst
```
rich.json
=========

.. automodule:: rich.json
    :members:
```

## File: docs/source/reference/layout.rst
```
rich.layout
===========

.. automodule:: rich.layout
    :members:
```

## File: docs/source/reference/live.rst
```
rich.live
=========

.. automodule:: rich.live
    :members:
```

## File: docs/source/reference/logging.rst
```
.. _logging:

rich.logging
============

.. automodule:: rich.logging
    :members: RichHandler
```

## File: docs/source/reference/markdown.rst
```
rich.markdown
=============

.. automodule:: rich.markdown
    :members:
```

## File: docs/source/reference/markup.rst
```
rich.markup
===========

.. automodule:: rich.markup
    :members:
```

## File: docs/source/reference/measure.rst
```
rich.measure
============

.. automodule:: rich.measure
    :members:
```

## File: docs/source/reference/padding.rst
```
rich.padding
============

.. automodule:: rich.padding
    :members:
```

## File: docs/source/reference/panel.rst
```
rich.panel
==========

.. automodule:: rich.panel
    :members: Panel
```

## File: docs/source/reference/pretty.rst
```
rich.pretty
===========

.. automodule:: rich.pretty
    :members:
```

## File: docs/source/reference/progress_bar.rst
```
rich.progress_bar
=================

.. automodule:: rich.progress_bar
    :members:
```

## File: docs/source/reference/progress.rst
```
rich.progress
=============

.. automodule:: rich.progress
    :members:
```

## File: docs/source/reference/prompt.rst
```
rich.prompt
===========

.. automodule:: rich.prompt
    :members:
```

## File: docs/source/reference/protocol.rst
```
rich.protocol
=============

.. automodule:: rich.protocol
    :members:
```

## File: docs/source/reference/rule.rst
```
rich.rule
=========

.. automodule:: rich.rule
    :members:
```

## File: docs/source/reference/segment.rst
```
rich.segment
============

.. automodule:: rich.segment
    :members:
```

## File: docs/source/reference/spinner.rst
```
rich.spinner
============

.. automodule:: rich.spinner
    :members:
```

## File: docs/source/reference/status.rst
```
rich.status
============

.. automodule:: rich.status
    :members:
```

## File: docs/source/reference/style.rst
```
rich.style
==========

.. automodule:: rich.style
    :members:
    :special-members: __call__
```

## File: docs/source/reference/styled.rst
```
rich.styled
===========

.. automodule:: rich.styled
    :members:
```

## File: docs/source/reference/syntax.rst
```
rich.syntax
===========

.. automodule:: rich.syntax
    :members: Syntax
```

## File: docs/source/reference/table.rst
```
rich.table
==========

.. automodule:: rich.table
    :members:
```

## File: docs/source/reference/text.rst
```
rich.text
=========

.. automodule:: rich.text
    :members: Text, TextType
```

## File: docs/source/reference/theme.rst
```
rich.theme
==========

.. automodule:: rich.theme
    :members: Theme
```

## File: docs/source/reference/traceback.rst
```
rich.traceback
==============

.. automodule:: rich.traceback
    :members: Traceback, install
```

## File: docs/source/reference/tree.rst
```
rich.tree
=========

.. automodule:: rich.tree
    :members:
```

## File: docs/source/appendix.rst
```
Appendix
=========

.. toctree::
   :maxdepth: 3

   appendix/box.rst
   appendix/colors.rst
```

## File: docs/source/columns.rst
```
Columns
=======

Rich can render text or other Rich renderables in neat columns with the :class:`~rich.columns.Columns` class. To use, construct a Columns instance with an iterable of renderables and print it to the Console.

The following example is a very basic clone of the ``ls`` command in OSX / Linux to list directory contents::

    import os
    import sys

    from rich import print
    from rich.columns import Columns

    if len(sys.argv) < 2:
        print("Usage: python columns.py DIRECTORY")
    else:
        directory = os.listdir(sys.argv[1])
        columns = Columns(directory, equal=True, expand=True)
        print(columns)


See `columns.py <https://github.com/willmcgugan/rich/blob/master/examples/columns.py>`_ for an example which outputs columns containing more than just text.
```

## File: docs/source/console.rst
```
Console API
===========

For complete control over terminal formatting, Rich offers a :class:`~rich.console.Console` class. Most applications will require a single Console instance, so you may want to create one at the module level or as an attribute of your top-level object. For example, you could add a file called "console.py" to your project::

    from rich.console import Console
    console = Console()

Then you can import the console from anywhere in your project like this::

    from my_project.console import console

The console object handles the mechanics of generating ANSI escape sequences for color and style. It will auto-detect the capabilities of the terminal and convert colors if necessary.


Attributes
----------

The console will auto-detect a number of properties required when rendering.

* :obj:`~rich.console.Console.size` is the current dimensions of the terminal (which may change if you resize the window).
* :obj:`~rich.console.Console.encoding` is the default encoding (typically "utf-8").
* :obj:`~rich.console.Console.is_terminal` is a boolean that indicates if the Console instance is writing to a terminal or not.
* :obj:`~rich.console.Console.color_system` is a string containing the Console color system (see below).


Color systems
-------------

There are several "standards" for writing color to the terminal which are not all universally supported. Rich will auto-detect the appropriate color system, or you can set it manually by supplying a value for ``color_system`` to the :class:`~rich.console.Console` constructor.

You can set ``color_system`` to one of the following values:

* ``None`` Disables color entirely.
* ``"auto"`` Will auto-detect the color system.
* ``"standard"`` Can display 8 colors, with normal and bright variations, for 16 colors in total.
* ``"256"`` Can display the 16 colors from "standard" plus a fixed palette of 240 colors.
* ``"truecolor"`` Can display 16.7 million colors, which is likely all the colors your monitor can display.
* ``"windows"`` Can display 8 colors in legacy Windows terminal. New Windows terminal can display "truecolor".

.. warning::
    Be careful when setting a color system, if you set a higher color system than your terminal supports, your text may be unreadable.


Printing
--------

To write rich content to the terminal use the :meth:`~rich.console.Console.print` method. Rich will convert any object to a string via its (``__str__``) method and perform some simple syntax highlighting. It will also do pretty printing of any containers, such as dicts and lists. If you print a string it will render :ref:`console_markup`. Here are some examples::

    console.print([1, 2, 3])
    console.print("[blue underline]Looks like a link")
    console.print(locals())
    console.print("FOO", style="white on blue")

You can also use :meth:`~rich.console.Console.print` to render objects that support the :ref:`protocol`, which includes Rich's built-in objects such as :class:`~rich.text.Text`, :class:`~rich.table.Table`, and :class:`~rich.syntax.Syntax` -- or other custom objects.


Logging
-------

The :meth:`~rich.console.Console.log` method offers the same capabilities as print, but adds some features useful for debugging a running application. Logging writes the current time in a column to the left, and the file and line where the method was called to a column on the right. Here's an example::

    >>> console.log("Hello, World!")

.. raw:: html

    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #7fbfbf">[16:32:08] </span>Hello, World!                                         <span style="color: #7f7f7f">&lt;stdin&gt;:1</span>
    </pre>

To help with debugging, the log() method has a ``log_locals`` parameter. If you set this to ``True``, Rich will display a table of local variables where the method was called.


Printing JSON
-------------

The :meth:`~rich.console.Console.print_json` method will pretty print (format and style) a string containing JSON. Here's a short example::

    console.print_json('[false, true, null, "foo"]')

You can also *log* json by logging a :class:`~rich.json.JSON` object::

    from rich.json import JSON
    console.log(JSON('["foo", "bar"]'))

Because printing JSON is a common requirement, you may import ``print_json`` from the main namespace::

    from rich import print_json

You can also pretty print JSON via the command line with the following::

    python -m rich.json cats.json


Low level output
----------------

In additional to :meth:`~rich.console.Console.print` and :meth:`~rich.console.Console.log`, Rich has an :meth:`~rich.console.Console.out` method which provides a lower-level way of writing to the terminal. The out() method converts all the positional arguments to strings and won't pretty print, word wrap, or apply markup to the output, but can apply a basic style and will optionally do highlighting.

Here's an example::

    >>> console.out("Locals", locals())


Rules
-----

The :meth:`~rich.console.Console.rule` method will draw a horizontal line with an optional title, which is a good way of dividing your terminal output into sections.

    >>> console.rule("[bold red]Chapter 2")

.. raw:: html

    <pre style="font-family:Menlo,\'DejaVu Sans Mono\',consolas,\'Courier New\',monospace"><span style="color: #00ff00">─────────────────────────────── </span><span style="color: #800000; font-weight: bold">Chapter 2</span><span style="color: #00ff00"> ───────────────────────────────</span></pre>

The rule method also accepts a ``style`` parameter to set the style of the line, and an ``align`` parameter to align the title ("left", "center", or "right").


Status
------

Rich can display a status message with a 'spinner' animation that won't interfere with regular console output. Run the following command for a demo of this feature::

    python -m rich.status

To display a status message, call :meth:`~rich.console.Console.status` with the status message (which may be a string, Text, or other renderable). The result is a context manager which starts and stops the status display around a block of code. Here's an example::

    with console.status("Working..."):
        do_work()

You can change the spinner animation via the ``spinner`` parameter::

    with console.status("Monkeying around...", spinner="monkey"):
        do_work()

Run the following command to see the available choices for ``spinner``::

    python -m rich.spinner


Justify / Alignment
-------------------

Both print and log support a ``justify`` argument which if set must be one of "default", "left", "right", "center", or "full".  If "left", any text printed (or logged) will be left aligned, if "right" text will be aligned to the right of the terminal, if "center" the text will be centered, and if "full" the text will be lined up with both the left and right edges of the terminal (like printed text in a book).

The default for ``justify`` is ``"default"`` which will generally look the same as ``"left"`` but with a subtle difference. Left justify will pad the right of the text with spaces, while a default justify will not. You will only notice the difference if you set a background color with the ``style`` argument. The following example demonstrates the difference::

    from rich.console import Console

    console = Console(width=20)

    style = "bold white on blue"
    console.print("Rich", style=style)
    console.print("Rich", style=style, justify="left")
    console.print("Rich", style=style, justify="center")
    console.print("Rich", style=style, justify="right")


This produces the following output:

.. raw:: html

    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #c0c0c0; background-color: #000080; font-weight: bold">Rich
    Rich               &nbsp;
            Rich       &nbsp;
                    Rich
    </span></pre>

Overflow
--------

Overflow is what happens when text you print is larger than the available space. Overflow may occur if you print long 'words' such as URLs for instance, or if you have text inside a panel or table cell with restricted space.

You can specify how Rich should handle overflow with the ``overflow`` argument to :meth:`~rich.console.Console.print` which should be one of the following strings: "fold", "crop", "ellipsis", or "ignore". The default is "fold" which will put any excess characters on the following line, creating as many new lines as required to fit the text.

The "crop" method truncates the text at the end of the line, discarding any characters that would overflow.

The "ellipsis" method is similar to "crop", but will insert an ellipsis character ("…") at the end of any text that has been truncated.

The following code demonstrates the basic overflow methods::

    from typing import List
    from rich.console import Console, OverflowMethod

    console = Console(width=14)
    supercali = "supercalifragilisticexpialidocious"

    overflow_methods: List[OverflowMethod] = ["fold", "crop", "ellipsis"]
    for overflow in overflow_methods:
        console.rule(overflow)
        console.print(supercali, overflow=overflow, style="bold blue")
        console.print()

This produces the following output:

.. raw:: html

    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #00ff00">──── </span>fold<span style="color: #00ff00"> ────</span>
    <span style="color: #000080; font-weight: bold">supercalifragi
    listicexpialid
    ocious
    </span>
    <span style="color: #00ff00">──── </span>crop<span style="color: #00ff00"> ────</span>
    <span style="color: #000080; font-weight: bold">supercalifragi
    </span>
    <span style="color: #00ff00">── </span>ellipsis<span style="color: #00ff00"> ──</span>
    <span style="color: #000080; font-weight: bold">supercalifrag…
    </span>
    </pre>

You can also set overflow to "ignore" which allows text to run on to the next line. In practice this will look the same as "crop" unless you also set ``crop=False`` when calling :meth:`~rich.console.Console.print`.


Console style
-------------

The Console has a ``style`` attribute which you can use to apply a style to everything you print. By default ``style`` is None meaning no extra style is applied, but you can set it to any valid style. Here's an example of a Console with a style attribute set::

    from rich.console import Console
    blue_console = Console(style="white on blue")
    blue_console.print("I'm blue. Da ba dee da ba di.")


Soft Wrapping
-------------

Rich word wraps text you print by inserting line breaks. You can disable this behavior by setting ``soft_wrap=True`` when calling :meth:`~rich.console.Console.print`. With *soft wrapping* enabled any text that doesn't fit will run on to the following line(s), just like the built-in ``print``.


Cropping
--------

The :meth:`~rich.console.Console.print` method has a boolean ``crop`` argument. The default value for crop is True which tells Rich to crop any content that would otherwise run on to the next line. You generally don't need to think about cropping, as Rich will resize content to fit within the available width.

.. note::
    Cropping is automatically disabled if you print with ``soft_wrap=True``.


Input
-----

The console class has an :meth:`~rich.console.Console.input` method which works in the same way as Python's built-in :func:`input` function, but can use anything that Rich can print as a prompt. For example, here's a colorful prompt with an emoji::

    from rich.console import Console
    console = Console()
    console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")

If Python's builtin :mod:`readline` module is previously loaded, elaborate line editing and history features will be available.

Exporting
---------

The Console class can export anything written to it as either text, svg, or html. To enable exporting, first set ``record=True`` on the constructor. This tells Rich to save a copy of any data you ``print()`` or ``log()``. Here's an example::

    from rich.console import Console
    console = Console(record=True)

After you have written content, you can call :meth:`~rich.console.Console.export_text`, :meth:`~rich.console.Console.export_svg` or :meth:`~rich.console.Console.export_html` to get the console output as a string. You can also call :meth:`~rich.console.Console.save_text`, :meth:`~rich.console.Console.save_svg`, or :meth:`~rich.console.Console.save_html` to write the contents directly to disk.

For examples of the html output generated by Rich Console, see :ref:`appendix-colors`.

Exporting SVGs
^^^^^^^^^^^^^^

When using :meth:`~rich.console.Console.export_svg` or :meth:`~rich.console.Console.save_svg`, the width of the SVG will match the width of your terminal window (in terms of characters), while the height will scale automatically to accommodate the console output.

You can open the SVG in a web browser. You can also insert it in to a webpage with an ``<img>`` tag or by copying the markup in to your HTML.

The image below shows an example of an SVG exported by Rich.

.. image:: ../images/svg_export.svg

You can customize the theme used during SVG export by importing the desired theme from the :mod:`rich.terminal_theme` module and passing it to :meth:`~rich.console.Console.export_svg` or :meth:`~rich.console.Console.save_svg` via the ``theme`` parameter::


    from rich.console import Console
    from rich.terminal_theme import MONOKAI

    console = Console(record=True)
    console.save_svg("example.svg", theme=MONOKAI)

Alternatively, you can create a theme of your own by constructing a :class:`rich.terminal_theme.TerminalTheme` instance yourself and passing that in.

.. note::
    The SVGs reference the Fira Code font. If you embed a Rich SVG in your page, you may also want to add a link to the `Fira Code CSS <https://cdnjs.com/libraries/firacode>`_

Error console
-------------

The Console object will write to ``sys.stdout`` by default (so that you see output in the terminal). If you construct the Console with ``stderr=True`` Rich will write to ``sys.stderr``. You may want to use this to create an *error console* so you can split error messages from regular output. Here's an example::

    from rich.console import Console
    error_console = Console(stderr=True)

You might also want to set the ``style`` parameter on the Console to make error messages visually distinct. Here's how you might do that::

    error_console = Console(stderr=True, style="bold red")

File output
-----------

You can tell the Console object to write to a file by setting the ``file`` argument on the constructor -- which should be a file-like object opened for writing text. You could use this to write to a file without the output ever appearing on the terminal. Here's an example::

    import sys
    from rich.console import Console
    from datetime import datetime

    with open("report.txt", "wt") as report_file:
        console = Console(file=report_file)
        console.rule(f"Report Generated {datetime.now().ctime()}")

Note that when writing to a file you may want to explicitly set the ``width`` argument if you don't want to wrap the output to the current console width.

Capturing output
----------------

There may be situations where you want to *capture* the output from a Console rather than writing it directly to the terminal. You can do this with the :meth:`~rich.console.Console.capture` method which returns a context manager. On exit from this context manager, call :meth:`~rich.console.Capture.get` to return the string that would have been written to the terminal. Here's an example::

    from rich.console import Console
    console = Console()
    with console.capture() as capture:
        console.print("[bold red]Hello[/] World")
    str_output = capture.get()

An alternative way of capturing output is to set the Console file to a :py:class:`io.StringIO`. This is the recommended method if you are testing console output in unit tests. Here's an example::

    from io import StringIO
    from rich.console import Console
    console = Console(file=StringIO())
    console.print("[bold red]Hello[/] World")
    str_output = console.file.getvalue()

Paging
------

If you have some long output to present to the user you can use a *pager* to display it. A pager is typically an application on your operating system which will at least support pressing a key to scroll, but will often support scrolling up and down through the text and other features.

You can page output from a Console by calling :meth:`~rich.console.Console.pager` which returns a context manager. When the pager exits, anything that was printed will be sent to the pager. Here's an example::

    from rich.__main__ import make_test_card
    from rich.console import Console

    console = Console()
    with console.pager():
        console.print(make_test_card())

Since the default pager on most platforms don't support color, Rich will strip color from the output. If you know that your pager supports color, you can set ``styles=True`` when calling the :meth:`~rich.console.Console.pager` method.

.. note::
    Rich will look at ``MANPAGER`` then the ``PAGER`` environment variables (``MANPAGER`` takes priority) to get the pager command. On Linux and macOS you can set one of these to ``less -r`` to enable paging with ANSI styles.

Alternate screen
----------------

.. warning::
    This feature is currently experimental. You might want to wait before using it in production.

Terminals support an 'alternate screen' mode which is separate from the regular terminal and allows for full-screen applications that leave your stream of input and commands intact. Rich supports this mode via the :meth:`~rich.console.Console.set_alt_screen` method, although it is recommended that you use :meth:`~rich.console.Console.screen` which returns a context manager that disables alternate mode on exit.

Here's an example of an alternate screen::

    from time import sleep
    from rich.console import Console

    console = Console()
    with console.screen():
        console.print(locals())
        sleep(5)

The above code will display a pretty printed dictionary on the alternate screen before returning to the command prompt after 5 seconds.

You can also provide a renderable to :meth:`~rich.console.Console.screen` which will be displayed in the alternate screen when you call :meth:`~rich.ScreenContext.update`.

Here's an example::

    from time import sleep

    from rich.console import Console
    from rich.align import Align
    from rich.text import Text
    from rich.panel import Panel

    console = Console()

    with console.screen(style="bold white on red") as screen:
        for count in range(5, 0, -1):
            text = Align.center(
                Text.from_markup(f"[blink]Don't Panic![/blink]\n{count}", justify="center"),
                vertical="middle",
            )
            screen.update(Panel(text))
            sleep(1)

Updating the screen with a renderable allows Rich to crop the contents to fit the screen without scrolling.

For a more powerful way of building full screen interfaces with Rich, see :ref:`live`.


.. note::
    If you ever find yourself stuck in alternate mode after exiting Python code, type ``reset`` in the terminal

Terminal detection
------------------

If Rich detects that it is not writing to a terminal it will strip control codes from the output. If you want to write control codes to a regular file then set ``force_terminal=True`` on the constructor.

Letting Rich auto-detect terminals is useful as it will write plain text when you pipe output to a file or other application.

.. _interactive_mode:

Interactive mode
----------------

Rich will remove animations such as progress bars and status indicators when not writing to a terminal as you probably don't want to write these out to a text file (for example). You can override this behavior by setting the ``force_interactive`` argument on the constructor. Set it to ``True`` to enable animations or ``False`` to disable them.


Environment variables
---------------------

Rich respects some standard environment variables.

Setting the environment variable ``TERM`` to ``"dumb"`` or ``"unknown"`` will disable color/style and some features that require moving the cursor, such as progress bars.

If the environment variable ``FORCE_COLOR`` is set and non-empty, then color/styles will be enabled regardless of the value of ``TERM``.

If the environment variable ``NO_COLOR`` is set, Rich will disable all color in the output. ``NO_COLOR`` takes precedence over ``FORCE_COLOR``. See `no_color <https://no-color.org/>`_ for details.

.. note::
    The ``NO_COLOR`` environment variable removes *color* only. Styles such as dim, bold, italic, underline etc. are preserved.

The environment variable ``TTY_COMPATIBLE`` is used to override Rich's auto-detection of terminal support. If ``TTY_COMPATIBLE`` is set to ``1`` then Rich will assume it is writing to a device which can handle escape sequences like a terminal. If ``TTY_COMPATIBLE`` is set to ``"0"``, then Rich will assume that it is writing to a device that is *not* capable of displaying escape sequences (such as a regular file). If the variable is not set, or set to a value other than "0" or "1", then Rich will attempt to auto-detect terminal support.

The environment variable ``TTY_INTERACTIVE`` is used to override Rich's auto-detection of :ref:`interactive_mode`. If you set this to ``"0"``, it will disable interactive mode even if Rich thinks it is writing to a terminal. Set this to ``"1"`` to force interactive mode on. If this environment variable is not set, or set to any other value, then interactive mode will be auto-detected as normal.

.. note::
    If you want Rich output in CI or Github Actions, then you should set ``TTY_COMPATIBLE=1`` and ``TTY_INTERACTIVE=0``. The combination of both these variables tells rich that it can output escape sequences,
    and also that there is no user interacting with the terminal -- so it won't bother animating progress bars.

If ``width`` / ``height`` arguments are not explicitly provided as arguments to ``Console`` then the environment variables ``COLUMNS`` / ``LINES`` can be used to set the console width / height. ``JUPYTER_COLUMNS`` / ``JUPYTER_LINES`` behave similarly and are used in Jupyter.

Note that environment variables set defaults in the Console object. If you explicitly set any variables in the constructor then these will take precedence.
```

## File: docs/source/group.rst
```
Render Groups
=============

The :class:`~rich.console.Group` class allows you to group several renderables together so they may be rendered in a context where only a single renderable may be supplied. For instance, you might want to display several renderables within a :class:`~rich.panel.Panel`.

To render two panels within a third panel, you would construct a Group with the *child* renderables as positional arguments then wrap the result in another Panel::

    from rich import print
    from rich.console import Group
    from rich.panel import Panel

    panel_group = Group(
        Panel("Hello", style="on blue"),
        Panel("World", style="on red"),
    )
    print(Panel(panel_group))


This pattern is nice when you know in advance what renderables will be in a group, but can get awkward if you have a larger number of renderables, especially if they are dynamic. Rich provides a :func:`~rich.console.group` decorator to help with these situations. The decorator builds a group from an iterator of renderables. The following is the equivalent of the previous example using the decorator::

    from rich import print
    from rich.console import group
    from rich.panel import Panel

    @group()
    def get_panels():
        yield Panel("Hello", style="on blue")
        yield Panel("World", style="on red")

    print(Panel(get_panels()))
```

## File: docs/source/highlighting.rst
```
.. _highlighting:

Highlighting
============

Rich will automatically highlight patterns in text, such as numbers, strings, collections, booleans, None, and a few more exotic patterns such as file paths, URLs and UUIDs.

You can disable highlighting either by setting ``highlight=False`` on :meth:`~rich.console.Console.print` or :meth:`~rich.console.Console.log`, or by setting ``highlight=False`` on the :class:`~rich.console.Console` constructor which disables it everywhere. If you disable highlighting on the constructor, you can still selectively *enable* highlighting with ``highlight=True`` on print / log.

Custom Highlighters
-------------------

If the default highlighting doesn't fit your needs, you can define a custom highlighter. The easiest way to do this is to extend the :class:`~rich.highlighter.RegexHighlighter` class which applies a style to any text matching a list of regular expressions.

Here's an example which highlights text that looks like an email address::

    from rich.console import Console
    from rich.highlighter import RegexHighlighter
    from rich.theme import Theme

    class EmailHighlighter(RegexHighlighter):
        """Apply style to anything that looks like an email."""

        base_style = "example."
        highlights = [r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)"]


    theme = Theme({"example.email": "bold magenta"})
    console = Console(highlighter=EmailHighlighter(), theme=theme)
    console.print("Send funds to money@example.org")


The ``highlights`` class variable should contain a list of regular expressions. The group names of any matching expressions are prefixed with the ``base_style`` attribute and used as styles for matching text. In the example above, any email addresses will have the style "example.email" applied, which we've defined in a custom :ref:`Theme <themes>`.

Setting the highlighter on the Console will apply highlighting to all text you print (if enabled). You can also use a highlighter on a more granular level by using the instance as a callable and printing the result. For example, we could use the email highlighter class like this::


    console = Console(theme=theme)
    highlight_emails = EmailHighlighter()
    console.print(highlight_emails("Send funds to money@example.org"))


While :class:`~rich.highlighter.RegexHighlighter` is quite powerful, you can also extend its base class :class:`~rich.highlighter.Highlighter` to implement a custom scheme for highlighting. It contains a single method :class:`~rich.highlighter.Highlighter.highlight` which is passed the :class:`~rich.text.Text` to highlight.

Here's a silly example that highlights every character with a different color::

    from random import randint

    from rich import print
    from rich.highlighter import Highlighter


    class RainbowHighlighter(Highlighter):
        def highlight(self, text):
            for index in range(len(text)):
                text.stylize(f"color({randint(16, 255)})", index, index + 1)


    rainbow = RainbowHighlighter()
    print(rainbow("I must not fear. Fear is the mind-killer."))

Builtin Highlighters
--------------------

The following builtin highlighters are available.

* :class:`~rich.highlighter.ISO8601Highlighter` Highlights ISO8601 date time strings.
* :class:`~rich.highlighter.JSONHighlighter` Highlights JSON formatted strings.
```

## File: docs/source/index.rst
```
.. Rich documentation master file, created by
   sphinx-quickstart on Thu Dec 26 17:03:20 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Rich's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction.rst
   console.rst
   style.rst
   markup.rst
   text.rst
   highlighting.rst
   pretty.rst
   logging.rst
   traceback.rst
   prompt.rst

   columns.rst
   group.rst   
   markdown.rst
   padding.rst
   panel.rst
   progress.rst
   syntax.rst
   tables.rst
   tree.rst
   live.rst
   layout.rst

   protocol.rst

   reference.rst
   appendix.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

## File: docs/source/introduction.rst
```
Introduction
============

Rich is a Python library for writing *rich* text (with color and style) to the terminal, and for displaying advanced content such as tables, markdown, and syntax highlighted code.

Use Rich to make your command line applications visually appealing and present data in a more readable way. Rich can also be a useful debugging aid by pretty printing and syntax highlighting data structures.

Requirements
------------

Rich works with macOS, Linux and Windows.

On Windows both the (ancient) cmd.exe terminal is supported and the new `Windows Terminal <https://github.com/microsoft/terminal/releases>`_. The latter has much improved support for color and style.

Rich requires Python 3.8.0 and above.

.. note::
    PyCharm users will need to enable "emulate terminal" in output console option in run/debug configuration to see styled output.

Installation
------------

You can install Rich from PyPI with `pip` or your favorite package manager::

    pip install rich

Add the ``-U`` switch to update to the current version, if Rich is already installed.

If you intend to use Rich with Jupyter then there are some additional dependencies which you can install with the following command::

    pip install "rich[jupyter]"

Demo
----

To check if Rich was installed correctly, and to see a little of what Rich can do, run the following from the command line::

    python -m rich

Quick Start
-----------

The quickest way to get up and running with Rich is to import the alternative ``print`` function which takes the same arguments as the built-in ``print`` and may be used as a drop-in replacement. Here's how you would do that::

    from rich import print

You can then print strings or objects to the terminal in the usual way. Rich will do some basic syntax :ref:`highlighting<highlighting>` and format data structures to make them easier to read.

Strings may contain :ref:`console_markup` which can be used to insert color and styles in to the output.

The following demonstrates both console markup and pretty formatting of Python objects::

    >>> print("[italic red]Hello[/italic red] World!", locals())

This writes the following output to the terminal (including all the colors and styles):

.. raw:: html

    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800000; font-style: italic">Hello</span> World!
    <span style="font-weight: bold">{</span>
        <span style="color: #008000">'__annotations__'</span>: <span style="font-weight: bold">{}</span>,
        <span style="color: #008000">'__builtins__'</span>: <span style="font-weight: bold"><</span><span style="color: #ff00ff">module</span><span style="color: #000000"> </span><span style="color: #008000">'builtins'</span><span style="color: #000000"> </span><span style="color: #000000; font-weight: bold">(</span><span style="color: #000000">built-in</span><span style="color: #000000; font-weight: bold">)</span><span style="font-weight: bold">></span>,
        <span style="color: #008000">'__doc__'</span>: <span style="color: #800080; font-style: italic">None</span>,
        <span style="color: #008000">'__loader__'</span>: <span style="font-weight: bold"><</span><span style="color: #ff00ff">class</span><span style="color: #000000"> </span><span style="color: #008000">'_frozen_importlib.BuiltinImporter'</span><span style="font-weight: bold">></span>,
        <span style="color: #008000">'__name__'</span>: <span style="color: #008000">'__main__'</span>,
        <span style="color: #008000">'__package__'</span>: <span style="color: #800080; font-style: italic">None</span>,
        <span style="color: #008000">'__spec__'</span>: <span style="color: #800080; font-style: italic">None</span>,
        <span style="color: #008000">'print'</span>: <span style="font-weight: bold"><</span><span style="color: #ff00ff">function</span><span style="color: #000000"> print at </span><span style="color: #000080; font-weight: bold">0x1027fd4c0</span><span style="font-weight: bold">></span>,
    <span style="font-weight: bold">}</span> </pre>


If you would rather not shadow Python's built-in print, you can import ``rich.print`` as ``rprint`` (for example)::

    from rich import print as rprint

Continue reading to learn about the more advanced features of Rich.

Rich in the REPL
----------------

Rich may be installed in the REPL so that Python data structures are automatically pretty printed with syntax highlighting. Here's how::

    >>> from rich import pretty
    >>> pretty.install()
    >>> ["Rich and pretty", True]

You can also use this feature to try out Rich *renderables*. Here's an example::

    >>> from rich.panel import Panel
    >>> Panel.fit("[bold yellow]Hi, I'm a Panel", border_style="red")

Read on to learn more about Rich renderables.

IPython Extension
~~~~~~~~~~~~~~~~~

Rich also includes an IPython extension that will do this same pretty install + pretty tracebacks. Here's how to load it::

    In [1]: %load_ext rich

You can also have it load by default by adding `"rich"` to the ``c.InteractiveShellApp.extension`` variable in
`IPython Configuration <https://ipython.readthedocs.io/en/stable/config/intro.html>`_.

Rich Inspect
------------

Rich has an :meth:`~rich.inspect` function which can generate a report on any Python object. It is a fantastic debug aid, and a good example of the output that Rich can generate. Here is a simple example::

    >>> from rich import inspect
    >>> from rich.color import Color
    >>> color = Color.parse("red")
    >>> inspect(color, methods=True)
```

## File: docs/source/layout.rst
```
Layout
======

Rich offers a :class:`~rich.layout.Layout` class which can be used to divide the screen area in to parts, where each part may contain independent content. It can be used with :ref:`Live` to create full-screen "applications" but may be used standalone.

To see an example of a Layout, run the following from the command line::

    python -m rich.layout

Creating layouts
----------------

To define a layout, construct a Layout object and print it::

    from rich import print
    from rich.layout import Layout

    layout = Layout()
    print(layout)

This will draw a box the size of the terminal with some information regarding the layout. The box is a "placeholder" because we have yet to add any content to it. Before we do that, let's create a more interesting layout by calling the :meth:`~rich.layout.Layout.split_column` method to divide the layout in to two sub-layouts::

    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )
    print(layout)

This will divide the terminal screen in to two equal sized portions, one on top of the other. The ``name`` attribute is an internal identifier we can use to look up the sub-layout later. Let's use that to create another split, this time we will call :meth:`~rich.layout.Layout.split_row` to split the lower layout in to a row of two sub-layouts::

    layout["lower"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    print(layout)

You should now see the screen area divided in to 3 portions; an upper half and a lower half that is split in to two quarters.

.. raw:: html

    <pre style="font-size:90%;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080">╭─────────────────────────────── </span><span style="color: #008000">'upper'</span><span style="color: #000080"> </span><span style="color: #000080; font-weight: bold">(</span><span style="color: #000080; font-weight: bold">84</span><span style="color: #000080"> x </span><span style="color: #000080; font-weight: bold">13</span><span style="color: #000080; font-weight: bold">)</span><span style="color: #000080"> ────────────────────────────────╮</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>          <span style="font-weight: bold">{</span><span style="color: #008000">'size'</span>: <span style="color: #800080; font-style: italic">None</span>, <span style="color: #008000">'minimum_size'</span>: <span style="color: #000080; font-weight: bold">1</span>, <span style="color: #008000">'ratio'</span>: <span style="color: #000080; font-weight: bold">1</span>, <span style="color: #008000">'name'</span>: <span style="color: #008000">'upper'</span><span style="font-weight: bold">}</span>          <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                                                                  <span style="color: #000080">│</span>
    <span style="color: #000080">╰──────────────────────────────────────────────────────────────────────────────────╯</span>
    <span style="color: #000080">╭─────────── </span><span style="color: #008000">'left'</span><span style="color: #000080"> </span><span style="color: #000080; font-weight: bold">(</span><span style="color: #000080; font-weight: bold">42</span><span style="color: #000080"> x </span><span style="color: #000080; font-weight: bold">14</span><span style="color: #000080; font-weight: bold">)</span><span style="color: #000080"> ───────────╮╭────────── </span><span style="color: #008000">'right'</span><span style="color: #000080"> </span><span style="color: #000080; font-weight: bold">(</span><span style="color: #000080; font-weight: bold">42</span><span style="color: #000080"> x </span><span style="color: #000080; font-weight: bold">14</span><span style="color: #000080; font-weight: bold">)</span><span style="color: #000080"> ───────────╮</span>
    <span style="color: #000080">│</span>                                        <span style="color: #000080">││</span>                                        <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                        <span style="color: #000080">││</span>                                        <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                        <span style="color: #000080">││</span>                                        <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>         <span style="font-weight: bold">{</span>                              <span style="color: #000080">││</span>         <span style="font-weight: bold">{</span>                              <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>             <span style="color: #008000">'size'</span>: <span style="color: #800080; font-style: italic">None</span>,              <span style="color: #000080">││</span>             <span style="color: #008000">'size'</span>: <span style="color: #800080; font-style: italic">None</span>,              <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>             <span style="color: #008000">'minimum_size'</span>: <span style="color: #000080; font-weight: bold">1</span>,         <span style="color: #000080">││</span>             <span style="color: #008000">'minimum_size'</span>: <span style="color: #000080; font-weight: bold">1</span>,         <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>             <span style="color: #008000">'ratio'</span>: <span style="color: #000080; font-weight: bold">1</span>,                <span style="color: #000080">││</span>             <span style="color: #008000">'ratio'</span>: <span style="color: #000080; font-weight: bold">1</span>,                <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>             <span style="color: #008000">'name'</span>: <span style="color: #008000">'left'</span>             <span style="color: #000080">││</span>             <span style="color: #008000">'name'</span>: <span style="color: #008000">'right'</span>            <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>         <span style="font-weight: bold">}</span>                              <span style="color: #000080">││</span>         <span style="font-weight: bold">}</span>                              <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                        <span style="color: #000080">││</span>                                        <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                        <span style="color: #000080">││</span>                                        <span style="color: #000080">│</span>
    <span style="color: #000080">│</span>                                        <span style="color: #000080">││</span>                                        <span style="color: #000080">│</span>
    <span style="color: #000080">╰────────────────────────────────────────╯╰────────────────────────────────────────╯</span>
    </pre>

You can continue to call split() in this way to create as many parts to the screen as you wish.

Setting renderables
-------------------

The first position argument to ``Layout`` can be any Rich renderable, which will be sized to fit within the layout's area. Here's how we might divide the "right" layout in to two panels::

    from rich.panel import Panel
    
    layout["right"].split(
        Layout(Panel("Hello")),
        Layout(Panel("World!"))
    )

You can also call :meth:`~rich.layout.Layout.update` to set or replace the current renderable::

    layout["left"].update(
        "The mystery of life isn't a problem to solve, but a reality to experience."
    )
    print(layout)

Fixed size
----------

You can set a layout to use a fixed size by setting the ``size`` argument on the Layout constructor or by setting the attribute. Here's an example::

    layout["upper"].size = 10
    print(layout)

This will set the upper portion to be exactly 10 rows, no matter the size of the terminal. If the parent layout is horizontal rather than vertical, then the size applies to the number of characters rather that rows.

Ratio
-----

In addition to a fixed size, you can also make a flexible layout setting the ``ratio`` argument on the constructor or by assigning to the attribute. The ratio defines how much of the screen the layout should occupy in relation to other layouts. For example, let's reset the size and set the ratio of the upper layout to 2::

    layout["upper"].size = None
    layout["upper"].ratio = 2
    print(layout)

This makes the top layout take up two thirds of the space. This is because the default ratio is 1, giving the upper and lower layouts a combined total of 3. As the upper layout has a ratio of 2, it takes up two thirds of the space, leaving the remaining third for the lower layout.

A layout with a ratio set may also have a minimum size to prevent it from getting too small. For instance, here's how we could set the minimum size of the lower sub-layout so that it won't shrink beyond 10 rows::

    layout["lower"].minimum_size = 10

Visibility
----------

You can make a layout invisible by setting the ``visible`` attribute to False. Here's an example::

    layout["upper"].visible = False
    print(layout)

The top layout is now invisible, and the "lower" layout will expand to fill the available space. Set ``visible`` to True to bring it back::

    layout["upper"].visible = True
    print(layout)

You could use this to toggle parts of your interface based on your application's configuration.

Tree
----

To help visualize complex layouts you can print the ``tree`` attribute which will display a summary of the layout as a tree::

    print(layout.tree)


Example
-------

See `fullscreen.py <https://github.com/willmcgugan/rich/blob/master/examples/fullscreen.py>`_ for an example that combines :class:`~rich.layout.Layout` and :class:`~rich.live.Live` to create a fullscreen "application".
```

## File: docs/source/live.rst
```
.. _live:

Live Display
============

Progress bars and status indicators use a *live* display to animate parts of the terminal. You can build custom live displays with the :class:`~rich.live.Live` class.

For a demonstration of a live display, run the following command::

    python -m rich.live

.. note::

    If you see ellipsis "...", this indicates that the terminal is not tall enough to show the full table.

Basic usage
~~~~~~~~~~~

To create a live display, construct a :class:`~rich.live.Live` object with a renderable and use it as a context manager. The live display will persist for the duration of the context. You can update the renderable to update the display::


    import time

    from rich.live import Live
    from rich.table import Table

    table = Table()
    table.add_column("Row ID")
    table.add_column("Description")
    table.add_column("Level")

    with Live(table, refresh_per_second=4):  # update 4 times a second to feel fluid
        for row in range(12):
            time.sleep(0.4)  # arbitrary delay
            # update the renderable internally
            table.add_row(f"{row}", f"description {row}", "[red]ERROR")


Updating the renderable
~~~~~~~~~~~~~~~~~~~~~~~

You can also change the renderable on-the-fly by calling the :meth:`~rich.live.Live.update` method. This may be useful if the information you wish to display is too dynamic to generate by updating a single renderable. Here is an example::

    import random
    import time

    from rich.live import Live
    from rich.table import Table


    def generate_table() -> Table:
        """Make a new table."""
        table = Table()
        table.add_column("ID")
        table.add_column("Value")
        table.add_column("Status")

        for row in range(random.randint(2, 6)):
            value = random.random() * 100
            table.add_row(
                f"{row}", f"{value:3.2f}", "[red]ERROR" if value < 50 else "[green]SUCCESS"
            )
        return table


    with Live(generate_table(), refresh_per_second=4) as live:
        for _ in range(40):
            time.sleep(0.4)
            live.update(generate_table())


Alternate screen
~~~~~~~~~~~~~~~~

You can opt to show a Live display in the "alternate screen" by setting ``screen=True`` on the constructor. This will allow your live display to go full screen and restore the command prompt on exit.

You can use this feature in combination with :ref:`Layout` to display sophisticated terminal "applications".

Transient display
~~~~~~~~~~~~~~~~~

Normally when you exit live context manager (or call :meth:`~rich.live.Live.stop`) the last refreshed item remains in the terminal with the cursor on the following line.
You can also make the live display disappear on exit by setting ``transient=True`` on the Live constructor.

Auto refresh
~~~~~~~~~~~~

By default, the live display will refresh 4 times a second. You can set the refresh rate with the ``refresh_per_second`` argument on the :class:`~rich.live.Live` constructor.
You should set this to something lower than 4 if you know your updates will not be that frequent or higher for a smoother feeling.

You might want to disable auto-refresh entirely if your updates are not very frequent, which you can do by setting ``auto_refresh=False`` on the constructor.
If you disable auto-refresh you will need to call :meth:`~rich.live.Live.refresh` manually or :meth:`~rich.live.Live.update` with ``refresh=True``.

Vertical overflow
~~~~~~~~~~~~~~~~~

By default, the live display will display ellipsis if the renderable is too large for the terminal. You can adjust this by setting the
``vertical_overflow`` argument on the :class:`~rich.live.Live` constructor.

- "crop" Show renderable up to the terminal height. The rest is hidden.
- "ellipsis" Similar to crop except last line of the terminal is replaced with "...". This is the default behavior.
- "visible" Will allow the whole renderable to be shown. Note that the display cannot be properly cleared in this mode.

.. note::

    Once the live display stops on a non-transient renderable, the last frame will render as **visible** since it doesn't have to be cleared.


Print / log
~~~~~~~~~~~

The Live class will create an internal Console object which you can access via ``live.console``. If you print or log to this console, the output will be displayed *above* the live display. Here's an example::

    import time

    from rich.live import Live
    from rich.table import Table

    table = Table()
    table.add_column("Row ID")
    table.add_column("Description")
    table.add_column("Level")

    with Live(table, refresh_per_second=4) as live:  # update 4 times a second to feel fluid
        for row in range(12):
            live.console.print(f"Working on row #{row}")
            time.sleep(0.4)
            table.add_row(f"{row}", f"description {row}", "[red]ERROR")


If you have another Console object you want to use, pass it in to the :class:`~rich.live.Live` constructor. Here's an example::

    from my_project import my_console

    with Live(console=my_console) as live:
        my_console.print("[bold blue]Starting work!")
        ...

.. note::

    If you are passing in a file console, the live display only show the last item once the live context is left.

Redirecting stdout / stderr
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid breaking the live display visuals, Rich will redirect ``stdout`` and ``stderr`` so that you can use the builtin ``print`` statement.
This feature is enabled by default, but you can disable by setting ``redirect_stdout`` or ``redirect_stderr`` to ``False``.

Nesting Lives
-------------

If you create a Live instance within the context of an existing Live instance, then the content of the inner Live will be displayed below the outer Live.

Prior to version 14.0.0 this would have resulted in a :class:`~rich.errors.LiveError` exception.


Examples
--------

See `table_movie.py <https://github.com/willmcgugan/rich/blob/master/examples/table_movie.py>`_ and
`top_lite_simulator.py <https://github.com/willmcgugan/rich/blob/master/examples/top_lite_simulator.py>`_
for deeper examples of live displaying.
```

## File: docs/source/logging.rst
```
Logging Handler
===============

Rich supplies a :ref:`logging handler<logging>` which will format and colorize text written by Python's logging module.

Here's an example of how to set up a rich logger::

    import logging
    from rich.logging import RichHandler

    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    log = logging.getLogger("rich")
    log.info("Hello, World!")

Rich logs won't render :ref:`console_markup` in logging by default as most libraries won't be aware of the need to escape literal square brackets, but you can enable it by setting ``markup=True`` on the handler. Alternatively you can enable it per log message by supplying the ``extra`` argument as follows::

    log.error("[bold red blink]Server is shutting down![/]", extra={"markup": True})

Similarly, the highlighter may be overridden per log message::

    log.error("123 will not be highlighted", extra={"highlighter": None})


Handle exceptions
-------------------

The :class:`~rich.logging.RichHandler` class may be configured to use Rich's :class:`~rich.traceback.Traceback` class to format exceptions, which provides more context than a built-in exception. To get beautiful exceptions in your logs set ``rich_tracebacks=True`` on the handler constructor::


    import logging
    from rich.logging import RichHandler

    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    log = logging.getLogger("rich")
    try:
        print(1 / 0)
    except Exception:
        log.exception("unable print!")


There are a number of other options you can use to configure logging output, see the :class:`~rich.logging.RichHandler` reference for details.

Suppressing Frames
------------------

If you are working with a framework (click, django etc), you may only be interested in seeing the code from your own application within the traceback. You can exclude framework code by setting the `suppress` argument on `Traceback`, `install`, and `Console.print_exception`, which should be a list of modules or str paths.

Here's how you would exclude `click <https://click.palletsprojects.com/en/8.0.x/>`_ from Rich exceptions:: 

    import click
    import logging
    from rich.logging import RichHandler

    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])]
    )

Suppressed frames will show the line and file only, without any code.
```

## File: docs/source/markdown.rst
```
Markdown
========

Rich can render Markdown to the console. To render markdown, construct a :class:`~rich.markdown.Markdown` object then print it to the console. Markdown is a great way of adding rich content to your command line applications. Here's an example of use::

    MARKDOWN = """
    # This is an h1

    Rich can do a pretty *decent* job of rendering markdown.

    1. This is a list item
    2. This is another list item
    """
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    md = Markdown(MARKDOWN)
    console.print(md)

Note that code blocks are rendered with full syntax highlighting!

You can also use the Markdown class from the command line. The following example displays a readme in the terminal::

    python -m rich.markdown README.md

Run the following to see the full list of arguments for the markdown command::

    python -m rich.markdown -h
```

## File: docs/source/markup.rst
```
.. _console_markup:

Console Markup
==============

Rich supports a simple markup which you can use to insert color and styles virtually everywhere Rich would accept a string (e.g. :meth:`~rich.console.Console.print` and :meth:`~rich.console.Console.log`).

Run the following command to see some examples::

    python -m rich.markup

Syntax
------

Console markup uses a syntax inspired by `bbcode <https://en.wikipedia.org/wiki/BBCode>`_. If you write the style (see :ref:`styles`) in square brackets, e.g. ``[bold red]``, that style will apply until it is *closed* with a corresponding ``[/bold red]``.

Here's a simple example::

    from rich import print
    print("[bold red]alert![/bold red] Something happened")

If you don't close a style, it will apply until the end of the string. Which is sometimes convenient if you want to style a single line. For example::

    print("[bold italic yellow on red blink]This text is impossible to read")

There is a shorthand for closing a style. If you omit the style name from the closing tag, Rich will close the last style. For example::

    print("[bold red]Bold and red[/] not bold or red")

These markup tags may be use in combination with each other and don't need to be strictly nested. The following example demonstrates overlapping of markup tags:: 

    print("[bold]Bold[italic] bold and italic [/bold]italic[/italic]")

Errors
~~~~~~

Rich will raise :class:`~rich.errors.MarkupError` if the markup contains one of the following errors:

- Mismatched tags, e.g. ``"[bold]Hello[/red]"``
- No matching tag for implicit close, e.g. ``"no tags[/]"``


Links
~~~~~

Console markup can output hyperlinks with the following syntax: ``[link=URL]text[/link]``. Here's an example::

    print("Visit my [link=https://www.willmcgugan.com]blog[/link]!")

If your terminal software supports hyperlinks, you will be able to click the word "blog" which will typically open a browser. If your terminal doesn't support hyperlinks, you will see the text but it won't be clickable.


Escaping
~~~~~~~~

Occasionally you may want to print something that Rich would interpret as markup. You can *escape* a tag by preceding it with a backslash. Here's an example::

    >>> from rich import print
    >>> print(r"foo\[bar]")
    foo[bar]

Without the backslash, Rich will assume that ``[bar]`` is a tag and remove it from the output if there is no "bar" style.

.. note::
    If you want to prevent the backslash from escaping the tag and output a literal backslash before a tag you can enter two backslashes.

The function :func:`~rich.markup.escape` will handle escaping of text for you.

Escaping is important if you construct console markup dynamically, with ``str.format`` or f strings (for example). Without escaping it may be possible to inject tags where you don't want them. Consider the following function::

    def greet(name):
        console.print(f"Hello {name}!")

Calling ``greet("Will")`` will print a greeting, but if you were to call ``greet("[blink]Gotcha![/blink]")`` then you will also get blinking text, which may not be desirable. The solution is to escape the arguments::

    from rich.markup import escape
    def greet(name):
        console.print(f"Hello {escape(name)}!")

Emoji
~~~~~

If you add an *emoji code* to markup it will be replaced with the equivalent unicode character. An emoji code consists of the name of the emoji surrounded be colons (:). Here's an example::

    >>> from rich import print
    >>> print(":warning:")
    ⚠️

Some emojis have two variants, the "emoji" variant displays in full color, and the "text" variant displays in monochrome (whatever your default colors are set to). You can specify the variant you want by adding either `"-emoji"` or `"-text"` to the emoji code. Here's an example:

    >>> from rich import print
    >>> print(":red_heart-emoji:")
    >>> print(":red_heart-text:")

To see a list of all the emojis available, run the following command::

    python -m rich.emoji


Rendering Markup
----------------

By default, Rich will render console markup when you explicitly pass a string to :meth:`~rich.console.Print.print` or implicitly when you embed a string in another renderable object such as :class:`~rich.table.Table` or :class:`~rich.panel.Panel`.

Console markup is convenient, but you may wish to disable it if the syntax clashes with the string you want to print. You can do this by setting ``markup=False`` on the :meth:`~rich.console.Print.print` method or on the :class:`~rich.console.Console` constructor.


Markup API
----------

You can convert a string to styled text by calling :meth:`~rich.text.Text.from_markup`, which returns a :class:`~rich.text.Text` instance you can print or add more styles to.
```

## File: docs/source/padding.rst
```
Padding
=======

The :class:`~rich.padding.Padding` class may be used to add whitespace around text or other renderable. The following example will print the word "Hello" with a padding of 1 character, so there will be a blank line above and below, and a space on the left and right edges::

    from rich import print
    from rich.padding import Padding
    test = Padding("Hello", 1)
    print(test)

You can specify the padding on a more granular level by using a tuple of values rather than a single value. A tuple of 2 values sets the top/bottom and left/right padding, whereas a tuple of 4 values sets the padding for top, right, bottom, and left sides. You may recognize this scheme if you are familiar with CSS.

For example, the following displays 2 blank lines above and below the text, and a padding of 4 spaces on the left and right sides::

    from rich import print
    from rich.padding import Padding
    test = Padding("Hello", (2, 4))
    print(test)

The Padding class can also accept a ``style`` argument which applies a style to the padding and contents, and an ``expand`` switch which can be set to False to prevent the padding from extending to the full width of the terminal. Here's an example which demonstrates both these arguments::

    from rich import print
    from rich.padding import Padding
    test = Padding("Hello", (2, 4), style="on blue", expand=False)
    print(test)

Note that, as with all Rich renderables, you can use Padding in any context. For instance, if you want to emphasize an item in a :class:`~rich.table.Table` you could add a Padding object to a row with a padding of 1 and a style of "on red".
```

## File: docs/source/panel.rst
```
Panel
=====

To draw a border around text or other renderable, construct a :class:`~rich.panel.Panel` with the renderable as the first positional argument. Here's an example::

    from rich import print
    from rich.panel import Panel
    print(Panel("Hello, [red]World!"))

You can change the style of the panel by setting the ``box`` argument to the Panel constructor. See :ref:`appendix_box` for a list of available box styles.

Panels will extend to the full width of the terminal. You can make panel *fit* the content by setting ``expand=False`` on the constructor, or by creating the Panel with :meth:`~rich.panel.Panel.fit`. For example::

    from rich import print
    from rich.panel import Panel
    print(Panel.fit("Hello, [red]World!"))

The Panel constructor accepts a ``title`` argument which will draw a title on the top of the panel, as well as a ``subtitle`` argument which will draw a subtitle on the bottom of the panel::

    from rich import print
    from rich.panel import Panel
    print(Panel("Hello, [red]World!", title="Welcome", subtitle="Thank you"))

See :class:`~rich.panel.Panel` for details how to customize Panels.
```

## File: docs/source/pretty.rst
```
Pretty Printing
===============

In addition to syntax highlighting, Rich will format (i.e. *pretty print*) containers such as lists, dicts, and sets.

Run the following command to see an example of pretty printed output::

    python -m rich.pretty

Note how the output will change to fit within the terminal width.

pprint method
-------------

The :func:`~rich.pretty.pprint` method offers a few more arguments you can use to tweak how objects are pretty printed. Here's how you would import it::

    >>> from rich.pretty import pprint
    >>> pprint(locals())

Indent guides
~~~~~~~~~~~~~

Rich can draw *indent guides* to highlight the indent level of a data structure. These can make it easier to read more deeply nested output. The pprint method enables indent guides by default. You can set ``indent_guides=False`` to disable this feature.

Expand all
~~~~~~~~~~

Rich is quite conservative about expanding data structures and will try to fit as much in each line as it can. If you prefer, you can tell Rich to fully expand all data structures by setting ``expand_all=True``. Here's an example::

    >>> pprint(["eggs", "ham"], expand_all=True)

Truncating pretty output
~~~~~~~~~~~~~~~~~~~~~~~~

Very long data structures can be difficult to read and you may find yourself scrolling through multiple pages in the terminal to find the data you are interested in. Rich can truncate containers and long strings to give you an overview without swamping your terminal.


If you set the ``max_length`` argument to an integer, Rich will truncate containers with more than the given number of elements. If data is truncated, Rich will display an ellipsis ``...`` and the number of elements not shown.

Here's an example::

    >>> pprint(locals(), max_length=2)

If you set the ``max_string`` argument to an integer, Rich will truncate strings over that length. Truncated string will be appended with the number of characters that have not been shown. Here's an example::

    >>> pprint("Where there is a Will, there is a Way", max_string=21)

Pretty renderable
-----------------

Rich offers a :class:`~rich.pretty.Pretty` class which you can use to insert pretty printed data in to another renderable.

The following example displays pretty printed data within a simple panel::

    from rich import print
    from rich.pretty import Pretty
    from rich.panel import Panel

    pretty = Pretty(locals())
    panel = Panel(pretty)
    print(panel)

There are a large number of options to tweak the pretty formatting, See the :class:`~rich.pretty.Pretty` reference for details.

Rich Repr Protocol
------------------

Rich is able to syntax highlight any output, but the formatting is restricted to built-in containers, dataclasses, and other objects Rich knows about, such as objects generated by the `attrs <https://www.attrs.org/en/stable/>`_ library. To add Rich formatting capabilities to custom objects, you can implement the *rich repr protocol*.

Run the following command to see an example of what the Rich repr protocol can generate::

    python -m rich.repr

First, let's look at a class that might benefit from a Rich repr::

    class Bird:
        def __init__(self, name, eats=None, fly=True, extinct=False):
            self.name = name
            self.eats = list(eats) if eats else []
            self.fly = fly
            self.extinct = extinct

        def __repr__(self):
            return f"Bird({self.name!r}, eats={self.eats!r}, fly={self.fly!r}, extinct={self.extinct!r})"

    BIRDS = {
        "gull": Bird("gull", eats=["fish", "chips", "ice cream", "sausage rolls"]),
        "penguin": Bird("penguin", eats=["fish"], fly=False),
        "dodo": Bird("dodo", eats=["fruit"], fly=False, extinct=True)
    }
    print(BIRDS)

The result of this script would be::

    {'gull': Bird('gull', eats=['fish', 'chips', 'ice cream', 'sausage rolls'], fly=True, extinct=False), 'penguin': Bird('penguin', eats=['fish'], fly=False, extinct=False), 'dodo': Bird('dodo', eats=['fruit'], fly=False, extinct=True)}

The output is long enough to wrap on to the next line, which can make it hard to read. The repr strings are informative but a little verbose since they include default arguments. If we print this with Rich, things are improved somewhat::

    {
        'gull': Bird('gull', eats=['fish', 'chips', 'ice cream', 'sausage rolls'],
    fly=True, extinct=False),
        'penguin': Bird('penguin', eats=['fish'], fly=False, extinct=False),
        'dodo': Bird('dodo', eats=['fruit'], fly=False, extinct=True)
    }

Rich knows how to format the container dict, but the repr strings are still verbose, and there is some wrapping of the output (assumes an 80 character terminal).

We can solve both these issues by adding the following ``__rich_repr__`` method::

    def __rich_repr__(self):
        yield self.name
        yield "eats", self.eats
        yield "fly", self.fly, True
        yield "extinct", self.extinct, False

Now if we print the same object with Rich we would see the following::

    {
        'gull': Bird(
            'gull',
            eats=['fish', 'chips', 'ice cream', 'sausage rolls']
        ),
        'penguin': Bird('penguin', eats=['fish'], fly=False),
        'dodo': Bird('dodo', eats=['fruit'], fly=False, extinct=True)
    }

The default arguments have been omitted, and the output has been formatted nicely. The output remains readable even if we have less room in the terminal, or our objects are part of a deeply nested data structure::

    {
        'gull': Bird(
            'gull',
            eats=[
                'fish',
                'chips',
                'ice cream',
                'sausage rolls'
            ]
        ),
        'penguin': Bird(
            'penguin',
            eats=['fish'],
            fly=False
        ),
        'dodo': Bird(
            'dodo',
            eats=['fruit'],
            fly=False,
            extinct=True
        )
    }

You can add a ``__rich_repr__`` method to any class to enable the Rich formatting. This method should return an iterable of tuples. You could return a list of tuples, but it's easier to express with the ``yield`` keywords, making it a *generator*.

Each tuple specifies an element in the output.

- ``yield value`` will generate a positional argument.
- ``yield name, value`` will generate a keyword argument.
- ``yield name, value, default`` will generate a keyword argument *if* ``value`` is not equal to ``default``.

If you use ``None`` as the ``name``, then it will be treated as a positional argument as well, in order to support having ``tuple`` positional arguments.

You can also tell Rich to generate the *angular bracket* style of repr, which tend to be used where there is no easy way to recreate the object's constructor. To do this set the function attribute ``"angular"`` to ``True`` immediately after your ``__rich_repr__`` method. For example::

    __rich_repr__.angular = True

This will change the output of the Rich repr example to the following::

    {
        'gull': <Bird 'gull' eats=['fish', 'chips', 'ice cream', 'sausage rolls']>,
        'penguin': <Bird 'penguin' eats=['fish'] fly=False>,
        'dodo': <Bird 'dodo' eats=['fruit'] fly=False extinct=True>
    }


Note that you can add ``__rich_repr__`` methods to third-party libraries *without* including Rich as a dependency. If Rich is not installed, then nothing will break. Hopefully more third-party libraries will adopt Rich repr methods in the future.

Typing
~~~~~~

If you want to type the Rich repr method you can import and return ``rich.repr.Result``, which will help catch logical errors::


    import rich.repr


    class Bird:
        def __init__(self, name, eats=None, fly=True, extinct=False):
            self.name = name
            self.eats = list(eats) if eats else []
            self.fly = fly
            self.extinct = extinct

        def __rich_repr__(self) -> rich.repr.Result:
            yield self.name
            yield "eats", self.eats
            yield "fly", self.fly, True
            yield "extinct", self.extinct, False


Automatic Rich Repr
~~~~~~~~~~~~~~~~~~~

Rich can generate a rich repr automatically if the parameters are named the same as your attributes.

To automatically build a rich repr, use the :meth:`~rich.repr.auto` class decorator. The Bird example above follows the above rule, so we don't strictly need to implement our own ``__rich_repr__``. The following code would generate the same repr::

    import rich.repr

    @rich.repr.auto
    class Bird:
        def __init__(self, name, eats=None, fly=True, extinct=False):
            self.name = name
            self.eats = list(eats) if eats else []
            self.fly = fly
            self.extinct = extinct


    BIRDS = {
        "gull": Bird("gull", eats=["fish", "chips", "ice cream", "sausage rolls"]),
        "penguin": Bird("penguin", eats=["fish"], fly=False),
        "dodo": Bird("dodo", eats=["fruit"], fly=False, extinct=True)
    }
    from rich import print
    print(BIRDS)

Note that the decorator will also create a `__repr__`, so you will get an auto-generated repr even if you don't print with Rich.

If you want to auto-generate the angular type of repr, then set ``angular=True`` on the decorator::

    @rich.repr.auto(angular=True)
    class Bird:
        def __init__(self, name, eats=None, fly=True, extinct=False):
            self.name = name
            self.eats = list(eats) if eats else []
            self.fly = fly
            self.extinct = extinct


Example
-------

See `repr.py <https://github.com/willmcgugan/rich/blob/master/examples/repr.py>`_ for the example code used in this page.
```

## File: docs/source/progress.rst
```
.. _progress:

Progress Display
================

Rich can display continuously updated information regarding the progress of long running tasks / file copies etc. The information displayed is configurable, the default will display a description of the 'task', a progress bar, percentage complete, and estimated time remaining.

Rich progress display supports multiple tasks, each with a bar and progress information. You can use this to track concurrent tasks where the work is happening in threads or processes.

To see how the progress display looks, try this from the command line::

    python -m rich.progress


.. note::

    Progress works with Jupyter notebooks, with the caveat that auto-refresh is disabled. You will need to explicitly call :meth:`~rich.progress.Progress.refresh` or set ``refresh=True`` when calling :meth:`~rich.progress.Progress.update`. Or use the :func:`~rich.progress.track` function which does a refresh automatically on each loop.

Basic Usage
-----------

For basic usage call the :func:`~rich.progress.track` function, which accepts a sequence (such as a list or range object) and an optional description of the job you are working on. The track function will yield values from the sequence and update the progress information on each iteration. Here's an example::

    import time
    from rich.progress import track

    for i in track(range(20), description="Processing..."):
        time.sleep(1)  # Simulate work being done

Advanced usage
--------------

If you require multiple tasks in the display, or wish to configure the columns in the progress display, you can work directly with the :class:`~rich.progress.Progress` class. Once you have constructed a Progress object, add task(s) with (:meth:`~rich.progress.Progress.add_task`) and update progress with :meth:`~rich.progress.Progress.update`.

The Progress class is designed to be used as a *context manager* which will start and stop the progress display automatically.

Here's a simple example::

    import time

    from rich.progress import Progress

    with Progress() as progress:

        task1 = progress.add_task("[red]Downloading...", total=1000)
        task2 = progress.add_task("[green]Processing...", total=1000)
        task3 = progress.add_task("[cyan]Cooking...", total=1000)

        while not progress.finished:
            progress.update(task1, advance=0.5)
            progress.update(task2, advance=0.3)
            progress.update(task3, advance=0.9)
            time.sleep(0.02)

The ``total`` value associated with a task is the number of steps that must be completed for the progress to reach 100%. A *step* in this context is whatever makes sense for your application; it could be number of bytes of a file read, or number of images processed, etc.


Starting and stopping
~~~~~~~~~~~~~~~~~~~~~

The context manager is recommended if you can use it. If you don't use the context manager, be sure to call :meth:`~rich.progress.Progress.start` to start the progress display, and :meth:`~rich.progress.Progress.stop` to stop it.

Here's an example that doesn't use the context manager::

    import time

    from rich.progress import Progress

    progress = Progress()
    progress.start()
    try:
        task1 = progress.add_task("[red]Downloading...", total=1000)
        task2 = progress.add_task("[green]Processing...", total=1000)
        task3 = progress.add_task("[cyan]Cooking...", total=1000)

        while not progress.finished:
            progress.update(task1, advance=0.5)
            progress.update(task2, advance=0.3)
            progress.update(task3, advance=0.9)
            time.sleep(0.02)
    finally:
        progress.stop()

Note the use of the try / finally, to ensure that ``stop()`` is called.

Updating tasks
~~~~~~~~~~~~~~

When you call :meth:`~rich.progress.Progress.add_task` you get back a `Task ID`. Use this ID to call :meth:`~rich.progress.Progress.update` whenever you have completed some work, or any information has changed. Typically you will need to update ``completed`` every time you have completed a step. You can do this by setting ``completed`` directly or by setting ``advance`` which will add to the current ``completed`` value.

The :meth:`~rich.progress.Progress.update` method collects keyword arguments which are also associated with the task. Use this to supply any additional information you would like to render in the progress display. The additional arguments are stored in ``task.fields`` and may be referenced in :ref:`Column classes<Columns>`.

Hiding tasks
~~~~~~~~~~~~

You can show or hide tasks by updating the tasks ``visible`` value. Tasks are visible by default, but you can also add an invisible task by calling :meth:`~rich.progress.Progress.add_task` with ``visible=False``.


Transient progress
~~~~~~~~~~~~~~~~~~

Normally when you exit the progress context manager (or call :meth:`~rich.progress.Progress.stop`) the last refreshed display remains in the terminal with the cursor on the following line. You can also make the progress display disappear on exit by setting ``transient=True`` on the Progress constructor. Here's an example::

    with Progress(transient=True) as progress:
        task = progress.add_task("Working", total=100)
        do_work(task)

Transient progress displays are useful if you want more minimal output in the terminal when tasks are complete.

Indeterminate progress
~~~~~~~~~~~~~~~~~~~~~~

When you add a task it is automatically *started*, which means it will show a progress bar at 0% and the time remaining will be calculated from the current time. This may not work well if there is a long delay before you can start updating progress; you may need to wait for a response from a server or count files in a directory (for example). In these cases you can call :meth:`~rich.progress.Progress.add_task` with ``start=False`` or ``total=None`` which will display a pulsing animation that lets the user know something is working. This is known as an *indeterminate* progress bar. When you have the number of steps you can call :meth:`~rich.progress.Progress.start_task` which will display the progress bar at 0%, then :meth:`~rich.progress.Progress.update` as normal.

Auto refresh
~~~~~~~~~~~~

By default, the progress information will refresh 10 times a second. You can set the refresh rate with the ``refresh_per_second`` argument on the :class:`~rich.progress.Progress` constructor. You should set this to something lower than 10 if you know your updates will not be that frequent.

You might want to disable auto-refresh entirely if your updates are not very frequent, which you can do by setting ``auto_refresh=False`` on the constructor. If you disable auto-refresh you will need to call :meth:`~rich.progress.Progress.refresh` manually after updating your task(s).


Expand
~~~~~~

The progress bar(s) will use only as much of the width of the terminal as required to show the task information. If you set the ``expand`` argument on the Progress constructor, then Rich will stretch the progress display to the full available width.


Columns
~~~~~~~

You may customize the columns in the progress display with the positional arguments to the :class:`~rich.progress.Progress` constructor. The columns are specified as either a `format string <https://docs.python.org/3/library/string.html#formatspec>`_ or a :class:`~rich.progress.ProgressColumn` object.

Format strings will be rendered with a single value `"task"` which will be a :class:`~rich.progress.Task` instance. For example ``"{task.description}"`` would display the task description in the column, and ``"{task.completed} of {task.total}"`` would display how many of the total steps have been completed. Additional fields passed via keyword arguments to `~rich.progress.Progress.update` are stored in ``task.fields``. You can add them to a format string with the following syntax: ``"extra info: {task.fields[extra]}"``.

The default columns are equivalent to the following::

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    )

To create a Progress with your own columns in addition to the defaults, use :meth:`~rich.progress.Progress.get_default_columns`::

    progress = Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
    )

The following column objects are available:

- :class:`~rich.progress.BarColumn` Displays the bar.
- :class:`~rich.progress.TextColumn` Displays text.
- :class:`~rich.progress.TimeElapsedColumn` Displays the time elapsed.
- :class:`~rich.progress.TimeRemainingColumn` Displays the estimated time remaining.
- :class:`~rich.progress.MofNCompleteColumn` Displays completion progress as ``"{task.completed}/{task.total}"`` (works best if completed and total are ints).
- :class:`~rich.progress.FileSizeColumn` Displays progress as file size (assumes the steps are bytes).
- :class:`~rich.progress.TotalFileSizeColumn` Displays total file size (assumes the steps are bytes).
- :class:`~rich.progress.DownloadColumn` Displays download progress (assumes the steps are bytes).
- :class:`~rich.progress.TransferSpeedColumn` Displays transfer speed (assumes the steps are bytes).
- :class:`~rich.progress.SpinnerColumn` Displays a "spinner" animation.
- :class:`~rich.progress.RenderableColumn` Displays an arbitrary Rich renderable in the column.

To implement your own columns, extend the :class:`~rich.progress.ProgressColumn` class and use it as you would the other columns.


Table Columns
~~~~~~~~~~~~~

Rich builds a :class:`~rich.table.Table` for the tasks in the Progress instance. You can customize how the columns of this *tasks table* are created by specifying the ``table_column`` argument in the Column constructor, which should be a :class:`~rich.table.Column` instance.

The following example demonstrates a progress bar where the description takes one third of the width of the terminal, and the bar takes up the remaining two thirds::

    from time import sleep

    from rich.table import Column
    from rich.progress import Progress, BarColumn, TextColumn

    text_column = TextColumn("{task.description}", table_column=Column(ratio=1))
    bar_column = BarColumn(bar_width=None, table_column=Column(ratio=2))
    progress = Progress(text_column, bar_column, expand=True)

    with progress:
        for n in progress.track(range(100)):
            progress.print(n)
            sleep(0.1)


Print / log
~~~~~~~~~~~

The Progress class will create an internal Console object which you can access via ``progress.console``. If you print or log to this console, the output will be displayed *above* the progress display. Here's an example::

    with Progress() as progress:
        task = progress.add_task("twiddling thumbs", total=10)
        for job in range(10):
            progress.console.print(f"Working on job #{job}")
            run_job(job)
            progress.advance(task)

If you have another Console object you want to use, pass it in to the :class:`~rich.progress.Progress` constructor. Here's an example::

    from my_project import my_console

    with Progress(console=my_console) as progress:
        my_console.print("[bold blue]Starting work!")
        do_work(progress)


Redirecting stdout / stderr
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid breaking the progress display visuals, Rich will redirect ``stdout`` and ``stderr`` so that you can use the built-in ``print`` statement. This feature is enabled by default, but you can disable by setting ``redirect_stdout`` or ``redirect_stderr`` to ``False``


Customizing
~~~~~~~~~~~

If the :class:`~rich.progress.Progress` class doesn't offer exactly what you need in terms of a progress display, you can override the :class:`~rich.progress.Progress.get_renderables` method. For example, the following class will render a :class:`~rich.panel.Panel` around the progress display::

    from rich.panel import Panel
    from rich.progress import Progress

    class MyProgress(Progress):
        def get_renderables(self):
            yield Panel(self.make_tasks_table(self.tasks))

Reading from a file
~~~~~~~~~~~~~~~~~~~

Rich provides an easy way to generate a progress bar while reading a file. If you call :func:`~rich.progress.open` it will return a context manager which displays a progress bar while you read. This is particularly useful when you can't easily modify the code that does the reading.

The following example demonstrates how we might show progress when reading a JSON file::

    import json
    import rich.progress

    with rich.progress.open("data.json", "rb") as file:
        data = json.load(file)
    print(data)

If you already have a file object, you can call :func:`~rich.progress.wrap_file` which returns a context manager that wraps your file so that it displays a progress bar. If you use this function you will need to set the number of bytes or characters you expect to read.

Here's an example that reads a url from the internet::

    from time import sleep
    from urllib.request import urlopen

    from rich.progress import wrap_file

    response = urlopen("https://www.textualize.io")
    size = int(response.headers["Content-Length"])

    with wrap_file(response, size) as file:
        for line in file:
            print(line.decode("utf-8"), end="")
            sleep(0.1)


If you expect to be reading from multiple files, you can use :meth:`~rich.progress.Progress.open` or :meth:`~rich.progress.Progress.wrap_file` to add a file progress to an existing Progress instance.

See `cp_progress.py <https://github.com/willmcgugan/rich/blob/master/examples/cp_progress.py>`_ for a minimal clone of the ``cp`` command which shows a progress bar as the file is copied.


Nesting Progress bars
---------------------

If you create a new progress bar within the context of an existing progress bar (with the context manager or `track` function), then Rich will display the inner progress bar(s) under the initial bar.

Here's an example that nests progress bars::

    from rich.progress import track
    from time import sleep


    for count in track(range(10)):
        for letter in track("ABCDEF", transient=True):
            print(f"Stage {count}{letter}")
            sleep(0.1)
        sleep(0.1)

The inner loop creates a new progress bar below the first, but both can update.

Note that if you nest progress bars like this, then the nested bars will updating according to the `refresh_per_second` attribute of the outer bar.


Multiple Progress
-----------------

You can't have different columns per task with a single Progress instance. However, you can have as many Progress instances as you like in a :ref:`live`. See `live_progress.py <https://github.com/willmcgugan/rich/blob/master/examples/live_progress.py>`_ and `dynamic_progress.py <https://github.com/willmcgugan/rich/blob/master/examples/dynamic_progress.py>`_ for examples of using multiple Progress instances.

Example
-------

See `downloader.py <https://github.com/willmcgugan/rich/blob/master/examples/downloader.py>`_ for a realistic application of a progress display. This script can download multiple concurrent files with a progress bar, transfer speed and file size.
```

## File: docs/source/prompt.rst
```
Prompt
======

Rich has a number of :class:`~rich.prompt.Prompt` classes which ask a user for input and loop until a valid response is received (they all use the :ref:`Console API<Input>` internally). Here's a simple example::

    >>> from rich.prompt import Prompt
    >>> name = Prompt.ask("Enter your name")

The prompt may be given as a string (which may contain :ref:`console_markup` and emoji code) or as a :class:`~rich.text.Text` instance.

You can set a default value which will be returned if the user presses return without entering any text::

    >>> from rich.prompt import Prompt
    >>> name = Prompt.ask("Enter your name", default="Paul Atreides")

If you supply a list of choices, the prompt will loop until the user enters one of the choices::

    >>> from rich.prompt import Prompt
    >>> name = Prompt.ask("Enter your name", choices=["Paul", "Jessica", "Duncan"], default="Paul")

By default this is case sensitive, but you can set `case_sensitive=False` to make it case insensitive::

    >>> from rich.prompt import Prompt
    >>> name = Prompt.ask("Enter your name", choices=["Paul", "Jessica", "Duncan"], default="Paul", case_sensitive=False)

Now, it would accept "paul" or "Paul" as valid responses.

In addition to :class:`~rich.prompt.Prompt` which returns strings, you can also use :class:`~rich.prompt.IntPrompt` which asks the user for an integer, and :class:`~rich.prompt.FloatPrompt` for floats.

The :class:`~rich.prompt.Confirm` class is a specialized prompt which may be used to ask the user a simple yes / no question. Here's an example::

    >>> from rich.prompt import Confirm
    >>> is_rich_great = Confirm.ask("Do you like rich?")
    >>> assert is_rich_great

The Prompt class was designed to be customizable via inheritance. See `prompt.py <https://github.com/willmcgugan/rich/blob/master/rich/prompt.py>`_ for examples.

To see some of the prompts in action, run the following command from the command line::

    python -m rich.prompt
```

## File: docs/source/protocol.rst
```
.. _protocol:

Console Protocol
================

Rich supports a simple protocol to add rich formatting capabilities to custom objects, so you can :meth:`~rich.console.Console.print` your object with color, styles and formatting.

Use this for presentation or to display additional debugging information that might be hard to parse from a typical ``__repr__`` string.


Console Customization
---------------------

The easiest way to customize console output for your object is to implement a ``__rich__`` method. This method accepts no arguments, and should return an object that Rich knows how to render, such as a :class:`~rich.text.Text` or :class:`~rich.table.Table`. If you return a plain string it will be rendered as :ref:`console_markup`. Here's an example::

    class MyObject:
        def __rich__(self) -> str:
            return "[bold cyan]MyObject()"

If you were to print or log an instance of ``MyObject`` it would render as ``MyObject()`` in bold cyan. Naturally, you would want to put this to better use, perhaps by adding specialized syntax highlighting.


Console Render
--------------

The ``__rich__`` method is limited to a single renderable object. For more advanced rendering, add a ``__rich_console__`` method to your class.

The ``__rich_console__`` method should accept a :class:`~rich.console.Console` and a :class:`~rich.console.ConsoleOptions` instance. It should return an iterable of other renderable objects. Although that means it *could* return a container such as a list, it generally easier implemented by using the ``yield`` statement (making the method a generator).

Here's an example of a ``__rich_console__`` method::

    from dataclasses import dataclass
    from rich.console import Console, ConsoleOptions, RenderResult
    from rich.table import Table

    @dataclass
    class Student:
        id: int
        name: str
        age: int
        def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
            yield f"[b]Student:[/b] #{self.id}"
            my_table = Table("Attribute", "Value")
            my_table.add_row("name", self.name)
            my_table.add_row("age", str(self.age))
            yield my_table

If you were to print a ``Student`` instance, it would render a simple table to the terminal.


Low Level Render
~~~~~~~~~~~~~~~~

For complete control over how a custom object is rendered to the terminal, you can yield :class:`~rich.segment.Segment` objects. A Segment consists of a piece of text and an optional Style. The following example writes multi-colored text when rendering a ``MyObject`` instance::

    class MyObject:
        def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
            yield Segment("My", Style(color="magenta"))
            yield Segment("Object", Style(color="green"))
            yield Segment("()", Style(color="cyan"))


Measuring Renderables
~~~~~~~~~~~~~~~~~~~~~

Sometimes Rich needs to know how many characters an object will take up when rendering. The :class:`~rich.table.Table` class, for instance, will use this information to calculate the optimal dimensions for the columns. If you aren't using one of the renderable objects in the Rich module, you will need to supply a ``__rich_measure__`` method which accepts a :class:`~rich.console.Console` and :class:`~rich.console.ConsoleOptions` and returns a :class:`~rich.measure.Measurement` object. The Measurement object should contain the *minimum* and *maximum* number of characters required to render.

For example, if we are rendering a chess board, it would require a minimum of 8 characters to render. The maximum can be left as the maximum available width (assuming a centered board)::

    class ChessBoard:
        def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
            return Measurement(8, options.max_width)
```

## File: docs/source/reference.rst
```
Reference
=========

.. toctree::
   :maxdepth: 3

   reference/align.rst
   reference/bar.rst
   reference/color.rst
   reference/columns.rst
   reference/console.rst
   reference/emoji.rst
   reference/highlighter.rst
   reference/init.rst
   reference/json.rst
   reference/layout.rst
   reference/live.rst
   reference/logging.rst
   reference/markdown.rst
   reference/markup.rst
   reference/measure.rst
   reference/padding.rst
   reference/panel.rst
   reference/pretty.rst
   reference/progress_bar.rst
   reference/progress.rst
   reference/prompt.rst
   reference/protocol.rst
   reference/rule.rst
   reference/segment.rst
   reference/spinner.rst
   reference/status.rst
   reference/style.rst
   reference/styled.rst
   reference/syntax.rst
   reference/table.rst
   reference/text.rst
   reference/theme.rst
   reference/traceback.rst
   reference/tree.rst
   reference/abc.rst
```

## File: docs/source/style.rst
```
.. _styles:


Styles
======

In various places in the Rich API you can set a "style" which defines the color of the text and various attributes such as bold, italic etc. A style may be given as a string containing a *style definition* or as an instance of a :class:`~rich.style.Style` class.


Defining Styles
---------------

A style definition is a string containing one or more words to set colors and attributes.

To specify a foreground color use one of the 256 :ref:`appendix-colors`. For example, to print "Hello" in magenta::

    console.print("Hello", style="magenta")

You may also use the color's number (an integer between 0 and 255) with the syntax ``"color(<number>)"``. The following will give the equivalent output::

    console.print("Hello", style="color(5)")

Alternatively you can use a CSS-like syntax to specify a color with a "#" followed by three pairs of hex characters, or in RGB form with three decimal integers. The following two lines both print "Hello" in the same color (purple)::

    console.print("Hello", style="#af00ff")
    console.print("Hello", style="rgb(175,0,255)")

The hex and rgb forms allow you to select from the full *truecolor* set of 16.7 million colors.

.. note::
    Some terminals only support 256 colors. Rich will attempt to pick the closest color it can if your color isn't available.

By itself, a color will change the *foreground* color. To specify a *background* color, precede the color with the word "on". For example, the following prints text in red on a white background::

    console.print("DANGER!", style="red on white")

You can also set a color with the word ``"default"`` which will reset the color to a default managed by your terminal software. This works for backgrounds as well, so the style of ``"default on default"`` is what your terminal starts with.

You can set a style attribute by adding one or more of the following words:

* ``"bold"`` or ``"b"`` for bold text.
* ``"blink"`` for text that flashes (use this one sparingly).
* ``"blink2"`` for text that flashes rapidly (not supported by most terminals).
* ``"conceal"`` for *concealed* text (not supported by most terminals).
* ``"italic"`` or ``"i"`` for italic text (not supported on Windows).
* ``"reverse"`` or ``"r"`` for text with foreground and background colors reversed.
* ``"strike"`` or ``"s"`` for text with a line through it.
* ``"underline"`` or ``"u"`` for underlined text.

Rich also supports the following styles, which are not well supported and may not display in your terminal:

* ``"underline2"`` or ``"uu"`` for doubly underlined text.
* ``"frame"`` for framed text.
* ``"encircle"`` for encircled text.
* ``"overline"`` or ``"o"`` for overlined text.

Style attributes and colors may be used in combination with each other. For example::

    console.print("Danger, Will Robinson!", style="blink bold red underline on white")

Styles may be negated by prefixing the attribute with the word "not". This can be used to turn off styles if they overlap. For example::

    console.print("foo [not bold]bar[/not bold] baz", style="bold")

This will print "foo" and "baz" in bold, but "bar" will be in normal text.

Styles may also have a ``"link"`` attribute, which will turn any styled text in to a *hyperlink* (if supported by your terminal software).

To add a link to a style, the definition should contain the word ``"link"`` followed by a URL. The following example will make a clickable link::

    console.print("Google", style="link https://google.com")

.. note::
    If you are familiar with HTML you may find applying links in this way a little odd, but the terminal considers a link to be another attribute just like bold, italic etc. 
    


Style Class
-----------

Ultimately the style definition is parsed and an instance of a :class:`~rich.style.Style` class is created. If you prefer, you can use the Style class in place of the style definition. Here's an example::

    from rich.style import Style
    danger_style = Style(color="red", blink=True, bold=True)
    console.print("Danger, Will Robinson!", style=danger_style)

It is slightly quicker to construct a Style class like this, since a style definition takes a little time to parse -- but only on the first call, as Rich will cache parsed style definitions.

Styles may be combined by adding them together, which is useful if you want to modify attributes of an existing style. Here's an example::

    from rich.console import Console
    from rich.style import Style
    console = Console()

    base_style = Style.parse("cyan")
    console.print("Hello, World", style = base_style + Style(underline=True))

You can parse a style definition explicitly with the :meth:`~rich.style.Style.parse` method, which accepts the style definition and returns a Style instance. For example, the following two lines are equivalent::
    
    style = Style(color="magenta", bgcolor="yellow", italic=True)
    style = Style.parse("italic magenta on yellow")

.. _themes:


Style Themes
------------

If you reuse styles it can be a maintenance headache if you ever want to modify an attribute or color -- you would have to change every line where the style is used. Rich provides a :class:`~rich.theme.Theme` class which you can use to define custom styles that you can refer to by name. That way you only need to update your styles in one place.

Style themes can make your code more semantic, for instance a style called ``"warning"`` better expresses intent than ``"italic magenta underline"``.

To use a style theme, construct a :class:`~rich.theme.Theme` instance and pass it to the :class:`~rich.console.Console` constructor. Here's an example::

    from rich.console import Console
    from rich.theme import Theme
    custom_theme = Theme({
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red"
    })
    console = Console(theme=custom_theme)
    console.print("This is information", style="info")
    console.print("[warning]The pod bay doors are locked[/warning]")
    console.print("Something terrible happened!", style="danger")


.. note::
    style names must be lower case, start with a letter, and only contain letters or the characters ``"."``, ``"-"``, ``"_"``.


Customizing Defaults
~~~~~~~~~~~~~~~~~~~~

The Theme class will inherit the default styles built-in to Rich. If your custom theme contains the name of an existing style, it will replace it. This allows you to customize the defaults as easily as you can create your own styles. For instance, here's how you can change how Rich highlights numbers::

    from rich.console import Console
    from rich.theme import Theme
    console = Console(theme=Theme({"repr.number": "bold green blink"}))
    console.print("The total is 128")

You can disable inheriting the default theme by setting ``inherit=False`` on the :class:`rich.theme.Theme` constructor.

To see the default theme, run the following commands::

    python -m rich.theme
    python -m rich.default_styles


Loading Themes
~~~~~~~~~~~~~~

If you prefer, you can write your styles in an external config file rather than in Python. Here's an example of the format::

    [styles]
    info = dim cyan
    warning = magenta
    danger = bold red

You can read these files with the :meth:`~rich.theme.Theme.read` method.
```

## File: docs/source/syntax.rst
```
Syntax
======

Rich can syntax highlight various programming languages with line numbers.

To syntax highlight code, construct a :class:`~rich.syntax.Syntax` object and print it to the console. Here's an example::

    from rich.console import Console
    from rich.syntax import Syntax

    console = Console()
    with open("syntax.py", "rt") as code_file:
        syntax = Syntax(code_file.read(), "python")
    console.print(syntax)

You may also use the :meth:`~rich.syntax.Syntax.from_path` alternative constructor which will load the code from disk and auto-detect the file type. The example above could be re-written as follows::


    from rich.console import Console
    from rich.syntax import Syntax

    console = Console()
    syntax = Syntax.from_path("syntax.py")
    console.print(syntax)


Line numbers
------------

If you set ``line_numbers=True``, Rich will render a column for line numbers::

    syntax = Syntax.from_path("syntax.py", line_numbers=True)


Theme
-----

The Syntax constructor (and :meth:`~rich.syntax.Syntax.from_path`) accept a ``theme`` attribute which should be the name of a `Pygments theme <https://pygments.org/demo/>`_. It may also be one of the special case theme names "ansi_dark" or "ansi_light" which will use the color theme configured by the terminal.


Background color
----------------

You can override the background color from the theme by supplying a ``background_color`` argument to the constructor. This should be a string in the same format a style definition accepts, e.g. "red", "#ff0000", "rgb(255,0,0)" etc. You may also set the special value "default" which will use the default background color set in the terminal.


Syntax CLI
----------

You can use this class from the command line. Here's how you would syntax highlight a file called "syntax.py"::

    python -m rich.syntax syntax.py

For the full list of arguments, run the following::

    python -m rich.syntax -h
```

## File: docs/source/tables.rst
```
Tables
======

Rich's :class:`~rich.table.Table` class offers a variety of ways to render tabular data to the terminal.

To render a table, construct a :class:`~rich.table.Table` object, add columns with :meth:`~rich.table.Table.add_column`, and rows with :meth:`~rich.table.Table.add_row` -- then print it to the console.

Here's an example::

    from rich.console import Console
    from rich.table import Table

    table = Table(title="Star Wars Movies")

    table.add_column("Released", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Box Office", justify="right", style="green")

    table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
    table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
    table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
    table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")

    console = Console()
    console.print(table)

This produces the following output:

.. raw:: html

    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                           Star Wars Movies                           </span>
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
    ┃<span style="font-weight: bold">     Released </span>┃<span style="font-weight: bold"> Title                             </span>┃<span style="font-weight: bold">     Box Office </span>┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
    │<span style="color: #008080"> Dec 20, 2019 </span>│<span style="color: #800080"> Star Wars: The Rise of Skywalker  </span>│<span style="color: #008000">   $952,110,690 </span>│
    │<span style="color: #008080"> May 25, 2018 </span>│<span style="color: #800080"> Solo: A Star Wars Story           </span>│<span style="color: #008000">   $393,151,347 </span>│
    │<span style="color: #008080"> Dec 15, 2017 </span>│<span style="color: #800080"> Star Wars Ep. V111: The Last Jedi </span>│<span style="color: #008000"> $1,332,539,889 </span>│
    │<span style="color: #008080"> Dec 16, 2016 </span>│<span style="color: #800080"> Rogue One: A Star Wars Story      </span>│<span style="color: #008000"> $1,332,439,889 </span>│
    └──────────────┴───────────────────────────────────┴────────────────┘
    </pre>


Rich will calculate the optimal column sizes to fit your content, and will wrap text to fit if the terminal is not wide enough to fit the contents.

.. note::
    You are not limited to adding text in the ``add_row`` method. You can add anything that Rich knows how to render (including another table).

Table Options
~~~~~~~~~~~~~

There are a number of keyword arguments on the Table constructor you can use to define how a table should look.

- ``title`` Sets the title of the table (text shown above the table).
- ``caption`` Sets the table caption (text shown below the table).
- ``width`` Sets the desired width of the table (disables automatic width calculation).
- ``min_width`` Sets a minimum width for the table.
- ``box`` Sets one of the :ref:`appendix_box` styles for the table grid, or ``None`` for no grid.
- ``safe_box`` Set to ``True`` to force the table to generate ASCII characters rather than unicode.
- ``padding`` An integer, or tuple of 1, 2, or 4 values to set the padding on cells (see :ref:`Padding`).
- ``collapse_padding`` If True the padding of neighboring cells will be merged.
- ``pad_edge`` Set to False to remove padding around the edge of the table.
- ``expand`` Set to True to expand the table to the full available size.
- ``show_header`` Set to True to show a header, False to disable it.
- ``show_footer`` Set to True to show a footer, False to disable it.
- ``show_edge`` Set to False to disable the edge line around the table.
- ``show_lines`` Set to True to show lines between rows as well as header / footer.
- ``leading`` Additional space between rows.
- ``style`` A Style to apply to the entire table, e.g. "on blue"
- ``row_styles`` Set to a list of styles to style alternating rows. e.g. ``["dim", ""]`` to create *zebra stripes*
- ``header_style`` Set the default style for the header.
- ``footer_style`` Set the default style for the footer.
- ``border_style`` Set a style for border characters.
- ``title_style`` Set a style for the title.
- ``caption_style`` Set a style for the caption.
- ``title_justify`` Set the title justify method ("left", "right", "center", or "full")
- ``caption_justify`` Set the caption justify method ("left", "right", "center", or "full")
- ``highlight`` Set to True to enable automatic highlighting of cell contents.

Border Styles
~~~~~~~~~~~~~

You can set the border style by importing one of the preset :class:`~rich.box.Box` objects and setting the ``box`` argument in the table constructor. Here's an example that modifies the look of the Star Wars table::

    from rich import box
    table = Table(title="Star Wars Movies", box=box.MINIMAL_DOUBLE_HEAD)

See :ref:`appendix_box` for other box styles.

You can also set ``box=None`` to remove borders entirely.

The :class:`~rich.table.Table` class offers a number of configuration options to set the look and feel of the table, including how borders are rendered and the style and alignment of the columns.


Lines
~~~~~

By default, Tables will show a line under the header only. If you want to show lines between all rows add ``show_lines=True`` to the constructor.

You can also force a line on the next row by setting ``end_section=True`` on the call to :meth:`~rich.table.Table.add_row`, or by calling the :meth:`~rich.table.Table.add_section` to add a line between the current and subsequent rows.


Empty Tables
~~~~~~~~~~~~

Printing a table with no columns results in a blank line. If you are building a table dynamically and the data source has no columns, you might want to print something different. Here's how you might do that::

    if table.columns:
        print(table)
    else:
        print("[i]No data...[/i]")


Adding Columns
~~~~~~~~~~~~~~

You may also add columns by specifying them in the positional arguments of the :class:`~rich.table.Table` constructor. For example, we could construct a table with three columns like this::

    table = Table("Released", "Title", "Box Office", title="Star Wars Movies")

This allows you to specify the text of the column only. If you want to set other attributes, such as width and style, you can add a :class:`~rich.table.Column` class. Here's an example::

    from rich.table import Column, Table
    table = Table(
        "Released",
        "Title",
        Column(header="Box Office", justify="right"),
        title="Star Wars Movies"
    )

Column Options
~~~~~~~~~~~~~~

There are a number of options you can set on a column to modify how it will look.

- ``header_style`` Sets the style of the header, e.g. "bold magenta".
- ``footer_style`` Sets the style of the footer.
- ``style`` Sets a style that applies to the column. You could use this to highlight a column by setting the background with "on green" for example.
- ``justify`` Sets the text justify to one of "left", "center", "right", or "full".
- ``vertical`` Sets the vertical alignment of the cells in a column, to one of "top", "middle", or "bottom".
- ``width`` Explicitly set the width of a row to a given number of characters (disables automatic calculation).
- ``min_width`` When set to an integer will prevent the column from shrinking below this amount.
- ``max_width`` When set to an integer will prevent the column from growing beyond this amount.
- ``ratio`` Defines a ratio to set the column width. For instance, if there are 3 columns with a total of 6 ratio, and ``ratio=2`` then the column will be a third of the available size.
- ``no_wrap`` Set to True to prevent this column from wrapping.
- ``highlight`` Set to True to enable automatic highlighting of cell contents.

Vertical Alignment
~~~~~~~~~~~~~~~~~~

You can define the vertical alignment of a column by setting the ``vertical`` parameter of the column. You can also do this per-cell by wrapping your text or renderable with a :class:`~rich.align.Align` class::


    table.add_row(Align("Title", vertical="middle"))

Grids
~~~~~

The Table class can also make a great layout tool. If you disable headers and borders you can use it to position content within the terminal. The alternative constructor :meth:`~rich.table.Table.grid` can create such a table for you.

For instance, the following code displays two pieces of text aligned to both the left and right edges of the terminal on a single line::


    from rich import print
    from rich.table import Table

    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_row("Raising shields", "[bold magenta]COMPLETED [green]:heavy_check_mark:")

    print(grid)
```

## File: docs/source/text.rst
```
.. _rich_text:

Rich Text
=========

Rich has a :class:`~rich.text.Text` class you can use to mark up strings with color and style attributes. You can use a Text instance anywhere a string is accepted, which gives you a lot of control over presentation.

You can consider this class to be like a string with marked up regions of text. Unlike a built-in ``str``, a Text instance is mutable, and most methods operate in-place rather than returning a new instance. 

One way to add a style to Text is the :meth:`~rich.text.Text.stylize` method which applies a style to a start and end offset. Here is an example::

    from rich.console import Console
    from rich.text import Text

    console = Console()
    text = Text("Hello, World!")
    text.stylize("bold magenta", 0, 6)
    console.print(text)

This will print "Hello, World!" to the terminal, with the first word in bold magenta.

Alternatively, you can construct styled text by calling :meth:`~rich.text.Text.append` to add a string and style to the end of the Text. Here's an example::

    text = Text()
    text.append("Hello", style="bold magenta")
    text.append(" World!")
    console.print(text)

If you would like to use text that is already formatted with ANSI codes, call :meth:`~rich.text.Text.from_ansi` to convert it to a ``Text`` object::

    text = Text.from_ansi("\033[1;35mHello\033[0m, World!")
    console.print(text.spans)

Since building Text instances from parts is a common requirement, Rich offers :meth:`~rich.text.Text.assemble` which will combine strings or pairs of string and Style, and return a Text instance. The following example is equivalent to the ANSI example above::

    text = Text.assemble(("Hello", "bold magenta"), ", World!")
    console.print(text)

You can apply a style to given words in the text with :meth:`~rich.text.Text.highlight_words` or for ultimate control call :meth:`~rich.text.Text.highlight_regex` to highlight text matching a *regular expression*. 


Text attributes
~~~~~~~~~~~~~~~

The Text class has a number of parameters you can set on the constructor to modify how the text is displayed.

- ``justify`` should be "left", "center", "right", or "full", and will override default justify behavior.
- ``overflow`` should be "fold", "crop", or "ellipsis", and will override default overflow.
- ``no_wrap`` prevents wrapping if the text is longer then the available width.
- ``tab_size`` Sets the number of characters in a tab.

A Text instance may be used in place of a plain string virtually everywhere in the Rich API, which gives you a lot of control in how text renders within other Rich renderables. For instance, the following example right aligns text within a :class:`~rich.panel.Panel`::

    from rich import print
    from rich.panel import Panel
    from rich.text import Text
    panel = Panel(Text("Hello", justify="right"))
    print(panel)
```

## File: docs/source/traceback.rst
```
Traceback
=========

Rich can render Python tracebacks with syntax highlighting and formatting. Rich tracebacks are easier to read and show more code than standard Python tracebacks.

To see an example of a Rich traceback, running the following command::

    python -m rich.traceback


Printing tracebacks
-------------------

The :meth:`~rich.console.Console.print_exception` method will print a traceback for the current exception being handled. Here's an example::

    from rich.console import Console
    console = Console()

    try:
        do_something()
    except Exception:
        console.print_exception(show_locals=True)

The ``show_locals=True`` parameter causes Rich to display the value of local variables for each frame of the traceback.
 
See `exception.py <https://github.com/willmcgugan/rich/blob/master/examples/exception.py>`_ for a larger example.


Traceback Handler
-----------------

Rich can be installed as the default traceback handler so that all uncaught exceptions will be rendered with highlighting. Here's how::

    from rich.traceback import install
    install(show_locals=True)

There are a few options to configure the traceback handler, see :func:`~rich.traceback.install` for details.

Automatic Traceback Handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases you may want to have the traceback handler installed automatically without having to worry about importing the code in your module. You can do that by modifying the `sitecustomize.py` in your virtual environment. Typically it would be located in your virtual environment path, underneath the `site-packages` folder, something like this::

    ./.venv/lib/python3.9/site-packages/sitecustomize.py

In most cases this file will not exist. If it doesn't exist, you can create it by::

    $ touch .venv/lib/python3.9/site-packages/sitecustomize.py

Add the following code to the file::

    from rich.traceback import install
    install(show_locals=True)

At this point, the traceback will be installed for any code that is run within the virtual environment.

.. note::
    If you plan on sharing your code, it is probably best to include the traceback install in your main entry point module.


Suppressing Frames
------------------

If you are working with a framework (click, django etc), you may only be interested in seeing the code from your own application within the traceback. You can exclude framework code by setting the `suppress` argument on `Traceback`, `install`, `Console.print_exception`, and `RichHandler`, which should be a list of modules or str paths.

Here's how you would exclude `click <https://click.palletsprojects.com/en/8.0.x/>`_ from Rich exceptions:: 

    import click
    from rich.traceback import install
    install(suppress=[click])

Suppressed frames will show the line and file only, without any code.

Max Frames
----------

A recursion error can generate very large tracebacks that take a while to render and contain a lot of repetitive frames. Rich guards against this with a `max_frames` argument, which defaults to 100. If a traceback contains more than 100 frames then only the first 50, and last 50 will be shown. You can disable this feature by setting `max_frames` to 0.

Here's an example of printing a recursive error::

    from rich.console import Console


    def foo(n):
        return bar(n)


    def bar(n):
        return foo(n)


    console = Console()

    try:
        foo(1)
    except Exception:
        console.print_exception(max_frames=20)
```

## File: docs/source/tree.rst
```
Tree
====

Rich has a :class:`~rich.tree.Tree` class which can generate a tree view in the terminal. A tree view is a great way of presenting the contents of a filesystem or any other hierarchical data. Each branch of the tree can have a label which may be text or any other Rich renderable.

Run the following command to see a demonstration of a Rich tree::

    python -m rich.tree

The following code creates and prints a tree with a simple text label::

    from rich.tree import Tree
    from rich import print

    tree = Tree("Rich Tree")
    print(tree)

With only a single ``Tree`` instance this will output nothing more than the text "Rich Tree". Things get more interesting when we call :meth:`~rich.tree.Tree.add` to add more branches to the Tree. The following code adds two more branches::

    tree.add("foo")
    tree.add("bar")
    print(tree)

The tree will now have two branches connected to the original tree with guide lines.

When you call :meth:`~rich.tree.Tree.add` a new Tree instance is returned. You can use this instance to add more branches to, and build up a more complex tree. Let's add a few more levels to the tree::

    baz_tree = tree.add("baz")
    baz_tree.add("[red]Red").add("[green]Green").add("[blue]Blue")
    print(tree)


Tree Styles
~~~~~~~~~~~

The Tree constructor and :meth:`~rich.tree.Tree.add` method allows you to specify a ``style`` argument which sets a style for the entire branch, and ``guide_style`` which sets the style for the guide lines. These styles are inherited by the branches and will apply to any sub-trees as well.

If you set ``guide_style`` to bold, Rich will select the thicker variations of unicode line characters. Similarly, if you select the "underline2" style you will get double line style of unicode characters.


Examples
~~~~~~~~

For a more practical demonstration, see `tree.py <https://github.com/willmcgugan/rich/blob/master/examples/tree.py>`_ which can generate a tree view of a directory in your hard drive.
```
