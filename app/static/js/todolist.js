$(document).ready(function() {
  $(':checkbox').on('click', changeTodoStatus);
});

function showNotification(message, type) {
  var notification = $('<div class="todo-notification ' + type + '">' + message + '</div>');
  $('body').append(notification);
  notification.fadeIn(300);
  setTimeout(function() {
    notification.fadeOut(300, function() {
      $(this).remove();
    });
  }, 3000);
}

function changeTodoStatus() {
  var checkbox = $(this);
  var todoId = checkbox.data('todo-id');
  var wasChecked = checkbox.is(':checked');
  
  if (wasChecked) {
    putNewStatus(todoId, true, checkbox);
  } else {
    putNewStatus(todoId, false, checkbox);
  }
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// function from the django docs
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(
          cookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return cookieValue;
}

function putNewStatus(todoID, isFinished, checkbox) {

  // setup ajax to csrf token
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  // send put request using the todo of the get for the same id
  var todoURL = '/api/todo/' + todoID + '/'
  $.getJSON(todoURL, function(todo) {
    todo.is_finished = isFinished;
    $.ajax({
      url: todoURL,
      type: 'PUT',
      contentType: 'application/json',
      data: JSON.stringify(todo),
      success: function(response) {
        if (isFinished) {
          var duration = response.duration || 'just now';
          showNotification('Congratulations! You completed: "' + response.description + '" (Duration: ' + duration + ')', 'success');
        } else {
          showNotification('Todo reopened: "' + response.description + '"', 'info');
        }
        setTimeout(function() {
          location.reload();
        }, 1500);
      },
      error: function() {
        showNotification('Error updating todo status', 'error');
        checkbox.prop('checked', !isFinished);
      }
    });
  });
}
