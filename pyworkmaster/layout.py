class Tree:
    def __init__(self, name='root', children=None):
        self.name = name
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.name + (str(self.children) if self.children else "")

    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)


def parse(expr):
    """ Parse layout expression into a tree structure.

    | split vertically
    / split horizontally

    ex. parse("A|B")
      "|"
     /   \
    A     B

    ex. parse("A|(B/C)")
         "|"
        /   \
      A     "/"
           /   \
         B       C
    """
    tree, _ = parse_tree(expr)
    return tree


def parse_tree(expr, start_from=0, left_parentheses=False):
    node = Tree()
    s_ptr = start_from
    curr_name = ""
    expect_rhs = False
    while s_ptr < len(expr):
        s = expr[s_ptr]
        if s.isalpha():
            expect_rhs = False
            curr_name += s
        else:
            if curr_name:
                node.add_child(Tree(curr_name))
                curr_name = ""

            if s == '|' or s == "/":
                if node.name == "root" or node.name == s:
                    expect_rhs = True
                    node.name = s
                else:
                    raise Exception("ambigious")
            elif s == '(':
                expect_rhs = False
                subtree, s_ptr = parse_tree(expr, start_from=s_ptr+1, left_parentheses=True)
                node.add_child(subtree)
            elif s == ')':
                if left_parentheses:
                    left_parentheses = False
                    break
                else:
                    raise Exception("where is left parentheses")
        s_ptr += 1

    if left_parentheses:
        raise Exception("where is right parentheses")
    if expect_rhs:
        raise Exception("got not rhs")
    if curr_name:
        node.add_child(Tree(curr_name))
    if node.name == "root" and len(node.children) == 1:
        node = node.children[0]
    return node, s_ptr
