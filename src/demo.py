import json
import textmate

if __name__ == '__main__':
    textmate.initialize(libdir='../resources')
    
    out = textmate.tokenize(
        ['../test_cases/test.js', '../test_cases/test1.js'])
    print(f'out = {out}')
    
    # Discard blank lines
    out = [l for l in out[0] if l['raw'] != '']
    
    # Show structure
    print('\nstructure of each result:', json.dumps(out, indent=4, ))
    
    # Filter 'string.quoted.other.template.js' scope
    strings = []
    for line in out:
        for token in line['tokens']:
            if 'string.quoted.other.template.js' in token['scopes']:
                text = line['raw'][token['startIndex']:token['endIndex']]
                if text != '"':
                    strings.append(text)
    print('\nfilter "string.quoted.other.template.js":\n', strings, ' -> ', str().join(strings))
