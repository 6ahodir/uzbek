var app = app || {};

(function ($) {
	'use strict';

	// Quiz View
	// --------------

	app.QuizView = Backbone.View.extend({
        el: '#quiz',

		template: _.template($('#quiz-template').html()),

		// The DOM events specific to an item.
		events: {
		},

		initialize: function () {
			//this.listenTo(this.model, 'change', this.render);
            this.render();
		},

		render: function () {
			this.$el.html(this.template(this.model.toJSON()));
            var $question = this.$el.find('#question'),
                $suggestions = this.$el.find('#suggestions');
            $('.suggestion', $suggestions).draggable({
                opacity: 0.5,
                //revert: 'invalid',
                scope: 'quiz'//,
                //snap: '.placeholder',
                //snapMode: 'inner'
            });
            $('#question .placeholder').droppable({
                accept: '#suggestions .suggestion',
                drop: function (event, ui) {
                    //$(this).addClass( "ui-state-highlight").find( "p" )
                        //.html( "Dropped!" );
                },
                scope: 'quiz'
            });
			return this;
		}
	});
})(jQuery);
