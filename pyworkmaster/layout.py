class Tree:
    def __init__(self, name="root", children=None, size=None):
        self.name = name
        self.size = None
        self.children = []
        self.last_added = None
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        ssize = f"[{self.size}%]"if self.size else ""
        schild = (str(self.children) if self.children else "")
        return f"{self.name}{ssize}{schild}"

    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)
        self.last_added = node

    def add_size(self, size):
        if self.last_added:
            self.last_added.size = size
        else:
            raise Exception("assigning size to unknown")


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
    if expr:
        tree, _ = parse_tree(expr)
        return tree


def parse_tree(expr, start_from=0, left_parentheses=False):
    node = Tree()
    s_ptr = start_from
    curr_name = ""
    expect_rhs = False
    while s_ptr < len(expr):
        s = expr[s_ptr]
        if s.isalpha() or s.isnumeric():
            expect_rhs = False
            curr_name += s

        elif not s.isspace():
            if curr_name:
                node.add_child(Tree(curr_name))
                curr_name = ""

            if s == "|" or s == "/":
                if node.name == "root" or node.name == s:
                    expect_rhs = True
                    node.name = s
                else:
                    raise Exception("ambigious")
            elif s == "%":
                raise Exception("why % here?")
            elif s == "(":
                expect_rhs = False
                subtree, s_ptr = parse_tree(
                    expr, start_from=s_ptr + 1, left_parentheses=True
                )
                node.add_child(subtree)
            elif s == ")":
                if left_parentheses:
                    left_parentheses = False
                    break
                else:
                    raise Exception("where is left parentheses")
            elif s == "[":
                num_val = ""
                while s_ptr < len(expr):
                    s_ptr += 1
                    s = expr[s_ptr]
                    if s.isnumeric():
                        num_val += s
                    elif s == "%":
                        continue
                    elif s == "]":
                        break
                    else:
                        raise Exception(f"unexpected: {s}")
                if num_val:
                    node.add_size(int(num_val))

            elif s == "]":
                raise Exception("where is left bracket")
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
