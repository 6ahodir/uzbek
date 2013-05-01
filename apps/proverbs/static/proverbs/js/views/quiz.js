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
    
    // Answer View
    // ------------
    app.AnswerView = Backbone.View.extend({
        tagName: 'li',
        template: _.template($('#answer-template').html()),
        events: {},
        initialize: function() {
        },
        render: function() {
			this.$el.html(this.template(this.model.toJSON()));
            this.model.set('view', this);
            return this;
        }
    });

    // Suggestion View
    // ------------
    app.SuggestionView = Backbone.View.extend({
        tagName: 'li',
        template: _.template($('#suggestion-template').html()),
        events: {},
        initialize: function() {
        },
        render: function() {
			this.$el.html(this.template(this.model.toJSON()));
            this.model.set('view', this);
            return this;
        }
    });

	// Quiz View
	// --------------

	app.QuizView = Backbone.View.extend({
        el: '#quiz',

		template: _.template($('#quiz-template').html()),

		// The DOM events specific to an item.
		events: {
            'click #next .next': 'showNextQuestion'
		},

		initialize: function() {
            _.bindAll(this, 'makeSuggestionsDraggable', 'makeAnswersDroppable',
                    'checkAnswer', 'showNextQuestion', 'showQuestion',
                    'addAnswers', 'addSuggestions', 'disableButton',
                    'enableButton', 'updateScore');


            this.answers = new app.Answers();
            this.suggestions = new app.Suggestions();

			//this.listenTo(this.model, 'change:question', this.model.setAnswer);
            this.listenTo(this.model, 'change:number', this.showQuestion);
            this.listenTo(this.model, 'change:score', this.updateScore);
            this.listenTo(this.answers, 'reset', this.addAnswers);
            this.listenTo(this.suggestions, 'reset', this.addSuggestions);
            this.render();
		},

		render: function() {
            var that = this,
                $answers,
                $suggestions,
                defaultPlaceholderWidth;

			this.$el.html(this.template(this.model.toJSON()));

            this.$answers = this.$el.find('#answers');
            this.$suggestions = this.$el.find('#suggestions');

            this.timer = new app.Timer({}, {'time': this.model.get('time')});
            this.timerView = new app.TimerView({model: this.timer});

            this.showQuestion();

			return this;
		},

        showQuestion: function() {
            var answers = [],
                suggestions = [];

            // create the answers data
            _.each(this.model.get('question'), function (val, key) {
                // ignore punctuation
                answers.push({
                    id: key + 1,
                    val: val
                });
            });

            // create the suggestions collection
            _.each(this.model.get('suggestions'), function (val, key) {
                // ignore punctuation
                suggestions.push({
                    id: key + 1,
                    text: val
                });
            });

            // show description
            this.$el.find('#desc').text(this.model.get('description'));

            this.answers.reset(answers);
            this.suggestions.reset(suggestions);

            this.makeSuggestionsDraggable();
            this.makeAnswersDroppable();
            this.defaultPlaceholderWidth = this.$answers.find('.placeholder:first').width();
        },

        addAnswers: function () {
            this.$el.find('#answers').html('');
			this.answers.each(function (answer) {
                var view = new app.AnswerView({model: answer});
                this.$el.find('#answers').append(view.render().el);
            }, this);
        },

        addSuggestions: function () {
            this.$el.find('#suggestions').html('');
			this.suggestions.each(function (suggestion) {
                var view = new app.SuggestionView({model: suggestion});
                this.$el.find('#suggestions').append(view.render().el);
            }, this);
        },

        makeSuggestionsDraggable: function() {
            var that = this,
                suggestionView,
                suggestion;
            $('.suggestion', that.$suggestions).draggable({
                opacity: 0.5,
                scope: 'quiz',
                start: function (event, ui) {
                    suggestion = that.suggestions.get(ui.helper.data('id'));
                    suggestion.set('used', false);
                },
                stop: function (event, ui) {
                    suggestion = that.suggestions.get(ui.helper.data('id'));
                    suggestionView = suggestion.get('view');

                    if (!suggestion.get('used')) {
                        ui.helper.animate({top: 0, left: 0}).removeClass('used').removeClass('capital');
                        if (suggestion.get('answerId')) {
                            that.answers.get(suggestion.get('answerId')).set('suggestionId', '');
                            suggestion.set('answerId', '');
                        }
                    } else if (that.answers.get(suggestion.get('answerId')).get('val') === 'u') {
                        ui.helper.addClass('capital');
                    } else {
                        ui.helper.removeClass('capital');
                    }
                }
            });
        },

        makeAnswersDroppable: function() {
            var that = this;
            that.$answers.find('.placeholder').droppable({
                accept: '#suggestions .suggestion',
                drop: function(event, ui) {
                    var $this = $(this),
                        answer = that.answers.get($this.data('id')),
                        answerView = answer.get('view'),
                        suggestion = that.suggestions.get(ui.draggable.data('id')),
                        suggestionView = suggestion.get('view');
                    
                    //$this.droppable('option', 'disabled', true);
                    // is already filled?
                    if (answer.get('suggestionId')) {
                        var existingSuggestion = that.suggestions.get(answer.get('suggestionId'));
                        // is replacement already being used?
                        if (suggestion.get('answerId')) {
                            // swap places
                            var movedAnswerId = suggestion.get('answerId'),
                                movedSuggestionId = suggestion.get('id'),
                                movedAnswer = that.answers.get(movedAnswerId),
                                movedOffset = movedAnswer.get('view').$el.find('.placeholder').offset();

                            existingSuggestion.set({
                                'answerId': movedAnswerId,
                                'used': true
                            });
                            movedAnswer.set('suggestionId', existingSuggestion.get('id'));
                            movedAnswer.get('view').$el.find('.placeholder').css('width', existingSuggestion.get('view').$el.find('.suggestion').width() + 5);
                            if (movedAnswer.get('val') === 'u') {
                                existingSuggestion.get('view').$el.find('.suggestion').addClass('capital');
                            } else {
                                existingSuggestion.get('view').$el.find('.suggestion').removeClass('capital');
                            }
                            existingSuggestion.get('view').$el.find('.suggestion').offset(movedOffset);
                        } else {
                            existingSuggestion.get('view').$el.find('.suggestion').animate({top: 0, left: 0}).removeClass('used').removeClass('capital');
                            that.answers.get(existingSuggestion.get('answerId')).get('view').$el.find('.placeholder').css('width', that.defaultPlaceholderWidth);
                            existingSuggestion.set({
                                'answerId': '',
                                'used': false
                            });
                        }
                    } else if (suggestion.get('answerId')) {
                        // dragging from another answer to this empty answer
                        that.answers.get(suggestion.get('answerId')).set('suggestionId', '');
                    }

                    answer.set('suggestionId', suggestion.get('id'));
                    suggestion.set('answerId', answer.get('id'));
                    suggestion.set('used', true);
                    ui.draggable.addClass('used');
                    $this.css('width', ui.draggable.width() + 5); // for punctuation


                    // move other dragged elements too because of the width change above
                    that.suggestions.each(function(suggestion) {
                        if (suggestion.get('answerId')) {
                            suggestion.get('view').$el.find('.suggestion').offset(
                                that.answers.get(suggestion.get('answerId')).get('view').$el.find('.placeholder').offset()
                            );
                        }
                    });

                    // check answer if there are no more slots to fill
                    if (that.answers.areAllAnswered()) {
                        that.checkAnswer();
                    }
                },
                over: function(event, ui) {
                },
                tolerance: 'pointer',
                scope: 'quiz'
            });
        },

        updateNextButton: function() {
            // Toggle between 'next' and 'skip' depending on the answers
            if (this.answers.areAllAnswered()) {
                this.$el.find('.next').text('Next');
            } else {
                this.$el.find('.next').text('Skip');
            }
        },

        checkAnswer: function(event) {
            // show the next question if answer is correct
            var that = this;

            if (event) {
                event.preventDefault();
            }

            $.ajax({
                url: that.model.get('checkUrl'),
                type: 'POST',
                data: $.param({
                    'answers': that.answers.getWords(that.suggestions),
                    'uuid': that.model.get('uuid'),
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                }),
                beforeSend: function() {
                    that.disableButton(that.$el.find('.next'));
                },
                complete: function () {
                    that.enableButton(that.$el.find('.next'));
                },
                success: function(response) {
                    if (typeof response.answer !== 'undefined' && 
                        response.answer === 'correct') {
                            that.model.set('score', that.model.get('score') +
                                response.score);
                        alert('correct');
                    } else if (response === 'wrong') {
                        alert('wrong');
                    }
                    console.log(response);
                },
                error: function() {
                
                }
            });
        },

        showNextQuestion: function(event) {
            // show the next question
            var that = this;

            event.preventDefault();

            $.ajax({
                url: that.model.get('nextUrl'),
                type: 'GET',
                data: {
                    'uuid': that.model.get('uuid')
                },
                beforeSend: function() {
                    that.disableButton(that.$el.find('.next'));
                },
                complete: function () {
                    that.enableButton(that.$el.find('.next'));
                },
                success: function(response) {
                    if (typeof response.success !== 'undefined') {
                        if (response.success) {
                            that.model.set({
                                'description': response.description,
                                'question': response.question,
                                'suggestions': response.suggestions,
                                'number': response.number
                            });
                        } else {
                        
                        }
                    } else if (response === 'no more') {
                        // todo: show the results popup
                    }
                    console.log(response);
                },
                error: function() {
                
                }
            });
        },

        disableButton: function($target) {
            $target.attr('disabled', true);
        },

        enableButton: function($target) {
            $target.attr('disabled', false);
        },

        updateScore: function() {
            this.$el.find('#score').text(this.model.get('score'));
        }
	});
})(jQuery);
