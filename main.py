import argparse

from src import token, lexer, parser, evaluator

argparser = argparse.ArgumentParser()
argparser.add_argument('--repl', action='store_true')
argparser.add_argument('--lexer', action='store_true')
argparser.add_argument('--parser', action='store_true')
args = argparser.parse_args()

# ===
# Test Lexer
# ===

if __name__ == '__main__':


    if args.repl:
        while True:
            inp = input('>>> ')
            l = lexer.Lexer(inp=inp)
            lexer.read_char(l)
            p = parser.Parser(l=l)
            program = p.parse_program()
            if len(p.errors) > 0:
                for err in p.errors: print(err)
            else:
                evaluated = evaluator.eval_(program)
                print(evaluated.Inspect())

    elif args.lexer:
        inp = """let five = 5;
let ten = 10;

let add = fn(x, y) {
    x+y;
}

let result = add(five, ten);
!-/*5;
5 < 10 > 5;

if (5 < 10) {
    return true;
} else {
   return false;
}

10 == 10;
10 != 9;""".strip()

        l = lexer.Lexer(inp=inp)
        lexer.read_char(l)
        cnt = 0
        while True:
            tok = lexer.next_token(l)
            print(tok)
            if tok.type_ == token.EOF:
                break

    elif args.parser:
        inp = '''let x = 5;
let y = 10;
let foobar = 838383;

return 5;
foobar;
5;
-5;
!15;
5 - 5;
5 + 5;
5 * 5;
5 / 5;
5 == 5;
5 != 5;
-a * b + c;
a+b*x/d;
true;
false;
let foo = true;
let bar = false;

- (5 + 5) * 10 - 1;
x < y

if (x < y) { x };
if (x < y) { 5 } else { 0 } ;

fn(x, y) { return x + y; }

fn(x, y) { x + y; }

add(2, 3);
add(1, a + b + c * d / f + g, 2)
add(2, 3, add(4, 5));
'''.strip()
        l = lexer.Lexer(inp=inp)
        lexer.read_char(l)
        p = parser.Parser(l=l)
        program = p.parse_program()
        if len(p.errors) > 0:
            for err in p.errors: print(err)
        else:
            print(program)


    else:
        inp = """
5;
""".strip()
        l = lexer.Lexer(inp=inp)
        lexer.read_char(l)
        p = parser.Parser(l=l)
        program = p.parse_program()
        if len(p.errors) > 0:
            for err in p.errors: print(err)
            exit(0)
        ans = evaluator.eval_(program)
        print(ans.Inspect())

