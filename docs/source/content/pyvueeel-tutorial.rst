Py, Vue and eel
===============

How to develop application with these tools and how to use mypythontools functions in such an app.

It's recommended way to download ``project-starter`` where all the files for gui are already edited and ready to use.
There are also working examples of calling from python to js and vice versa as well as example of alerting or plotting.

https://github.com/Malachov/mypythontools/tree/master/content

If you want to build just what is necessary from scratch, you can use this tutorial.
Go in web documentation on readthedocs if reading from IDE


Structure
---------
::

    - myproject
        - gui
            - generated with Vue CLI
        - app.py

app.py
------
::

    from mypythontools import pyvueeel
    from mypythontools.pyvueeel import expose

    # Expose python functions to Js with decorator
    @expose
    def load_data(settings):
        return {'Hello': 1}
    if __name__ == '__main__':
        pyvueeel.run_gui()

You can return dict - will be object in js
You can return list - will be an array in js

**Call js function from Py**::

    pyvueeel.eel.load_data()

gui
---

Generate gui folder with Vue CLI

    npm install -g @vue/cli
    vue create gui

Goto folder and optionally::

    vue add vuex
    vue add vuetify
    vue add router

main.js
-------
::

    if (process.env.NODE_ENV == 'development') {

    try {
        window.eel.set_host("ws://localhost:8686");

    } catch (error) {
        document.getElementById('app').innerHTML = 'Py side is not running. Start app.py with debugger.'
        console.error(error);
    }

    Vue.config.productionTip = true
    Vue.config.devtools = true
    } else {
    Vue.config.productionTip = false
    Vue.config.devtools = false
    }

You can expose function to be callable from python. Import and then
window.eel.expose(function_name, 'function_name')

.env
----

Create empty files .env.development and add `VUE_APP_EEL=http://localhost:8686/eel.js`

Create empty .env.production and add `VUE_APP_EEL=eel.js`


index.html
----------

In public folder add to index.html::

    <script type="text/javascript" src="<%= VUE_APP_EEL %>"></script>

vue.config.js
-------------::

    let devtool_mode

    if (process.env.NODE_ENV === "development") {
      devtool_mode = "source-map";
    } else {
      devtool_mode = false;
    }

    module.exports = {
      outputDir: "web_builded",
      transpileDependencies: ["vuetify"],
      productionSourceMap: process.env.NODE_ENV != "production",

      configureWebpack: {
        devtool: devtool_mode,
      },
    };


Tips, tricks
------------

**VS Code plugins for developing**

- npm
- vetur
- Vue VSCode Snippets
- vuetify-vscode
