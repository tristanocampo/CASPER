from lark import Lark, Lexer as LarkLexerBase, Token as LarkToken, UnexpectedToken
from Lexer import Lexer  # Your custom Lexer class
from Token import TokenType  # Your TokenType enum

# Custom lexer class to bridge your Lexer with Lark
class LarkLexer(LarkLexerBase):
    def __init__(self, lexer_conf):
        # No initialization needed here; Lark passes this but we initialize in lex
        pass

    def lex(self, data):
        # Initialize your Lexer with the input data
        lexer = Lexer(data)
        while True:
            tok = lexer.next_token()
            # Stop when we reach EOF
            if tok.type == TokenType.EOF:
                break
            # Calculate column number from position
            column = self._calculate_column(data, tok.position)
            # Convert your Token to a Lark Token
            lark_tok = LarkToken(
                type=tok.type.name,      # Use the enum name (e.g., "IDENT", "INT_LIT")
                value=tok.literal,       # The token's literal value
                start_pos=tok.position,  # Starting position in the source
                line=tok.line_no,        # Line number
                column=column            # Calculated column number
            )
            yield lark_tok

    def _calculate_column(self, data, position):
        # Find the start of the line to calculate the column
        line_start = data.rfind('\n', 0, position) + 1
        return position - line_start + 1

# Define the grammar for your language
# Lark grammar
grammar = """
    // Program structure
    program: BIRTH unli_newline global_dec maybe_newline function_statements maybe_newline main_function unli_newline GHOST

    // Newlines
    maybe_newline: | NEWLINE maybe_newline
    unli_newline: NEWLINE | NEWLINE unli_newline

    // Main function
    main_function: MAIN_CASPER "(" ")" maybe_newline "{" maybe_newline statements maybe_newline "}"

    // Global declarations
    global_dec: (global_statement unli_newline global_tail) | empty
    global_tail: global_dec
    global_statement: data_type IDENT global_statement_tail
    global_statement_tail: empty | "," IDENT global_statement_tail | "=" global_dec_value global_tail2
    global_tail2: empty | "," IDENT global_statement_tail
    global_dec_value: global_value | "[" list_element "]"
    global_value: expression

    // Variable statements
    var_statement: data_type IDENT var_tail unli_newline
    var_tail: empty | "=" tail_value var_tail2 | "," IDENT var_tail
    var_tail2: empty | "," IDENT var_tail
    tail_value: value | "[" list_element "]"

    // List elements
    list_element: literal element_tail
    element_tail: empty | "," list_element

    // Data types
    data_type: INT | FLT | BLN | CHR | STR

    // Values and expressions
    value: type_cast | expression | function_call
    type_cast: CONVERT_TO_INT "(" typecast_value ")" | CONVERT_TO_FLT "(" typecast_value ")" 
             | CONVERT_TO_BLN "(" typecast_value ")" | CONVERT_TO_STR "(" typecast_value ")"
    typecast_value: expression | FUNCTION_NAME "(" ")" | input_statement
    expression: factor factor_tail
    factor: var_call | literal | "~" literal | "(" expression ")"
    factor_tail: empty | "+" expression | "-" expression | "*" expression | "/" expression 
                | "%" expression | "**" expression | ">" expression | "<" expression 
                | "==" expression | ">=" expression | "<=" expression | "!=" expression 
                | "and" expression | "or" expression
    literal: INT_LIT | FLT_LIT | DAY | NIGHT | CHR_LIT | STR_LIT

    // Variable calls
    var_call: IDENT var_call_tail
    var_call_tail: empty | "[" index "]"
    index: INT_LIT | IDENT

    // Function statements
    function_statements: (maybe_newline ret_type FUNCTION_NAME "(" parameters ")" maybe_newline "{" unli_newline statements revive maybe_newline "}") | empty
    ret_type: FUNCTION | function_dtype
    function_dtype: FUNCTION_INT | FUNCTION_FLT | FUNCTION_CHR | FUNCTION_BLN | FUNCTION_STR 
                  | FUNCTION_LIST_INT | FUNCTION_LIST_FLT | FUNCTION_LIST_CHR | FUNCTION_LIST_STR | FUNCTION_LIST_BLN
    parameters: (data_type IDENT parameters_tail) | empty
    parameters_tail: empty | "," data_type IDENT parameters_tail
    revive: (REVIVE value) | empty

    // Statements
    statements: empty | (local_dec maybe_newline statements_tail)
    statements_tail: (string_operation_statement | conditional_statement | switch_statement 
                     | loop_statement | function_call | output_statement) unli_newline statements_tail2
    statements_tail2: statements
    local_dec: empty | var_statement

    // Conditional statements (simplified)
    conditional_statement: CHECK "(" expression ")" maybe_newline "{" maybe_newline statements "}" maybe_newline conditional_tail maybe_newline OTHERWISE maybe_newline "{" maybe_newline statements "}"
    conditional_tail: empty | OTHERWISE_CHECK "(" expression ")" maybe_newline "{" maybe_newline statements "}" maybe_newline conditional_tail

    // Add more rules as needed...

    // Empty rule
    empty:

    // Terminals (ensure these match your lexer's token types)
    %declare BIRTH GHOST NEWLINE MAIN_CASPER IDENT INT FLT BLN CHR STR INT_LIT FLT_LIT DAY NIGHT CHR_LIT STR_LIT 
             CONVERT_TO_INT CONVERT_TO_FLT CONVERT_TO_BLN CONVERT_TO_STR FUNCTION_NAME INPUT DISPLAY 
             FUNCTION FUNCTION_INT FUNCTION_FLT FUNCTION_CHR FUNCTION_BLN FUNCTION_STR 
             FUNCTION_LIST_INT FUNCTION_LIST_FLT FUNCTION_LIST_CHR FUNCTION_LIST_STR FUNCTION_LIST_BLN 
             REVIVE CHECK OTHERWISE OTHERWISE_CHECK SWAP SHIFT FOR UNTIL REPEAT
"""

# Create the Lark parser with your custom lexer
parser = Lark(grammar, parser='lalr', lexer=LarkLexer)

# Function to parse code
def parse(code):
    try:
        tree = parser.parse(code)
        return {"status": "success", "tree": str(tree)}
    except UnexpectedToken as e:
        # Get the unexpected token and the expected token types
        unexpected = e.token
        expected = e.expected  # A set of token type names expected at this point
        error_msg = (
            f"Syntax error at line {unexpected.line}, column {unexpected.column}: "
            f"unexpected token '{unexpected.value}' (type: {unexpected.type}).\n"
            f"Expected one of: {', '.join(sorted(expected))}"
        )
        return {"status": "error", "message": error_msg}
    except Exception as e:
        # Catch any other unexpected errors
        return {"status": "error", "message": f"Unexpected error: {e}"}