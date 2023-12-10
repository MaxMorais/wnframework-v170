SELECT CONCAT(REPEAT('	 ', COUNT(parent.name) - 1), node.name) AS name FROM [tab%(based_on)s] AS node,[tab%(based_on)s] AS parent WHERE node.lft BETWEEN parent.lft AND parent.rgt AND node.docstatus !=2 GROUP BY node.name ORDER BY node.lft