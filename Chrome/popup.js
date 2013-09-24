

var LinkBox = {
  /**
   * API endpoint 
   *
   * @type {string}
   * @private
   */
  endpoint_: 'http://localhost:11080',

  /**
   * 
   *
   * @public
   */
  publicFunction: function() {
    
  },

  /**
   * 
   * @param {ProgressEvent} e The XHR ProgressEvent.
   * @private
   */
  privateFunction_: function (e) {
    
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

      $('#url', form).val(tab.url);
      $('#title', form).val(tab.title);
      $('#favicon', form).val(tab.favIconUrl);
      $('#comment', form).val('');

      $('#url').toggleClass('preview', true);
      $('#title').toggleClass('preview', true);

    }
  },

  handleShareSubmit: function(ev) {
    var form = $(ev.target);



  },

  /**
   * share the bundle of properties in data. Bundle should contain:
   * {
   *   url: url to share
   *   title: title of page
   *   comment: optional user comment
   *   favicon: favicon of page
   * }
   *
   * @param {tabs} the tabs object after querying for the current tab
   * @private
   */
  shareLink_: function (linkBundle) {
    $.ajax({
      type: 'PUT',
      url: LinkBox.endpoint_ + '/links', 
      data: linkBundle,
      success: LinkBox.loadLinks,
      statusCode: {
        401: LinkBox.promptForLogin
      },
    });

  },

  markAsRead: function(ev) {
    var link = $(ev.target);
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


document.addEventListener('DOMContentLoaded', function () {
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

$('.share.button').click(function(ev) {
  var q = {
    'currentWindow': true, 
    'active': true,
    'highlighted': true
  };
  chrome.tabs.query(q, LinkBox.shareLinkForCurrentTab);
});

$(document).on('click', '#links a', LinkBox.markAsRead);
