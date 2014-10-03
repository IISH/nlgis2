{
 "metadata": {
  "name": "",
  "signature": "sha256:9509cd5ecf7e3d91bfc019d1efa4a828e592bd352e0a16093905deb34d5021cf"
 },
 "nbformat": 3,
 "nbformat_minor": 0,
 "worksheets": [
  {
   "cells": [
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "%matplotlib inline\n",
      "import urllib2\n",
      "import simplejson\n",
      "import json\n",
      "import sys\n",
      "import pandas as pd\n",
      "import random\n",
      "import vincent\n",
      "\n",
      "# Global\n",
      "apiurl = \"http://node-128.dev.socialhistoryservices.org/api/data\"\n",
      "amscodecolumn = 'amsterdam_code'\n",
      "yearcolumn = 'year'\n",
      "\n",
      "def load_api_data(apiurl, code, year):\n",
      "    amscode = str(code)\n",
      "    jsondataurl = apiurl + \"?code=\" + str(code)\n",
      "    \n",
      "    req = urllib2.Request(jsondataurl)\n",
      "    opener = urllib2.build_opener()\n",
      "    f = opener.open(req)\n",
      "    dataframe = simplejson.load(f)\n",
      "    return dataframe\n",
      "\n",
      "def data2frame(dataframe):\n",
      "    data = dataframe['data']\n",
      "    years = {}\n",
      "    debug = 0\n",
      "    datavalues = {}\n",
      "        \n",
      "    for item in data:\n",
      "        amscode = item[amscodecolumn]\n",
      "        year = item[yearcolumn]\n",
      "        datavalues[year] = item\n",
      "        if debug:\n",
      "            print str(amscode) + ' ' + str(year)\n",
      "            print item\n",
      "    \n",
      "    for year in datavalues:        \n",
      "        values = datavalues[year]\n",
      "        for name in values:\n",
      "            if debug:\n",
      "                print name + ' ' + str(values[name])\n",
      "    return datavalues\n",
      "    \n",
      "varcode = \"TXCU\"\n",
      "varyear = \"1997\"\n",
      "data = load_api_data(apiurl, varcode, varyear)\n",
      "# 'indicator': 'TK', 'code': 'TXCU', 'naam': 'ADORP', 'amsterdam_code': '10996', 'value': 89.0, 'year': 1937, 'id': 1, 'cbsnr': '1'\n",
      "# Create DataFrame object pf and load data \n",
      "df = pd.DataFrame(data['data'])\n",
      "#print df['indicator']\n",
      "\n",
      "# Exploring dataset\n",
      "print df.head()\n",
      "newframe = df[['year', 'amsterdam_code', 'naam', 'value']]"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [
      {
       "output_type": "stream",
       "stream": "stdout",
       "text": [
        "  amsterdam_code cbsnr  code   id indicator        naam  value  year\n",
        "0          10996     1  TXCU    1        TK       ADORP     89  1937\n",
        "1          10999     2  TXCU  209        TK      ADUARD     49  1937\n",
        "2          10886     3  TXCU  426        TK  APPINGEDAM    315  1937\n",
        "3          10539     4  TXCU  660        TK       BAFLO    260  1937\n",
        "4          10425     5  TXCU  877        TK       BEDUM    263  1937\n",
        "\n",
        "[5 rows x 8 columns]\n"
       ]
      }
     ],
     "prompt_number": 137
    },
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "Now let's calculate total values for each city and show 10 cities"
     ]
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "newframe = df[['naam', 'value']][:20]\n",
      "print newframe"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [
      {
       "output_type": "stream",
       "stream": "stdout",
       "text": [
        "             naam  value\n",
        "0           ADORP     89\n",
        "1          ADUARD     49\n",
        "2      APPINGEDAM    315\n",
        "3           BAFLO    260\n",
        "4           BEDUM    263\n",
        "5          BEERTA     57\n",
        "6          BIERUM    420\n",
        "7        TEN BOER    247\n",
        "8        DELFZIJL    288\n",
        "9          EENRUM    128\n",
        "10         EZINGE     42\n",
        "11   FINSTERWOLDE     54\n",
        "12      GRONINGEN   2331\n",
        "13     GROOTEGAST    389\n",
        "14     GRIJPSKERK     73\n",
        "15       HAREN GR    327\n",
        "16        KANTENS    189\n",
        "17  KLOOSTERBUREN     78\n",
        "18           LEEK    375\n",
        "19          LEENS    195\n",
        "\n",
        "[20 rows x 2 columns]\n"
       ]
      }
     ],
     "prompt_number": 138
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "values = newframe['value'][:20]\n",
      "names = newframe['naam'][:20]\n",
      "list_data = []\n",
      "for value in values:\n",
      "    list_data.append(value)\n",
      "\n",
      "bar = vincent.Bar(list_data)\n",
      "print list_data\n",
      "vincent.core.initialize_notebook()\n",
      "\n",
      "bar.axis_titles(x='CityID', y='Value')\n",
      "bar.display()"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [
      {
       "output_type": "stream",
       "stream": "stdout",
       "text": [
        "[89.0, 49.0, 315.0, 260.0, 263.0, 57.0, 420.0, 247.0, 288.0, 128.0, 42.0, 54.0, 2331.0, 389.0, 73.0, 327.0, 189.0, 78.0, 375.0, 195.0]\n"
       ]
      },
      {
       "html": [
        "\n",
        "           <script>\n",
        "               \n",
        "                function vct_load_lib(url, callback){\n",
        "                      if(typeof d3 !== 'undefined' &&\n",
        "                         url === 'http://d3js.org/d3.v3.min.js'){\n",
        "                        callback()\n",
        "                      }\n",
        "                      var s = document.createElement('script');\n",
        "                      s.src = url;\n",
        "                      s.async = true;\n",
        "                      s.onreadystatechange = s.onload = callback;\n",
        "                      s.onerror = function(){\n",
        "                        console.warn(\"failed to load library \" + url);\n",
        "                        };\n",
        "                      document.getElementsByTagName(\"head\")[0].appendChild(s);\n",
        "                };\n",
        "                var vincent_event = new CustomEvent(\n",
        "                  \"vincent_libs_loaded\",\n",
        "                  {bubbles: true, cancelable: true}\n",
        "                );\n",
        "                \n",
        "               function load_all_libs(){\n",
        "                  console.log('Loading Vincent libs...')\n",
        "                  vct_load_lib('http://d3js.org/d3.v3.min.js', function(){\n",
        "                  vct_load_lib('http://d3js.org/d3.geo.projection.v0.min.js', function(){\n",
        "                  vct_load_lib('http://wrobstory.github.io/d3-cloud/d3.layout.cloud.js', function(){\n",
        "                  vct_load_lib('http://wrobstory.github.io/vega/vega.v1.3.3.js', function(){\n",
        "                  window.dispatchEvent(vincent_event);\n",
        "                  });\n",
        "                  });\n",
        "                  });\n",
        "                  });\n",
        "               };\n",
        "               if(typeof define === \"function\" && define.amd){\n",
        "                    if (window['d3'] === undefined ||\n",
        "                        window['topojson'] === undefined){\n",
        "                        require.config(\n",
        "                            {paths: {\n",
        "                              d3: 'http://d3js.org/d3.v3.min',\n",
        "                              topojson: 'http://d3js.org/topojson.v1.min'\n",
        "                              }\n",
        "                            }\n",
        "                          );\n",
        "                        require([\"d3\"], function(d3){\n",
        "                            console.log('Loading Vincent from require.js...')\n",
        "                            window.d3 = d3;\n",
        "                            require([\"topojson\"], function(topojson){\n",
        "                                window.topojson = topojson;\n",
        "                                load_all_libs();\n",
        "                            });\n",
        "                        });\n",
        "                    } else {\n",
        "                        load_all_libs();\n",
        "                    };\n",
        "               }else{\n",
        "                    console.log('Require.js not found, loading manually...')\n",
        "                    load_all_libs();\n",
        "               };\n",
        "\n",
        "           </script>"
       ],
       "metadata": {},
       "output_type": "display_data",
       "text": [
        "<IPython.core.display.HTML at 0xaf76672c>"
       ]
      },
      {
       "html": [
        "<div id=\"vis6875aef783df4a92bc278bf3d63896d9\"></div>\n",
        "<script>\n",
        "   ( function() {\n",
        "     var _do_plot = function() {\n",
        "       if (typeof vg === 'undefined') {\n",
        "         window.addEventListener('vincent_libs_loaded', _do_plot)\n",
        "         return;\n",
        "       }\n",
        "       vg.parse.spec({\"axes\": [{\"scale\": \"x\", \"title\": \"CityID\", \"type\": \"x\"}, {\"scale\": \"y\", \"title\": \"Value\", \"type\": \"y\"}], \"data\": [{\"name\": \"table\", \"values\": [{\"col\": \"data\", \"idx\": 0, \"val\": 89.0}, {\"col\": \"data\", \"idx\": 1, \"val\": 49.0}, {\"col\": \"data\", \"idx\": 2, \"val\": 315.0}, {\"col\": \"data\", \"idx\": 3, \"val\": 260.0}, {\"col\": \"data\", \"idx\": 4, \"val\": 263.0}, {\"col\": \"data\", \"idx\": 5, \"val\": 57.0}, {\"col\": \"data\", \"idx\": 6, \"val\": 420.0}, {\"col\": \"data\", \"idx\": 7, \"val\": 247.0}, {\"col\": \"data\", \"idx\": 8, \"val\": 288.0}, {\"col\": \"data\", \"idx\": 9, \"val\": 128.0}, {\"col\": \"data\", \"idx\": 10, \"val\": 42.0}, {\"col\": \"data\", \"idx\": 11, \"val\": 54.0}, {\"col\": \"data\", \"idx\": 12, \"val\": 2331.0}, {\"col\": \"data\", \"idx\": 13, \"val\": 389.0}, {\"col\": \"data\", \"idx\": 14, \"val\": 73.0}, {\"col\": \"data\", \"idx\": 15, \"val\": 327.0}, {\"col\": \"data\", \"idx\": 16, \"val\": 189.0}, {\"col\": \"data\", \"idx\": 17, \"val\": 78.0}, {\"col\": \"data\", \"idx\": 18, \"val\": 375.0}, {\"col\": \"data\", \"idx\": 19, \"val\": 195.0}]}, {\"name\": \"stats\", \"source\": \"table\", \"transform\": [{\"keys\": [\"data.idx\"], \"type\": \"facet\"}, {\"type\": \"stats\", \"value\": \"data.val\"}]}], \"height\": 500, \"legends\": [], \"marks\": [{\"from\": {\"data\": \"table\", \"transform\": [{\"keys\": [\"data.col\"], \"type\": \"facet\"}, {\"height\": \"data.val\", \"point\": \"data.idx\", \"type\": \"stack\"}]}, \"marks\": [{\"properties\": {\"enter\": {\"fill\": {\"field\": \"data.col\", \"scale\": \"color\"}, \"width\": {\"band\": true, \"offset\": -1, \"scale\": \"x\"}, \"x\": {\"field\": \"data.idx\", \"scale\": \"x\"}, \"y\": {\"field\": \"y\", \"scale\": \"y\"}, \"y2\": {\"field\": \"y2\", \"scale\": \"y\"}}}, \"type\": \"rect\"}], \"type\": \"group\"}], \"padding\": \"auto\", \"scales\": [{\"domain\": {\"data\": \"table\", \"field\": \"data.idx\"}, \"name\": \"x\", \"range\": \"width\", \"type\": \"ordinal\", \"zero\": false}, {\"domain\": {\"data\": \"stats\", \"field\": \"sum\"}, \"name\": \"y\", \"nice\": true, \"range\": \"height\"}, {\"domain\": {\"data\": \"table\", \"field\": \"data.col\"}, \"name\": \"color\", \"range\": \"category20\", \"type\": \"ordinal\"}], \"width\": 960}, function(chart) {\n",
        "         chart({el: \"#vis6875aef783df4a92bc278bf3d63896d9\"}).update();\n",
        "       });\n",
        "     };\n",
        "     _do_plot();\n",
        "   })();\n",
        "</script>\n",
        "<style>.vega canvas {width: 100%;}</style>\n",
        "        "
       ],
       "metadata": {},
       "output_type": "display_data",
       "text": [
        "<IPython.core.display.HTML at 0xadc5a28c>"
       ]
      }
     ],
     "prompt_number": 142
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [],
     "language": "python",
     "metadata": {},
     "outputs": [],
     "prompt_number": 139
    }
   ],
   "metadata": {}
  }
 ]
}