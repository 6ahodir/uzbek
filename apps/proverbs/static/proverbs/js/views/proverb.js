var app = app || {};

(function ($) {
	'use strict';

	// Proverb Item View
	// --------------

	app.ProverbView = Backbone.View.extend({
		tagName:  'li',

		// Cache the template function for a single item.
		//template: _.template($('#proverb-template').html()),

		// The DOM events specific to an item.
		events: {
		},

		initialize: function () {
			//this.listenTo(this.model, 'change', this.render);
		},

		render: function () {
			this.$el.html(this.template(this.model.toJSON()));
			return this;
		}
	});
})(jQuery);
