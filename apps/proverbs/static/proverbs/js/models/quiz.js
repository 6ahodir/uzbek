/*global Backbone */
var app = app || {};

(function () {
	'use strict';

	// Quiz Model
	// ----------

	app.Quiz = Backbone.Model.extend({
        defaults: {
            // answer will be populated once suggestions are dragged & dropped
            answer: {}
        },

        initialize: function (options) {
            this.setAnswer();
        },

        setAnswer: function () {
            var answer = {};
            _.each(this.get('question'), function (val, key) {
                // ignore punctuation
                if (val === 'u' || val === 'l') {
                    answer[key] = "";
                }
            });
            this.set('answer', answer);
        }
	});
})();
