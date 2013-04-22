/*jshint unused:false */
var app = app || {};

(function ($) {
	'use strict';

	// The Application
	// ---------------

	// Our overall **AppView** is the top-level piece of UI.
	app.AppView = Backbone.View.extend({
		el: '#proverb-app',

		events: {
		},

		initialize: function () {
			//app.Proverbs.fetch();
		},

		render: function () {
		}
	});
})(jQuery);
