cur_frm.cscript.onload = function(doc, dt, dn) {
  if(!doc.status) set_multiple(dt,dn,{status:'Draft'});
  if(doc.customer) cur_frm.cscript.customer(doc,cdt,cdn);
    
  if(doc.__islocal){
    set_multiple(dt,dn,{mntc_date:get_today()});
    hide_field(['customer_address','contact_person','customer_name','address_display','contact_display','contact_mobile','contact_email','territory','customer_group']);
  }   
    
  //if(doc.maintenance_type) cur_frm.cscript.maintenance_type(doc,cdt,cdn);
}


//customer
cur_frm.cscript.customer = function(doc,dt,dn) {
  var callback = function(r,rt) {
      var doc = locals[cur_frm.doctype][cur_frm.docname];
      cur_frm.refresh();
  }   

  if(doc.customer) $c_obj(make_doclist(doc.doctype, doc.name), 'get_default_customer_address', '', callback);
  if(doc.customer) unhide_field(['customer_address','contact_person','customer_name','address_display','contact_display','contact_mobile','contact_email','territory','customer_group']);
}

cur_frm.cscript.customer_address = cur_frm.cscript.contact_person = function(doc,dt,dn) {    
  if(doc.customer) get_server_fields('get_customer_address', JSON.stringify({customer: doc.customer, address: doc.customer_address, contact: doc.contact_person}),'', doc, dt, dn, 1);
}

cur_frm.fields_dict.customer_address.on_new = function(dn) {
  locals['Address'][dn].customer = locals[cur_frm.doctype][cur_frm.docname].customer;
  locals['Address'][dn].customer_name = locals[cur_frm.doctype][cur_frm.docname].customer_name;
}

cur_frm.fields_dict.contact_person.on_new = function(dn) {
  locals['Contact'][dn].customer = locals[cur_frm.doctype][cur_frm.docname].customer;
  locals['Contact'][dn].customer_name = locals[cur_frm.doctype][cur_frm.docname].customer_name;
}

cur_frm.fields_dict['customer_address'].get_query = function(doc, cdt, cdn) {
  return 'SELECT name,address_line1,city FROM tabAddress WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.fields_dict['contact_person'].get_query = function(doc, cdt, cdn) {
  return 'SELECT name,CONCAT(first_name," ",ifnull(last_name,"")) As FullName,department,designation FROM tabContact WHERE customer = "'+ doc.customer +'" AND docstatus != 2 AND name LIKE "%s" ORDER BY name ASC LIMIT 50';
}

cur_frm.cscript['Get Items'] = function(doc, dt, dn) {
  var callback = function(r,rt) { 
	  unhide_field(['customer_address','contact_person','customer_name','address_display','contact_display','contact_mobile','contact_email','territory','customer_group']);
	  cur_frm.refresh();
  }
  get_server_fields('fetch_items','','',doc, dt, dn,1,callback);
}


/*
cur_frm.cscript.maintenance_type = function(doc,cdt,cdn){
  if(doc.maintenance_type == 'Scheduled') {
    hide_field('sales_order_no');
    hide_field('customer_issue_no');
    hide_field('Get Items');
    doc.customer_issue_no = '';
    doc.sales_order_no = '';
  }
  else if(doc.maintenance_type == 'Unscheduled') {
    unhide_field('sales_order_no');
    hide_field('customer_issue_no');
    unhide_field('Get Items');
    doc.customer_issue_no = '';
  }
  else if(doc.maintenance_type == 'Breakdown') {
    hide_field('sales_order_no');
    unhide_field('customer_issue_no');
    unhide_field('Get Items');
    doc.sales_order_no = '';
  }
}*/

cur_frm.fields_dict['maintenance_visit_details'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
  return 'SELECT tabItem.name,tabItem.item_name,tabItem.description FROM tabItem WHERE tabItem.is_service_item="Yes" AND tabItem.docstatus != 2 AND tabItem.%(key)s LIKE "%s" LIMIT 50';
}

cur_frm.cscript.item_code = function(doc, cdt, cdn) {
  var fname = cur_frm.cscript.fname;
  var d = locals[cdt][cdn];
  if (d.item_code) {
    get_server_fields('get_item_details',d.item_code, 'maintenance_visit_details',doc,cdt,cdn,1);
  }
}

cur_frm.fields_dict['sales_order_no'].get_query = function(doc) {
  doc = locals[this.doctype][this.docname];
  var cond = '';
  if(doc.customer) {
    cond = '[tabSales Order].customer = "'+doc.customer+'" AND';
  }
  //return repl('SELECT DISTINCT [tabSales Order].name FROM [tabSales Order], [tabSales Order Detail] WHERE [tabSales Order].company = "%(company)s" AND [tabSales Order].docstatus = 1 AND %(cond)s [tabSales Order].name LIKE "%s" ORDER BY [tabSales Order].name DESC LIMIT 50', {company:doc.company, cond:cond});
  return repl('SELECT DISTINCT [tabSales Order].name FROM [tabSales Order], [tabSales Order Detail], [tabItem] WHERE [tabSales Order].company = "%(company)s" AND [tabSales Order].docstatus = 1 AND [tabSales Order Detail].parent = [tabSales Order].name AND [tabSales Order Detail].item_code = [tabItem].name AND [tabItem].is_service_item = "Yes" AND %(cond)s [tabSales Order].name LIKE "%s" ORDER BY [tabSales Order].name DESC LIMIT 50', {company:doc.company, cond:cond});
}

cur_frm.fields_dict['customer_issue_no'].get_query = function(doc) {
  doc = locals[this.doctype][this.docname];
  var cond = '';
  if(doc.customer) {
    cond = '[tabCustomer Issue].customer = "'+doc.customer+'" AND';
  }
  return repl('SELECT [tabCustomer Issue].name FROM [tabCustomer Issue] WHERE [tabCustomer Issue].company = "%(company)s" AND %(cond)s [tabCustomer Issue].docstatus = 1 AND ([tabCustomer Issue].status = "Open" OR [tabCustomer Issue].status = "Work In Progress") AND [tabCustomer Issue].name LIKE "%s" ORDER BY [tabCustomer Issue].name DESC LIMIT 50', {company:doc.company, cond:cond});
}

//get query select Territory
//=======================================================================================================================
cur_frm.fields_dict['territory'].get_query = function(doc,cdt,cdn) {
  return 'SELECT [tabTerritory].[name],[tabTerritory].[parent_territory] FROM [tabTerritory] WHERE [tabTerritory].[is_group] = "No" AND [tabTerritory].[docstatus]!= 2 AND [tabTerritory].%(key)s LIKE "%s"  ORDER BY  [tabTerritory].[name] ASC LIMIT 50';
}
