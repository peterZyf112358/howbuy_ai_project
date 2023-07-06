def parse_sql_to_tree(sql):
    # Split the SQL statement into individual clauses
    clauses = sql.split()

    # Construct the tree structure
    result = {}
    elements = []
    words = ''
    count = 0
    null_list = ["union", "except", "limit", "intersect"]
    empty_list = ["select", "from", "where", "having", "select"]

    for clause in clauses:
        count += 1
        # print(clause.lower() in null_list, clause.lower() in empty_list , words, elements, result)
        if clause.lower() == 'by':
            continue
        elif clause.lower() in null_list:
            if words.lower() in null_list:
                if elements:
                    result[words] = elements
                else:
                    result[words] = 'null'
            elif words.lower() in empty_list:
                result[words] = elements
            words = clause.lower()
            elements = []
        elif clause.lower() in empty_list:
            if words.lower() in null_list:
                if elements:
                    result[words] = elements
                else:
                    result[words] = 'null'
            elif words.lower() in empty_list:
                result[words] = elements
            words = clause.lower()
            elements = []
        elif clause.lower() == 'order' and clauses[count].lower() == 'by':
            if words.lower() in null_list:
                if elements:
                    result[words] = elements
                else:
                    result[words] = 'null'
            elif words.lower() in empty_list:
                result[words] = elements
            words = 'orderBy'
            elements = []
        else:
            elements.append(clause)
    result[words] = elements
    for item in null_list:
        if not result.get(item):
            result[item] = "null"
    for item in empty_list:
        if not result.get(item):
            result[item] = []
    return result


# Example usage
if __name__ == '__main__':
    sql_statement = "SELECT column1, column2 FROM table1 WHERE column1 > 10 ORDER BY column2 LIMIT 5"
    tree_structure = parse_sql_to_tree(sql_statement)
    print(tree_structure)
