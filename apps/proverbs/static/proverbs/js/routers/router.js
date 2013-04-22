/*global Backbone */
var app = app || {};

(function () {
	'use strict';

	// Proverb Router
	// ----------
	var Workspace = Backbone.Router.extend({
		routes: {
		}
	});

	app.ProverbRouter = new Workspace();
	Backbone.history.start();
})();
