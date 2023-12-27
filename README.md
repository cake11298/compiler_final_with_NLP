# compiler_final_with_NLP

My current compiler has limited capabilities for independent problem-solving, but by integrating it with a large-scale language model, it can effectively handle additional parsing challenges.

# Usage Method:

1. Execute the command `python3 list.py < {your_lisp_code}`.
2. Wait for the result to be generated.

# Design
In this compiler project, I utilize **Pushdown Automata and Recursive Descent Parsing**. 
For instance, given an input like "(or (or #f #t #f) (and (and (and #t #t) #t) #t) #t)", 
the compiler first parses nested expressions such as "(and #t #t)" in the middle. 
It continues to process these nested expressions sequentially, based on their results. 
Upon completion of the recursion, the compiler generates the final result of the Lisp code.

# Risk Considerations in This Code

Due to the nature of the Large-Scale Language Model acting as a black box, there are inherent uncertainties in the returned results. Specifically, if there is a potential for network packet interception and modification by an attacker, this could compromise the security of your system. The compiler could become vulnerable if the modified code returned by the language model is executed without proper validation. Therefore, users are advised to exercise caution and ensure the integrity of the code before execution, especially when using the compiler in a networked environment.
