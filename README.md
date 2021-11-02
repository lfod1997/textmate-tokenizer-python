# Python Wrapper of Textmate Tokenizer

A Python3 wrapper of the [vscode-textmate](https://github.com/microsoft/vscode-textmate) package, very dirty.

## Install

Make sure you have [Node.js](https://nodejs.org) installed, then:

1. Clone this repository and `cd` into it,
2. Run `python install.py` and make sure it's finished successfully,
3. It's ready -- you may install dependencies globally by running `npm install -g`, *this is optional*.

## Usage

**Note:** Because neither Python nor JavaScript is my major language and my knowledge is not very much beyond hello-worlds, the code is a ton of shit so if you find it annoying that's normal. You are super welcomed to contribute because I'm not likely to maintain this repo so long as it doesn't blow up my machine.

### 1. Try the JS

The `tokenize.js` works on its own:

```console
node src/tokenize.js your_file syntax_of_the_file path_to_the_resources_dir
```

and it pumps out a JSON array, each member is a JSON dict that contains the result of one line:

```json
[{"raw":"function sayHello(name) {","tokens":[{"startIndex":0,"endIndex":8,"scopes":["source.js","meta.function.js","storage.type.function.js"]},{"startIndex":8,"endIndex":9,"scopes":["source.js","meta.function.js"]},{"startIndex":9,"endIndex":17,"scopes":["source.js","meta.function.js","entity.name.function.js"]}...
```

It takes 3 parameters:

1. the path to your file to be tokenized,
2. the file's syntax, this can be found in `resources/ext.json`, which is a map from file extensions to syntaxes -- use the syntaxes provided here and nothing else,
3. the path of the resources folder, this *is* optional but *only* when the resource folder is located at exactly the working directory, so sadly you have to provide it if it's not.

The script can also process multiple files at one time, this saves the time spent on disk IO. In this case, the last parameter (the path of the resources folder) *must* be given, because I'm too lazy to parse any further:

```console
node src/tokenize.js file1 file2 file3... syntax_of_the_files path_to_the_resources_dir
```

and it prints multiple lines (actual linefeeds), each line is a JSON result that matches one file you provided, in order. You may redirect the output to a file or something but obviously that's not gonna be a valid JSON lol.

### 2. Try the wrapper

```console
cd src
python demo.py
```

This aims to demonstrate the format of the result, the `cd` is necessary.

### 3. To integrate into your project

The `resources` folder is important because it contains .tmLanguage files and the `ext.json` lookup table. As long as you can provide that folder and the JS script, the module will work.

I will not instruct here because, for Pyinstaller and Nuitka users, this may require some testing and design choices need to be made (if or not to include these files in your package). Anyway, if you've settled where to include these files, call the module's `initialize` function to specify them.

### 4. To add .tmLanguage files

Very simple:

1. [Download one](http://github.com/orgs/textmate/repositories) and open it, search for "`source.`" and you will find many matches, all of them followed by a same name like "js", and that's the "syntax" name,
2. Rename the file as "(the syntax name you've found).tmLanguage",
3. Put it in the `resources` folder,
4. Open the `ext.json`, append a key (the extension name of your file to be tokenized) and a string value (the syntax name), save.
