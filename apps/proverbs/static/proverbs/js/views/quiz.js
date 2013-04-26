var app = app || {};

(function($) {
	'use strict';

    // Timer View
    app.TimerView = Backbone.View.extend({
        el: '#timer',

        template: _.template($('#timer-template').html()),

        events: {
        },

        initialize: function() {
            _.bindAll(this, 'tick');
			//this.listenTo(this.model, 'change', this.render);
            this.render();
        },

        render: function() {
			this.$el.html(this.template(this.model.toJSON()));
            this.interval = setInterval(this.tick, 1000);
        },

        tick: function() {
            var mins,
                secs;

            if (this.model.get('paused')) {
                return;
            }

            mins = this.model.get('mins');
            secs = this.model.get('secs');
            if (mins >= 0 && secs >= 0) {
                if (secs === 0 && mins > 0) {
                    mins -= 1;
                    secs = 59;
                } else if (!(secs === 0 && mins === 0)) {
                    secs -= 1;
                }
                this.$el.find('.mins').text(mins);
                this.$el.find('.secs').text((secs < 10) ? '0' + secs : secs);
                this.model.set({
                    'mins': mins,
                    'secs': secs
                });
            } else {
                clearInterval(this.interval);
            }
        }
    });
	// Quiz View
	// --------------

	app.QuizView = Backbone.View.extend({
        el: '#quiz',

		template: _.template($('#quiz-template').html()),

		// The DOM events specific to an item.
		events: {
		},

		initialize: function() {
			this.listenTo(this.model, 'change:question', this.model.setAnswer);
            this.render();
		},

		render: function() {
            var that = this,
                $question,
                $suggestions,
                defaultPlaceholderWidth;

			this.$el.html(this.template(this.model.toJSON()));

            this.timer = new app.Timer({}, {'time': this.model.get('time')});
            this.timerView = new app.TimerView({model: this.timer});


            $question = this.$el.find('#question');
            $suggestions = this.$el.find('#suggestions');
            defaultPlaceholderWidth = $question.find('.placeholder:first').width();

            $('.suggestion', $suggestions).draggable({
                opacity: 0.5,
                scope: 'quiz',
                start: function (event, ui) {
                    // clear the answer
                    var suggestionKey = parseInt(ui.helper.data('key'), 10);
                    _.each(that.model.get('answer'), function (val, key) {
                        if (suggestionKey === val) {
                            that.model.get('answer')[key] = '';
                            $question.find('.placeholder[data-key=' + key + ']').droppable('option', 'disabled', false).css({width: defaultPlaceholderWidth});
                            // move other dragged elements too because of the widht change above
                            _.each(that.model.get('answer'), function (val2, key2) {
                                if (val2) {
                                    $suggestions.find('.suggestion[data-key=' + val2 + ']').offset(
                                            $question.find('.placeholder[data-key=' + key2 + ']').offset()
                                        );
                                }
                            });
                        }
                    });
                },
                stop: function (event, ui) {
                    var suggestionKey = parseInt(ui.helper.data('key'), 10);
                    // put to default position if not dropped onto a placeholder
                    if (!_.contains(that.model.get('answer'), suggestionKey)) {
                        ui.helper.animate({top: 0, left: 0}).removeClass('used').removeClass('capital');
                    } else {
                        _.each(that.model.get('answer'), function (val, key) {
                            if (suggestionKey === val && that.model.get('question')[key] === 'u') {
                                ui.helper.addClass('capital');
                            }
                        });
                    }
                }
            });
            $('#question .placeholder').droppable({
                accept: '#suggestions .suggestion',
                drop: function(event, ui) {
                    var $this = $(this),
                        suggestionKey;
                    if (ui.draggable) {
                        that.model.get('answer')[$this.data('key')] = 
                            ui.draggable.data('key');
                        $this.droppable('option', 'disabled', true);
                        ui.draggable.addClass('used');
                        $this.css('width', ui.draggable.width() + 5); // for punctuation
                        // move other dragged elements too because of the widht change above
                        _.each(that.model.get('answer'), function (val, key) {
                            if (val) {
                                $suggestions.find('.suggestion[data-key=' + val + ']').offset(
                                        $question.find('.placeholder[data-key=' + key + ']').offset()
                                    );
                            }
                        });
                    }
                },
                over: function(event, ui) {
                },
                tolerance: 'pointer',
                scope: 'quiz'
            });
			return this;
		}
	});
})(jQuery);
