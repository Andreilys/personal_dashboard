var prev_data = Object();           // remember data fetched last time
var waiting_for_update = false; // are we currently waiting?
var LONG_POLL_DURATION = 60000; // how long should we wait? (msec)

/**
 * Load data from /data, optionally providing a query parameter read
 * from the #format select
 */
function load_data() {
    $.ajax({ url: '/data',
             success: function(data) {
                          display_data(data);
                          wait_for_update();
                      },
    });
    return true;
}


/**
 * Uses separate update notification and data providing URLs. Could be combined, but if
 * they're separated, the Python routine that provides data needn't be changed from
 * what's required for standard, non-long-polling web app. If they're combined, arguably
 * over-loads the purpose of the function.
 */
function wait_for_update() {
    if (!waiting_for_update) {
        waiting_for_update = true;
        $.ajax({ url: '/updated',
                 success:  load_data,        // if /update signals results ready, load them!
                 complete: function () {
                    waiting_for_update = false;
                    setTimeout(wait_for_update, 50000); // if the wait_for_update poll times out, rerun
                 },
                 timeout:  LONG_POLL_DURATION,
               });
    }

    // wait_for_update guard to ensure not re-entering already running wait code
    // added after user suggestion. This check has not been needed in my apps
    // and testing, but concurrency is an area where an abundance of caution is
    // often the best policy.
}


/**
 * show the data acquired by load_data()
 */
function display_data(data) {
    if (data && (data != prev_data)) {      // if there is data, and it's changed
        // update the contents of several HTML divs via jQuery
        $('#rescue_time_daily_productivity').html(data.rescue_time_daily_productivity);
        $('#rescue_time_daily_unproductivity').html(data.rescue_time_daily_unproductivity);
        $('#rescue_time_daily_top_three').html(data.rescue_time_daily_top_three);
        $('#rescue_time_past_seven_productivity').html(data.rescue_time_past_seven_productivity);
        $('#rescue_time_past_seven_unproductivity').html(data.rescue_time_past_seven_unproductivity);
        $('#rescue_time_past_seven_top_five').html(data.rescue_time_past_seven_top_five);
        // $('#next_bus').html(data.next_bus);
        $('#weight').html(data.weight);
        $('#total_tasks').html("Number of outstanding tasks: " + data.total_tasks);
        $('#daily_completed_tasks').html("Number of tasks completed today: " + data.daily_completed_tasks);
        $('#past_seven_completed_tasks').html("Number of tasks completed in the last 7 days: " + data.past_seven_completed_tasks);
        $('#top_tracks').html(data.top_tracks);
        $('#top_artists').html(data.top_artists);
        $('#weather_hourly').html(data.weather_hourly);
        $('#temp').html(data.temp);
        $('#weather_today').html(data.weather_today);
        $('#current_steps').html("Steps today: " + String(data.current_steps)  + " steps");
        $('#average_past_seven_steps').html(data.average_past_seven_steps),
        $('#chess_rating').html(data.chess_rating);
        $('#chess_games').html(data.chess_games);
        $('#daily_pomodoros').html(data.daily_pomodoros);
        $('#past_seven_days_pomodoros').html(data.past_seven_days_pomodoros);
        //remove loading text from HTML
        $('#loading').remove();

        $.ajax({
            type: 'GET',
            url: 'https://wakatime.com/share/@0c62f2ad-9fa5-43c7-a08f-7b1562918a7d/43cd4128-5361-43db-b51b-d965e3c575a5.json',
            dataType: 'jsonp',
            success: function(response) {
              console.log(response.data);
            },
          });


          $.ajax({
            type: 'GET',
            url: 'https://wakatime.com/share/@0c62f2ad-9fa5-43c7-a08f-7b1562918a7d/27967d19-0ce0-42a6-9f4a-c3c2440cf575.json',
            dataType: 'jsonp',
            success: function(response) {
              console.log(response.data);
            },
          });

        // unproductivity_doughnut = get_unproductivity_doughnut()
        // steps_doughnut = get_steps_doughnut()
        // //This is meant to update the doughnut for unproductivity since my goal is to
        // // have less than 1 hour of unproductive time each day
        // var max_unproductivity_value = 1
        // // We need to get the difference between last update and current update.
        // // first we have to check if prev_Data is null so we don't throw an error
        // var difference_in_unproductivity = prev_data.hasOwnProperty(rescue_time_daily_unproductivity) ? data.rescue_time_daily_unproductivity - prev_data.rescue_time_daily_unproductivity : data.rescue_time_daily_unproductivity;
        // if ((unproductivity_doughnut.segments[0].value >= max_unproductivity_value) || (difference_in_unproductivity >= max_unproductivity_value)) {
        //   unproductivity_doughnut.segments[0].value = max_unproductivity_value;
        //   unproductivity_doughnut.segments[1].value = 0;
        //   steps_doughnut.update()
        // } else {
        //   unproductivity_doughnut.segments[0].value = unproductivity_doughnut.segments[0].value + difference_in_unproductivity;
        //   unproductivity_doughnut.segments[1].value = unproductivity_doughnut.segments[1].value - difference_in_unproductivity;
        //   unproductivity_doughnut.update();
        // }
        //
        // //This is meant to update the steps doughnut since my goal is to have
        // // at least 5000 steps a day
        // var max_steps_value = 5000
        // // We need to get the difference between last update and current update.
        // // first we have to check if prev_Data is null so we don't throw an error
        // var difference_in_steps = prev_data.hasOwnProperty(current_steps) ? data.current_steps - prev_data.current_steps : data.current_steps;
        // if ((steps_doughnut.segments[0].value >= max_steps_value) || (difference_in_steps >= max_steps_value)) {
        //   steps_doughnut.segments[0].value = max_steps_value;
        //   steps_doughnut.segments[1].value = 0;
        //   steps_doughnut.update()
        // } else {
        //   steps_doughnut.segments[0].value = steps_doughnut.segments[0].value + difference_in_steps
        //   steps_doughnut.segments[1].value = steps_doughnut.segments[1].value - difference_in_steps
        //   steps_doughnut.update()
        // }
        // remember this data, in case want to compare it to next update
        prev_data = data;
      }
}

// function get_unproductivity_doughnut(){
//     var max_value = 1.5;
//     chartOptions = {
//         segmentShowStroke: false,
//         percentageInnerCutout: 75,
//         animation: false
//     };
//
//     chartData = [{
//         value: 0,
//         color: '#ff0000'
//     },{
//         value: max_value,
//         color: '#DDDDDD'
//     }];
//     var ctx = $('#unproductivity_doughnut').get(0).getContext("2d");
//     var unproductivity_dougnut = new Chart(ctx).Doughnut(chartData,chartOptions);
//     return unproductivity_dougnut
// }
//
// function get_steps_doughnut(){
//   var max_value = 5000
//   chartOptions = {
//     segmentShowStroke: false,
//     percentageInnerCutout: 75,
//     animation: false
//   };
//
//   chartData = [{
//       value: 0,
//       color: '#4FD134'
//   },{
//       value: max_value,
//       color: '#DDDDDD'
//   }];
//   var ctx = $('#steps_doughnut').get(0).getContext("2d");
//   var steps_doughnut = new Chart(ctx).Doughnut(chartData,chartOptions);
//   return steps_doughnut
// }

function create_doughnuts(){
  $(function () {
    var totalRevenue = 15341110,
        totalUsers = 7687036;

    // CanvasJS doughnut chart to show annual sales percentage from United States(US)
    var steps_doughnut = new CanvasJS.Chart("steps_doughnut", {
      animationEnabled: true,
      backgroundColor: "transparent",
      title: {
        fontColor: "#848484",
        fontSize: 60,
        horizontalAlign: "center",
        text: "47%",
        fontFamily: "Roboto",
        verticalAlign: "center"
      },
      toolTip: {
        backgroundColor: "#ffffff",
        borderThickness: 0,
        cornerRadius: 0,
        fontColor: "#424242"
      },
      data: [
        {
          explodeOnClick: false,
          innerRadius: "94%",
          radius: "90%",
          startAngle: 270,
          type: "doughnut",
          dataPoints: [
            { y: 10, color: "#c70000", toolTipContent: "United States: $<span>" + CanvasJS.formatNumber(Math.round(47 / 100 * totalRevenue), '#,###,###') + "</span>" },
            { y: 90, color: "#424242", toolTipContent: null }
          ]
        }
      ]
    });

    // CanvasJS doughnut chart to show annual sales percentage from Netherlands(NL)
    var pomodoro_doughnut = new CanvasJS.Chart("pomodoro_doughnut", {
      animationEnabled: true,
      backgroundColor: "transparent",
      title: {
        fontColor: "#848484",
        fontSize: 60,
        horizontalAlign: "center",
        text: "19%",
        fontFamily: "Roboto",
        verticalAlign: "center"
      },
      toolTip: {
        backgroundColor: "#ffffff",
        borderThickness: 0,
        cornerRadius: 0,
        fontColor: "#424242"
      },
      data: [
        {
          explodeOnClick: false,
          innerRadius: "96%",
          radius: "90%",
          startAngle: 270,
          type: "doughnut",
          dataPoints: [
            { y: 19, color: "#c70000", toolTipContent: "Netherlands: $<span>" + CanvasJS.formatNumber(Math.round(19 / 100 * totalRevenue), '#,###,###') + "</span>" },
            { y: 81, color: "#424242", toolTipContent: null }
          ]
        }
      ]
    });

    // CanvasJS doughnut chart to show annual sales percentage from Germany(DE)
    var unproductivity_doughnut = new CanvasJS.Chart("unproductivity_doughnut", {
      animationEnabled: true,
      backgroundColor: "transparent",
      title: {
        fontColor: "#848484",
        fontSize: 60,
        horizontalAlign: "center",
        text: "12%",
        fontFamily: "Roboto",
        verticalAlign: "center"
      },
      toolTip: {
        backgroundColor: "#ffffff",
        borderThickness: 0,
        cornerRadius: 0,
        fontColor: "#424242"
      },
      data: [
        {
          explodeOnClick: false,
          innerRadius: "96%",
          radius: "90%",
          startAngle: 270,
          type: "doughnut",
          dataPoints: [
            { y: 12, color: "#c70000", toolTipContent: "Netherlands: $<span>" + CanvasJS.formatNumber(Math.round(12 / 100 * totalRevenue), '#,###,###') + "</span>" },
            { y: 88, color: "#424242", toolTipContent: null }
          ]
        }
      ]
    });

          jQuery.scrollSpeed(100, 400); // for smooth mouse wheel scrolling

    // jQuery.inview plugin
    $('.inview').one('inview', function (e, isInView) {
      if (isInView) {
        switch (this.id) {
          case "steps_doughnut": steps_doughnut.render();
            break;
          case "pomodoro_doughnut": pomodoro_doughnut.render();
            break;
          case "unproductivity_doughnut": unproductivity_doughnut.render();
            break;
        }
      }
    });

  });
}

$(document).ready(function() {
  //Create unproductivity_doughnut
  create_doughnuts();
  load_data();
});
