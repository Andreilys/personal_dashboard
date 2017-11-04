var prev_data = Object();           // remember data fetched last time
var waiting_for_update = false; // are we currently waiting?
var LONG_POLL_DURATION = 60000; // how long should we wait? (msec)
var first_time_rendering_chart = true;
var global_steps_doughnut = Object(),
  global_pomodoro_doughnut = Object(),
  global_unproductive_doughnut = Object(),
  global_coding_chart = Object(),
  global_coding_type_chart = Object(),
  global_rescuetime_pie = Object(),
  global_rescuetime_bar = Object(),
  global_toggl_pie = Object(),
  global_toggl_bar = Object(),
  global_cal = Object();
const STEPS_GOAL = 5000;
const POMODORO_GOAL = 2.5;
const UNPRODUCTIVITY_GOAL = 1;
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
        $('#weight').html(String(data.weight) + " lbs");
        $('#total_tasks').html("Number of outstanding tasks: " + data.total_tasks);
        $('#daily_completed_tasks').html("Number of tasks completed today: " + data.daily_completed_tasks);
        $('#past_seven_completed_tasks').html("Number of tasks completed in the last 7 days: " + data.past_seven_completed_tasks);
        $('#top_tracks').html(data.top_tracks);
        $('#top_artists').html(data.top_artists);
        $('#weather_hourly').html(data.weather_hourly);
        $('#temp').html(data.temp);
        $('#weather_today').html(data.weather_today);
        $('#current_steps').html("Steps today: " + String(data.current_steps)  + " steps");
        $('#average_past_seven_steps').html("Past 7 day avg. " +String(data.average_past_seven_steps) + " steps");
        $('#chess_rating').html(data.chess_rating);
        $('#chess_games').html(data.chess_games);
        $('#daily_pomodoros').html(data.daily_pomodoros);
        $('#past_seven_days_pomodoros').html(String(data.past_seven_days_pomodoros));
        $('#quote_content').html(data.quote_content);
        $('#quote_author').html(data.quote_author);
        //remove loading text from HTML
        $('#loading').remove();

        // {'data': [{'name': 'Python', 'percent': 61.39}, {'name': 'JavaScript', 'percent': 25.49}, {'name': 'HTML', 'percent': 10.29}, {'name': 'CSS', 'percent': 2.83}]}
        //
        coding_time = format_coding_data(data.coding_time);
        coding_type = format_coding_type_data(data.coding_type)
        if (first_time_rendering_chart) {
            global_steps_doughnut = create_steps_doughnut(data);
            global_pomodoro_doughnut = create_pomodoro_doughnut(data);
            global_unproductive_doughnut = create_unproductive_doughnut(data);
            global_cal = create_goal_calendar();
            global_coding_chart = create_coding_chart(coding_time);
            global_coding_type_chart = create_coding_type_chart(coding_type);
            global_rescuetime_pie = create_rescuetime_pie(data.rescue_time_past_seven_productivity, data.rescue_time_past_seven_unproductivity);
            global_rescuetime_bar = create_rescuetime_bar(data.rescuetime_bar_data, data.rescuetime_bar_data_dates);
            global_toggl_pie = create_toggl_pie(data.past_seven_days_pomodoros);
            create_toggl_bar(data.past_seven_days_pomodoros)
            first_time_rendering_chart = false;
        }
        else {
          update_doughnuts(global_steps_doughnut, global_pomodoro_doughnut, global_unproductive_doughnut, data);
          update_coding_chart(coding_time);
          update_coding_type_chart(coding_type);
          update_rescuetime_pie(data.rescue_time_past_seven_productivity, data.rescue_time_past_seven_unproductivity);
          update_rescuetime_bar(data.rescuetime_bar_data, data.rescuetime_bar_data_dates);
          update_toggl_pie(data.past_seven_days_pomodoros);
          global_cal.update('/datesCompletedGoals');
        }

        // remember this data, in case want to compare it to next update
        prev_data = data;
      }
}

function create_goal_calendar(){
  calendar = new CalHeatMap();
  calendar.init({
      itemSelector: "#cal-heatmap",
      domain: "year",
      subDomain: "day",
      data: '/datesCompletedGoals',
      dataType: "json",
      start: new Date(2017, 0),
      cellSize: 10,
      range: 1,
      displayLegend: false
  });
  return calendar;
}

//Row 1 - Start of Doughuts
function update_doughnuts(steps_doughnut, pomodoro_doughnut, unproductive_doughnut, data) {
  var total_pomodoros = 0;
  for (var key in data.daily_doughnut_pomodoro){
    total_pomodoros += data.daily_doughnut_pomodoro[key];
  }
  var current_pomodoro_percent = total_pomodoros > POMODORO_GOAL ? 100 : Math.round(total_pomodoros/POMODORO_GOAL * 100),
      current_steps_percent = data.current_steps > STEPS_GOAL ? 100 : Math.round(data.current_steps/STEPS_GOAL * 100),
      current_unproductive_percent = data.rescue_time_daily_unproductivity > UNPRODUCTIVITY_GOAL ? 100 : Math.round(data.rescue_time_daily_unproductivity/UNPRODUCTIVITY_GOAL * 100);
    //Updating steps doughnut
      steps_doughnut.options.title.text = String(current_steps_percent) + "%";
      steps_doughnut.options.data[0].dataPoints[0].y = current_steps_percent;
      steps_doughnut.options.data[0].dataPoints[1].y = 100 - current_steps_percent;
      steps_doughnut.options.data[0].dataPoints[0].toolTipContent = String(data.current_steps) + " steps",
    //Updating pomodoro doughnut
      pomodoro_doughnut.options.title.text = String(current_pomodoro_percent) + "%";
      pomodoro_doughnut.options.data[0].dataPoints[0].y = current_pomodoro_percent;
      pomodoro_doughnut.options.data[0].dataPoints[1].y = 100 - current_pomodoro_percent;
      pomodoro_doughnut.options.data[0].dataPoints[0].toolTipContent = String(total_pomodoros) + " hours",

    //Updating unproductivity doughnut
    unproductive_doughnut.options.title.text = String(current_unproductive_percent) + "%";
    unproductive_doughnut.options.data[0].dataPoints[0].y = current_unproductive_percent;
    unproductive_doughnut.options.data[0].dataPoints[1].y = 100 - current_unproductive_percent;
    unproductive_doughnut.options.data[0].dataPoints[0].toolTipContent= String(data.rescue_time_daily_unproductivity) + " hours",

    //Re-rendering the doughnuts
    steps_doughnut.render();
    pomodoro_doughnut.render();
    unproductive_doughnut.render();
}


function create_pomodoro_doughnut(data){
  var total_pomodoros = 0;
  for (var key in data.daily_doughnut_pomodoro){
    total_pomodoros += data.daily_doughnut_pomodoro[key];
  }
  var current_pomodoro_percent = total_pomodoros > POMODORO_GOAL ? 100 : Math.round(total_pomodoros/POMODORO_GOAL * 100);
  var pomodoro_doughnut = new CanvasJS.Chart("pomodoro_doughnut", {
    animationEnabled: true,
    backgroundColor: "transparent",
    title: {
      fontColor: "#848484",
      fontSize: 60,
      horizontalAlign: "center",
      text: String(current_pomodoro_percent) + "%",
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
          { y: current_pomodoro_percent, color: "#33702a", toolTipContent: String(total_pomodoros) + " hours"},
          { y: 100 - current_pomodoro_percent, color: "#424242", toolTipContent: null }
        ]
      }
    ]
  });

  pomodoro_doughnut.render();
  return pomodoro_doughnut;
}


function create_unproductive_doughnut(data){
  var current_unproductive_percent = data.rescue_time_daily_unproductivity > UNPRODUCTIVITY_GOAL ? 100 : Math.round(data.rescue_time_daily_unproductivity/UNPRODUCTIVITY_GOAL * 100);
  var unproductive_doughnut = new CanvasJS.Chart("unproductivity_doughnut", {
    animationEnabled: true,
    backgroundColor: "transparent",
    title: {
      fontColor: "#848484",
      fontSize: 60,
      horizontalAlign: "center",
      text: String(current_unproductive_percent) + "%",
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
          { y: current_unproductive_percent, color: "#b30000", toolTipContent: String(data.rescue_time_daily_unproductivity) + " hours"},
          { y: 100 - current_unproductive_percent, color: "#424242", toolTipContent: null }
        ]
      }
    ]
  });

  unproductive_doughnut.render()
  return unproductive_doughnut;
}


//This creates and returns the steps doughnut chart
function create_steps_doughnut(data) {
    var current_steps_percent = data.current_steps > STEPS_GOAL ? 100 : Math.round(data.current_steps/STEPS_GOAL * 100);
    var steps_doughnut = new CanvasJS.Chart("steps_doughnut", {
      animationEnabled: true,
      backgroundColor: "transparent",
      title: {
        fontColor: "#848484",
        fontSize: 60,
        horizontalAlign: "center",
        text: String(current_steps_percent) + "%",
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
            { y: current_steps_percent, color: "#33702a", toolTipContent: String(data.current_steps) + " steps" },
            { y: 100 - current_steps_percent, color: "#424242", toolTipContent: null }
          ]
        }
      ]
    });
    // jQuery.inview plugin
    steps_doughnut.render()
    return steps_doughnut;
}


// Row 2: Start of Coding data
//Helper function to format the dates for Chartjs column graph
function changing_date_format(coding_time_unformatted){
  coding_time_formatted = []
  for (data of coding_time_unformatted){
    months_days = data['range']['date'].split('-').slice(1).join('-');
    year = data['range']['date'].split('-')[0];
    new_date = months_days + "-" + year
    data['range']['date'] = new_date
    coding_time_formatted.push(data)
  }
  return coding_time_formatted
}


function format_coding_data(coding_time_unformatted){
  coding_time_formatted = changing_date_format(coding_time_unformatted)
  coding_time = []
  for (data of coding_time_formatted) {
    coding_time.push({x: new Date(data['range']['date']), y: data['grand_total']['total_seconds']/60/60});
  }
  return coding_time
}

function format_coding_type_data(coding_type_unformated){
  coding_type = []
  for (data of coding_type_unformated) {
    coding_type.push({name: data['name'], y: data['percent'], indexLabel: String(data['name']) + " - " + String(data['percent']) + "%", legendText: data['name']});
  }
  return coding_type
}

function update_coding_chart(coding_time){
    global_coding_chart = create_coding_chart(coding_time);
    global_coding_chart.render();
}

function create_coding_chart(coding_time) {
  var coding_chart = new CanvasJS.Chart("coding_time", {
    animationEnabled: true,
    backgroundColor: "transparent",
    theme: "theme2",
    axisX: {
      labelFontSize: 14,
      valueFormatString: "MMM DD"
    },
    axisY: {
      labelFontSize: 14,
    },
    toolTip: {
      borderThickness: 0,
      cornerRadius: 0
    },
    data: [
      {
        type: "column",
        color: "#27a6e5",
        yValueFormatString: "###,###.##",
        dataPoints: coding_time
      }
    ]
  });
  coding_chart.render();
  return coding_chart;
}


function update_coding_type_chart(coding_type){
  global_coding_type_chart = create_coding_type_chart(coding_type);
  global_coding_type_chart.render();

}

function create_coding_type_chart(){
  var create_coding_type_chart = new CanvasJS.Chart("coding_type", {
    animationEnabled: true,
    theme: "theme2",
    legend: {
      fontSize: 12,
      display: true,
      position: 'bottom',
      fullWidth: true,
      reverse: false,
    },
    toolTip: {
      borderThickness: 0,
      content: "<span style='\"'color: {color};'\"'>{name}</span>: {y}%",
      cornerRadius: 0
    },
    data: [
      {
        indexLabelFontColor: "#676464",
        indexLabelFontSize: 10,
        legendMarkerType: "square",
        legendText: "{indexLabel}",
        showInLegend: true,
        startAngle:  90,
        type: "pie",
        dataPoints: coding_type
      }
    ]
  });

  create_coding_type_chart.render();
  return create_coding_type_chart;
}

//Row 3 Rescuetime Data
function format_rescuetime_data(rescue_time_past_seven_productivity, rescue_time_past_seven_unproductivity){
  rescuetime_weekly_data = [];
  total = rescue_time_past_seven_productivity + rescue_time_past_seven_unproductivity;
  rescuetime_weekly_data.push({name: "Productive Time", y: rescue_time_past_seven_productivity, indexLabel: "Productive Hours" + " - " + String(rescue_time_past_seven_productivity) + " (" + String((rescue_time_past_seven_productivity/total*100).toFixed(2)) + "%)", legendText: "Productive Hours"});
  rescuetime_weekly_data.push({name: "Unproductive Time", y: rescue_time_past_seven_unproductivity, indexLabel: "Unproductive Hours" + " - " + String(rescue_time_past_seven_unproductivity) + " (" + String((rescue_time_past_seven_unproductivity/total*100).toFixed(2)) + "%)", legendText: "Unproductive Hours"});
  return rescuetime_weekly_data;
}


function update_rescuetime_pie(rescue_time_past_seven_productivity, rescue_time_past_seven_unproductivity){
  global_rescuetime_pie = create_rescuetime_pie(rescue_time_past_seven_productivity, rescue_time_past_seven_unproductivity);
  global_rescuetime_pie.render();
}


function create_rescuetime_pie(rescue_time_past_seven_productivity, rescue_time_past_seven_unproductivity){
  var rescuetime_weekly_data = format_rescuetime_data(rescue_time_past_seven_productivity, rescue_time_past_seven_unproductivity);
  var rescuetime_pie = new CanvasJS.Chart("rescuetime_pie", {
    animationEnabled: true,
    theme: "theme2",
    legend: {
      fontSize: 12,
      display: true,
      position: 'bottom',
      fullWidth: true,
      reverse: false,
    },
    toolTip: {
      borderThickness: 0,
      content: "<span style='\"'color: {color};'\"'>{name}</span>: {y}",
      cornerRadius: 0
    },
    data: [
      {
        indexLabelFontColor: "#676464",
        indexLabelFontSize: 10,
        legendMarkerType: "square",
        legendText: "{indexLabel}",
        showInLegend: true,
        startAngle:  90,
        type: "pie",
        dataPoints: rescuetime_weekly_data
      }
    ]
  });
  rescuetime_pie.render();
  return rescuetime_pie;
}

function update_rescuetime_bar(rescuetime_data, dates){
  global_rescuetime_bar = create_rescuetime_bar(rescuetime_data, dates);
  global_rescuetime_pie.render();
}

function create_rescuetime_bar(rescuetime_data, dates){
  var ctx = document.getElementById("rescuetime_bar");
  var rescuetime_bar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: dates,
      datasets: rescuetime_data
    },
    options: {
      animation: {
        duration: 0
      },
       barValueSpacing: 20,
       scales: {
           yAxes: [{
               ticks: {
                   min: 0,
               }
           }]
       }
     }
   });

  rescuetime_bar.render()
  return rescuetime_bar;
}

//Row 4 Toggl data
function format_toggl_data(toggl_data){
  toggl_weekly_data = [];
  total = 0;
  for (var key in toggl_data){
    total += toggl_data[key];
  }
  for (var key in toggl_data) {
    toggl_weekly_data.push({name: key, y: toggl_data[key], indexLabel: String(key) + " - " + String(toggl_data[key]) + " (" + String((toggl_data[key]/total*100).toFixed(2)) + "%)", legendText: key});
  }
  return toggl_weekly_data;
}


function update_toggl_pie(toggl_data){
  global_toggl_pie = create_toggl_pie(toggl_data);
  global_toggl_pie.render();
}


function create_toggl_pie(toggl_data){
  var toggl_data_formatted = format_toggl_data(toggl_data);
  var toggl_pie = new CanvasJS.Chart("toggl_pie", {
    animationEnabled: true,
    theme: "theme2",
    legend: {
      fontSize: 14,
      display: true,
      position: 'bottom',
      fullWidth: true,
      reverse: false,
    },
    toolTip: {
      borderThickness: 0,
      content: "<span style='\"'color: {color};'\"'>{name}</span>: {y}",
      cornerRadius: 0
    },
    data: [
      {
        indexLabelFontColor: "#676464",
        indexLabelFontSize: 10,
        legendMarkerType: "square",
        legendText: "{indexLabel}",
        showInLegend: true,
        startAngle:  90,
        type: "pie",
        dataPoints: toggl_data_formatted
      }
    ]
  });
  toggl_pie.render();
  return toggl_pie;
}
//
// function format_toggl_data_bar(toggl_data){
//   toggl_data_formatted = []
//   for (data in toggl_data){
//     data_points_formatted = []
//     for (other_data in data){
//       data_points_formatted.push(x: new Date(other_data['date']), y: other_data['value'])
//     }
//     toggl_data_formatted.push({type:"stackedBar", dataPoints: data_points_formatted})
//   }
//   return toggl_data_formatted;
// }


function update_toggl_bar(toggl_data){
  global_toggl_bar = create_toggl_bar(rescuetime_data, dates);
  global_toggl_bar.render();
}


function create_toggl_bar(toggl_data){
  // toggl_data_formatted = format_toggl_data_bar(toggl_data)
  var chart = new CanvasJS.Chart("toggl_bar",
    {
      data: [
        {
        type: "stackedBar",
         dataPoints: [
        { x: new Date(2012, 01, 1), y: 71 },
        { x: new Date(2012, 02, 1), y: 55},
        { x: new Date(2012, 03, 1), y: 50 },
        { x: new Date(2012, 04, 1), y: 65 },
        { x: new Date(2012, 05, 1), y: 95 }

        ]
      },
        {
        type: "stackedBar",
         dataPoints: [
           { x: new Date(2012, 01, 1), y: 71 },
           { x: new Date(2012, 02, 1), y: 55},
           { x: new Date(2012, 03, 1), y: 50 },
           { x: new Date(2012, 04, 1), y: 65 },
           { x: new Date(2012, 05, 1), y: 95 }

        ]
      }
      ]
    });
    chart.render();
    return chart;
}

$(document).ready(function() {
  //Create unproductivity_doughnut
  load_data();
});
