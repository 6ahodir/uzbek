/*global Backbone */
var app = app || {};

(function () {
	'use strict';

	app.Suggestions = Backbone.Collection.extend({
		model: app.Suggestion
	});

	app.Answers = Backbone.Collection.extend({
		model: app.Answer,

        areAllAnswered: function() {
            var result = true;
            _.each(this.models, function(model) {
                if ((model.get('val') === 'u' || model.get('val') === 'l') && model.get('suggestionId') === '') {
                    result = false;
                }
            });
            return result;
        },

        getWords: function(suggestions) {
            var result = [];
            _.each(this.models, function(model) {
                if (model.get('suggestionId')) {
                    result.push(suggestions.get(model.get('suggestionId')).get('text'));
                }
            });
            return result;
        }
	});

	app.TopScorers = Backbone.Collection.extend({
		model: app.TopScorer
	});

})();
