from lark import Lark
from lark.lexer import Lexer as LarkLexerBase, Token as LarkToken
from lark.exceptions import UnexpectedToken
from Lexer import Lexer  # orig lexer class ni casper
from Token import TokenType  # orig tokentype class ni casper

# Custom lexer class for lark
class LarkLexer(LarkLexerBase):
    def __init__(self, lexer_conf):
        pass

    def lex(self, data):
        # Initialize the lexer (orig class natin)
        lexer = Lexer(data)
        while True:
            tok = lexer.next_token()
           
            if tok.type == TokenType.EOF:
                break

            # Calculates column number from position
            column = self._calculate_column(data, tok.position)
    
            lark_tok = LarkToken(
                type=tok.type.name,      # Uses the enum name (e.g., "IDENT", "INT_LIT")
                value=tok.literal,       # The token's literal value
                start_pos=tok.position,  # Starting position in the source
                line=tok.line_no,        # Line number
                column=column            # Calculated column number
            )
            yield lark_tok

    def _calculate_column(self, data, position):
        line_start = data.rfind('\n', 0, position) + 1
        return position - line_start + 1


grammar = """
    // Program structure
    program: BIRTH global_dec function_statements MAIN_CASPER LPAREN RPAREN LBRACE statements RBRACE GHOST

    // Global declarations
    global_dec: (global_statement global_tail)?
    global_tail: global_dec
    global_statement: data_type IDENT global_statement_tail
    global_statement_tail: | "," IDENT global_statement_tail | "=" global_dec_value global_tail2
    global_tail2: "," IDENT global_statement_tail | empty
    global_dec_value: global_value | "[" list_element "]"
    global_value: expression

    // Variable statements
    var_statement: data_type IDENT var_tail
    var_tail: | "=" tail_value var_tail2 | "," IDENT var_tail
    var_tail2: "," IDENT var_tail | empty
    tail_value: value | "[" list_element "]"

    // List elements
    list_element: literal element_tail
    element_tail: "," list_element | empty

    // Index
    index: INT_LIT | IDENT

    // Data types
    data_type: INT | FLT | BLN | CHR | STR

    // Values and expressions
    value: type_cast | expression | function_call
    type_cast: CONVERT_TO_INT LPAREN typecast_value RPAREN
            | CONVERT_TO_FLT LPAREN typecast_value RPAREN
            | CONVERT_TO_BLN LPAREN typecast_value RPAREN
            | CONVERT_TO_STR LPAREN typecast_value RPAREN
    typecast_value: expression | FUNCTION_NAME LPAREN RPAREN | input_statement
    expression: factor factor_tail
    factor: var_call | literal | "~" literal | "(" expression ")"
    factor_tail: ("+" | "-" | "*" | "/" | "%" | "**" | ">" | "<" | "==" | ">=" | "<=" | "!=" | "&&" | "||") factor factor_tail | empty
    literal: INT_LIT | FLT_LIT | DAY | NIGHT | CHR_LIT | STR_LIT

    // Variable calls
    var_call: IDENT var_call_tail
    var_call_tail: "[" index "]" | empty

    // Function statements
    function_statements: (ret_type FUNCTION_NAME LPAREN parameters RPAREN LBRACE statements revive RBRACE)?
    ret_type: FUNCTION | function_dtype
    function_dtype: FUNCTION_INT | FUNCTION_FLT | FUNCTION_CHR | FUNCTION_BLN | FUNCTION_STR 
                | FUNCTION_LIST_INT | FUNCTION_LIST_FLT | FUNCTION_LIST_CHR | FUNCTION_LIST_STR | FUNCTION_LIST_BLN
    parameters: (data_type IDENT parameters_tail)?
    parameters_tail: "," data_type IDENT parameters_tail | empty
    revive: REVIVE value | empty

    // Statements
    statements: local_dec statements_tail
    local_dec: var_statement | empty
    statements_tail: (conditional_statement | switch_statement | loop_statement | function_call | string_operation_statement | output_statement statements_tail2) | empty
    statements_tail2: statements

    // Conditional statements
    conditional_statement: CHECK LPAREN expression RPAREN LBRACE statements RBRACE conditional_tail OTHERWISE LBRACE statements RBRACE
    conditional_tail: otherwise_check_tail | empty
    otherwise_check_tail: OTHERWISE_CHECK LPAREN expression RPAREN LBRACE statements RBRACE conditional_tail

    // Switch statements
    switch_statement: SWAP LPAREN IDENT RPAREN LBRACE switch_condition OTHERWISE statements RBRACE
    switch_condition: SHIFT value COLON statements switchcond_tail
    switchcond_tail: switch_condition | empty

    // Loop statements
    loop_statement: for_loop | until_loop | repeat_until
    for_loop: FOR LPAREN control_variable SEMICOLON expression SEMICOLON update RPAREN LBRACE statements RBRACE
    until_loop: UNTIL LPAREN expression RPAREN LBRACE statements RBRACE
    repeat_until: REPEAT LBRACE statements RBRACE UNTIL LPAREN expression RPAREN
    control_variable: INT IDENT EQ INT_LIT
    update: var_call update_tail
    update_tail: postfix | assign_op value
    postfix: PLUS_PLUS | MINUS_MINUS

    // Function calls
    function_call: FUNCTION_NAME LPAREN arguments RPAREN

    // Arguments
    arguments: (arg_value arg_tail)?
    arg_tail: "," arg_value arg_tail | empty
    arg_value: literal | var_call

    // Output statements
    output_statement: DISPLAY value next_val
    next_val: "," value next_val | empty

    // Input statements
    input_statement: INPUT LPAREN RPAREN

    // String operation statements
    string_operation_statement: var_call string_operation_tail
    string_operation_tail: "+" string_val stringcon_tail | update_tail
    stringcon_tail: "+" string_val stringcon_tail | empty
    string_val: var_call | STR_LIT

    // Assignment operators
    assign_op: PLUS_EQ | MINUS_EQ | MUL_EQ | DIV_EQ | MOD_EQ | EQ

    // Empty rule
    empty:

    // Terminal declarations
    %declare BIRTH GHOST MAIN_CASPER LPAREN RPAREN LBRACE RBRACE COMMA IDENT INT FLT BLN CHR STR INT_LIT FLT_LIT DAY NIGHT CHR_LIT STR_LIT CONVERT_TO_INT CONVERT_TO_FLT CONVERT_TO_BLN CONVERT_TO_STR FUNCTION_NAME INPUT DISPLAY FUNCTION FUNCTION_INT FUNCTION_FLT FUNCTION_CHR FUNCTION_BLN FUNCTION_STR FUNCTION_LIST_INT FUNCTION_LIST_FLT FUNCTION_LIST_CHR FUNCTION_LIST_STR FUNCTION_LIST_BLN REVIVE CHECK OTHERWISE OTHERWISE_CHECK SWAP SHIFT FOR UNTIL REPEAT COLON SEMICOLON PLUS MINUS MULTIPLY DIVISION MODULO EXPONENT GT LT EQ_EQ GT_EQ LT_EQ NOT_EQ AND OR TILDE PLUS_PLUS MINUS_MINUS PLUS_EQ MINUS_EQ MUL_EQ DIV_EQ MOD_EQ EQ
"""


parser = Lark(grammar, parser='lalr', lexer=LarkLexer, start='program')

def parse(code):
    try:
        tree = parser.parse(code)
        return {"status": "success", "tree": str(tree)}
    except UnexpectedToken as e:
        unexpected = e.token
        expected = e.expected  
        error_msg = (
            f"Syntax error at line {unexpected.line}, column {unexpected.column}\n"
            f"Unexpected token '{unexpected.value}'\n"
            f"Expected: {', '.join(sorted(expected))}"
        )
        return error_msg
    except Exception as e:
        return f"Unexpected error: {e}"