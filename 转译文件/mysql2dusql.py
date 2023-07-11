################################
# Assumptions:
#   1. sql is correct
#   2. only table name has alias
#   3. only one intersect/union/except
#
# val: number(float)/string(str)/sql(dict)
# col_unit: (agg_id, col_id, isDistinct(bool))
# val_unit: (unit_op, col_unit1, col_unit2)
# table_unit: (table_type, col_unit/sql)
# cond_unit: (not_op, op_id, val_unit, val1, val2)
# condition: [cond_unit1, 'and'/'or', cond_unit2, ...]
# sql {
#   'select': (isDistinct(bool), [(agg_id, val_unit), (agg_id, val_unit), ...])
#   'from': {'table_units': [table_unit1, table_unit2, ...], 'conds': condition}
#   'where': condition
#   'groupBy': [col_unit1, col_unit2, ...]
#   'orderBy': ('asc'/'desc', [val_unit1, val_unit2, ...])
#   'having': condition
#   'limit': None/limit value
#   'intersect': None/sql
#   'except': None/sql
#   'union': None/sql
# }
################################

import json
import sqlite3
import nltk

from nltk import word_tokenize

CLAUSE_KEYWORDS = ('select', 'from', 'where', 'group',
                   'order', 'limit', 'intersect', 'union', 'except')
JOIN_KEYWORDS = ('join', 'on', 'as')

WHERE_OPS = ('not', 'between', '=', '>', '<', '>=',
             '<=', '!=', 'in', 'like', 'is', 'exists')
UNIT_OPS = ('none', '-', '+', "*", '/')
AGG_OPS = ('none', 'max', 'min', 'count', 'sum', 'avg')
TABLE_TYPE = {
    'sql': "sql",
    'table_unit': "table_unit",
}

COND_OPS = ('and', 'or')
SQL_OPS = ('intersect', 'union', 'except')
ORDER_OPS = ('desc', 'asc')


class Schema:
    """
    Simple schema which maps table&column to a unique identifier
    """

    def __init__(self, schema, table_names, column_names):
        self._schema = schema
        self._idMap, self._colId, self._tabId = self._map(self._schema)

    @property
    def schema(self):
        return self._schema

    @property
    def idMap(self):
        return self._idMap

    @property
    def colId(self):
        return self._colId

    @property
    def tabId(self):
        return self._tabId

    def _map(self, schema):
        idMap = {'*': "__all__"}
        colId = {'*': 0}
        tabId = {}
        col_id = 1
        for key, vals in schema.items():
            for val in vals:
                idMap[key.lower() + "." + val.lower()] = "__" + \
                                                         key.lower() + "." + val.lower() + "__"
                colId[key.lower() + "." + val.lower()] = col_id
                col_id += 1
        tab_id = 0
        for key in schema:
            idMap[key.lower()] = "__" + key.lower() + "__"
            tabId[key.lower()] = tab_id
            tab_id += 1

        return idMap, colId, tabId


def get_schema(db):

    """
    从db获得schema
    Get database's schema, which is a dict with table name as key
    and list of column  names as value
    :param db: database path
    :return: schema dict
    """

    schema = {}
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    # conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # fetch table names
    cursor.execute("show fields from kg.基金表")
    tables = cursor.fetchall()
    # #print(tables)
    column_name = [str(table[0].lower()) for table in tables]
    # fetch table info

    for index in range(len(tables)):
        schema[column_name[index]] = str(tables[index][1].lower())

    return schema


def get_schema_from_json(fpath):
    "从json获得schema"
    with open(fpath) as f:
        data = json.load(f)

    schema = {}
    for entry in data:
        table_dict = entry['tables']
        for tablename in table_dict:
            cols = [str(col) for col in table_dict[tablename]['header']]
            schema[tablename] = cols

    return schema


def tokenize(string):
    ""
    string = str(string)
    # ensures all string values wrapped by "" problem??
    string = string.replace("\'", "\"")
    quote_idxs = [idx for idx, char in enumerate(string) if char == '"']
    assert len(quote_idxs) % 2 == 0, "Unexpected quote"

    # keep string value as token
    vals = {}
    for i in range(len(quote_idxs) - 1, -1, -2):
        qidx1 = quote_idxs[i - 1]
        qidx2 = quote_idxs[i]
        val = string[qidx1: qidx2 + 1]
        key = "__val_{}_{}__".format(qidx1, qidx2)
        string = string[:qidx1] + key + string[qidx2 + 1:]
        vals[key] = val

    toks = [word.lower() for word in word_tokenize(string)]
    # replace with string value token
    for i in range(len(toks)):
        if toks[i] in vals:
            toks[i] = vals[toks[i]]

    # find if there exists !=, >=, <=
    eq_idxs = [idx for idx, tok in enumerate(toks) if tok == "="]
    eq_idxs.reverse()
    prefix = ('!', '>', '<')
    for eq_idx in eq_idxs:
        pre_tok = toks[eq_idx - 1]
        if pre_tok in prefix:
            toks = toks[:eq_idx - 1] + [pre_tok + "="] + toks[eq_idx + 1:]

    return toks


def scan_alias(toks):
    """Scan the index of 'as' and build the map for all alias"""
    as_idxs = [idx for idx, tok in enumerate(toks) if tok == 'as']
    alias = {}
    for idx in as_idxs:
        alias[toks[idx + 1]] = toks[idx - 1]
    # #print('scan_alias', alias)
    return alias


def get_tables_with_alias(schema, toks):
    tables = scan_alias(toks)
    # print('get_tables_with_alias',tables)
    for key in schema:
        assert key not in tables, "Alias {} has the same name in table".format(
            key)
        tables[key] = key
    return tables


def parse_col(toks, start_idx, tables_with_alias, schema, default_tables=None):
    """
        :returns next idx, column id
    """
    # print(toks)
    tok = toks[start_idx]
    if tok == "*":
        return start_idx + 1, schema.colId[tok]

    if '.' in tok:  # if token is a composite
        alias, col = tok.split('.')
        key = tables_with_alias[alias] + "." + col
        return start_idx + 1, schema.colId[key]

    assert default_tables is not None and len(
        default_tables) > 0, "Default tables should not be None or empty"

    for alias in default_tables:
        table = tables_with_alias[alias]
        if tok in schema.schema[table]:
            key = table + "." + tok
            return start_idx + 1, schema.colId[key]

    assert False, "Error col: {}".format(tok)


def parse_col_unit(toks, start_idx, tables_with_alias, schema, default_tables=None):
    """
        :returns next idx, (agg_op id, col_id)
    """
    idx = start_idx
    len_ = len(toks)
    isBlock = False
    isDistinct = False
    if toks[idx] == '(':
        isBlock = True
        idx += 1

    if toks[idx] in AGG_OPS:
        agg_id = AGG_OPS.index(toks[idx])
        idx += 1
        assert idx < len_ and toks[idx] == '('
        idx += 1
        if toks[idx] == "distinct":
            idx += 1
            isDistinct = True
        idx, col_id = parse_col(
            toks, idx, tables_with_alias, schema, default_tables)
        assert idx < len_ and toks[idx] == ')'
        idx += 1
        return idx, (agg_id, col_id, isDistinct)

    if toks[idx] == "distinct":
        idx += 1
        isDistinct = True
    agg_id = AGG_OPS.index("none")
    idx, col_id = parse_col(
        toks, idx, tables_with_alias, schema, default_tables)

    if isBlock:
        assert toks[idx] == ')'
        idx += 1  # skip ')'

    return idx, (agg_id, col_id, isDistinct)


def parse_val_unit(toks, start_idx, tables_with_alias, schema, default_tables=None):
    idx = start_idx
    len_ = len(toks)
    isBlock = False
    if toks[idx] == '(':
        isBlock = True
        idx += 1

    col_unit1 = None
    col_unit2 = None
    unit_op = UNIT_OPS.index('none')

    idx, col_unit1 = parse_col_unit(
        toks, idx, tables_with_alias, schema, default_tables)
    if idx < len_ and toks[idx] in UNIT_OPS:
        unit_op = UNIT_OPS.index(toks[idx])
        idx += 1
        idx, col_unit2 = parse_col_unit(
            toks, idx, tables_with_alias, schema, default_tables)

    if isBlock:
        assert toks[idx] == ')'
        idx += 1  # skip ')'

    return idx, (unit_op, col_unit1, col_unit2)


def parse_table_unit(toks, start_idx, tables_with_alias, schema, db_id):
    """
        :returns next idx, table id, table name
    """
    idx = start_idx
    len_ = len(toks)
    key = tables_with_alias[toks[idx]]

    if idx + 1 < len_ and toks[idx + 1] == "as":
        idx += 3
    else:
        idx += 1

    return idx, schema.tabId[key], key


def parse_value(toks, start_idx, tables_with_alias, schema, default_tables=None):
    idx = start_idx
    len_ = len(toks)

    isBlock = False
    if toks[idx] == '(':
        isBlock = True
        idx += 1

    if toks[idx] == 'select':
        idx, val = parse_sql(toks, idx, tables_with_alias, schema)
    elif "\"" in toks[idx]:  # token is a string value
        val = toks[idx]
        idx += 1
    else:
        try:
            val = float(toks[idx])
            val = toks[idx]
            idx += 1
        except:
            end_idx = idx
            while end_idx < len_ and toks[end_idx] != ',' and toks[end_idx] != ')' \
                    and toks[end_idx] != 'and' and toks[end_idx] not in CLAUSE_KEYWORDS and toks[
                end_idx] not in JOIN_KEYWORDS:
                end_idx += 1

            idx, val = parse_col_unit(
                toks[start_idx: end_idx], 0, tables_with_alias, schema, default_tables)
            idx = end_idx

    if isBlock:
        assert toks[idx] == ')'
        idx += 1

    return idx, val


def parse_condition(toks, start_idx, tables_with_alias, schema, default_tables=None):
    idx = start_idx
    len_ = len(toks)
    conds = []

    while idx < len_:
        idx, val_unit = parse_val_unit(
            toks, idx, tables_with_alias, schema, default_tables)
        not_op = False
        if toks[idx] == 'not':
            not_op = True
            idx += 1

        assert idx < len_ and toks[idx] in WHERE_OPS, "Error condition: idx: {}, tok: {}".format(
            idx, toks[idx])
        op_id = WHERE_OPS.index(toks[idx])
        idx += 1
        val1 = val2 = None
        # between..and... special case: dual values
        if op_id == WHERE_OPS.index('between'):
            idx, val1 = parse_value(
                toks, idx, tables_with_alias, schema, default_tables)
            assert toks[idx] == 'and'
            idx += 1
            idx, val2 = parse_value(
                toks, idx, tables_with_alias, schema, default_tables)
        else:  # normal case: single value
            idx, val1 = parse_value(
                toks, idx, tables_with_alias, schema, default_tables)
            val2 = None

        conds.append((not_op, op_id, val_unit, val1, val2))

        if idx < len_ and (toks[idx] in CLAUSE_KEYWORDS or toks[idx] in (")", ";") or toks[idx] in JOIN_KEYWORDS):
            break

        if idx < len_ and toks[idx] in COND_OPS:
            conds.append(toks[idx])
            idx += 1  # skip and/or

    return idx, conds


def parse_select(toks, start_idx, tables_with_alias, schema, default_tables=None):
    idx = start_idx
    len_ = len(toks)

    assert toks[idx] == 'select', "'select' not found"
    idx += 1
    isDistinct = False
    if idx < len_ and toks[idx] == 'distinct':
        idx += 1
        isDistinct = True
    val_units = []

    while idx < len_ and toks[idx] not in CLAUSE_KEYWORDS:
        agg_id = AGG_OPS.index("none")
        if toks[idx] in AGG_OPS:
            agg_id = AGG_OPS.index(toks[idx])
            idx += 1
        idx, val_unit = parse_val_unit(
            toks, idx, tables_with_alias, schema, default_tables)
        val_units.append((agg_id, val_unit))
        if idx < len_ and toks[idx] == ',':
            idx += 1  # skip ','

    return idx, (isDistinct, val_units)


def parse_from(toks, start_idx, tables_with_alias, schema, db_id):
    """
    Assume in the from clause, all table units are combined with join
    """
    assert 'from' in toks[start_idx:], "'from' not found"

    len_ = len(toks)
    idx = toks.index('from', start_idx) + 1
    default_tables = []
    table_units = []
    conds = []

    while idx < len_:
        isBlock = False
        if toks[idx] == '(':
            isBlock = True
            idx += 1

        if toks[idx] == 'select':
            idx, sql = parse_sql(toks, idx, tables_with_alias, schema)
            table_units.append((TABLE_TYPE['sql'], sql))
        else:
            if idx < len_ and toks[idx] == 'join':
                idx += 1  # skip join
            idx, table_unit, table_name = parse_table_unit(
                toks, idx, tables_with_alias, schema, db_id)
            table_units.append((TABLE_TYPE['table_unit'], table_unit))
            default_tables.append(table_name)
        if idx < len_ and toks[idx] == "on":
            idx += 1  # skip on
            idx, this_conds = parse_condition(
                toks, idx, tables_with_alias, schema, default_tables)
            if len(conds) > 0:
                conds.append('and')
            conds.extend(this_conds)

        if isBlock:
            assert toks[idx] == ')'
            idx += 1
        if idx < len_ and (toks[idx] in CLAUSE_KEYWORDS or toks[idx] in (")", ";")):
            break

    return idx, table_units, conds, default_tables


def parse_where(toks, start_idx, tables_with_alias, schema, default_tables):
    idx = start_idx
    len_ = len(toks)

    if idx >= len_ or toks[idx] != 'where':
        return idx, []

    idx += 1
    idx, conds = parse_condition(
        toks, idx, tables_with_alias, schema, default_tables)
    return idx, conds


def parse_group_by(toks, start_idx, tables_with_alias, schema, default_tables):
    idx = start_idx
    len_ = len(toks)
    col_units = []

    if idx >= len_ or toks[idx] != 'group':
        return idx, col_units

    idx += 1
    assert toks[idx] == 'by'
    idx += 1

    while idx < len_ and not (toks[idx] in CLAUSE_KEYWORDS or toks[idx] in (")", ";")):
        idx, col_unit = parse_col_unit(
            toks, idx, tables_with_alias, schema, default_tables)
        col_units.append(col_unit)
        if idx < len_ and toks[idx] == ',':
            idx += 1  # skip ','
        else:
            break

    return idx, col_units


def parse_order_by(toks, start_idx, tables_with_alias, schema, default_tables):
    idx = start_idx
    len_ = len(toks)
    val_units = []
    order_type = 'asc'  # default type is 'asc'

    if idx >= len_ or toks[idx] != 'order':
        return idx, val_units

    idx += 1
    assert toks[idx] == 'by'
    idx += 1

    while idx < len_ and not (toks[idx] in CLAUSE_KEYWORDS or toks[idx] in (")", ";")):
        idx, val_unit = parse_val_unit(
            toks, idx, tables_with_alias, schema, default_tables)
        val_units.append(val_unit)
        if idx < len_ and toks[idx] in ORDER_OPS:
            order_type = toks[idx]
            idx += 1
        if idx < len_ and toks[idx] == ',':
            idx += 1  # skip ','
        else:
            break

    return idx, (order_type, val_units)


def parse_having(toks, start_idx, tables_with_alias, schema, default_tables):
    idx = start_idx
    len_ = len(toks)

    if idx >= len_ or toks[idx] != 'having':
        return idx, []

    idx += 1
    idx, conds = parse_condition(
        toks, idx, tables_with_alias, schema, default_tables)
    return idx, conds


def parse_limit(toks, start_idx):
    idx = start_idx
    len_ = len(toks)

    if idx < len_ and toks[idx] == 'limit':
        idx += 2
        return idx, int(toks[idx - 1])

    return idx, None


def parse_sql(toks, start_idx, tables_with_alias, schema, db_id):
    isBlock = False  # indicate whether this is a block of sql/sub-sql
    len_ = len(toks)
    idx = start_idx

    sql = {}
    if toks[idx] == '(':
        isBlock = True
        idx += 1

    # parse from clause in order to get default tables
    from_end_idx, table_units, conds, default_tables = parse_from(
        toks, start_idx, tables_with_alias, schema, db_id)
    sql['from'] = {'table_units': table_units, 'conds': conds}
    # select clause
    _, select_col_units = parse_select(
        toks, idx, tables_with_alias, schema, default_tables)
    idx = from_end_idx
    sql['select'] = select_col_units
    # where clause
    idx, where_conds = parse_where(
        toks, idx, tables_with_alias, schema, default_tables)
    sql['where'] = where_conds
    # group by clause
    idx, group_col_units = parse_group_by(
        toks, idx, tables_with_alias, schema, default_tables)
    sql['groupBy'] = group_col_units
    # having clause
    idx, having_conds = parse_having(
        toks, idx, tables_with_alias, schema, default_tables)
    sql['having'] = having_conds
    # order by clause
    idx, order_col_units = parse_order_by(
        toks, idx, tables_with_alias, schema, default_tables)
    sql['orderBy'] = order_col_units
    # limit clause
    idx, limit_val = parse_limit(toks, idx)
    sql['limit'] = limit_val

    idx = skip_semicolon(toks, idx)
    if isBlock:
        assert toks[idx] == ')'
        idx += 1  # skip ')'
    idx = skip_semicolon(toks, idx)

    # intersect/union/except clause
    for op in SQL_OPS:  # initialize IUE
        sql[op] = None
    if idx < len_ and toks[idx] in SQL_OPS:
        sql_op = toks[idx]
        idx += 1
        idx, IUE_sql = parse_sql(toks, idx, tables_with_alias, schema)
        sql[sql_op] = IUE_sql
    return idx, sql


def load_data(fpath):
    with open(fpath) as f:
        data = json.load(f)
    return data


def get_sql(schema, query, db_id):
    #print('get_sql', schema)
    toks = tokenize(query)
    # print(schema.schema, toks)
    tables_with_alias = get_tables_with_alias(schema.schema, toks)
    # print('get_sql table_with_alias', tables_with_alias)
    _, sql = parse_sql(toks, 0, tables_with_alias, schema, db_id)

    return sql


def skip_semicolon(toks, start_idx):
    idx = start_idx
    while idx < len(toks) and toks[idx] == ";":
        idx += 1
    return idx


def get_schema_from_json2(fpath):
    with open(fpath, encoding='utf-8') as f:
        data = json.load(f)

    schemas = {}
    table_schemas = []
    dbs = []
    # #print('get_schema_from_json2', data)
    for entry in data:
        schema = {}
        db_id = entry["db_id"]
        db = {}
        dbs.append(db)
        db["db_id"] = db_id
        table_names_original = entry.get("table_names_original", entry["table_names"])
        column_names_original = entry.get("column_names_original", entry["column_names"])
        type_ = entry.get("column_types", [])
        # #print(column_names_original, type_)
        assert len(column_names_original) == len(type_), "%d,%d" % (len(column_names_original), len(type_))
        db_tables = {}
        db["tables"] = db_tables
        for i, table in enumerate(table_names_original):
            #print('get_schema_from_json2', table_names_original)
            header = []
            cells = []
            db_tables[table] = {"cell": cells, "header": header, "table_name": table, "type": type_}

            table = table.lower()
            schema[table] = []
            for j, column in enumerate(column_names_original):
                if j == 0:
                    continue
                if i == column[0]:
                    schema[table].append(column[1].lower())
                    header.append(column[1])
            kkk = ["海外型", "类固收", "股权型", "对冲型", "股票型"]
            kkkk = ["在售", "非在售", "在售", "非在售", "非在售"]
            for kk in range(5):
                cell = []
                for h in header:
                    if h == "产品分类":
                        cell.append(kkk[kk])
                    elif h == "是否在销":
                        cell.append(kkkk[kk])
                    else:
                        cell.append("")
                cells.append(cell)
        #print("get_schema_from_json2", schemas)
        schemas[db_id] = Schema(schema, table_names_original, column_names_original)
    return schemas, dbs

import pymysql
import pandas as pd
import numpy as np

def get_mysql_conn():
    conn = pymysql.connect(host='192.168.209.110', port=3307, user='messi', password='messi', charset='utf8',
                           database='kg')
    return conn

def get_data_from_db(sql):
    conn = get_mysql_conn()
    rst = pd.read_sql(sql, conn)
    return rst

# def generate_schema():
#     results = []
#     result = {"db_id":"kg"}
#     schema_df =pd.read_excel('C:/Users/yifan.zhao01/Desktop/模板.xlsx')
#     #print(schema_df)
#     result["table_names"] = ["基金表", "基金经理表", "机构表"]
#     # result["table_names"] = ["基金表"]
#     result["table_names_original"] = result["table_names"]
#     result["column_types"] = ["text"]
#     result["column_names"] = [[-1,"*"]]
#     result['foreign_keys'] = []
#     result['primary_keys'] = []
#     for idx,row in schema_df.iterrows():
#         col_name = row['列名']
#         col_type = str(row['字段类型'])
#         table_name = row['表名']
#         pk = row['主键']
#         fk = row['外键']
#         if col_type.startswith('varchar') or col_type.startswith('text'):
#             col_type = 'text'
#         elif col_type.startswith('double'):
#             col_type = 'number'
#         elif col_type.startswith('date'):
#             col_type = 'time'
#         else:
#             raise Exception('new Type %s' % (col_type))
#         if pk == 'pk':
#             result['primary_keys'].append(idx+1)
#
#         if not pd.isnull(fk):
#             result['foreign_keys'].append([idx+1,int(fk)])
#
#         result["column_names"].append([result["table_names"].index(table_name),col_name])
#         result["column_types"].append(col_type)
#     result['column_names_original'] = result["column_names"]
#
#     results.append(result)
#     json.dump(results,open('C:/Users/yifan.zhao01/Desktop/db_schema.json',encoding='utf-8',mode='w'),ensure_ascii=False)


# def generate_content():
#     results = []
#     result = {"db_id":"kg","tables": {}}
#     entity_df = pd.read_excel('D:/work_task/RAT-SQL/数据生成/样例实体.xlsx')
#     fund_list = []
#     company_list = []
#     manager_list = []
#     for idx, row in entity_df.iterrows():
#         if row['实体类型'] == '基金':
#             fund_list.append(str(row['实体']))
#
#         if row['实体类型'] == '基金经理':
#             manager_list.append(str(row['实体']))
#
#         if row['实体类型'] == '机构':
#             company_list.append(str(row['实体']))
#
#
#     table_detail = generate_table_cells(fund_list,"基金表","基金全称")
#     result["tables"].update(table_detail)
#
#     table_detail = generate_table_cells(manager_list,"基金经理表","经理姓名")
#     result["tables"].update(table_detail)
#
#     table_detail = generate_table_cells(company_list,"机构表","机构名称")
#     result["tables"].update(table_detail)
#     results.append(result)
#     json.dump(results, open('D:\work_task\RAT-SQL\数据生成\db_content.json', encoding='utf-8', mode='w'), ensure_ascii=False)


def generate_table_cells(fund_list,table_name,condition,colum_names ='*'):
    """

    :param fund_list: 基金列
    :param table_name: 表名
    :param condition: 结构
    :param colum_names:
    :return:
    """

    schema_df = pd.read_excel('C:/Users/yifan.zhao01/Desktop/模板.xlsx')
    types = []
    for col_type in schema_df[schema_df['表名'] == table_name]['字段类型'].values:
        if col_type.startswith('varchar') or col_type.startswith('text'):
            types.append('text')
        elif col_type.startswith('double'):
            types.append('number')
        elif col_type.startswith('date'):
            types.append('time')

    colum_names = ','.join(schema_df[schema_df['表名'] == table_name]["列名"].tolist())
    table_detail = {}
    sql = "select %s from kg.%s where %s in (\"%s\")" % (colum_names,table_name,condition,"\",\"".join(fund_list))
    df = get_data_from_db(sql)
    cell = []
    table_detail['header'] = df.columns.values.tolist()
    table_detail['table_name'] = table_name
    table_detail['type'] = types
    for idx,row in df.iterrows():
        c = []
        for value in row.values:
            if value is None or pd.isnull(value) or value == "":
                c.append('')
            else:
                c.append(str(value))
        cell.append(c)
    table_detail['cell'] = cell
    return {table_name:table_detail}


def convert_schema():
    with open('D:\work_task\RAT-SQL\数据生成\db_schema.json',encoding='utf-8') as f:
        schemas_json = json.load(f)

    with open('D:\work_task\RAT-SQL\数据生成\db_content.json',encoding='utf-8') as f:
        dbs = json.load(f)
    schemas = {}
    for entry in schemas_json:
        schema = {}
        db_id = entry["db_id"]
        db = {}
        dbs.append(db)
        db["db_id"] = db_id
        table_names_original = entry.get("table_names_original", entry["table_names"])
        column_names_original = entry.get("column_names_original", entry["column_names"])
        type_ = entry.get("column_types", [])
        assert len(column_names_original) == len(type_), "%d,%d" % (len(column_names_original), len(type_))
        db_tables = {}
        db["tables"] = db_tables
        for i, table in enumerate(table_names_original):
            header = []
            cells = []
            db_tables[table] = {"cell": cells, "header": header, "table_name": table, "type": type_}

            table = table.lower()
            schema[table] = []
            for j, column in enumerate(column_names_original):
                if j == 0:
                    continue
                if i == column[0]:
                    schema[table].append(column[1].lower())
                    header.append(column[1])
        schemas[db_id] = Schema(
            schema, table_names_original, column_names_original)
    return schemas, dbs

def process(file1,file2, train,val,test, schemas):
    df_datas = pd.read_excel(file1)
    df_datas = df_datas.sort_values('RAND', ascending=False).groupby(['表名', '属性名']).head(50)
    df_select_entity_from_single_attr = pd.read_excel(file2)
    #print(len(df_datas))
    df_datas = pd.concat([df_datas, df_select_entity_from_single_attr], axis=0)
    #print(len(df_datas))
    df_datas = df_datas.sample(frac=1, random_state=666).reset_index(drop=True)

    train_size = int(len(df_datas) * 0.8)
    val_size = int(len(df_datas) * 0.1)
    test_size = int(len(df_datas) * 0.1)
    # test_size = 10

    real_train = []

    for idx, row in df_datas.loc[0:train_size].iterrows():
        data = {}
        data["db_id"] = 'kg'
        data["query"] = str(row['SQL'])
        data["question"] = str(row['NL'])
        data["question_id"] = "qid" + str(idx)
        sql_ast = get_sql(schemas[db_id], str(row['SQL']), db_id)
        data["sql"] = sql_ast
        train.append(data)
        real_train.append("%s#%s" % (str(row['NL']), str(row['SQL'])))
    #print(len(train))

    real_vals = []
    for idx, row in df_datas.loc[train_size:train_size + val_size].iterrows():
        data = {}
        data["db_id"] = 'kg'
        data["query"] = str(row['SQL'])
        data["question"] = str(row['NL'])
        data["question_id"] = "qid" + str(idx)
        sql_ast = get_sql(schemas[db_id], str(row['SQL']), db_id)
        data["sql"] = sql_ast
        val.append(data)
    #print(len(val))

    for idx, row in df_datas.loc[train_size + val_size:].iterrows():
        data = {}
        data["db_id"] = 'kg'
        data["query"] = str(row['SQL'])
        data["question"] = str(row['NL'])
        data["question_id"] = "qid" + str(idx)
        sql_ast = get_sql(schemas[db_id], str(row['SQL']), db_id)
        data["sql"] = sql_ast
        test.append(data)
        real_vals.append("%s#%s" % (str(row['NL']), str(row['SQL'])))
    #print(len(test))
    return real_vals, real_train


if __name__ == "__main__":
    db_id = "kg"
    query = "select 基金表.基金全称 from 基金表 where 基金表.到期日期 > '2021-02-01'"
    test1 = get_schema("E:\project\da orderta\DuSQL\db_schema.json")

    schema_df = pd.read_excel('C:/Users/yifan.zhao01/Desktop/模板.xlsx', sheet_name='实体查多属性模板')

    schemas = get_schema_from_json2(
        "E:\project\data\DuSQL\db_schema.json")
    ##print('获得schemas')

    sql = get_sql(schemas[0][db_id], query, db_id)
    print(sql)
    #print('获得sql')
    #print(json.dumps(sql))
    # sss = json.dumps(sql, indent=2, ensure_ascii=False)
    # #print(sss)
    # db_id = "kg"
    # # schemas, dbs = get_schema_from_json2(
    # #     "/data/text2sql_learn/pro/rat-sql/data/howbuy/db_schema.json")
    # # generate_schema()
    # # generate_content()
    # schemas, dbs = convert_schema()
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # train = []
    # dev = []
    # db_content = []
    # qid = 0
    # test = []
    # real_vals,real_train = process("D:\work_task\RAT-SQL\数据生成\实体查单属性.xlsx","D:\work_task\RAT-SQL\数据生成\单属性查实体.xlsx", train,dev,test)
    # # process("data/howbuy/sql-kg.txt", train)
    # # process("data/howbuy/test.sql", train)


    # def process_test(file, train):
    #     with open(file, "r") as r:
    #         for line in r.readlines():
    #             data = {}
    #             devdata = {}
    #             line = line.strip()
    #             if line:
    #                 sql_arr = line.split("#")
    #                 sql = sql_arr[-1].lower()
    #                 if "from" in sql:
    #                     sql = sql.replace("`", "").replace(";", "")
    #                     #print(sql_arr[0], sql_arr[-1])
    #                     data["query"] = ""
    #                     devdata["query"] = ""
    #                     data["db_id"] = db_id
    #                     devdata["db_id"] = db_id
    #                     data["question"] = sql_arr[0]
    #                     devdata["question"] = sql_arr[0]
    #                     data["question_id"] = "qid" + str(len(train))
    #                     devdata["question_id"] = "qid" + str(len(dev))
    #                     sql_ast = get_sql(schemas[db_id], sql, db_id)
    #                     data["sql"] = ""
    #                     devdata["sql"] = ""
    #                     #print(sql_ast)
    #                     train.append(data)
    #                     dev.append(devdata)
    #
    #
    # process("data/howbuy/test.sql", test)
    #

    # json.dump(train,open("D:\work_task\RAT-SQL\数据生成\\train.json",encoding='utf-8',mode='w'),ensure_ascii=False)
    # json.dump(dev, open("D:\work_task\RAT-SQL\数据生成\\dev.json", encoding='utf-8', mode='w'), ensure_ascii=False)
    # json.dump(test, open("D:\work_task\RAT-SQL\数据生成\\test.json", encoding='utf-8', mode='w'), ensure_ascii=False)
    # with open("D:\work_task\RAT-SQL\数据生成\\test.sql", "w",encoding='utf-8') as w:
    #     w.write('\n'.join(real_vals))
    # with open("D:\work_task\RAT-SQL\数据生成\\train.sql", "w",encoding='utf-8') as w:
    #     w.write('\n'.join(real_train))
    # with open("D:\work_task\RAT-SQL\数据生成\\dev.json", "w",encoding='utf-8') as w:
    #     w.write(json.dumps(dev, indent=2, ensure_ascii=False))
    # with open("D:\work_task\RAT-SQL\数据生成\\test.json", "w") as w:
    #     w.write(json.dumps(test, indent=2, ensure_ascii=False))
    # with open("data/howbuy/dev.json", "w") as w:
    #     w.write(json.dumps(train, indent=2, ensure_ascii=False))
    # with open("data/howbuy/test.json", "w") as w:
    #     w.write(json.dumps(test, indent=2, ensure_ascii=False))

    # with open("data/howbuy/db_content.json", "w") as ww:
    #     ww.write(json.dumps(dbs, indent=2, ensure_ascii=False))
