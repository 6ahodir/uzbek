/*global Backbone */
var app = app || {};

(function () {
	'use strict';

	app.Timer = Backbone.Model.extend({
        defaults: {
            paused: false
        },

        initialize: function (attributes, options) {
            var time = options.time,    // in minutes
                mins = Math.floor(time),
                secs = Math.floor(60 * (time - mins));
            this.set({
                mins: mins,
                secs: secs
            });
        },

        pause: function() {
            this.set('paused', true);
        },

        resume: function() {
            this.set('paused', false);
        }
	});

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
