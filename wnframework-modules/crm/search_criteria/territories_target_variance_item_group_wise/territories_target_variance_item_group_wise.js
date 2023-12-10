report.customize_filters = function() {

  this.hide_all_filters();

  this.add_filter({fieldname:'territory', label:'Territory', fieldtype:'Link', options:'Territory',ignore : 1,parent:'Target Detail'});
  
  this.add_filter({fieldname:'fiscal_year', label:'Fiscal Year', fieldtype:'Link', options:'Fiscal Year', report_default:sys_defaults.fiscal_year, ignore : 1, parent:'Target Detail'});
 
  this.add_filter({fieldname:'period', label:'Period', fieldtype:'Select', options:'Monthly'+NEWLINE+'Quarterly'+NEWLINE+'Half Yearly'+NEWLINE+'Annual',report_default:'Quarterly',ignore : 1, parent:'Target Detail'});
  
  this.add_filter({fieldname:'under', label:'Under',fieldtype:'Select', options:'Sales Order'+NEWLINE+'Delivery Note'+NEWLINE+'Sales Invoice',report_default:'Sales Order',ignore : 1, parent:'Target Detail'});
  
  this.add_filter({fieldname : 'target_on', label:'Target On', fieldtype:'Select', options:'Quantity'+NEWLINE+'Amount',report_default:'Quantity',ignore : 1,parent:'Target Detail'});
  this.filter_fields_dict['Target Detail'+FILTER_SEP +'Territory'].df.in_first_page = 1;
}
this.mytabs.items['Select Columns'].hide();
report.get_query = function() {

  territory = this.filter_fields_dict['Target Detail'+FILTER_SEP+'Territory'].get_value();
  target_on = this.filter_fields_dict['Target Detail'+FILTER_SEP+'Target On'].get_value();   
  under = this.filter_fields_dict['Target Detail'+FILTER_SEP+'Under'].get_value();   
  if(under == 'Sales Invoice') under = 'Receivable Voucher';

  if(target_on == 'Quantity'){
	q1 = 't1.target_qty AS "Target Quantity"';
	q2 = '0 AS "Target Quantity"';
	cond1 = 'ifnull(t1.target_qty,"")!=""';
	cond2 = 'ifnull(t5.target_qty,"")!=""';
  }  
  else{
	q1 = 't1.target_amount AS "Target Amount"';
	q2 = '0 AS "Target Amount"';
	cond1 = 'ifnull(t1.target_amount,"")!=""';
	cond2 = 'ifnull(t5.target_amount,"")!=""';
  }
  if(under =='Receivable Voucher')
	tab = 'RV';
  else
	tab = under;

  var q ='SELECT distinct t1.item_group AS "Item Group", '+q1+', t2.distribution_id AS "Distribution Id" FROM [tabTarget Detail] t1, [tabTerritory] t2 WHERE t1.parenttype = "Territory" AND t1.parent = "'+territory+'" AND t1.parent=t2.name AND ifnull(t1.item_group,"")!="" AND '+cond1+' UNION SELECT distinct t3.item_group AS "Item Group", '+q2+',"" AS "Distribution Id" FROM [tab'+tab+' Detail] t3,[tab'+under+'] t4 where t3.item_group NOT IN (SELECT t5.item_group FROM [tabTarget Detail] t5, [tabTerritory] t6 WHERE t5.parenttype = "Territory" AND t5.parent = "'+territory+'" AND t5.parent=t6.name AND '+cond2+') AND t4.territory = "'+territory+'" AND t3.parent = t4.name AND t4.docstatus = 1';

  return q;

}