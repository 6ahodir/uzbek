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

    app.Suggestion = Backbone.Model.extend({
        defaults: {
            used: false,
            answerId: ''  // user's answer
        }
    });

    app.Answer = Backbone.Model.extend({
        defaults: {
            suggestionId: ''  // user's answer
        }
    });

    app.TopScorer = Backbone.Model.extend({});

	// Quiz Model
	// ----------

	app.Quiz = Backbone.Model.extend({
        defaults: {
        },

        initialize: function (options) {
        }
	});
})();
