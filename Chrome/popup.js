

var LinkBox = {
  /**
   * API endpoint 
   *
   * @type {string}
   * @private
   */
  endpoint_: 'http://localhost:11080',

  /**
   * Event handler for after a link has been succcessfully shared
   *
   * @public
   */
  shareSuccess: function() {
    // hide the form, and reload the links list
    $('form#share').slideUp('slow', LinkBox.loadLinks);
  },

  /**
   * Ensure container is visible, and load the list of links as
   * necessary
   *
   * @public
   */
  loadLinks: function() {
    LinkBox.loadLinksInner_();
    if ($('#error').is(':visible')) {
      $('#error').slideUp('slow', LinkBox.loadLinksInner_);

    } else {
      LinkBox.loadLinksInner_();
    }

  },

  /**
   * inner function for actually retrieving links. Wrapped inside
   * the outer function, which shows parent div as necessary
   *
   * @private
   */
  loadLinksInner_: function () {

    $.ajax({
      type: 'GET',
      url: LinkBox.endpoint_ + '/links', 
      dataType: 'json',

      success: function (data) {
        $('ul#links').empty();

        for (var i=0; i<data.length; i++) {
          var link = data[i];
          
          var title = link.title || link.url;
          var subtitle = link.comment || link.url;
          var favicon = link.favicon || 'default-favicon.png';

          
          var elem = '<li class="CLASS"><a target="_blank" href="URL" data-id="ID">' + 
            '<img src="FAVICON" class="favicon" width="32" height="32" />' + 
            '<span class="title">TITLE</span>' + 
            '<span class="subtitle">SUBTITLE</span></a></li>';

          elem = elem.replace('CLASS', link.read ? 'read' : 'unread');
          elem = elem.replace('FAVICON', favicon);
          elem = elem.replace('URL', link.url);
          elem = elem.replace('TITLE', title);
          elem = elem.replace('SUBTITLE', subtitle);
          elem = elem.replace('ID', link.id);

          $('ul#links').append(elem);
        }
      },

      error: function(jqXHR, textStatus, errorThrown) {
        if (textStatus == 'error' && errorThrown != 'Unauthorized') {
          LinkBox.connectionError();

        }
      },

      statusCode: {
        401: LinkBox.promptForLogin
      },
    })

  },

  /**
   * share the URL for the current tab
   *
   * @param {tabs} the tabs object after querying for the current tab
   * @public
   */
  shareLinkForCurrentTab: function (tabs) {
    if (tabs.length > 0) {
      var tab = tabs[0];

      var form = $('form#share');
      $('#to', form).val('');
      $('#url', form).val(tab.url);
      $('#title', form).val(tab.title);
      $('#favicon', form).val(tab.favIconUrl);
      $('#comment', form).val('');
      
      $('#url').toggleClass('preview', true);
      $('#title').toggleClass('preview', true);

      $('form#share').slideToggle('slow');
    }
  },

  handleShareSubmit: function(ev) {
    var form = $(ev.target);

    var form = $('form#share');

    var bundle = {
      to: $('#to', form).val(),
      url: $('#url', form).val(),
      title: $('#title', form).val(),
      comment: $('#comment', form).val(),
      favicon: $('#favicon', form).val(),
    };

    LinkBox.shareLink_(bundle);
  },

  /**
   * share the bundle of properties in data. Bundle should contain:
   * {
   *   url: url to share
   *   title: title of page
   *   comment: optional user comment
   *   favicon: url of page's favicon
   * }
   *
   * @param {linkBundle} a dict containing url, title, commment and favicon
   * @private
   */
  shareLink_: function (linkBundle) {
    $.ajax({
      type: 'PUT',
      url: LinkBox.endpoint_ + '/links', 
      data: linkBundle,
      success: LinkBox.shareSuccess,
      statusCode: {
        401: LinkBox.promptForLogin
      },
    });

  },

  markAsRead: function(ev) {
    var link = $(ev.target);

    if (!link.is('a')) {
      // descendant was clicked on - get the link, it has the properties
      link = link.parent('a');
    }

    var id = link.data('id');
    $.post(LinkBox.endpoint_ + '/links', {
      'id': id,
      'read': 'True'
    });
  },

  promptForLogin: function() {
    $("#loginPrompt").show();
    $("#connectionError").hide();

    if (! $('#error').is(':visible')) {
      $('#error').slideDown();
    }

  },

  connectionError: function() {
    $("#loginPrompt").hide();
    $("#connectionError").show();

    if (! $('#error').is(':visible')) {
      $('#error').slideDown();
    }
  },

  logout: function() {
    $.get(LinkBox.endpoint_ + '/logout', function() {
      LinkBox.promptForLogin();
    });
  },

  callback_loggedIn: function() {
    LinkBox.loadLinks();
  },

  callback_loggedOut: function() {

  },
};


var preload_data = [
  { id: 'user1', text: 'Jane Doe'}, 
  { id: 'user5', text: 'Spongebob Squarepants'}, 
  { id: 'user6', text: 'Planet Bob' }, 
  { id: 'user7', text: 'Inigo Montoya' }
];

document.addEventListener('DOMContentLoaded', function () {
  $('#to').select2({
    placeholder: "Select a contact, or type an email address",
    multiple: true,
    closeOnSelect: false,

    createSearchChoice: function(term) {
      var comma = term.indexOf(',');
      if (comma >= 0)
        term = term.substr(0, comma);

      var emailPattern = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;

      if (! emailPattern.test(term)) {
        return null;
      }

      return {
        id: 'mailto:' + term,
        text: term,
        email: true
      };
    },

    query: function(query){
      var data = {results: []};

      $.each(preload_data, function() {
          if (query.term.length == 0 || this.text.toUpperCase().indexOf(query.term.toUpperCase()) >= 0 ) {
              data.results.push({id: this.id, text: this.text });
          }
      });

      query.callback(data);
    },

    formatNoMatches: function(term) {
      return term + "<em> - invalid email</em>";
    }
  });

  $('#loginLink').attr('href', LinkBox.endpoint_ + '/login');
  $('form#share').attr('action', LinkBox.endpoint_ + '/links');
  LinkBox.loadLinks();
});

$('#loginLink').click(function(ev) {
  window.open(LinkBox.endpoint_ + '/login', 'authWindow', 'width=800,height=400');
});

$('.reload.button').click(function(ev) {
  LinkBox.loadLinks();

});

$('.logout.button').click(function(ev) {
  LinkBox.logout();

});

$('form#share input[type="submit"]').click(LinkBox.handleShareSubmit);

$('.share.button').click(function(ev) {
  var q = {
    'currentWindow': true, 
    'active': true,
    'highlighted': true
  };
  chrome.tabs.query(q, LinkBox.shareLinkForCurrentTab);
});

$('ul#links').on('click', 'a', LinkBox.markAsRead);
