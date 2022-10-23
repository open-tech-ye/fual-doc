// Copyright (c) 2022, malnoziliye@gmail.com	 and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import XML', {
	refresh: function(frm) {
		if(frm.is_new()){
			frm.toggle_display("import_xml", false);
		}
		else{
			frm.toggle_display("import_xml", true);
		
		}

	}
});
