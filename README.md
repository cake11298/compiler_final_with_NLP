# compiler_final_with_NLP

My current compiler has limited capabilities for independent problem-solving, but by integrating it with a large-scale language model, it can effectively handle additional parsing challenges.

# Using Method:

1. python3 list.py < {your_lisp_code}
2. wait for the result

# Design
I use the **Pushdown Automata and Recursive Decent Parser** in this compiler Project.
if there is "(or (or #f #t #f) (and (and (and #t #t) #t) #t) #t)"
it will parse "(and #t #t)" in the middle first
so on parse this "(and #t #t)" because the (and #t #t) result is #t
...
Once Upon the recursion end.
it will generate the result of this list code. by process_exp() function

In the very beginning I use Token_parser to split the input string to token stream.