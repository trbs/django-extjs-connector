// A reusable error reader class for XML forms
Ext.form.XmlErrorReader = function(){
    Ext.form.XmlErrorReader.superclass.constructor.call(this, {
            record : 'field',
            success: '@success'
        }, [
            'id', 'msg'
        ]
    );
};
Ext.extend(Ext.form.XmlErrorReader, Ext.data.XmlReader);

Ext.form.XmlLoadFormReader = function(){
    Ext.form.XmlLoadFormReader.superclass.constructor.call(this, {
            record : 'field',
            success: '@success'
        }, [
            'id', 'type', 'config'
        ]
    );
};
Ext.extend(Ext.form.XmlLoadFormReader, Ext.data.XmlReader);

Ext.form.Action.LoadServerForm = function(form, options){
    Ext.form.Action.LoadServerForm.superclass.constructor.call(this, form, options);
};

Ext.extend(Ext.form.Action.LoadServerForm, Ext.form.Action, {
    type : 'loadForm',
    
    run : function(){
	Ext.lib.Ajax.request(
	    'POST',
	    this.form.formUrl,
	    this.createCallback(),
	    this.getParams());
    },
    
    success : function(response){
	var result = this.processResponse(response);
	if(!result.success){
	    this.form.afterAction(this, true);
	    return;
	}
	if(result.data){
	    this.form.generateForm(result.data, this.options.ct);
	}
	this.form.afterAction(this, false);
    },
    
    handleResponse : function(response){
	var loadFormReader = new Ext.form.XmlLoadFormReader();
	var rs = loadFormReader.read(response);
	var data = [];
	if (rs.records){
	    for(var i=0, len=rs.records.length; i<len; i++) {
		var r = rs.records[i];
		data[i] = r.data;
	    }
	}
	if(data.length<1){
	    data = null;
	}
	return {
	    success: rs.success,
	    data: data
	};
    }
});


Ext.form.ServerForm = function(config){
    Ext.form.ServerForm.superclass.constructor.call(this, config);
    //this.typemap = {}; // holder for typemap
    //this.formUrl = '';
    //this.submitFormUrl = '';
    this.errorReader = new Ext.form.XmlErrorReader();
};

Ext.extend(Ext.form.ServerForm, Ext.form.Form, {
    renderServerForm : function(options){
	if (this.formUrl){
	    //this.serverLoadMask = new Ext.LoadMask(Ext.get(options.ct), {msg: "Loading..."});
	    //this.serverLoadMask.enable();
	    Ext.get(options.ct).mask("Loading...");
	    action = new Ext.form.Action.LoadServerForm(this, options);
	    if(this.fireEvent('beforeaction', this, action) !== false){
		this.beforeAction(action);
		action.run.defer(100, action);
	    }
	}
    },
    
    generateForm : function(dataset, ct){
	if (dataset){
	    for(var i=0, len=dataset.length; i<len; i++) {
		var map = dataset[i];
		var key = map['id'];
		var type = eval(map['type'], Ext.form);
		var elk = "id_"+key;
		var tc = eval("("+map['config']+")");
		if (!tc.fieldLabel) {
		    tc['fieldLabel'] = key;
		}
		if (!tc.name) {
	            tc['name'] = key;
		}
		if (tc.vtypeFunc) {
		    var vt = Ext.form.VTypes;
		    var fn = eval("("+tc.vtypeFunc+")");
		    vt[tc.vtype] = fn;
		    vt[""+tc.vtype+"Test"] = tc.vtypeText;
		}
		//var field = new tm[0](config);
		//field.applyTo(elk);
		this.add(new type(tc));
	    }
	    this.alreadyGenerated = true;
	    //Ext.form.ServerForm.superclass.render(ct);
	    this.render(ct);
	    Ext.get(ct).unmask();
	}
    },
    /*
    render : function(ct){
	if (!this.alreadyGenerated) {
	    this.loadServerForm({ct:ct});
	}
    }*/
    
    eojs:function(){}
});

var EDS = function(){
    var loadUrl = '/extdjango/extform/';
    var submitUrl = '/extdjango/extformsubmit/';
    
    return {
	init: function() {
	    Ext.QuickTips.init();
	    Ext.form.Field.prototype.msgTarget="side";
	    
	    var tabs = new Ext.TabPanel("tabs");
	    tabs.addTab('extform', 'ExtJS ServerForm');
	    tabs.addTab('djangoform', 'Django Form');
	    tabs.addTab('info', 'More Information');
	    tabs.activate('extform');
	    
	    var form = new Ext.form.ServerForm({
		formUrl: loadUrl,
		submitFormUrl: submitUrl,
		labelAlign: 'right',
		labelWidth: 75,
		waitMsgTarget: 'box-dg'
	    });
	    
	    var reset = form.addButton({
		text: 'Reset form',
		handler: function(){
		    form.reset();
		}
	    });
	    var submit = form.addButton({
		text: 'Submit',
		handler: function(){
		    form.submit({url: submitUrl, params: {submit:true}, waitMsg:'Saving Data...'});
		}
	    });
	    //form.render('form-ct');
	    form.renderServerForm({ct:'form-ct'});
	}
    }
}();
Ext.onReady(EDS.init, EDS, true);
