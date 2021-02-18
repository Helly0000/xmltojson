# -*- coding:UTF-8 -*-
import sqlparse
import xmltodict
import json
ParatranzTestDict = {}
ParatranzTestList = []


class ParatranzItem():
    def __init__(self):
        self.key = None
        self.original = None
        self.translation = None


def getAttagFunc(xml_node):
    if '@Tag' in xml_node.keys():
        item = ParatranzItem()
        item.key = xml_node['@Tag']
        if '@Language' in xml_node.keys():
            if xml_node['@Language'] == "zh_Hans_CN":
                item.translation = xml_node['Text']
            elif xml_node['@Language'] == "en_US":
                item.original = xml_node['Text']
            else:
                return
        else:
            item.original = xml_node['Text']
        if xml_node['@Tag'] in ParatranzTestDict.keys():
            if item.original is not None:
                ParatranzTestDict[xml_node['@Tag']].original = item.original
            if item.translation is not None:
                ParatranzTestDict[xml_node['@Tag']].translation = item.translation
        else:
            ParatranzTestDict[xml_node['@Tag']] = item


def getAttag(xml_node):
    if not xml_node:
        return
    if type(xml_node) == type([]):
        for listnode in xml_node:
            getAttagFunc(listnode)
    else:
        getAttagFunc(xml_node)
        for node in xml_node:
            getAttag(xml_node[node])


def getSQLnode(sql):
    stmts = sqlparse.split(sql)
    for stmt in stmts:
        # 解析SQL
        stmt_parsed = sqlparse.parse(stmt)
        if len(stmt_parsed) < 1:
            break
        for token in stmt_parsed[0].tokens:
            if str(type(token)) == "<class 'sqlparse.sql.Function'>":
                # print('Function', token.value) # 跳过了插入结构命令，反正哪个字段在哪儿也不重要，后面是根据关键字匹配的
                pass
            if str(type(token)) == "<class 'sqlparse.sql.Values'>":
                for subtoken in token.tokens:
                    if str(type(subtoken)) == "<class 'sqlparse.sql.Parenthesis'>":
                        for subtokenlv2 in subtoken.tokens:
                            if str(type(subtokenlv2)) == "<class 'sqlparse.sql.IdentifierList'>":
                                i = 0
                                for subtokenlv3 in subtokenlv2.tokens:
                                    if str(type(subtokenlv3)) == "<class 'sqlparse.sql.Identifier'>":
                                        sql_str = eval(str(subtokenlv3))
                                        i += 1
                                # print (i)
                                if i == 3 or i == 2:
                                    new_item = ParatranzItem()
                                    for subtokenlv3 in subtokenlv2.tokens:
                                        if str(type(subtokenlv3)) == "<class 'sqlparse.sql.Identifier'>":
                                            sql_str = eval(str(subtokenlv3))
                                            if "en_US" in sql_str:
                                                # language_tag = "en_US"
                                                pass  # en_US 不是必须的
                                            elif "LOC_" in sql_str and not (sql_str[0] == "{" and sql_str[-1] == "}"):
                                                # if sql_str[0] == "{" and sql_str[-1] == "}":
                                                #     break
                                                new_item.key = sql_str
                                            else:
                                                new_item.original = sql_str
                                    # ParatranzTestDict[new_item.key] = new_item
                                    if new_item.key is not None and new_item.key in ParatranzTestDict.keys():
                                        if new_item.original is not None:
                                            ParatranzTestDict[new_item.key].original = new_item.original
                                        if new_item.translation is not None:
                                            ParatranzTestDict[new_item.key].translation = new_item.translation
                                            if ParatranzTestDict[new_item.key].translation == new_item.original:
                                                ParatranzTestDict[new_item.key].translation = None
                                    else:
                                        ParatranzTestDict[new_item.key] = new_item


def loadXMLfile(data_path):
    xml_data = open(data_path, 'r', encoding='utf-8')
    xml_data_str = xml_data.read()
    xml_data_dict = xmltodict.parse(xml_data_str, encoding='utf-8')
    getAttag(xml_data_dict)


def loadSQLfile(data_sql_path):
    sql_str = open(data_sql_path, 'r', encoding='utf-8')
    sql_data_str = sql_str.read()  # TODO
    getSQLnode(sql_data_str)


def main():
    # loadXMLfile(r'C:\xmltocsv\en.xml')
    loadXMLfile(r'C:\xmltocsv\cn2.xml')
    loadSQLfile(r'C:\xmltocsv\en2.sql')
    # 中英文XML或者SQL都可以加入任意数量
    for item in ParatranzTestDict:
        if ParatranzTestDict[item].original is not None:
            if ParatranzTestDict[item].original != ParatranzTestDict[item].translation:
                ParatranzTestList.append(
                    {"key": ParatranzTestDict[item].key, "original": ParatranzTestDict[item].original, "translation": ParatranzTestDict[item].translation})
            else:
                ParatranzTestList.append(
                    {"key": ParatranzTestDict[item].key, "original": ParatranzTestDict[item].original, "translation": None})
        else:
            print('无原文tag：', ParatranzTestDict[item].key)
            ParatranzTestList.append({"key": ParatranzTestDict[item].key, "original": ParatranzTestDict[item].key, "translation": ParatranzTestDict[item].translation})

    # print (json.dumps(ParatranzTestList, indent = 4, ensure_ascii=False))
    output_path = r'C:\xmltocsv\output2.json'
    json_output = open(output_path, 'w', encoding='utf-8')
    json_output.writelines(json.dumps(
        ParatranzTestList, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
