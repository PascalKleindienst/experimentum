# Experimentum Example Application
This folder contains an example application to illustrate how the framework can be used to create/execute experiments and how to analyze and visualize them. This README will roughly explain how to such an example was created with the framework.

## Prerequisite
You already have installed Python & pip and the experimentum framework.

## Initialization
At first we need to initialize the base files and folders. To do that the frameworks provides the `experimentum-quickstart` command:

~~~console
$ experimentum-quickstart --root example
Welcome to the experimentum 1.0.0 quickstart utility.

Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets)

Selected root path: example

› Enter the name of the config folder [config]:
› Enter the name of the migrations folder [migrations]:
› Enter the name of the repositories folder [repositories]:
› Enter the name of the experiments folder [experiments]:
› Enter the name of the logs folder [logs]:
› Enter the name of the app: Example App
› Enter the description of the app []: This is an example on how to use the experimentum framework.
› Enter the name of the program [main.py]:

Creating folders ...
Creating main entry point ...
Creating config files ...
Creating migrations ...
Creating repositories ...
Done.
~~~
