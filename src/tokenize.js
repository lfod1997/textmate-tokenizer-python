const fs = require('fs');
const path = require('path');
const vsctm = require('vscode-textmate');
const onig = require('vscode-oniguruma');

var reg = null;
var grammar = null;

function readFilePromise(path) {
    return new Promise((resolve, reject) =>
        fs.readFile(path, { encoding: 'utf-8' },
            (error, data) => error ? reject(error) : resolve(data)));
}

function tmInitialize(sourceSyntaxName, libDir = './resources') {
    let grammarFile = path.join(libDir, `${sourceSyntaxName}.tmLanguage`);
    let wasmFile = path.join(libDir, 'onig.wasm');
    reg = new vsctm.Registry({
        onigLib: onig.loadWASM(fs.readFileSync(wasmFile).buffer)
            .then(() => {
                return {
                    createOnigScanner(patterns) { return new onig.OnigScanner(patterns); },
                    createOnigString(s) { return new onig.OnigString(s); }
                };
            }),
        loadGrammar: (_) => readFilePromise(grammarFile).then(vsctm.parseRawGrammar)
    });

    return reg.loadGrammar('source.' + sourceSyntaxName).then(g => { grammar = g; });
}

function tmTokenize(sourceFile) {
    return new Promise((callback, _) => {
        let sourceText = fs.readFileSync(sourceFile, { encoding: 'utf-8' }).split(/\r?\n|(?<!\n)\r/g);
        let ruleStack = vsctm.INITIAL;
        let lines = [];
        let result = '';
        for (let i = 0; i < sourceText.length; i++) {
            let lineObj = {
                raw: sourceText[i],
                tokens: []
            };
            let lineTokens = grammar.tokenizeLine(lineObj.raw, ruleStack);
            for (let j = 0; j < lineTokens.tokens.length; j++) {
                lineObj.tokens.push(lineTokens.tokens[j]);
            }
            lines.push(lineObj);
            ruleStack = lineTokens.ruleStack;
        }
        result = JSON.stringify(lines);
        callback(result);
    });
}

if (process.argv.length < 4) {
    console.error('usage 1: node tokenize.js <sourceFile> <sourceSyntaxName> [<libraryDir> - default: "./resources"]\nusage 2: node tokenize.js <sourceFiles...> <sourceSyntaxName> <libraryDir>');
    process.exit(1);
} else if (process.argv.length < 5) {
    tmInitialize(process.argv[3])
        .then(() => tmTokenize(process.argv[2]).then(console.log));
} else if (process.argv.length < 6) {
    tmInitialize(process.argv[3], process.argv[4])
        .then(() => tmTokenize(process.argv[2]).then(console.log));
} else {
    let argpos = process.argv.length - 2;
    let queue = tmInitialize(process.argv[argpos], process.argv[argpos + 1]);
    for (let i = 2; i < argpos; ++i) {
        queue = queue.then(() => tmTokenize(process.argv[i]).then(console.log));
    }
}
