/*global Backbone */
var app = app || {};

(function () {
	'use strict';

	app.Suggestions = Backbone.Collection.extend({
		model: app.Suggestion
	});

	app.Answers = Backbone.Collection.extend({
		model: app.Answer
	});

})();
