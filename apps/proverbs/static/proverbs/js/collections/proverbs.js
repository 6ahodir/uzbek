/*global Backbone */
var app = app || {};

(function () {
	'use strict';

	// Proverb Collection
	// ---------------

	var Proverbs = Backbone.Collection.extend({
		// Reference to this collection's model.
		model: app.Proverb
	});

	// Create our global collection of **Proverbs**.
	app.Proverbs = new Proverbs();
})();
