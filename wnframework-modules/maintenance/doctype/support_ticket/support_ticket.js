// threading structure
// -------- orginal message --------
// xoxoxoxo
// -------- reply 1 --------
// -------- reply 2 --------
// xoxoxoxo
// -------- new reply --------

var cs = cur_frm.cscript;
$.extend(cur_frm.cscript, {
	onload: function(doc, dt, dn) {
		//
		// help area
		//
		if(in_list(user_roles,'System Manager')) {
			cur_frm.page_layout.footer.help_area.innerHTML = '';
			new wn.widgets.Footer({
				parent:cur_frm.page_layout.footer.help_area,
				columns:2,
				items: [
					{
						column: 0,
						label:'Support Email Settings',
						description:'Integrate your incoming support emails to support ticket',
						onclick: function() { loaddoc('Support Email Settings','Support Email Settings'); }
					}, 					
				]
			})			
		}
	},
	
	refresh: function(doc) {
		cs.make_listing(doc);
		if(!doc.__islocal) {
			// can't change the main message & subject once set
			set_field_permlevel('subject',2);
			set_field_permlevel('description',2);
			set_field_permlevel('raised_by',2);
		}
	},
	
	//
	// make thread listing
	//
	make_listing: function(doc) {
		cur_frm.fields_dict['Thread HTML'].wrapper.innerHTML = '';
		
		// render first message
		new EmailMessage(cur_frm.fields_dict['Thread HTML'].wrapper, {
			from_email: doc.raised_by,
			creation: doc.creation,
			mail: doc.description,
			content_type: doc.content_type
		}, null, -1)
		
		// render thread		
		cs.thread_list = new wn.widgets.Listing({
			parent: cur_frm.fields_dict['Thread HTML'].wrapper,
			no_result_message: 'No responses yet',
			get_query: function() {
				return 'select mail, from_email, creation, content_type '+
				'from [tabSupport Ticket Response] where parent="'+doc.name+'" order by creation asc'
			},
			as_dict: 1,
			render_row: function(parent, data, list, idx) {
				new EmailMessage(parent, data, list, idx);
			}
		});
		cs.thread_list.run();

	},
	
	Send: function(doc, dt, dn) {
		$c_obj([doc], 'send_response', '', function(r,rt) {
			locals[dt][dn].new_response = '';
			refresh_field('new_response');
			cs.make_listing(doc);
		});
	}
})


EmailMessage = function(parent, args, list, idx) {
	var me = this;
	$.extend(this, args);
	this.make = function() {
		this.creation = wn.datetime.str_to_user(this.creation);
		if(this.from_email)
			this.from_email = this.from_email.replace('<', '&lt;').replace('>', '&gt;');
		
		// main wrapper
		w = $a(parent, 'div', '', 
			{margin:'7px 0px', padding:'0px', border:'1px solid #c8c8c8', backgroundColor:'#f9f9f9'}
		);
		$br(w, '7px');

		// sender and timestamp
		$a($a(w, 'div', '', {marginBottom:'7px', padding: '7px', backgroundColor:'#d2d2f2'}), 
			'span', 'link_type', {}, repl('By %(from_email)s on %(creation)s:', this), 
			function() {
				// toggle message display on timestamp
				if(me.message.style.display.toLowerCase()=='none') {
					$ds(me.message);
				} else {
					$dh(me.message);
				}
			}
		);
		
		// email text
		this.message = $a(w, 'div', '', 
			// style
			{lineHeight:'1.7em', display:'none', padding: '7px'}, 
			
			// newlines for text email
			(this.content_type=='text/plain' ? this.mail
				.replace(/\n[ ]*\n[\n\t ]*/g, '\n\n') // excess whitespace
				.replace(/\n/g, '<br>') : this.mail)
		);
		
		// show only first and last message
		if(idx==-1 || list && list.values.length-1==idx) {
			$ds(this.message)
		}
		
	}
	this.make();
}